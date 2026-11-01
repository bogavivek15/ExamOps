import http from 'http';
import { spawn } from 'child_process';

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function getJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let data = '';
      res.on('data', (c) => (data += c));
      res.on('end', () => resolve(JSON.parse(data)));
    }).on('error', reject);
  });
}

async function main() {
  const chrome = spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', [
    '--headless=new',
    '--remote-debugging-port=9444',
    '--disable-gpu',
    '--user-data-dir=C:\\Users\\USER\\AppData\\Local\\Temp\\chrome_outskill_logo',
  ]);

  try {
    await sleep(2000);
    const targets = await getJson('http://127.0.0.1:9444/json/list');
    let target = targets[0];
    if (!target) {
      target = await getJson('http://127.0.0.1:9444/json/new?https://www.outskill.com/');
    }

    const ws = new WebSocket(target.webSocketDebuggerUrl);
    await new Promise((r) => (ws.onopen = r));

    let msgId = 1;
    const send = (method, params = {}) =>
      new Promise((resolve) => {
        const id = msgId++;
        const handler = (e) => {
          const msg = JSON.parse(e.data);
          if (msg.id === id) {
            ws.removeEventListener('message', handler);
            resolve(msg.result);
          }
        };
        ws.addEventListener('message', handler);
        ws.send(JSON.stringify({ id, method, params }));
      });

    await send('Page.enable');
    await send('Runtime.enable');
    console.log('[*] Navigating to https://www.outskill.com/...');
    await send('Page.navigate', { url: 'https://www.outskill.com/' });
    await sleep(5000);

    const data = await send('Runtime.evaluate', {
      expression: `(() => {
        const header = document.querySelector('header') || document.querySelector('nav');
        const logoEl = document.querySelector('a[href="/"] img, img[alt*="logo" i], img[src*="logo" i], header svg, nav svg');
        const brandSvgs = Array.from(document.querySelectorAll('svg')).slice(0, 10).map(s => ({
          outer: s.outerHTML.slice(0, 300),
          fill: window.getComputedStyle(s).fill,
          color: window.getComputedStyle(s).color,
          parent: s.parentElement ? s.parentElement.className : ''
        }));
        
        const allButtons = Array.from(document.querySelectorAll('button, a[role="button"]')).map(b => ({
          text: (b.innerText || '').trim(),
          classes: b.className,
          bg: window.getComputedStyle(b).backgroundColor,
          color: window.getComputedStyle(b).color,
          border: window.getComputedStyle(b).borderColor,
          borderRadius: window.getComputedStyle(b).borderRadius,
          padding: window.getComputedStyle(b).padding,
          fontSize: window.getComputedStyle(b).fontSize,
          fontWeight: window.getComputedStyle(b).fontWeight,
          fontFamily: window.getComputedStyle(b).fontFamily,
          boxShadow: window.getComputedStyle(b).boxShadow
        }));

        const bodyStyle = window.getComputedStyle(document.body);
        const heroEl = document.querySelector('h1')?.closest('section, div');
        const heroStyle = heroEl ? window.getComputedStyle(heroEl) : null;

        return {
          title: document.title,
          bodyBg: bodyStyle.backgroundColor,
          bodyColor: bodyStyle.color,
          bodyFont: bodyStyle.fontFamily,
          headerOuter: header ? header.outerHTML.slice(0, 1200) : null,
          logoOuter: logoEl ? logoEl.outerHTML : null,
          brandSvgs,
          allButtons,
          heroBg: heroStyle ? heroStyle.backgroundColor : null,
          heroBgImage: heroStyle ? heroStyle.backgroundImage : null
        };
      })()`,
      returnByValue: true,
    });

    console.log(JSON.stringify(data.result ? data.result.value : data, null, 2));

    ws.close();
  } finally {
    chrome.kill();
  }
}

main();
