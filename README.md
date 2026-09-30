# Vertex Language Support

VS Code syntax highlighting for the [Vertex programming language](https://github.com/vertex-language/vertex-language):
every file the Vertex toolchain reads and writes.

| File | Language ID | Grammar scope | Read or written by |
|------|-------------|---------------|--------------------|
| `*.vs`, `*.vinterface` | `vertex` | `source.vtx` | [`vsc`](https://github.com/vertex-language/vsc); `vsc build --emit interface` writes `.vinterface` |
| `*.vsx` | `vertex-vsx` | `source.vtx.vsx` | `vsc`: Vertex with markup |
| `*.vss` | `vertex-vss` | `source.vss` | `vsc`: a package's styles |
| `*.vir` | `vertex-ir` | `source.vtxir` | [`ir`](https://github.com/vertex-language/ir), `vsc build --emit vir` |
| `vs.mod` | `vertex-mod` | `source.vtx.mod` | `vsc`: a module's path, toolchain, platforms and requirements |
| `vs.work` | `vertex-work` | `source.vtx.work` | `vsc`: local modules used in place of fetched ones |
| `vs.sum` | `vertex-sum` | `source.vtx.sum` | `vsc`: each required module version's tree hash |

Fenced code blocks in Markdown are highlighted too, tagged `vertex`/`vs`,
`vsx`, `vss`, `vertex-ir`/`vir`, `vs.mod`, `vs.work` or `vs.sum`.

## What's highlighted

**`.vs` and `.vinterface`.** Vertex shares its core dialect with Swift, so the
grammar covers the Swift syntax `vsc` reads: every reserved word, the
contextual keywords where they are keywords (`mutating func`, but not
`let mutating`), attributes, `#if` conditions, `#available`, the `#` literals,
macro expansions, nested `/* */` comments, doc comments and their
`- Parameter` fields, string interpolation, raw (`#"…"#`) and multiline
(`"""`) strings, regex literals, and binary, octal, hex and hex-float numbers.
A malformed number such as `0b12` is marked the way `vsc` reports it. On top of
that, the Vertex additions:

- `package` declarations (`package http`), told apart from `package func`
- folder imports, aliased and grouped (`import geom "./geometry"`, `import ( … )`)
- receiver methods and their ownership (`func (v: inout Vec2) scale(by:)`)
- the lowercase primitive types (`int32`, `uint8`, `float32`, `string`, `never`, …)
- the `kernel` and `graph` execution modifiers, only where a signature puts them

**`.vsx`.** Everything `.vs` has, and markup where the file may hold it: a
`<` opens a tag only where `vsc` reads one -- where a prefix operator would
stand, before a name or `>` -- so `a < b`, `Array<int>`, `sorted(by: <)` and a
declaration's generic clause (`func |> <T, U>`) stay what they are. Element
names (`div`) and components (`Counter`, `app.Window`) are scoped apart;
attributes, event handlers (`onClick`), `class:` and `style:` bindings,
spreads (`{...attrs}`), character entities and the text between tags each have
their own scope. `{…}` in markup is Vertex again, so markup nests in code and
code in markup.

**`.vss`.** The header -- `package kit`, and `import "ui/theme"` lines, single
or grouped -- and then VS Code's own CSS grammar, with nesting, `@layer`,
`@scope`, `@property` and custom properties.

**`.vir`.** The module header (`module`, `use`, `layout`), type, global, import,
alias and function declarations, every `ns.verb` instruction (`i64.add`,
`ptr.getaddr`, `v128.i32x4_add`, …), terminators and calls, registers
(`%0`, `%bb1.0`), symbols by role (a function after `call`, a type after `sret`,
a label on a branch), struct fields, metadata (`!dbg`), attributes, calling
conventions, orderings and literals.

**`vs.mod` and `vs.work`.** Each directive `vsc` accepts, on one line or as a
`( … )` block: `module`, `vertex`, `platform`, `require`, `exclude` and
`replace` in `vs.mod`; `vertex`, `use` and `replace` in `vs.work`. Module paths,
versions, local directories and the `=>` of a replacement are each scoped by
position, as `vsc` reads them, and any other directive is marked as the error
`vsc` makes it.

**`vs.sum`.** Each `module version h1:hash` line, with a line of any other shape
marked as the error `vsc` makes it.

## Editor behavior

- **`.vs`**: brackets and auto-closing for `{}`, `[]`, `()`, `"` and `` ` ``;
  `/** */` and `///` doc-comment continuation; indentation for `case`,
  `default` and `#if`; folding on `// MARK:`, `//#region` and `#if` blocks.
- **`.vsx`**: as `.vs`, and `'` auto-closing for attribute values.
- **`.vss`**: CSS's `/* */` comments, pairs, indentation and word selection.
- **`.vir`**: indentation after function bodies and block labels, and word
  selection that keeps `%reg`, `@symbol` and `i32.add` whole.
- **`vs.mod`, `vs.work`**: `//` comments, and indenting and folding of
  `( … )` blocks.

## Installation

```bash
git clone https://github.com/vertex-language/vscode-vertex.git
cd vscode-vertex
npx @vscode/vsce package
code --install-extension vscode-vertex-5.0.0.vsix
```

Or install the `.vsix` with **Extensions: Install from VSIX...** in the
Command Palette. The extension is not on the Marketplace yet.

## Working on the grammars

The grammars in `syntaxes/` are generated. Edit the generators in `scripts/`
and rebuild:

```bash
npm run build
```

`npm test` tokenizes the cases in `test/cases.json` with VS Code's own TextMate
engine and checks each token's scope. To see how a file tokenizes, or to find
anything marked invalid across a corpus:

```bash
node test/tokenize.js dump source.vtx path/to/file.vs
```

```bash
node test/tokenize.js invalid source.vtx ../*/*.vs
```

The source of truth is the toolchain: the scanner and parser in
[`vsc`](https://github.com/vertex-language/vsc) (`token/kind.go`,
`docs/vertex_spec.md`), its module files (`pkg/vsmod.go`, `importer/sum.go`),
and the IR specification and printer in
[`ir`](https://github.com/vertex-language/ir) (`spec/grammar.md`, `text/`).

## License

MIT
