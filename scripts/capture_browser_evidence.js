import http from 'http';
import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '..');
const SCREENSHOTS_DIR = path.join(ROOT_DIR, 'docs', 'screenshots');

if (!fs.existsSync(SCREENSHOTS_DIR)) {
  fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

// 1. Launch Chrome Headless
const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const chrome = spawn(chromePath, [
  '--headless=new',
  '--remote-debugging-port=9222',
  '--disable-gpu',
  '--window-size=1440,900',
  '--user-data-dir=C:\\Users\\USER\\AppData\\Local\\Temp\\chrome_cdp_eval',
]);

console.log('[*] Launched Chrome with PID:', chrome.pid);

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

async function run() {
  await sleep(2500);

  // Get active target
  const version = await getJson('http://127.0.0.1:9222/json/version');
  console.log('[*] Connected to Chrome CDP:', version.Browser);

  const targets = await getJson('http://127.0.0.1:9222/json/list');
  let target = targets.find((t) => t.type === 'page');
  if (!target) {
    target = await getJson('http://127.0.0.1:9222/json/new?http://localhost:5173/');
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

  console.log('[*] WebSocket connected to page debugger.');

  await send('Page.enable');
  await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', {
    width: 1440,
    height: 900,
    deviceScaleFactor: 1,
    mobile: false,
  });

  const routes = [
    { name: '01_overview_dashboard', path: '/', title: 'Overview Dashboard' },
    { name: '02_scheduling_workspace', path: '/scheduling', title: 'Scheduling Workspace' },
    { name: '03_exam_management', path: '/exams', title: 'Exam Management' },
    { name: '04_student_management', path: '/students', title: 'Student Management' },
    { name: '05_course_management', path: '/courses', title: 'Course Management' },
    { name: '06_room_management', path: '/rooms', title: 'Room Management' },
    { name: '07_invigilator_management', path: '/invigilators', title: 'Invigilator Management' },
    { name: '08_accommodation_management', path: '/accommodations', title: 'Accommodation Management' },
    { name: '09_exception_center', path: '/exceptions', title: 'Exception Center' },
    { name: '10_analytics_reports', path: '/analytics', title: 'Analytics & Reports' },
    { name: '11_audit_activity', path: '/audit', title: 'Audit & Activity' },
    { name: '12_administration', path: '/admin', title: 'Administration' },
  ];

  const results = [];

  for (const r of routes) {
    console.log(`\n--- Inspecting Module: ${r.title} (${r.path}) ---`);
    await send('Page.navigate', { url: `http://localhost:5173${r.path}` });
    await sleep(2200); // Allow data fetch and react render

    // Check page DOM
    const evalRes = await send('Runtime.evaluate', {
      expression: `
        (() => {
          const bodyText = document.body.innerText;
          const tableRows = document.querySelectorAll('tbody tr').length;
          const hasError = bodyText.includes('Failed to load') || bodyText.includes('Network Error');
          const heading = document.querySelector('h1')?.innerText || document.querySelector('h2')?.innerText || '';
          return {
            heading,
            tableRows,
            hasError,
            textSnippet: bodyText.substring(0, 300).replace(/\\n+/g, ' ')
          };
        })()
      `,
      returnByValue: true,
    });

    const info = evalRes.result.value;
    console.log(`  Heading: "${info.heading}"`);
    console.log(`  Table Rows: ${info.tableRows}`);
    console.log(`  Has Error: ${info.hasError}`);
    console.log(`  Snippet: ${info.textSnippet.substring(0, 100)}...`);

    // Capture screenshot
    const shotRes = await send('Page.captureScreenshot', { format: 'png' });
    const shotPath = path.join(SCREENSHOTS_DIR, `${r.name}.png`);
    fs.writeFileSync(shotPath, Buffer.from(shotRes.data, 'base64'));
    console.log(`  [PASS] Screenshot saved: ${shotPath} (${Math.round(shotRes.data.length * 0.75 / 1024)} KB)`);

    results.push({
      module: r.title,
      route: r.path,
      heading: info.heading,
      tableRows: info.tableRows,
      status: !info.hasError ? 'PASS' : 'FAIL',
    });
  }

  // Close debugger and Chrome
  ws.close();
  chrome.kill();

  console.log('\n' + '='.repeat(70));
  console.log('BROWSER VALIDATION SUMMARY:');
  console.table(results);
  console.log('='.repeat(70));
}

run().catch((err) => {
  console.error('[!] Test run error:', err);
  if (chrome) chrome.kill();
  process.exit(1);
});

