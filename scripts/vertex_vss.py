# Generates syntaxes/vertex-vss.tmLanguage.json: the grammar for .vss, a
# Vertex package's styles (proposed_vsx.md §7). A .vss file is a header --
# `package name`, then `import "path"` lines -- and standard CSS, which is
# VS Code's own CSS grammar (source.css): nesting, @layer, @scope and
# @property included. What .vss adds is the header, and the scopes that
# mark a package's tokens (`--kit-accent`) and the rules on the document.
import json, os, sys

ID = r'(?:[A-Za-z_][A-Za-z0-9_]*)'

IMPORT_PATH = {'match': r'(?:\b(' + ID + r')\s+)?(")([^"]*)(")',
               'captures': {'1': {'name': 'entity.name.namespace.alias.vss'},
                            '2': {'name': 'punctuation.definition.string.begin.vss'},
                            '3': {'name': 'string.quoted.double.import-path.vss'},
                            '4': {'name': 'punctuation.definition.string.end.vss'}}}

R = {
    'header-comment': {'patterns': [
        {'begin': r'/\*', 'end': r'\*/', 'name': 'comment.block.vss',
         'captures': {'0': {'name': 'punctuation.definition.comment.vss'}}},
        {'begin': r'//', 'end': r'$', 'name': 'comment.line.double-slash.vss',
         'beginCaptures': {'0': {'name': 'punctuation.definition.comment.vss'}}},
    ]},
    # `package kit`: the package the styles are part of.
    'package': {'match': r'^\s*(package)\s+(' + ID + r')\s*(?=$|//|/\*)',
                'captures': {'1': {'name': 'keyword.other.package.vss'},
                             '2': {'name': 'entity.name.namespace.vss'}}},
    # `import "ui/kit"`, or a group of them: packages whose tokens these
    # styles read, and which come before them in the cascade.
    'import': {'patterns': [
        {'begin': r'^\s*(import)\s*(\()', 'end': r'\)', 'name': 'meta.import.vss',
         'beginCaptures': {'1': {'name': 'keyword.control.import.vss'},
                           '2': {'name': 'punctuation.section.imports.begin.vss'}},
         'endCaptures': {'0': {'name': 'punctuation.section.imports.end.vss'}},
         'patterns': [{'include': '#header-comment'}, IMPORT_PATH]},
        {'begin': r'^\s*(import)\s+(?=(?:' + ID + r'\s+)?")', 'end': r'(?<=")|$', 'name': 'meta.import.vss',
         'beginCaptures': {'1': {'name': 'keyword.control.import.vss'}},
         'patterns': [IMPORT_PATH]},
    ]},
}

grammar = {
    '$schema': 'https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json',
    'name': 'Vertex Styles',
    'scopeName': 'source.vss',
    'fileTypes': ['vss'],
    'patterns': [
        {'include': '#package'},
        {'include': '#import'},
        # A // comment is Vertex's, which the header may use; CSS has /* */.
        {'begin': r'^\s*(//)', 'end': r'$', 'name': 'comment.line.double-slash.vss',
         'beginCaptures': {'1': {'name': 'punctuation.definition.comment.vss'}}},
        {'include': 'source.css'},
    ],
    'repository': R,
}
out = os.path.join(sys.argv[1], 'vertex-vss.tmLanguage.json')
with open(out, 'w') as f:
    json.dump(grammar, f, indent=2, ensure_ascii=False)
    f.write('\n')
