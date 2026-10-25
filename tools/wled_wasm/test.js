#!/usr/bin/env node
// Sweep every effect in the built module: run it on the installation's layout, as the controller's one logical strip
// and as the rolled 14 × tallest matrix, for a few seconds of frames each, and report any that trap or stay dark.
//   node tools/wled_wasm/test.js [frames]
const WledFx = require('./wled_fx.js');
const LENS = [57, 75, 93, 111, 93, 75, 57, 57, 75, 93, 111, 93, 75, 57];   // LEDs per tower, S1-T1 … S2-T7, 60/m above a 150 mm base
const FRAMES = parseInt(process.argv[2] || '120', 10);

WledFx().then(M => {
  const name = id => M.UTF8ToString(M._sim_mode_data(id));
  const count = M._sim_mode_count();
  const bad = [], dark = [];
  let ran = 0;
  for (const layout of ['strip', 'matrix']) {
    const w = layout === 'matrix' ? LENS.length : LENS.reduce((a, b) => a + b, 0), h = layout === 'matrix' ? Math.max(...LENS) : 1;
    for (let id = 0; id < count; id++) {
      const meta = name(id);
      if (meta === 'RSVD') continue;
      const flags = (meta.split('@')[1] || '').split(';')[3] || '';
      if (layout === 'strip' && flags && flags.includes('2') && !flags.includes('1')) continue;   // 2D-only effect
      M._sim_init(w, h);
      M._sim_set_bus(LENS.length, 0); LENS.forEach((n, i) => M._sim_set_bus(i, n));
      M._sim_set_mode(id, 1);
      M._sim_set_color(0, 255, 160, 0, 0); M._sim_set_color(1, 0, 0, 80, 0); M._sim_set_color(2, 0, 120, 0, 0);
      let lit = 0, t0 = Date.now();
      try {
        for (let f = 0; f < FRAMES; f++) {
          const p = M._sim_frame(1000 + f * 23) >>> 2;
          const px = M.HEAPU32.subarray(p, p + w * h);
          for (let i = 0; i < px.length; i += 5) if (px[i] & 0xFFFFFF) { lit++; break; }   // stride coprime with the 14 columns, or a one-column effect is missed
        }
      } catch (e) { bad.push(`${layout} ${id} ${meta.split('@')[0]}: ${e.message || e}`); continue; }
      ran++;
      const ms = (Date.now() - t0) / FRAMES;
      if (!lit) dark.push(`${layout} ${id} ${meta.split('@')[0]}`);
      if (ms > 4) console.log(`  slow: ${layout} ${id} ${meta.split('@')[0]} ${ms.toFixed(1)} ms/frame`);
    }
  }
  console.log(`${count} mode slots, ${ran} effect runs of ${FRAMES} frames`);
  if (dark.length) console.log(`never lit (${dark.length}):\n  ` + dark.join('\n  '));
  if (bad.length) { console.log(`FAILED (${bad.length}):\n  ` + bad.join('\n  ')); process.exit(1); }
  console.log('all effects ran');
}).catch(e => { console.error(e); process.exit(1); });
