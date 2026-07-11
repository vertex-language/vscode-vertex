# Vertex Language Support

VS Code syntax highlighting for the [Vertex programming language](https://github.com/vertex-language/vertex).

This extension covers all three file formats used by the Vertex toolchain:

| File     | Language ID  | Grammar scope   | Configuration file                |
|----------|--------------|-----------------|-----------------------------------|
| `*.vs`   | `vertex`     | `source.vtx`    | `language-configuration.json`     |
| `vs.mod` | `vertex-mod` | `source.vtxmod` | `language-configuration-mod.json` |
| `vs.lib` | `vertex-lib` | `source.vtxlib` | `language-configuration-lib.json` |

`vs.mod` and `vs.lib` are matched by exact filename, not extension — the same
approach the Go extension uses for `go.mod` / `go.sum`.

## Installation

### From source

```bash
git clone https://github.com/vertex-language/vscode-vertex.git
cd vscode-vertex
npm install -g @vscode/vsce
vsce package
```

This produces a `.vsix` file in the project directory. Install it with:

- **Command Palette** → `Extensions: Install from VSIX...`, or
- **Extensions view** → `...` menu → **Install from VSIX**, or
- from the terminal:

  ```bash
  code --install-extension vscode-vertex-1.0.3.vsix
  ```

### From the Marketplace

Not yet published — installation currently requires building from source as
described above.

## What's highlighted

- **`.vs` — Vertex source.** Full highlighting for the language: declarations,
  keywords, operators, types, literals, comments, and everything else the
  grammar covers.
- **`vs.mod` — module manifest.** Directive keywords, block syntax, strings,
  version literals, and module/replace paths.
- **`vs.lib` — native-library manifest.** The top-level directive, block
  keywords, provider kinds, fields, and strings.

## Editor behavior

Each file type also gets bracket matching, auto-closing pairs, comment
toggling, and indentation rules suited to its syntax:

- **`.vs`** — brackets and auto-closing for `{}`, `[]`, `()`, plus `"`, `` ` ``,
  and `'` quotes and `/* */` block comments; block-comment continuation on
  Enter (inserting ` * `); and `//#region` / `//#endregion` folding markers.
- **`vs.mod`** — scoped to `()` and `[]` brackets, with `"` and `` ` `` string
  auto-closing and line-comment toggling.
- **`vs.lib`** — scoped to `{}` braces, with `"` string auto-closing and
  line-comment toggling.

## Contributing

Issues and pull requests are welcome at
[vertex-language/vscode-vertex](https://github.com/vertex-language/vscode-vertex).

## License

MIT