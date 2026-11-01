import http from 'http';
import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '..');
const SCREENSHOTS_DIR = path.join(ROOT_DIR, 'docs', 'screenshots');

const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const CDP_PORT = 9777;
const chrome = spawn(chromePath, [
  '--headless=new',
  `--remote-debugging-port=${CDP_PORT}`,
  '--disable-gpu',
  '--window-size=1440,900',
  '--user-data-dir=C:\\Users\\USER\\AppData\\Local\\Temp\\chrome_new_icon_test',
]);

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
  }

  async connect() {
    this.ws = new WebSocket(this.wsUrl);
    this.ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
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

  async screenshot(filePath) {
    const res = await this.send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(filePath, Buffer.from(res.data, 'base64'));
    console.log(`[+] Captured: ${path.relative(ROOT_DIR, filePath)}`);
  }

  close() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

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

    // 1. Capture Dashboard with new sidebar brand icon
    await client.send('Page.navigate', { url: 'http://localhost:5173/' });
    await sleep(2500);
    await client.screenshot(path.join(SCREENSHOTS_DIR, 'after_desktop', '01_dashboard.png'));

    // 2. Capture close-up of icon and favicon preview
    await client.send('Page.navigate', { url: 'http://localhost:5173/icon_preview.html' });
    await sleep(1500);
    await client.screenshot(path.join(SCREENSHOTS_DIR, 'examops_brand_icon_and_favicon_preview.png'));

    client.close();
    console.log('[*] Done capturing icon evidence.');
  } catch (err) {
    console.error('Error during icon capture:', err);
  } finally {
    chrome.kill();
  }
}

main();
