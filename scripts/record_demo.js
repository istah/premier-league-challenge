// Captioned screen capture of the coach room for the demo video (about 1:45 raw; cut the live wait with ffmpeg, see docs/DEMO_SCRIPT.md).
// Needs: npm i playwright-core; npx playwright-core install ffmpeg; Chrome; server: FOUNDRY_HOSTED_AGENTS=1 uv run --extra foundry uvicorn plc.api:app --port 8765
const { chromium } = require('playwright-core');
(async () => {
  const b = await chromium.launch({ channel: 'chrome' });
  const ctx = await b.newContext({ viewport: { width: 1440, height: 810 }, recordVideo: { dir: './demo-video', size: { width: 1440, height: 810 } } });
  const p = await ctx.newPage(); const T0 = Date.now(); const marks = {};
  const t = () => (Date.now() - T0) / 1000;
  const cap = async (text) => p.evaluate(text => {
    let c = document.getElementById('democap');
    if (!c) { c = document.createElement('div'); c.id = 'democap'; c.style.cssText = 'position:fixed;left:50%;bottom:18px;transform:translateX(-50%);z-index:9999;max-width:1150px;background:rgba(10,15,30,.94);color:#fff;font:600 21px/1.35 system-ui,sans-serif;padding:12px 22px;border-radius:14px;border:1px solid #3b82f6;box-shadow:0 10px 30px #000a;text-align:center'; document.body.append(c); }
    c.innerHTML = text; c.style.display = text ? 'block' : 'none';
  }, text);
  const card = async (html) => p.evaluate(html => {
    let c = document.getElementById('democard');
    if (!c) { c = document.createElement('div'); c.id = 'democard'; c.style.cssText = 'position:fixed;inset:0;z-index:10000;background:#0b1220;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;font:600 30px/1.4 system-ui,sans-serif;gap:14px'; document.body.append(c); }
    c.innerHTML = html; c.style.display = html ? 'flex' : 'none';
  }, html);
  const st = () => p.evaluate(() => [document.getElementById('clock').textContent, document.getElementById('play').textContent]);
  const waitPause = async (clock, ms = 60000) => { const s = Date.now(); while (Date.now() - s < ms) { const v = await st(); if (v[1] === 'Resume' && (!clock || v[0] === clock)) return v; await p.waitForTimeout(250); } return null; };

  await p.goto('http://localhost:8765/'); await p.waitForTimeout(1900); await p.evaluate(() => { const b = document.getElementById('play'); if (b.textContent === 'Pause') b.click(); });
  await card('<div style="font-size:46px">Redmoor FC Coach Room</div><div>A team of AI agents that supports the coach during the match</div><div style="font-size:22px;color:#93c5fd">Microsoft Foundry · Agent Framework · Foundry Agent Service · Foundry evaluators</div><div style="font-size:18px;color:#94a3b8">Fictional club, synthetic data</div>');
  await p.waitForTimeout(3600); await card('');
  await p.selectOption('#speed', { index: 2 });
  await cap('A seeded match streams events onto a bus. Rules fire when something changes; an orchestrator routes each one to the right AI staff.');
  await p.click('#play');
  await waitPause("5'"); marks.five = t();
  await cap("5' · The staff flag two risks: a tired midfielder, and a player whose heart-rate data looks fine but whose own wellness check-in is poor.");
  await p.waitForTimeout(7000);
  const nn = await p.$('#callout button[data-co="x"]'); if (nn && await nn.isVisible()) await nn.click();
  if ((await st())[1] !== 'Pause') await p.click('#play');
  await cap('The coach starts them anyway. That is his call. Each staff note shows ✓ checked against the data.');
  await p.waitForTimeout(9000);
  await cap('Goals and shape changes wake the right agents. The 5 staff agents are hosted in Foundry Agent Service.');
  await waitPause("65'", 90000); marks.sixtyfive = t();
  await cap("65' · Petrov fades against his own baseline. Instant rule-written suggestion: Petrov off, Salah-Reyes on. The coach decides.");
  await p.waitForTimeout(6500);
  await cap('Meanwhile, live on Microsoft Foundry: 3 analysts in parallel → critic & revise → Coach Briefing → Fact-checker');
  marks.waitStart = t();
  const s = Date.now();
  while (Date.now() - s < 110000) { const txt = await p.evaluate(() => document.getElementById('staff').innerText); if (/65' · A player is fading · written by the AI staff/.test(txt)) break; await p.waitForTimeout(500); }
  marks.arrived = t();
  await cap('AI-written notes replace the instant ones only if the rules judge and the Fact-checker agent both pass them.');
  await p.waitForTimeout(6500);
  await cap('The coach disagrees and dictates his own change. A coach call always beats the AI; nothing is applied automatically.');
  await p.click('#fab'); await p.waitForTimeout(600); await p.fill('#vtext', 'take off Petrov, bring on Quinn'); await p.waitForTimeout(5000);
  await p.click('[data-tab="tactics"]'); await p.check('#showov');
  await cap('He changes formation. The AI shows who is pushed forward or dragged back, and every player’s new role on the pitch.');
  await p.waitForTimeout(800); await p.selectOption('#formation', { index: 2 }); await p.waitForTimeout(6500);
  await p.click('[data-tab="log"]');
  await cap('Every step is traceable: rule fired → agents in parallel → revisions → Coach Briefing → Fact-checker and judge verdicts.');
  await p.waitForTimeout(6500);
  await cap(''); await card('<div style="font-size:40px">AI is decision support. The coach decides.</div><div style="font-size:22px;color:#94a3b8">Synthetic data · real biometrics need player consent</div><div style="font-size:20px;color:#93c5fd">github.com/istah/premier-league-challenge</div>');
  await p.waitForTimeout(4500);
  marks.end = t(); console.log(JSON.stringify(marks));
  await ctx.close(); await b.close();
})();
