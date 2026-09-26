// Tokenizes with VS Code's own TextMate engine, against syntaxes/.
//   node test/tokenize.js dump <scope> <file>         each token and its scopes
//   node test/tokenize.js invalid <scope> <files...>  tokens scoped invalid.*
//   node test/tokenize.js expect <cases.json>         check each [scope, source, token, scope]
//
// In a case, the wanted scope is a substring of one of the token's
// scopes; a leading ! says none of them may contain it.
const fs = require('fs');
const path = require('path');
const vsctm = require('vscode-textmate');
const oniguruma = require('vscode-oniguruma');

const SYN = process.env.SYN || path.join(__dirname, '..', 'syntaxes');
const files = {
  'source.vtx': 'vertex.tmLanguage.json',
  'source.vtxir': 'vertex-ir.tmLanguage.json',
  'source.vtx.mod': 'vertex-mod.tmLanguage.json',
  'source.vtx.work': 'vertex-work.tmLanguage.json',
  'source.vtx.sum': 'vertex-sum.tmLanguage.json',
};

const wasm = fs.readFileSync(require.resolve('vscode-oniguruma/release/onig.wasm')).buffer;
const onigLib = oniguruma.loadWASM(wasm).then(() => ({
  createOnigScanner: (p) => new oniguruma.OnigScanner(p),
  createOnigString: (s) => new oniguruma.OnigString(s),
}));
const registry = new vsctm.Registry({
  onigLib,
  loadGrammar: async (scope) => {
    const f = files[scope];
    if (!f) return null;
    const p = path.join(SYN, f);
    return vsctm.parseRawGrammar(fs.readFileSync(p, 'utf8'), p);
  },
});

function tokenize(grammar, text) {
  let rule = vsctm.INITIAL;
  const out = [];
  text.split(/\r?\n/).forEach((line, i) => {
    const r = grammar.tokenizeLine(line, rule);
    for (const t of r.tokens) out.push({ line: i + 1, text: line.slice(t.startIndex, t.endIndex), scopes: t.scopes });
    rule = r.ruleStack;
  });
  return out;
}

(async () => {
  const [cmd, ...args] = process.argv.slice(2);
  if (cmd === 'dump') {
    const g = await registry.loadGrammar(args[0]);
    for (const t of tokenize(g, fs.readFileSync(args[1], 'utf8')))
      if (t.text.trim()) console.log(`${t.line}\t${JSON.stringify(t.text)}\t${t.scopes.slice(1).join(' ')}`);
  } else if (cmd === 'invalid') {
    const g = await registry.loadGrammar(args[0]);
    let n = 0;
    for (const f of args.slice(1)) {
      const t0 = Date.now();
      for (const t of tokenize(g, fs.readFileSync(f, 'utf8')))
        if (t.scopes.some((s) => s.startsWith('invalid'))) {
          if (n++ < 40) console.log(`${f}:${t.line}\t${JSON.stringify(t.text)}\t${t.scopes.slice(1).join(' ')}`);
        }
      const dt = Date.now() - t0;
      if (dt > 2000) console.log(`SLOW ${f}: ${dt} ms`);
    }
    console.log(`${n} invalid tokens in ${args.length - 1} files`);
  } else if (cmd === 'expect') {
    const cases = JSON.parse(fs.readFileSync(args[0], 'utf8'));
    let fail = 0;
    for (const [scope, src, text, want] of cases) {
      const g = await registry.loadGrammar(scope);
      const toks = tokenize(g, src).filter((t) => t.text === text);
      const ok = toks.some((t) => t.scopes.some((s) => (want.startsWith('!') ? false : s.includes(want))))
        || (want.startsWith('!') && toks.length && toks.every((t) => !t.scopes.some((s) => s.includes(want.slice(1)))));
      if (!ok) {
        fail++;
        console.log(`FAIL ${scope} ${JSON.stringify(src)}: ${JSON.stringify(text)} want ${want}; got ${toks.map((t) => t.scopes.slice(1).join(' ')).join(' | ') || '(no such token)'}`);
      }
    }
    console.log(`${cases.length - fail}/${cases.length} passed`);
    process.exitCode = fail ? 1 : 0;
  }
})();
