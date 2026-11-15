// Run the real application script with a minimal DOM and persistent browser storage.
// No browser dependencies are needed for state and input regression checks.
const {readFileSync, readdirSync} = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const {test} = require('node:test');
const data = readFileSync(readdirSync('.').find(f => /^data\..*\.json$/.test(f)), 'utf8');
const script = readFileSync('src.html', 'utf8').split('<script>')[1].split('</script>')[0]
  .replace('/*DATA*/[]', data);

function boot(storage = new Map()) {
  const elements = new Map(), listeners = {};
  const element = selector => {
    if (!elements.has(selector)) elements.set(selector, {
      hidden:false, disabled:false, innerHTML:'', textContent:'', dataset:{},
      style:{setProperty() {}}, classList:{toggle() {}},
      setAttribute() {}, addEventListener() {}, scrollIntoView() {}, blur() {},
    });
    return elements.get(selector);
  };
  const document = {
    querySelector:element, querySelectorAll:() => [], documentElement:element('root'),
    addEventListener:(event, fn) => { listeners[event] = fn; },
  };
  const context = vm.createContext({document, window:{}, addEventListener() {},
    matchMedia:() => ({matches:true}), setTimeout() {}, navigator:{},
    localStorage:{getItem:k => storage.get(k), setItem:(k, v) => storage.set(k, v)},
  });
  vm.runInContext(script, context);
  const run = code => vm.runInContext(code, context);
  run('S.sound = false;');
  const click = id => listeners.click({target:{closest:() => ({id, dataset:{}})}});
  return {run, click, element, storage};
}

test('hint reveals one new position, keeps typed input and spends no attempt', () => {
  const app = boot();
  app.run("select(0); buf = 'AB'; G().g[0] = [E().keys[0][0] + 'Z'.repeat(E().keys[0].length - 1)];");
  const before = app.run('JSON.stringify(G().g)');
  app.click('hint');
  assert.equal(app.run('JSON.stringify(G().g)'), before);
  assert.equal(app.run('buf'), 'AB');
  assert.equal(app.run('G().hint.player'), 0);
  assert.notEqual(app.run('G().hint.pos'), 0);
  assert.equal(app.element('#hint').disabled, true);
  assert.equal(app.element('#hintClue').hidden, false);
  assert.match(app.element('#hintClue').innerHTML, /Hint: letter/);
  const hint = app.run('JSON.stringify(G().hint)');
  app.run('select(1)');
  app.click('hint');
  assert.equal(app.run('JSON.stringify(G().hint)'), hint);
  assert.equal(app.element('#hintClue').hidden, true);
  app.run('select(0)');
  assert.equal(app.element('#hintClue').hidden, false);
  assert.match(app.run('shareText()'), /1 hint/);
});

test('hint survives reload and switching sports; new game grants one hint', () => {
  const app = boot();
  app.click('hint');
  const hint = app.run('JSON.stringify(G().hint)');
  const reloaded = boot(app.storage);
  assert.equal(reloaded.run('JSON.stringify(G().hint)'), hint);
  assert.equal(reloaded.element('#hint').disabled, true);
  reloaded.run("S.sport = 'bb'; newGame(false);");
  assert.equal(reloaded.run('G().hint'), null);
  reloaded.click('hint');
  reloaded.run("S.sport = 'fb'; render();");
  assert.equal(reloaded.run('JSON.stringify(G().hint)'), hint);
  reloaded.run('newGame(false)');
  assert.equal(reloaded.run('G().hint'), null);
  assert.equal(reloaded.element('#hint').disabled, false);
});

test('hint is blocked for solved, exhausted and given-up players', () => {
  for (const state of ['G().g[0] = [E().keys[0]]',
    "G().g[0] = Array(MAXT(G().hard)).fill('Z'.repeat(E().keys[0].length))",
    'G().gave = true']) {
    const app = boot();
    app.run(`select(0); ${state}; render();`);
    assert.equal(app.element('#hint').disabled, true);
    app.click('hint');
    assert.equal(app.run('G().hint'), null);
  }
});

test('all known positions do not spend the hint, including in hard mode', () => {
  const app = boot();
  app.run(`G().hard = true; select(0);
    const answer = E().keys[0];
    G().g[0] = ['Z' + answer.slice(1), answer[0] + 'Z'.repeat(answer.length - 1)];
    render();`);
  assert.equal(app.element('#hint').disabled, true);
  app.click('hint');
  assert.equal(app.run('G().hint'), null);
  app.run('select(1)');
  assert.equal(app.element('#hint').disabled, false);
  app.click('hint');
  assert.equal(app.run('G().hint.player'), 1);
});

test('old saves without a hint still work; reopening current Daily keeps its hint', () => {
  const app = boot();
  app.run('delete G().hint; save();');
  const reloaded = boot(app.storage);
  assert.equal(reloaded.element('#hint').disabled, false);
  reloaded.click('hint');
  assert.equal(reloaded.run('!!G().hint'), true);
  reloaded.run('newGame(true)');
  reloaded.click('hint');
  const hint = reloaded.run('JSON.stringify(G().hint)');
  reloaded.run('newGame(true)');
  assert.equal(reloaded.run('JSON.stringify(G().hint)'), hint);
  assert.equal(reloaded.element('#hint').disabled, true);
});

test('a saved excluded EuroLeague lineup is replaced by an eligible game on boot', () => {
  const app = boot();
  app.run("S.sport = 'bb'; newGame(false); G().id = 'bb|Real Madrid|2018/19|EuroLeague'; save();");
  const reloaded = boot(app.storage);
  assert.equal(reloaded.run('!!E()'), true);
  assert.equal(reloaded.run("E().cat !== 'euro' || Number(E().season.slice(0, 4)) >= 2020"), true);
  assert.equal(reloaded.run('G().hint'), null);
});
