// Renders og.png (1200x630) from tools/og.html and PNG icons from icon.svg. Needs Playwright:
//   node tools/make_images.mjs   (set FONTS_CSS=path to inline @font-face rules if Google Fonts is unreachable)
import { chromium } from 'playwright';
import fs from 'fs'; import path from 'path'; import url from 'url';
const root = path.dirname(path.dirname(url.fileURLToPath(import.meta.url)));
const b = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
let og = fs.readFileSync(path.join(root, 'tools/og.html'), 'utf8');
if (process.env.FONTS_CSS) og = og.replace('/*FONTS*/', fs.readFileSync(process.env.FONTS_CSS, 'utf8'));
const p = await b.newPage({ viewport: { width: 1200, height: 630 } });
await p.setContent(og, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready);
await p.screenshot({ path: path.join(root, 'og.png') });
const svg = fs.readFileSync(path.join(root, 'icon.svg'), 'utf8');
for (const [size, name] of [[180, 'apple-touch-icon.png'], [512, 'icon-512.png']]) {
  const q = await b.newPage({ viewport: { width: size, height: size } });
  // iOS paints transparent corners black and rounds the icon itself, so the touch icon is full-bleed
  const src = name === 'apple-touch-icon.png' ? svg.replace('rx="22"', 'rx="0"') : svg;
  await q.setContent(`<style>*{margin:0}svg{display:block;width:${size}px;height:${size}px}</style>${src}`);
  await q.screenshot({ path: path.join(root, name), omitBackground: true });
}
await b.close();
console.log('wrote og.png, apple-touch-icon.png, icon-512.png');
