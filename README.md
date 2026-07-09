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

### `.vs` — Vertex source

- Package/import directives: `package`, `build` (with the following namespace
  name), and `import`
- Keywords: control flow (`if`, `else`, `switch`, `case`, `default`,
  `fallthrough`, `for`, `in`, `while`, `break`, `continue`, `return`, `defer`,
  `select`) and the `as` conversion operator
- Declarations and storage: `let`, `var`, `func`, `struct`, `class`, `enum`,
  `type`, `chan`, `unique`
- Modifiers: `mut`, `own`, `unowned`
- Execution / hardware sigils: `thread`, `async`, `gpu`, `tpu`
- Function declarations, including receiver syntax
  (`func (recv: Type) name`, with an optional `mut`/`own` on the receiver)
- Type declarations (`struct`, `class`, `enum`, and `type` aliases)
- Built-in primitive types (`int`, `uint64`, `float32`, `bool`, `string`,
  `char`, `void`, ...)
- TPU tensor element types (`bf16`, `fp8e4m3`, `fp8e5m2`, `int4`)
- Generic container constructors used before `<...>` (`shared`, `weak`, `map`,
  `range`, `tensor`)
- Capitalized identifiers as type references
- Numeric literals: decimal, hex, octal, and binary integers; decimal floats;
  and hex floats with binary (`p`) exponents — all with `_` digit separators
- Strings: double-quoted, single-quoted character literals (both with escape
  and invalid-escape detection), and multiline raw backtick strings
- Constants: `true`, `false`, `nil`
- Enum shorthand (`.Variant`)
- Function calls, including generic calls (`name<...>(...)`)
- Test support: the `test` keyword and `Expected(...)`
- Full operator set: arithmetic and compound assignment, comparison, identity
  (`===`, `!==`), logical, bitwise, overflow-safe/wrapping (`&+`, `&-`, `&*`),
  bit shifts, range (`..`, `...`), coalescing (`??`), optional (`?`), and the
  `->` arrow
- Line and block comments

### `vs.mod` — module manifest

- Directive keywords: `module`, `vertex`, `toolchain`, `tool`, `ignore`,
  `dependencies`, `exclude`, `replace`, `retract`
- Factored block syntax, e.g. `dependencies ( ... )`
- Quoted strings (with escapes) and raw backtick strings
- `=>` replace arrows
- Version literals: semver (`v1.2.3`, with optional `-pre` / `+build`) and the
  bare directive form (`1.21`, `1.21rc1`)
- Module paths, and local file-path replace targets (`./dir`, `/abs/dir`)

### `vs.lib` — native-library manifest

- Top-level `library ImportPath` directive (bare, unquoted path)
- Block keywords: `provider`, `target`, `release`
- Recognized provider kinds: `apt`, `dnf`, `pacman`, `brew`, `vcpkg`, `fetch`
- `key = "value"` field syntax
- Quoted strings (with escapes)

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