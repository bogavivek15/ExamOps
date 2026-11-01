import http from 'http';
import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';

const previewHtml = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>ExamOps Brand Icon & Favicon Visual Test</title>
  <style>
    body {
      background: #08090A;
      color: #FFFFFF;
      font-family: 'Figtree', 'Inter', sans-serif;
      padding: 40px;
    }
    h2 { font-size: 18px; margin-bottom: 20px; color: #FFFFFF; }
    .grid { display: flex; gap: 30px; align-items: flex-start; }
    .box {
      background: #121212;
      border: 1px solid rgba(255, 255, 255, 0.18);
      border-radius: 8px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 16px;
    }
    .box-light {
      background: #F4F5F7;
      color: #000;
      border: 1px solid #D1D5DB;
    }
    .label { font-size: 12px; color: #9CA3AF; }
    .box-light .label { color: #6B7280; }
  </style>
</head>
<body>
  <h2>ExamOps Bespoke Brand Mark & Favicon Previews</h2>
  <div class="grid">
    <div class="box">
      <div class="label">Sidebar Header (36×36)</div>
      <div style="width: 36px; height: 36px;">
        <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- Calendar Binder Tabs -->
          <rect x="9" y="3" width="4" height="6" rx="2" fill="#B8EF43"/>
          <rect x="23" y="3" width="4" height="6" rx="2" fill="#B8EF43"/>
          <!-- Calendar / Timetable Outer Container -->
          <rect x="3.5" y="5.5" width="29" height="27" rx="5.5" fill="#141414" stroke="rgba(255, 255, 255, 0.22)" stroke-width="1.2"/>
          <!-- Calendar Header Line -->
          <line x1="3.5" y1="12" x2="32.5" y2="12" stroke="rgba(255, 255, 255, 0.14)" stroke-width="1"/>
          <!-- Timeline Vertical Track Spine (The 'E' Spine) -->
          <rect x="7" y="15" width="3" height="14" rx="1.5" fill="#FFFFFF"/>
          <!-- Morning Exam Slot (White) -->
          <rect x="12" y="15" width="11" height="3.2" rx="1.6" fill="#FFFFFF"/>
          <circle cx="26" cy="16.6" r="1.6" fill="#FCF7F3" fill-opacity="0.85"/>
          <!-- Midday Exam Slot (Electric Lime Signature Highlight - Optimized / Active) -->
          <rect x="12" y="20.4" width="15" height="3.2" rx="1.6" fill="#B8EF43"/>
          <!-- Afternoon Exam Slot (White / Secondary) -->
          <rect x="12" y="25.8" width="12" height="3.2" rx="1.6" fill="#FFFFFF" fill-opacity="0.85"/>
          <circle cx="27" cy="27.4" r="1.6" fill="#FCF7F3" fill-opacity="0.85"/>
        </svg>
      </div>
    </div>

    <div class="box">
      <div class="label">Favicon on Dark Tab (32×32)</div>
      <img src="favicon.svg" width="32" height="32" style="border-radius: 6px;">
    </div>

    <div class="box box-light">
      <div class="label">Favicon on Light Tab (32×32)</div>
      <img src="favicon.svg" width="32" height="32" style="border-radius: 6px;">
    </div>

    <div class="box">
      <div class="label">Favicon High-Res (64×64)</div>
      <img src="favicon.svg" width="64" height="64" style="border-radius: 12px;">
    </div>
  </div>
</body>
</html>`;

fs.writeFileSync('frontend/public/icon_preview.html', previewHtml);
console.log('Saved frontend/public/icon_preview.html');

