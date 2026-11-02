import http from 'http';
import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '..');
const SCREENSHOTS_DIR = path.join(ROOT_DIR, 'docs', 'screenshots', 'responsive');

if (!fs.existsSync(SCREENSHOTS_DIR)) {
  fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

const PORT = 5174;
const BASE_URL = `http://localhost:${PORT}`;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function getJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => (data += chunk));
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

async function main() {
  console.log('====================================================');
  console.log('ExamOps Browser Responsive & Language Verification');
  console.log('====================================================');

  // 1. Launch Chrome Headless with CDP
  const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
  const chrome = spawn(chromePath, [
    '--headless=new',
    '--remote-debugging-port=9222',
    '--disable-gpu',
    '--window-size=1440,900',
    '--user-data-dir=C:\\Users\\USER\\AppData\\Local\\Temp\\chrome_cdp_responsive_test',
  ]);

  console.log('[*] Chrome spawned with PID:', chrome.pid);
  await sleep(2500);

  // 2. Connect to CDP
  let target;
  try {
    const targets = await getJson('http://127.0.0.1:9222/json/list');
    target = targets.find((t) => t.type === 'page');
    if (!target) {
      target = await getJson(`http://127.0.0.1:9222/json/new?${BASE_URL}/`);
    }
  } catch (err) {
    console.error('[-] Could not connect to Chrome CDP:', err.message);
    chrome.kill();
    process.exit(1);
  }

  const ws = new WebSocket(target.webSocketDebuggerUrl);

  let msgId = 1;
  const pending = new Map();

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      if (msg.error) {
        reject(msg.error);
      } else {
        resolve(msg.result);
      }
    }
  };

  function send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = msgId++;
      pending.set(id, { resolve, reject });
      ws.send(JSON.stringify({ id, method, params }));
    });
  }

  await new Promise((resolve) => {
    if (ws.readyState === WebSocket.OPEN) resolve();
    else ws.onopen = resolve;
  });

  console.log('[*] Connected to Chrome DevTools Protocol via WebSocket.');

  await send('Page.enable');
  await send('Runtime.enable');
  await send('DOM.enable');

  const viewports = [
    { name: 'desktop_1440x900', width: 1440, height: 900, isMobile: false },
    { name: 'tablet_768x1024', width: 768, height: 1024, isMobile: true },
    { name: 'mobile_375x812', width: 375, height: 812, isMobile: true },
  ];

  const modules = [
    { id: 1, name: 'Overview Dashboard', path: '/', slug: '01_dashboard' },
    { id: 2, name: 'Scheduling Operations', path: '/scheduling', slug: '02_scheduling' },
    { id: 3, name: 'Examination Directory', path: '/exams', slug: '03_exams' },
    { id: 4, name: 'Student Registry', path: '/students', slug: '04_students' },
    { id: 5, name: 'Courses & Enrollments', path: '/courses', slug: '05_courses' },
    { id: 6, name: 'Rooms & Facilities', path: '/rooms', slug: '06_rooms' },
    { id: 7, name: 'Invigilators & Shifts', path: '/invigilators', slug: '07_invigilators' },
    { id: 8, name: 'Accommodations & Support', path: '/accommodations', slug: '08_accommodations' },
    { id: 9, name: 'Issue & Conflict Center', path: '/exceptions', slug: '09_exceptions' },
    { id: 10, name: 'Analytics & Reports', path: '/analytics', slug: '10_analytics' },
    { id: 11, name: 'Audit & Activity Log', path: '/audit', slug: '11_audit' },
    { id: 12, name: 'Administration & Settings', path: '/admin', slug: '12_admin' },
  ];

  const verificationResults = [];

  for (const mod of modules) {
    console.log(`\n====================================================`);
    console.log(`Testing Module ${mod.id}: ${mod.name} (${mod.path})`);
    console.log(`====================================================`);

    const modResult = {
      id: mod.id,
      name: mod.name,
      path: mod.path,
      viewports: {},
      languageAuditPassed: true,
      jargonFound: [],
      horizontalOverflowFound: false,
    };

    for (const vp of viewports) {
      await send('Emulation.setDeviceMetricsOverride', {
        width: vp.width,
        height: vp.height,
        deviceScaleFactor: 1,
        mobile: vp.isMobile,
      });

      await send('Page.navigate', { url: `${BASE_URL}${mod.path}` });
      await sleep(1800);

      // Evaluate responsive health and language check
      const evalRes = await send('Runtime.evaluate', {
        expression: `
          (() => {
            const docWidth = document.documentElement.scrollWidth;
            const winWidth = window.innerWidth;
            const hasHorizontalOverflow = docWidth > winWidth + 1; // 1px threshold for fractional pixels
            const title = document.querySelector('h1')?.innerText || document.querySelector('h2')?.innerText || '';
            const bodyText = document.body.innerText;
            
            // Check for forbidden raw technical jargon
            const forbiddenJargon = [
              'Execute Solver',
              'Algorithmic Decision Telemetry',
              'State Mutation Payload',
              'Deterministic Constraint Satisfaction',
              'Feasibility yield',
              'Authorization Rejection (HTTP 403)',
              'Synchronous candidate desks',
              'Clinical Documentation'
            ];

            const foundJargon = forbiddenJargon.filter(j => bodyText.includes(j));
            const hasErrorMessage = bodyText.includes('Failed to load') || bodyText.includes('Network Error');
            const tableRowCount = document.querySelectorAll('tbody tr').length;
            const buttonCount = document.querySelectorAll('button').length;

            return {
              docWidth,
              winWidth,
              hasHorizontalOverflow,
              title,
              foundJargon,
              hasErrorMessage,
              tableRowCount,
              buttonCount,
            };
          })()
        `,
        returnByValue: true,
      });

      const data = evalRes.result?.value || {};
      const statusPass = !data.hasHorizontalOverflow && data.foundJargon.length === 0;

      console.log(`  [${vp.name}] Width: ${data.docWidth}/${data.winWidth}px | Overflow: ${data.hasHorizontalOverflow ? 'FAIL' : 'PASS'} | Jargon: ${data.foundJargon.length === 0 ? 'CLEAN' : data.foundJargon.join(', ')}`);

      if (data.hasHorizontalOverflow) {
        modResult.horizontalOverflowFound = true;
      }
      if (data.foundJargon.length > 0) {
        modResult.languageAuditPassed = false;
        modResult.jargonFound.push(...data.foundJargon);
      }

      modResult.viewports[vp.name] = {
        passed: statusPass,
        overflow: data.hasHorizontalOverflow,
        title: data.title,
        tableRows: data.tableRowCount,
        buttons: data.buttonCount,
      };

      // Capture screenshot
      const shot = await send('Page.captureScreenshot', { format: 'png' });
      const filename = `${mod.slug}_${vp.name}.png`;
      fs.writeFileSync(path.join(SCREENSHOTS_DIR, filename), Buffer.from(shot.data, 'base64'));
    }

    verificationResults.push(modResult);
  }

  // 3. Test Mobile Drawer & Interaction Workflows
  console.log('\n--- Testing Mobile Hamburger Navigation & Interactive Workflows ---');
  await send('Emulation.setDeviceMetricsOverride', {
    width: 375,
    height: 812,
    deviceScaleFactor: 1,
    mobile: true,
  });

  await send('Page.navigate', { url: `${BASE_URL}/` });
  await sleep(1500);

  // Click hamburger menu
  const menuTest = await send('Runtime.evaluate', {
    expression: `
      (() => {
        const menuBtn = document.querySelector('button[aria-label="Open menu"]');
        if (menuBtn) {
          menuBtn.click();
          return { clicked: true };
        }
        return { clicked: false, error: 'Menu button not found' };
      })()
    `,
    returnByValue: true,
  });
  console.log('  [*] Mobile menu clicked:', menuTest.result?.value);
  await sleep(600);

  // Capture mobile drawer open
  const menuShot = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(path.join(SCREENSHOTS_DIR, 'mobile_navigation_drawer_open.png'), Buffer.from(menuShot.data, 'base64'));

  // Test Admin tab switching
  console.log('  [*] Testing Admin tabs on tablet view...');
  await send('Emulation.setDeviceMetricsOverride', {
    width: 768,
    height: 1024,
    deviceScaleFactor: 1,
    mobile: true,
  });
  await send('Page.navigate', { url: `${BASE_URL}/admin` });
  await sleep(1500);

  await send('Runtime.evaluate', {
    expression: `
      (() => {
        const tabs = Array.from(document.querySelectorAll('button')).filter(b => b.innerText.includes('Scheduling Rules'));
        if (tabs[0]) tabs[0].click();
      })()
    `,
  });
  await sleep(600);
  const tabShot = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(path.join(SCREENSHOTS_DIR, 'admin_scheduling_rules_tab_tablet.png'), Buffer.from(tabShot.data, 'base64'));

  // Save full results JSON
  fs.writeFileSync(
    path.join(ROOT_DIR, 'docs', 'frontend', 'responsive_test_results.json'),
    JSON.stringify(verificationResults, null, 2)
  );

  console.log('\n[✔] Automated Responsive & Language Browser Verification Complete!');
  console.log(`[✔] Captured screenshots saved to: ${SCREENSHOTS_DIR}`);

  chrome.kill();
  process.exit(0);
}

main().catch((err) => {
  console.error('Fatal execution error:', err);
  process.exit(1);
});

