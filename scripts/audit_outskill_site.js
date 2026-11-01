import http from 'http';
import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '..');
const SCREENSHOTS_DIR = path.join(ROOT_DIR, 'docs', 'design', 'screenshots');
const DESIGN_DIR = path.join(ROOT_DIR, 'docs', 'design');

if (!fs.existsSync(SCREENSHOTS_DIR)) {
  fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const CDP_PORT = 9333;
const chrome = spawn(chromePath, [
  '--headless=new',
  `--remote-debugging-port=${CDP_PORT}`,
  '--disable-gpu',
  '--window-size=1440,900',
  '--user-data-dir=C:\\Users\\USER\\AppData\\Local\\Temp\\chrome_outskill_audit',
]);

console.log('[*] Launched Chrome with PID:', chrome.pid, 'on port', CDP_PORT);

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
    console.log(`[+] Saved screenshot: ${path.relative(ROOT_DIR, filePath)}`);
  }

  async navigate(url) {
    console.log(`[*] Navigating to ${url}...`);
    await this.send('Page.navigate', { url });
    await sleep(6000); // Allow react hydration and external assets to settle
  }

  close() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// In-browser style extraction function
const extractStylesScript = `(() => {
  const result = {
    url: window.location.href,
    title: document.title,
    cssVariables: {},
    computedTokens: {},
    elements: [],
    gradients: [],
    svgs: []
  };

  // 1. CSS Custom Properties
  try {
    for (const sheet of document.styleSheets) {
      try {
        for (const rule of sheet.cssRules) {
          if (rule.selectorText === ':root' || rule.selectorText === 'html' || rule.selectorText === 'body') {
            for (let i = 0; i < rule.style.length; i++) {
              const prop = rule.style[i];
              if (prop.startsWith('--')) {
                result.cssVariables[prop] = rule.style.getPropertyValue(prop).trim();
              }
            }
          }
        }
      } catch (e) {
        // Cross-origin stylesheet restriction
      }
    }
  } catch (e) {}

  // 2. Sample computed styles of key semantic elements
  const selectors = [
    'body',
    'header',
    'nav',
    'main',
    'footer',
    'h1',
    'h2',
    'h3',
    'h4',
    'p',
    'a',
    'button',
    '[role="button"]',
    '.btn',
    'input',
    'select',
    'svg',
    '[class*="hero"]',
    '[class*="card"]',
    '[class*="badge"]',
    '[class*="pill"]',
    '[class*="tag"]',
    '[class*="nav"]',
    '[class*="header"]',
    '[class*="footer"]',
    '[class*="cta"]',
    '[class*="banner"]'
  ];

  const seenSels = new Set();
  const colorUsage = {};

  function addColorUsage(color, role, elInfo) {
    if (!color || color === 'rgba(0, 0, 0, 0)' || color === 'transparent') return;
    if (!colorUsage[color]) {
      colorUsage[color] = [];
    }
    colorUsage[color].push({ role, elInfo });
  }

  // Find elements and inspect styles
  const allElements = document.querySelectorAll('*');
  let elementIndex = 0;

  for (const el of allElements) {
    elementIndex++;
    if (elementIndex > 600) break; // Inspect up to 600 elements
    const tag = el.tagName.toLowerCase();
    const classes = el.className && typeof el.className === 'string' ? el.className.split(' ').filter(Boolean).slice(0, 5).join('.') : '';
    const id = el.id ? '#' + el.id : '';
    const textSnippet = (el.innerText || el.textContent || '').trim().slice(0, 40).replace(/\\s+/g, ' ');
    const desc = tag + id + (classes ? '.' + classes : '');

    const style = window.getComputedStyle(el);
    const bg = style.backgroundColor;
    const fg = style.color;
    const border = style.borderColor;
    const borderWidth = style.borderWidth;
    const borderRadius = style.borderRadius;
    const boxShadow = style.boxShadow;
    const bgImg = style.backgroundImage;
    const fontFamily = style.fontFamily;
    const fontSize = style.fontSize;
    const fontWeight = style.fontWeight;
    const lineHeight = style.lineHeight;

    if (bgImg && bgImg !== 'none') {
      if (bgImg.includes('gradient')) {
        result.gradients.push({ selector: desc, gradient: bgImg });
      }
    }

    addColorUsage(bg, 'background', desc);
    addColorUsage(fg, 'color', desc);
    if (borderWidth && borderWidth !== '0px') {
      addColorUsage(border, 'border', desc);
    }

    // Capture specific interesting elements
    const isButton = tag === 'button' || el.getAttribute('role') === 'button' || (tag === 'a' && (classes.includes('btn') || classes.includes('button')));
    const isHeading = ['h1', 'h2', 'h3', 'h4'].includes(tag);
    const isCard = classes.includes('card') || classes.includes('item') || classes.includes('feature') || classes.includes('box');
    const isBadge = classes.includes('badge') || classes.includes('pill') || classes.includes('tag');
    const isNav = tag === 'nav' || tag === 'header' || classes.includes('nav') || classes.includes('header');
    const isFooter = tag === 'footer' || classes.includes('footer');
    const isBody = tag === 'body';

    if (isButton || isHeading || isCard || isBadge || isNav || isFooter || isBody) {
      result.elements.push({
        type: isButton ? 'button' : isHeading ? 'heading' : isCard ? 'card' : isBadge ? 'badge' : isNav ? 'nav' : isFooter ? 'footer' : 'body',
        selector: desc,
        text: textSnippet,
        backgroundColor: bg,
        color: fg,
        borderColor: border,
        borderWidth,
        borderRadius,
        boxShadow,
        backgroundImage: bgImg,
        fontFamily,
        fontSize,
        fontWeight,
        lineHeight
      });
    }

    // Capture SVGs
    if (tag === 'svg') {
      result.svgs.push({
        selector: desc,
        fill: style.fill,
        stroke: style.stroke,
        color: fg
      });
    }
  }

  result.colorUsage = colorUsage;
  return result;
})()`;

async function main() {
  try {
    await sleep(2500);
    const version = await getJson(`http://127.0.0.1:${CDP_PORT}/json/version`);
    console.log('[*] Connected to Chrome CDP:', version.Browser);

    const targets = await getJson(`http://127.0.0.1:${CDP_PORT}/json/list`);
    let target = targets.find((t) => t.type === 'page');
    if (!target) {
      target = await getJson(`http://127.0.0.1:${CDP_PORT}/json/new?https://www.outskill.com/`);
    }

    const client = new CDPClient(target.webSocketDebuggerUrl);
    await client.connect();

    await client.send('Page.enable');
    await client.send('Runtime.enable');

    const auditData = {
      timestamp: new Date().toISOString(),
      pages: {}
    };

    // 1. Audit Home Page: https://www.outskill.com/
    console.log('=== AUDITING HOME PAGE ===');
    await client.navigate('https://www.outskill.com/');

    // Desktop
    await client.setViewport(1440, 900, false);
    await client.screenshot(path.join(SCREENSHOTS_DIR, 'outskill_home_1440.png'));

    // Tablet
    await client.setViewport(1024, 768, false);
    await client.screenshot(path.join(SCREENSHOTS_DIR, 'outskill_home_1024.png'));

    // Mobile
    await client.setViewport(390, 844, true);
    await client.screenshot(path.join(SCREENSHOTS_DIR, 'outskill_home_390.png'));

    // Reset to desktop for style extraction
    await client.setViewport(1440, 900, false);
    const homeStyles = await client.evaluate(extractStylesScript);
    auditData.pages['home'] = homeStyles;
    console.log(`[+] Home: found ${Object.keys(homeStyles?.colorUsage || {}).length} unique colors, ${homeStyles?.elements?.length || 0} sample elements, ${homeStyles?.gradients?.length || 0} gradients`);

    // 2. Hover test on home buttons
    const hoverStyles = await client.evaluate(`(() => {
      const btns = Array.from(document.querySelectorAll('button, a[role="button"], a.btn, header a'));
      return btns.slice(0, 10).map(b => {
        const defaultBg = window.getComputedStyle(b).backgroundColor;
        const defaultColor = window.getComputedStyle(b).color;
        const text = (b.innerText || '').trim().slice(0, 30);
        return { text, defaultBg, defaultColor, classes: b.className };
      });
    })()`);
    auditData.pages['home'].buttonSamples = hoverStyles;

    // 3. Audit Fellowship Page: https://www.outskill.com/6-month-ai-generalist-fellowship
    console.log('=== AUDITING FELLOWSHIP PAGE ===');
    await client.navigate('https://www.outskill.com/6-month-ai-generalist-fellowship');

    // Desktop
    await client.setViewport(1440, 900, false);
    await client.screenshot(path.join(SCREENSHOTS_DIR, 'outskill_fellowship_1440.png'));

    // Tablet
    await client.setViewport(1024, 768, false);
    await client.screenshot(path.join(SCREENSHOTS_DIR, 'outskill_fellowship_1024.png'));

    // Mobile
    await client.setViewport(390, 844, true);
    await client.screenshot(path.join(SCREENSHOTS_DIR, 'outskill_fellowship_390.png'));

    // Reset to desktop for style extraction
    await client.setViewport(1440, 900, false);
    const fellowshipStyles = await client.evaluate(extractStylesScript);
    auditData.pages['fellowship'] = fellowshipStyles;
    console.log(`[+] Fellowship: found ${Object.keys(fellowshipStyles?.colorUsage || {}).length} unique colors, ${fellowshipStyles?.elements?.length || 0} sample elements, ${fellowshipStyles?.gradients?.length || 0} gradients`);

    // Save full JSON audit data
    const jsonPath = path.join(DESIGN_DIR, 'outskill_extracted_styles.json');
    fs.writeFileSync(jsonPath, JSON.stringify(auditData, null, 2));
    console.log(`[+] Successfully wrote extracted styles to: ${jsonPath}`);

    client.close();
  } catch (err) {
    console.error('Audit failed with error:', err);
  } finally {
    console.log('[*] Terminating Chrome audit instance...');
    chrome.kill();
  }
}

main();

