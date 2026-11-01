import http from 'http';
import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '..');
const SCREENSHOTS_DESKTOP_DIR = path.join(ROOT_DIR, 'docs', 'screenshots', 'after_desktop');
const SCREENSHOTS_MOBILE_DIR = path.join(ROOT_DIR, 'docs', 'screenshots', 'after_mobile');

for (const d of [SCREENSHOTS_DESKTOP_DIR, SCREENSHOTS_MOBILE_DIR]) {
  if (!fs.existsSync(d)) {
    fs.mkdirSync(d, { recursive: true });
  }
}

const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const CDP_PORT = 9555;
const chrome = spawn(chromePath, [
  '--headless=new',
  `--remote-debugging-port=${CDP_PORT}`,
  '--disable-gpu',
  '--window-size=1440,900',
  '--user-data-dir=C:\\Users\\USER\\AppData\\Local\\Temp\\chrome_outskill_verify',
]);

console.log('[*] Launched Chrome verification on port', CDP_PORT);

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

class CDPClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.msgId = 1;
    this.pending = new Map();
    this.consoleLogs = [];
  }

  async connect() {
    this.ws = new WebSocket(this.wsUrl);
    this.ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.method === 'Runtime.consoleAPICalled') {
        const text = msg.params.args.map((a) => a.value || a.description || '').join(' ');
        this.consoleLogs.push({ type: msg.params.type, text });
      }
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        if (msg.error) {
          reject(msg.error);
        } else {
          resolve(msg.result);
        }
      }
    };
    await new Promise((resolve) => {
      if (this.ws.readyState === WebSocket.OPEN) resolve();
      else this.ws.onopen = resolve;
    });
  }

  send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = this.msgId++;
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  async evaluate(expression) {
    const res = await this.send('Runtime.evaluate', {
      expression,
      returnByValue: true,
      awaitPromise: true,
    });
    if (res.exceptionDetails) {
      console.error('Eval error:', res.exceptionDetails);
      return null;
    }
    return res.result?.value;
  }

  async setViewport(width, height, isMobile = false) {
    await this.send('Emulation.setDeviceMetricsOverride', {
      width,
      height,
      deviceScaleFactor: 1,
      mobile: isMobile,
    });
    await sleep(400);
  }

  async screenshot(filePath) {
    const res = await this.send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(filePath, Buffer.from(res.data, 'base64'));
  }

  close() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

const MODULES = [
  { name: '01_dashboard', path: '/', title: 'Overview Dashboard' },
  { name: '02_scheduling_workspace', path: '/scheduling', title: 'Scheduling Workspace' },
  { name: '03_exception_center', path: '/exceptions', title: 'Exception Center' },
  { name: '04_exam_management', path: '/exams', title: 'Exam Management' },
  { name: '05_student_management', path: '/students', title: 'Student Management' },
  { name: '06_course_management', path: '/courses', title: 'Course Management' },
  { name: '07_room_management', path: '/rooms', title: 'Room Management' },
  { name: '08_invigilator_management', path: '/invigilators', title: 'Invigilator Management' },
  { name: '09_accommodation_management', path: '/accommodations', title: 'Accommodation Management' },
  { name: '10_analytics_reports', path: '/analytics', title: 'Analytics & Reports' },
  { name: '11_audit_activity', path: '/audit', title: 'Audit & Activity' },
  { name: '12_administration', path: '/admin', title: 'Administration' },
];

async function main() {
  try {
    await sleep(2500);
    const version = await getJson(`http://127.0.0.1:${CDP_PORT}/json/version`);
    console.log('[*] Connected to Chrome CDP:', version.Browser);

    const targets = await getJson(`http://127.0.0.1:${CDP_PORT}/json/list`);
    let target = targets.find((t) => t.type === 'page');
    if (!target) {
      target = await getJson(`http://127.0.0.1:${CDP_PORT}/json/new?http://localhost:5173/`);
    }

    const client = new CDPClient(target.webSocketDebuggerUrl);
    await client.connect();

    await client.send('Page.enable');
    await client.send('Runtime.enable');

    // First, visit root and verify auth
    await client.send('Page.navigate', { url: 'http://localhost:5173/' });
    await sleep(3000);

    const verificationResults = [];

    for (const mod of MODULES) {
      console.log(`\n========================================`);
      console.log(`Testing Module: ${mod.title} (${mod.path})`);
      console.log(`========================================`);

      await client.send('Page.navigate', { url: `http://localhost:5173${mod.path}` });
      await sleep(2500); // Allow data fetch and react render

      // 1. Desktop Viewport (1440x900)
      await client.setViewport(1440, 900, false);
      const desktopShot = path.join(SCREENSHOTS_DESKTOP_DIR, `${mod.name}.png`);
      await client.screenshot(desktopShot);
      console.log(`  [+] Desktop 1440x900 screenshot saved`);

      // 2. Mobile Viewport (390x844)
      await client.setViewport(390, 844, true);
      const mobileShot = path.join(SCREENSHOTS_MOBILE_DIR, `${mod.name}.png`);
      await client.screenshot(mobileShot);
      console.log(`  [+] Mobile 390x844 screenshot saved`);

      // Reset to desktop for DOM evaluation
      await client.setViewport(1440, 900, false);

      // Evaluate Computed Styles and DOM metrics
      const domMetrics = await client.evaluate(`(() => {
        const bodyStyle = window.getComputedStyle(document.body);
        const heading = document.querySelector('h1, h2')?.innerText || '';
        const tableRows = document.querySelectorAll('tbody tr').length;
        const buttons = Array.from(document.querySelectorAll('button')).map(b => ({
          text: b.innerText.trim(),
          bg: window.getComputedStyle(b).backgroundColor,
          color: window.getComputedStyle(b).color,
          border: window.getComputedStyle(b).borderColor,
          radius: window.getComputedStyle(b).borderRadius
        }));
        const hasError = document.body.innerText.includes('Failed to load') || document.body.innerText.includes('Network Error');
        const svgs = document.querySelectorAll('svg').length;
        const cards = document.querySelectorAll('[class*="bg-brand-surface"], [class*="bg-[#121212]"]').length;

        // Check for presence of Outskill Lime (#B8EF43 or rgb(184, 239, 67))
        const allElements = Array.from(document.querySelectorAll('*'));
        let limeCount = 0;
        for (const el of allElements) {
          const s = window.getComputedStyle(el);
          if (s.backgroundColor.includes('184, 239, 67') || s.color.includes('184, 239, 67') || s.borderColor.includes('184, 239, 67')) {
            limeCount++;
          }
        }

        return {
          bodyBg: bodyStyle.backgroundColor,
          bodyColor: bodyStyle.color,
          heading,
          tableRows,
          hasError,
          svgs,
          cards,
          limeCount,
          sampleButtons: buttons.slice(0, 3)
        };
      })()`);

      console.log(`  Body Background: ${domMetrics.bodyBg}`);
      console.log(`  Heading: "${domMetrics.heading}"`);
      console.log(`  Table Rows: ${domMetrics.tableRows}`);
      console.log(`  Has Error: ${domMetrics.hasError}`);
      console.log(`  Outskill Lime Elements Count: ${domMetrics.limeCount}`);
      if (domMetrics.sampleButtons.length > 0) {
        console.log(`  Sample Button: "${domMetrics.sampleButtons[0].text}" -> bg: ${domMetrics.sampleButtons[0].bg}, text: ${domMetrics.sampleButtons[0].color}`);
      }

      const pass = !domMetrics.hasError && domMetrics.bodyBg.includes('8, 9, 10');
      verificationResults.push({
        module: mod.title,
        route: mod.path,
        bodyBg: domMetrics.bodyBg,
        tableRows: domMetrics.tableRows,
        limeElements: domMetrics.limeCount,
        hasError: domMetrics.hasError,
        status: pass ? 'PASS' : 'FAIL'
      });
    }

    console.log('\n' + '='.repeat(80));
    console.log('OUTSKILL THEME MIGRATION VERIFICATION MATRIX:');
    console.table(verificationResults);
    console.log('='.repeat(80));

    // Save results summary JSON
    fs.writeFileSync(
      path.join(ROOT_DIR, 'docs', 'design', 'verification_results.json'),
      JSON.stringify({ timestamp: new Date().toISOString(), results: verificationResults, consoleLogs: client.consoleLogs.slice(-20) }, null, 2)
    );

    client.close();
  } catch (err) {
    console.error('Verification script failed:', err);
  } finally {
    console.log('[*] Terminating Chrome test runner...');
    chrome.kill();
  }
}

main();

