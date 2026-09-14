# Vertex Language Support

VS Code syntax highlighting for the [Vertex programming language](https://github.com/vertex-language/vertex-language).

The extension covers the two file types the Vertex toolchain reads and writes:

| File    | Language ID | Grammar scope  | Configuration file              | Produced / read by |
|---------|-------------|----------------|---------------------------------|--------------------|
| `*.vs`  | `vertex`    | `source.vtx`   | `language-configuration.json`   | [`vsc`](https://github.com/vertex-language/vsc) |
| `*.vir` | `vertex-ir` | `source.vtxir` | `language-configuration-ir.json`| [`ir`](https://github.com/vertex-language/ir), `vsc --emit vir` |

Fenced code blocks in Markdown tagged `vertex` or `vs`, and `vertex-ir` or
`vir`, are highlighted with the same grammars.

## Installation

### From source

```bash
git clone https://github.com/vertex-language/vscode-vertex.git
cd vscode-vertex
npm install -g @vscode/vsce
vsce package
```

This produces `vscode-vertex-<version>.vsix` in the project directory. Install it with:

- **Command Palette** → `Extensions: Install from VSIX...`, or
- **Extensions view** → `...` menu → **Install from VSIX**, or
- from the terminal:

  ```bash
  code --install-extension vscode-vertex-4.0.0.vsix
  ```

### From the Marketplace

Not yet published — installation currently requires building from source as
described above.

## What's highlighted

- **`.vs` — Vertex source.** Vertex shares its core dialect with Swift, so the
  grammar covers the Swift syntax `vsc` accepts — declarations, reserved and
  contextual keywords, attributes, `#if` and the other `#` directives, macro
  expansions, nested block comments, string interpolation, raw (`#"…"#`) and
  multiline (`"""`) strings, extended regex literals, and binary, octal, hex
  and hex-float numbers — plus the Vertex extensions:
  - `package` declarations (`package app`)
  - folder imports, aliased and grouped (`import geom "./geometry"`)
  - receiver methods with ownership (`func (v: borrowing Vec2) length()`)
  - lowercase primitive spellings (`int32`, `uint8`, `float32`, `double`,
    `string`, `char`, `never`, …)
  - `kernel` and `graph` execution modifiers
- **`.vir` — Vertex IR.** Module header (`module`, `use`, `layout`), type,
  global, import, alias and function declarations, every `Type.Verb` mnemonic
  in the `i1`/`i32`/`i64`/`f32`/`f64`/`f80`/`f128`/`ptr`/`v128` namespaces
  (an unknown verb on a known namespace is marked invalid), bare mnemonics and
  terminators, registers (`%0`), symbols (`@_$s4main…`), metadata (`!dbg`),
  block labels, calling conventions, orderings, and literals.

## Editor behavior

- **`.vs`** — brackets and auto-closing for `{}`, `[]`, `()`, `"`, and `` ` ``
  (backtick-escaped identifiers); `/* */` and `/** */` comment continuation;
  `///` doc-comment continuation; indentation for `case`/`default` and
  `#if`/`#else`/`#endif`; folding on `//#region`, `// MARK:` and `#if` blocks.
- **`.vir`** — brackets and auto-closing for `{}`, `[]`, `()`, and `"`;
  indentation after function bodies and block labels (`@entry:`); word
  selection that keeps `%reg`, `@symbol` and `i32.add` whole.

## Contributing

Issues and pull requests are welcome at
[vertex-language/vscode-vertex](https://github.com/vertex-language/vscode-vertex).
The compiler ([`vsc`](https://github.com/vertex-language/vsc)) and the IR
specification ([`ir/spec`](https://github.com/vertex-language/ir/tree/main/spec))
are the source of truth for both grammars.

## License

MIT
