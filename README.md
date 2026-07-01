# Vertex Language Support

VS Code syntax highlighting for the [Vertex programming language](https://github.com/vertex-language/vertex).

This extension covers all three file formats used by the Vertex toolchain:

| File        | Language ID   | Grammar scope     | Configuration file                 |
|-------------|---------------|--------------------|-------------------------------------|
| `*.vs`      | `vertex`      | `source.vtx`       | `language-configuration.json`       |
| `vs.mod`    | `vertex-mod`  | `source.vtxmod`    | `language-configuration-mod.json`   |
| `vs.lib`    | `vertex-lib`  | `source.vtxlib`    | `language-configuration-lib.json`   |

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
  code --install-extension vscode-vertex-1.0.0.vsix
  ```

### From the Marketplace

Not yet published — installation currently requires building from source as
described above.

## What's highlighted

### `.vs` — Vertex source

- Keywords: control flow (`if`, `else`, `for`, `while`, `switch`, `return`,
  `defer`, ...), declarations (`func`, `struct`, `class`, `enum`, `type`,
  `let`, `var`, `const`, ...), and modifiers (`async`, `thread`, `gpu`,
  `state`, `weak`, ...)
- Function declarations, including receiver syntax (`func (recv: Type) name`)
- Type declarations (`struct`, `class`, `enum`, `type`)
- Built-in primitive types (`int`, `uint64`, `float32`, `bool`, `string`, ...)
- Numeric literals: decimal, hex, octal, binary integers, decimal floats, and
  hex floats with binary exponents
- Strings, character literals with escapes, and multiline backtick strings
- Line and block comments
- Enum shorthand (`.Variant`)
- Full operator set (arithmetic, comparison, logical, bitwise, overflow-safe,
  range, coalescing, etc.)

### `vs.mod` — module manifest

- Directive keywords: `module`, `vertex`, `toolchain`, `dependencies`,
  `exclude`, `replace`, `retract`, `tool`, `ignore`
- Factored block syntax, e.g. `dependencies ( ... )`
- Quoted strings and raw backtick strings
- `=>` replace arrows
- Version literals (semver and bare directive forms like `1.21rc1`)
- Module paths

### `vs.lib` — native-library manifest

- Block keywords: `provider`, `target`, `release`
- Recognized provider kinds: `apt`, `dnf`, `pacman`, `brew`, `vcpkg`, `fetch`
- `key = "value"` field syntax
- Quoted strings

## Editor behavior

Each file type also gets matching bracket-matching, auto-closing pairs,
comment toggling, and indentation rules suited to its syntax — for example,
`.vs` files support `{}`, `[]`, `()`, block comments, and triple string
delimiters, while `vs.mod` and `vs.lib` are scoped to the punctuation their
formats actually use.

## Contributing

Issues and pull requests are welcome at
[vertex-language/vscode-vertex](https://github.com/vertex-language/vscode-vertex).

## License

MIT