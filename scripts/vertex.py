# Generates syntaxes/vertex.tmLanguage.json: the grammar for Vertex source
# (.vs) and printed interfaces (.vinterface); and vertex-vsx.tmLanguage.json,
# the same with markup, for .vsx. The word lists follow
# vsc/token/kind.go (reserved words, # words, contextual words) and
# vsc/docs/vertex_spec.md (what Vertex adds to the core dialect).
import json, os, sys

ID = r'(?:[A-Za-z_\p{L}][A-Za-z0-9_\p{L}\p{N}]*)'
NAME = r'(?:' + ID + r'|`[^`]+`)'
OPCH = r'[/=\-+!*%<>&|^~?\p{Sm}]'

# Reserved words (token.keyword_beg .. keyword_end), by role.
CONTROL = 'if else guard switch case default for in while repeat do break continue fallthrough return throw defer catch'.split()
DECL = 'func var let struct class enum protocol extension typealias associatedtype init deinit subscript operator precedencegroup import'.split()
ACCESS = 'public private fileprivate internal'.split()
# Contextual modifiers: only a modifier when a declaration follows.
CTX_MODS = ('open package mutating nonmutating lazy weak unowned convenience required dynamic '
            'final override indirect optional nonisolated distributed infix prefix postfix '
            'borrowing consuming __consuming _const _local').split()
CTX_DECL = 'func var let class struct enum init subscript actor protocol extension case typealias deinit operator macro precedencegroup import associatedtype'.split()
PRIMS = 'bool char string void never int int8 int16 int32 int64 uint uint8 uint16 uint32 uint64 float float32 double float64'.split()
CORE_TYPES = ('Int Int8 Int16 Int32 Int64 UInt UInt8 UInt16 UInt32 UInt64 Float Float32 Float64 Double '
              'Bool String Character Substring Array Dictionary Set Optional Result Never Void Error '
              'Sendable Equatable Hashable Comparable Codable Encodable Decodable Identifiable '
              'Sequence Collection BidirectionalCollection RandomAccessCollection MutableCollection '
              'RangeReplaceableCollection IteratorProtocol Range ClosedRange StaticString '
              'UnsafePointer UnsafeMutablePointer UnsafeRawPointer UnsafeMutableRawPointer '
              'UnsafeBufferPointer UnsafeMutableBufferPointer UnsafeRawBufferPointer '
              'UnsafeMutableRawBufferPointer OpaquePointer AnyObject AnyHashable Task '
              'CustomStringConvertible Numeric BinaryInteger FixedWidthInteger SignedInteger '
              'UnsignedInteger FloatingPoint BinaryFloatingPoint ExpressibleByIntegerLiteral '
              'ExpressibleByStringLiteral ExpressibleByArrayLiteral Copyable Escapable').split()
POUND_KW = 'available unavailable selector keyPath sourceLocation'.split()
POUND_LIT = 'file fileID filePath line column function dsohandle colorLiteral fileLiteral imageLiteral'.split()
CONDITIONS = ('os arch canImport targetEnvironment swift compiler hasFeature hasAttribute '
              '_endian _pointerBitWidth _runtime _ptrauth _hasAtomicBitWidth _compiler_version').split()
PLATFORMS = ('macOS macOSApplicationExtension iOS iOSApplicationExtension tvOS watchOS visionOS '
             'macCatalyst Linux Windows Android FreeBSD OpenBSD WASI Cygwin Haiku').split()
ACCESSORS = 'get set willSet didSet _read _modify unsafeAddress unsafeMutableAddress init'.split()

def words(ws): return r'\b(?:' + '|'.join(ws) + r')\b'

def cap(n, name): return {str(n): {'name': name}}

R = {}

R['shebang'] = {'match': r'\A#!.*$', 'name': 'comment.line.shebang.vertex'}

R['code'] = {'patterns': [{'include': '#' + k} for k in [
    'comments', 'compiler-control', 'attributes', 'strings', 'regex', 'numbers',
    'package-declaration', 'import-declaration', 'function-declaration',
    'type-declaration', 'variable-declaration', 'enum-case', 'accessors',
    'execution-modifier', 'keywords', 'pound-words', 'macro-expansion', 'types',
    'backtick-identifier', 'special-identifiers', 'argument-label', 'function-call',
    'member-access', 'operators', 'brace-block', 'paren-group', 'punctuation']]}

# ---- comments ----
R['comments'] = {'patterns': [
    {'begin': r'/\*\*(?!/)', 'end': r'\*/', 'name': 'comment.block.documentation.vertex',
     'captures': {'0': {'name': 'punctuation.definition.comment.vertex'}},
     'patterns': [{'include': '#nested-block-comment'}, {'include': '#doc-markup'}]},
    {'begin': r'/\*', 'end': r'\*/', 'name': 'comment.block.vertex',
     'captures': {'0': {'name': 'punctuation.definition.comment.vertex'}},
     'patterns': [{'include': '#nested-block-comment'}]},
    {'begin': r'///', 'end': r'$', 'name': 'comment.line.triple-slash.documentation.vertex',
     'beginCaptures': {'0': {'name': 'punctuation.definition.comment.vertex'}},
     'patterns': [{'include': '#doc-markup'}]},
    {'match': r'(//)\s*(MARK|TODO|FIXME|NOTE|HACK|XXX)(:)?(.*)$', 'name': 'comment.line.double-slash.vertex',
     'captures': {'1': {'name': 'punctuation.definition.comment.vertex'},
                  '2': {'name': 'keyword.other.comment-tag.vertex'},
                  '3': {'name': 'punctuation.separator.vertex'}}},
    {'begin': r'//', 'end': r'$', 'name': 'comment.line.double-slash.vertex',
     'beginCaptures': {'0': {'name': 'punctuation.definition.comment.vertex'}}},
]}
# Block comments nest: /* /* */ */ is one comment (vsc/scanner blockComment).
R['nested-block-comment'] = {'begin': r'/\*', 'end': r'\*/', 'name': 'comment.block.nested.vertex',
                             'patterns': [{'include': '#nested-block-comment'}]}
R['doc-markup'] = {'patterns': [
    {'match': r'(?<=^|///|\*)\s*(-)\s+(Parameters?|Returns|Throws|Note|Warning|Important|Precondition|Postcondition|Complexity|SeeAlso|Author|Since|Version|Attention|Bug|Experiment|Invariant|Requires|Todo)\b(?:\s+(' + ID + r'))?\s*(:)',
     'captures': {'1': {'name': 'punctuation.definition.list.vertex'},
                  '2': {'name': 'keyword.other.documentation.vertex'},
                  '3': {'name': 'variable.parameter.documentation.vertex'},
                  '4': {'name': 'punctuation.separator.vertex'}}},
    {'match': r'`[^`]+`', 'name': 'markup.inline.raw.vertex'},
]}

# ---- #if, #available, #file and macro expansions ----
R['compiler-control'] = {'patterns': [
    {'begin': r'^\s*(#)(if|elseif)\b', 'end': r'(?=//|/\*)|$',
     'beginCaptures': {'0': {'name': 'keyword.control.directive.conditional.vertex'},
                       '1': {'name': 'punctuation.definition.directive.vertex'}},
     'name': 'meta.preprocessor.conditional.vertex',
     'patterns': [
         {'match': r'\b(' + '|'.join(CONDITIONS) + r')\s*(?=\()', 'captures': {'1': {'name': 'support.function.condition.vertex'}}},
         {'match': words(['true', 'false']), 'name': 'constant.language.boolean.vertex'},
         {'match': r'&&|\|\||!|>=|<', 'name': 'keyword.operator.logical.vertex'},
         {'include': '#numbers'},
         {'match': r'[()]', 'name': 'punctuation.section.parens.vertex'},
         {'match': ID, 'name': 'variable.other.condition.vertex'}]},
    {'match': r'^\s*(#)(else|endif)\b', 'captures': {'0': {'name': 'keyword.control.directive.conditional.vertex'},
                                                     '1': {'name': 'punctuation.definition.directive.vertex'}}},
    {'begin': r'(#)(error|warning)\s*(\()', 'end': r'\)',
     'beginCaptures': {'1': {'name': 'punctuation.definition.directive.vertex'},
                       '2': {'name': 'keyword.control.directive.diagnostic.vertex'},
                       '3': {'name': 'punctuation.section.arguments.begin.vertex'}},
     'endCaptures': {'0': {'name': 'punctuation.section.arguments.end.vertex'}},
     'patterns': [{'include': '#strings'}]},
]}
R['pound-words'] = {'patterns': [
    {'begin': r'(#)(available|unavailable)\s*(\()', 'end': r'\)',
     'beginCaptures': {'1': {'name': 'punctuation.definition.keyword.vertex'},
                       '2': {'name': 'keyword.other.availability.vertex'},
                       '3': {'name': 'punctuation.section.arguments.begin.vertex'}},
     'endCaptures': {'0': {'name': 'punctuation.section.arguments.end.vertex'}},
     'patterns': [
         {'match': r'\b(' + '|'.join(PLATFORMS) + r')\b', 'name': 'support.constant.platform.vertex'},
         {'match': r'\*', 'name': 'keyword.other.wildcard.vertex'},
         {'include': '#numbers'}, {'include': '#punctuation'}]},
    {'match': r'(#)(' + '|'.join(POUND_KW) + r')\b', 'captures': {'0': {'name': 'keyword.other.pound.vertex'},
                                                                   '1': {'name': 'punctuation.definition.keyword.vertex'}}},
    {'match': r'(#)(' + '|'.join(POUND_LIT) + r')\b', 'captures': {'0': {'name': 'support.variable.literal.vertex'},
                                                                    '1': {'name': 'punctuation.definition.keyword.vertex'}}},
]}
# Any other #name is a freestanding macro expansion (token.LookupPound).
R['macro-expansion'] = {'match': r'(#)(' + ID + r')', 'captures': {
    '1': {'name': 'punctuation.definition.macro.vertex'},
    '2': {'name': 'entity.name.function.macro.vertex'}}}

# ---- attributes ----
R['attributes'] = {'patterns': [
    {'begin': r'(@)(' + ID + r')\s*(\()', 'end': r'\)',
     'beginCaptures': {'1': {'name': 'punctuation.definition.attribute.vertex'},
                       '2': {'name': 'storage.modifier.attribute.vertex'},
                       '3': {'name': 'punctuation.section.arguments.begin.vertex'}},
     'endCaptures': {'0': {'name': 'punctuation.section.arguments.end.vertex'}},
     'name': 'meta.attribute.vertex',
     'patterns': [{'match': r'\b(' + ID + r')\s*(:)', 'captures': {'1': {'name': 'variable.parameter.attribute.vertex'},
                                                                   '2': {'name': 'punctuation.separator.vertex'}}},
                  {'include': '#code'}]},
    {'match': r'(@)(' + ID + r')', 'name': 'meta.attribute.vertex', 'captures': {
        '1': {'name': 'punctuation.definition.attribute.vertex'},
        '2': {'name': 'storage.modifier.attribute.vertex'}}},
]}

# ---- strings ----
ESC = r'\\(?:[0\\tnr"\']|u\{[0-9A-Fa-f]{1,8}\})'
def string_rule(begin, end, name, pounds):
    if pounds == 0:
        guts = [{'include': '#interpolation'},
                {'match': ESC, 'name': 'constant.character.escape.vertex'},
                {'match': r'\\.', 'name': 'invalid.illegal.escape.vertex'}]
    elif pounds == 1:
        # Only \# starts an escape or interpolation in a #"..."# literal.
        guts = [{'include': '#raw-interpolation'},
                {'match': r'\\#(?:[0\\tnr"\']|u\{[0-9A-Fa-f]{1,8}\})', 'name': 'constant.character.escape.vertex'}]
    else:
        guts = []
    return {'begin': begin, 'end': end, 'name': name,
            'beginCaptures': {'0': {'name': 'punctuation.definition.string.begin.vertex'}},
            'endCaptures': {'0': {'name': 'punctuation.definition.string.end.vertex'}},
            'patterns': guts}
R['strings'] = {'patterns': [
    string_rule(r'"""', r'"""', 'string.quoted.triple.vertex', 0),
    string_rule(r'#"""', r'"""#', 'string.quoted.triple.raw.vertex', 1),
    string_rule(r'(#{2,})"""', r'"""\1', 'string.quoted.triple.raw.vertex', 2),
    string_rule(r'"', r'"|$', 'string.quoted.double.vertex', 0),
    string_rule(r'#"', r'"#|$', 'string.quoted.double.raw.vertex', 1),
    string_rule(r'(#{2,})"', r'"\1|$', 'string.quoted.double.raw.vertex', 2),
]}
def interp(open_):
    return {'begin': open_, 'end': r'\)', 'contentName': 'source.vtx',
            'name': 'meta.embedded.line.vertex',
            'beginCaptures': {'0': {'name': 'punctuation.section.embedded.begin.vertex'}},
            'endCaptures': {'0': {'name': 'punctuation.section.embedded.end.vertex'}},
            'patterns': [{'include': '#code'}]}
R['interpolation'] = interp(r'\\\(')
R['raw-interpolation'] = interp(r'\\#\(')

# Regex literals: #/.../# always; a bare /.../ only where an operand may
# start and the slash is not followed by a space (SE-0354, tryRegex).
R['regex'] = {'patterns': [
    {'begin': r'(#+)/', 'end': r'/\1', 'name': 'string.regexp.extended.vertex',
     'beginCaptures': {'0': {'name': 'punctuation.definition.string.begin.regexp.vertex'}},
     'endCaptures': {'0': {'name': 'punctuation.definition.string.end.regexp.vertex'}},
     'patterns': [{'include': '#regex-guts'}]},
    {'match': r'(?<=^|[\s(\[{,:=;!&|?])(/)(?![\s/*])((?:\\.|[^/\\\n])+)(/)(?![\w/])',
     'name': 'string.regexp.vertex',
     'captures': {'1': {'name': 'punctuation.definition.string.begin.regexp.vertex'},
                  '2': {'patterns': [{'include': '#regex-guts'}]},
                  '3': {'name': 'punctuation.definition.string.end.regexp.vertex'}}},
]}
R['regex-guts'] = {'patterns': [
    {'match': r'\\[dDwWsSbBnrt]', 'name': 'constant.character.escape.backslash.regexp'},
    {'match': r'\\.', 'name': 'constant.character.escape.regexp'},
    {'match': r'[*+?]|\{\d+(?:,\d*)?\}', 'name': 'keyword.operator.quantifier.regexp'},
    {'match': r'[|^$]', 'name': 'keyword.operator.regexp'},
    {'match': r'\[\^?|\]', 'name': 'punctuation.definition.character-class.regexp'},
    {'match': r'\((?:\?(?:<' + ID + r'>|[:=!]|<[=!]))?|\)', 'name': 'punctuation.definition.group.regexp'},
]}

# ---- numbers (vsc/scanner literals.go) ----
R['numbers'] = {'patterns': [
    {'match': r'\b0x[0-9A-Fa-f][0-9A-Fa-f_]*(?:\.[0-9A-Fa-f][0-9A-Fa-f_]*)?[pP][+-]?[0-9][0-9_]*\b', 'name': 'constant.numeric.float.hexadecimal.vertex'},
    {'match': r'\b0x[0-9A-Fa-f][0-9A-Fa-f_]*\b', 'name': 'constant.numeric.integer.hexadecimal.vertex'},
    {'match': r'\b0o[0-7][0-7_]*\b', 'name': 'constant.numeric.integer.octal.vertex'},
    {'match': r'\b0b[01][01_]*\b', 'name': 'constant.numeric.integer.binary.vertex'},
    {'match': r'\b[0-9][0-9_]*(?:\.[0-9][0-9_]*(?:[eE][+-]?[0-9][0-9_]*)?|[eE][+-]?[0-9][0-9_]*)\b', 'name': 'constant.numeric.float.decimal.vertex'},
    {'match': r'\b[0-9][0-9_]*\b', 'name': 'constant.numeric.integer.decimal.vertex'},
    # 0b12, 1_000km, 0X1: one malformed literal, as the scanner reports it.
    {'match': r'(?<![.\w])[0-9][0-9A-Za-z_]*[A-Za-z_][0-9A-Za-z_]*\b', 'name': 'invalid.illegal.numeric.vertex'},
]}

# ---- declarations ----
# `package http` names the module; `package func` is an access modifier.
R['package-declaration'] = {'match': r'^\s*(package)\s+(?!(?:' + '|'.join(CTX_DECL + ACCESS + CTX_MODS + ['static']) + r')\b)(' + ID + r')\s*(?=$|//|;)',
    'captures': {'1': {'name': 'keyword.other.package.vertex'},
                 '2': {'name': 'entity.name.namespace.vertex'}}}

IMPORT_PATH = {'match': r'(?:\b(' + ID + r')\s+)?(")([^"]*)(")',
               'captures': {'1': {'name': 'entity.name.namespace.alias.vertex'},
                            '2': {'name': 'punctuation.definition.string.begin.vertex'},
                            '3': {'name': 'string.quoted.double.import-path.vertex'},
                            '4': {'name': 'punctuation.definition.string.end.vertex'}}}
R['import-declaration'] = {'patterns': [
    {'begin': r'\b(import)\s*(\()', 'end': r'\)', 'name': 'meta.import.vertex',
     'beginCaptures': {'1': {'name': 'keyword.control.import.vertex'},
                       '2': {'name': 'punctuation.section.imports.begin.vertex'}},
     'endCaptures': {'0': {'name': 'punctuation.section.imports.end.vertex'}},
     'patterns': [{'include': '#comments'}, IMPORT_PATH]},
    {'begin': r'\b(import)\s+(?=(?:' + ID + r'\s+)?")', 'end': r'(?<=")|$', 'name': 'meta.import.vertex',
     'beginCaptures': {'1': {'name': 'keyword.control.import.vertex'}},
     'patterns': [IMPORT_PATH]},
    {'match': r'\b(import)\s+(?:(typealias|struct|class|enum|protocol|let|var|func)\s+)?(' + ID + r'(?:\.' + ID + r')*)',
     'name': 'meta.import.vertex',
     'captures': {'1': {'name': 'keyword.control.import.vertex'},
                  '2': {'name': 'storage.type.vertex'},
                  '3': {'name': 'entity.name.namespace.vertex'}}},
]}

FUNC_NAME_AFTER_PAREN_EXCLUDE = r'(?!(?:throws|rethrows|async|kernel|graph|where)\b)'
R['function-declaration'] = {
    'begin': r'\b(func)\b|(?<!\.)\b(init|subscript)\b([?!])?(?=\s*[<(])',
    'beginCaptures': {'1': {'name': 'storage.type.function.vertex'},
                      '2': {'name': 'storage.type.function.vertex'},
                      '3': {'name': 'keyword.operator.optional.vertex'}},
    'end': r'(?<=\})|$',
    'name': 'meta.definition.function.vertex',
    'patterns': [
        {'include': '#comments'},
        # A receiver method: func (v: inout Vec2) scale(by:) (vertex_spec §3.3).
        {'begin': r'\G\s*(\()(?=\s*' + NAME + r'\s*:)', 'end': r'\)',
         'beginCaptures': {'1': {'name': 'punctuation.section.receiver.begin.vertex'}},
         'endCaptures': {'0': {'name': 'punctuation.section.receiver.end.vertex'}},
         'name': 'meta.receiver.vertex',
         'patterns': [
             {'match': r'\G\s*(' + NAME + r')\s*(:)',
              'captures': {'1': {'name': 'variable.parameter.receiver.vertex'},
                           '2': {'name': 'punctuation.separator.vertex'}}},
             {'match': words(['borrowing', 'consuming', 'inout', '__shared', '__owned']), 'name': 'storage.modifier.ownership.vertex'},
             {'include': '#types'}, {'include': '#paren-group'}, {'include': '#punctuation'}, {'include': '#operators'}]},
        {'match': r'(?<=\))\s*' + FUNC_NAME_AFTER_PAREN_EXCLUDE + r'(' + NAME + r')(?=\s*[<(])',
         'captures': {'1': {'name': 'entity.name.function.vertex'}}},
        {'match': r'\G\s+(' + NAME + r'|' + OPCH + r'+|\.' + OPCH + r'*)',
         'captures': {'1': {'name': 'entity.name.function.vertex'}}},
        {'include': '#generic-clause'},
        {'include': '#parameter-clause'},
        {'match': r'->', 'name': 'keyword.operator.arrow.vertex'},
        {'include': '#execution-modifier'},
        {'match': words(['async', 'throws', 'rethrows', 'reasync']), 'name': 'storage.modifier.effect.vertex'},
        {'match': r'\bwhere\b', 'name': 'keyword.other.where.vertex'},
        {'begin': r'\{', 'end': r'\}', 'name': 'meta.body.function.vertex',
         'beginCaptures': {'0': {'name': 'punctuation.section.function.begin.vertex'}},
         'endCaptures': {'0': {'name': 'punctuation.section.function.end.vertex'}},
         'patterns': [{'include': '#code'}]},
        {'include': '#code'},
    ]}
R['generic-clause'] = {'begin': r'<', 'end': r'>', 'name': 'meta.generic-clause.vertex',
    'beginCaptures': {'0': {'name': 'punctuation.definition.generic.begin.vertex'}},
    'endCaptures': {'0': {'name': 'punctuation.definition.generic.end.vertex'}},
    'patterns': [{'include': '#comments'},
                 {'match': r'\beach\b', 'name': 'storage.modifier.pack.vertex'},
                 {'match': r'\bwhere\b', 'name': 'keyword.other.where.vertex'},
                 {'include': '#generic-clause'}, {'include': '#types'},
                 {'match': ID, 'name': 'entity.name.type.parameter.vertex'},
                 {'include': '#punctuation'}, {'include': '#operators'}]}
R['parameter-clause'] = {'begin': r'\(', 'end': r'\)', 'name': 'meta.parameter-clause.vertex',
    'beginCaptures': {'0': {'name': 'punctuation.section.parameters.begin.vertex'}},
    'endCaptures': {'0': {'name': 'punctuation.section.parameters.end.vertex'}},
    'patterns': [
        {'include': '#comments'},
        # external label, then local name: `to dest:`, `_ x:`
        {'match': r'(?:^|(?<=[(,]))\s*(' + NAME + r')\s+(' + NAME + r')\s*(?=:)',
         'captures': {'1': {'name': 'entity.name.function.label.vertex'},
                      '2': {'name': 'variable.parameter.function.vertex'}}},
        {'match': r'(?:^|(?<=[(,]))\s*(' + NAME + r')\s*(?=:)',
         'captures': {'1': {'name': 'variable.parameter.function.vertex'}}},
        {'match': r':', 'name': 'punctuation.separator.parameter.vertex'},
        {'match': words(['inout', 'borrowing', 'consuming', '__shared', '__owned', 'sending', 'isolated', '_const']), 'name': 'storage.modifier.ownership.vertex'},
        {'match': r'\.\.\.', 'name': 'keyword.operator.variadic.vertex'},
        {'begin': r'=', 'end': r'(?=[,)])', 'beginCaptures': {'0': {'name': 'keyword.operator.assignment.vertex'}},
         'name': 'meta.default-value.vertex', 'patterns': [{'include': '#code'}]},
        {'include': '#code'},
    ]}

R['type-declaration'] = {'patterns': [
    {'match': r'\b(struct|class|enum|protocol|actor|extension)\s+(' + NAME + r'(?:\.' + NAME + r')*)',
     'captures': {'1': {'name': 'storage.type.$1.vertex'},
                  '2': {'name': 'entity.name.type.vertex'}}},
    {'match': r'\b(typealias|associatedtype)\s+(' + NAME + r')',
     'captures': {'1': {'name': 'storage.type.$1.vertex'},
                  '2': {'name': 'entity.name.type.vertex'}}},
    {'match': r'\b(precedencegroup)\s+(' + NAME + r')',
     'captures': {'1': {'name': 'storage.type.precedencegroup.vertex'},
                  '2': {'name': 'entity.name.type.precedencegroup.vertex'}}},
    {'match': r'\b(prefix|infix|postfix)?\s*\b(operator)\s+(' + OPCH + r'+|\.' + OPCH + r'*)',
     'captures': {'1': {'name': 'storage.modifier.vertex'},
                  '2': {'name': 'storage.type.operator.vertex'},
                  '3': {'name': 'entity.name.function.operator.vertex'}}},
    {'match': r'\b(macro)\s+(' + NAME + r')(?=\s*[<(])',
     'captures': {'1': {'name': 'storage.type.macro.vertex'},
                  '2': {'name': 'entity.name.function.macro.vertex'}}},
    {'match': r'\b(higherThan|lowerThan|associativity|assignment)\s*(:)',
     'captures': {'1': {'name': 'keyword.other.precedencegroup.vertex'},
                  '2': {'name': 'punctuation.separator.vertex'}}},
]}

R['variable-declaration'] = {'patterns': [
    {'match': r'\b(let)\s+(' + NAME + r')',
     'captures': {'1': {'name': 'storage.type.let.vertex'},
                  '2': {'name': 'variable.other.constant.vertex'}}},
    {'match': r'\b(var)\s+(' + NAME + r')',
     'captures': {'1': {'name': 'storage.type.var.vertex'},
                  '2': {'name': 'variable.other.readwrite.vertex'}}},
]}
R['enum-case'] = {'match': r'^\s*(?:(indirect)\s+)?(case)\s+(?!(?:let|var|is)\b)(' + NAME + r')(?=\s*(?:[(,=]|$|//))',
    'captures': {'1': {'name': 'storage.modifier.vertex'},
                 '2': {'name': 'keyword.other.case.vertex'},
                 '3': {'name': 'variable.other.enummember.vertex'}}}
R['accessors'] = {'match': r'(?:^|(?<=[{;])|(?<=\bget\s)|(?<=\bset\s)|(?<=\bmutating\s)|(?<=\bnonmutating\s))\s*\b(' + '|'.join(a for a in ACCESSORS if a != 'init') + r')\b(?=\s*(?:[{(};]|$|\b(?:get|set|async|throws|mutating|nonmutating)\b))',
    'captures': {'1': {'name': 'keyword.other.accessor.vertex'}}}
# Vertex's execution modifiers sit between the effects and the arrow
# (vertex_spec §3.4): func f(x: [float32]) kernel -> [float32].
R['execution-modifier'] = {'match': r'(?:(?<=\))|(?<=\bthrows)|(?<=\basync)|(?<=\brethrows))\s*\b(kernel|graph)\b(?=\s*(?:->|\{|\bwhere\b|$))',
    'captures': {'1': {'name': 'storage.modifier.execution.vertex'}}}

R['keywords'] = {'patterns': [
    {'match': r'\b(try|await)(?:([?!])|\b)', 'captures': {'1': {'name': 'keyword.control.$1.vertex'},
                                                          '2': {'name': 'keyword.operator.$1.vertex'}}},
    {'match': r'\b(as)([?!])', 'captures': {'1': {'name': 'keyword.operator.type.cast.vertex'},
                                          '2': {'name': 'keyword.operator.type.cast.vertex'}}},
    {'match': words(['as', 'is']), 'name': 'keyword.operator.type.vertex'},
    {'match': words(CONTROL), 'name': 'keyword.control.vertex'},
    {'match': words(DECL), 'name': 'storage.type.vertex'},
    {'match': words(ACCESS), 'name': 'storage.modifier.access.vertex'},
    {'match': r'\b(static)\b', 'name': 'storage.modifier.static.vertex'},
    {'match': r'\b(package|open)\b(?=\s*\((?:set)\)|\s+(?:' + '|'.join(CTX_MODS + ACCESS + ['static']) + r'\s+)*(?:' + '|'.join(CTX_DECL) + r')\b)', 'name': 'storage.modifier.access.vertex'},
    {'match': r'\b(' + '|'.join(CTX_MODS) + r')\b(?=\s*(?:\((?:safe|unsafe|set)\))?\s+(?:(?:' + '|'.join(CTX_MODS + ACCESS + ['static']) + r')\s+)*(?:' + '|'.join(CTX_DECL) + r')\b)', 'name': 'storage.modifier.vertex'},
    {'match': r'\b(async)\b(?=\s+(?:let|var)\b)', 'name': 'storage.modifier.effect.vertex'},
    {'match': words(['async', 'throws', 'rethrows']) + r'(?=\s*(?:->|\{|throws|kernel|graph|$|\())', 'name': 'storage.modifier.effect.vertex'},
    {'match': r'\b(some|any)\b(?=\s+[A-Za-z_(\[])', 'name': 'keyword.other.type.vertex'},
    {'match': words(['true', 'false']), 'name': 'constant.language.boolean.vertex'},
    {'match': r'\bnil\b', 'name': 'constant.language.nil.vertex'},
    {'match': words(['self', 'super']), 'name': 'variable.language.$0.vertex'},
    {'match': r'\bSelf\b', 'name': 'variable.language.self.type.vertex'},
    {'match': words(['consume', 'copy', 'discard', 'yield']) + r'(?=\s+[A-Za-z_(`$])', 'name': 'keyword.operator.ownership.vertex'},
    {'match': r'\bwhere\b', 'name': 'keyword.other.where.vertex'},
]}

R['types'] = {'patterns': [
    {'match': r'\bAny\b', 'name': 'support.type.any.vertex'},
    # Vertex's lowercase primitive spellings (vertex_spec §2.1).
    {'match': r'(?<![.\w])(' + '|'.join(PRIMS) + r'|any)\b(?!\s*:(?!:))', 'name': 'support.type.primitive.vertex'},
    {'match': r'\b(' + '|'.join(CORE_TYPES) + r')\b', 'name': 'support.type.vertex'},
    {'match': r'(?<=\.)(Type|Protocol)\b', 'name': 'keyword.other.metatype.vertex'},
    # A member of self is never a type, whatever its case.
    {'match': r'(?<=\bself\.)[A-Z][A-Za-z0-9_]*\b', 'name': 'variable.other.property.vertex'},
    {'match': r'\b_?[A-Z][A-Za-z0-9_]*\b', 'name': 'entity.name.type.vertex'},
]}

R['backtick-identifier'] = {'match': r'(`)[^`]+(`)', 'name': 'variable.other.escaped.vertex',
    'captures': {'1': {'name': 'punctuation.definition.identifier.vertex'},
                 '2': {'name': 'punctuation.definition.identifier.vertex'}}}
R['special-identifiers'] = {'patterns': [
    {'match': r'\$[0-9]+', 'name': 'variable.language.closure-argument.vertex'},
    {'match': r'\$' + ID, 'name': 'variable.other.projection.vertex'},
    {'match': r'(?<![\w$])_(?![\w$])', 'name': 'variable.language.wildcard.vertex'},
]}
R['argument-label'] = {'match': r'(?<=[(,])\s*(' + NAME + r')\s*(:)(?!:)',
    'captures': {'1': {'name': 'variable.parameter.argument-label.vertex'},
                 '2': {'name': 'punctuation.separator.argument-label.vertex'}}}
R['function-call'] = {'match': r'(?!(?:' + '|'.join(CONTROL + DECL + ACCESS + ['as', 'is', 'try', 'await', 'some', 'any', 'self', 'super', 'Self', 'nil', 'true', 'false', 'where', 'static']) + r')\b)\b(' + ID + r')(?=\s*\()',
    'captures': {'1': {'name': 'entity.name.function.call.vertex'}}}
R['member-access'] = {'match': r'(\.)(?=\s*(?:' + NAME + r'|[0-9]))', 'captures': {'1': {'name': 'punctuation.accessor.vertex'}}}

R['operators'] = {'patterns': [
    {'match': r'->', 'name': 'keyword.operator.arrow.vertex'},
    {'match': r'\.\.\.|\.\.<', 'name': 'keyword.operator.range.vertex'},
    {'match': r'\\(?=[.A-Za-z_(])', 'name': 'keyword.operator.key-path.vertex'},
    {'match': r'\?\?', 'name': 'keyword.operator.nil-coalescing.vertex'},
    {'match': r'&&|\|\||(?<![\w)\]?!])!(?!=)', 'name': 'keyword.operator.logical.vertex'},
    {'match': r'===|!==|==|!=|<=|>=|~=', 'name': 'keyword.operator.comparison.vertex'},
    {'match': r'(?:[-+*/%&|^]|<<|>>|&[-+*])=', 'name': 'keyword.operator.assignment.compound.vertex'},
    {'match': r'=(?!=)', 'name': 'keyword.operator.assignment.vertex'},
    {'match': r'&[-+*]|&<<|&>>', 'name': 'keyword.operator.arithmetic.overflow.vertex'},
    {'match': r'<<|>>|[&|^~]', 'name': 'keyword.operator.bitwise.vertex'},
    {'match': r'[-+*/%]', 'name': 'keyword.operator.arithmetic.vertex'},
    {'match': r'[<>]', 'name': 'keyword.operator.comparison.vertex'},
    {'match': r'(?<=[\w)\]>])[?!](?!=)', 'name': 'keyword.operator.optional.vertex'},
    {'match': r'\?', 'name': 'keyword.operator.ternary.vertex'},
    {'match': OPCH + r'+', 'name': 'keyword.operator.custom.vertex'},
]}
R['brace-block'] = {'begin': r'\{', 'end': r'\}',
    'beginCaptures': {'0': {'name': 'punctuation.section.block.begin.vertex'}},
    'endCaptures': {'0': {'name': 'punctuation.section.block.end.vertex'}},
    'patterns': [{'include': '#code'}]}
R['paren-group'] = {'begin': r'\(', 'end': r'\)',
    'beginCaptures': {'0': {'name': 'punctuation.section.parens.begin.vertex'}},
    'endCaptures': {'0': {'name': 'punctuation.section.parens.end.vertex'}},
    'patterns': [{'include': '#code'}]}
R['punctuation'] = {'patterns': [
    {'match': r',', 'name': 'punctuation.separator.comma.vertex'},
    {'match': r';', 'name': 'punctuation.terminator.statement.vertex'},
    {'match': r':', 'name': 'punctuation.separator.colon.vertex'},
    {'match': r'[\[\]]', 'name': 'punctuation.section.brackets.vertex'},
    {'match': r'\.', 'name': 'punctuation.accessor.vertex'},
]}


grammar = {
    '$schema': 'https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json',
    'name': 'Vertex',
    'scopeName': 'source.vtx',
    'fileTypes': ['vs', 'vinterface'],
    'patterns': [{'include': '#shebang'}, {'include': '#code'}],
    'repository': R,
}
out = os.path.join(sys.argv[1], 'vertex.tmLanguage.json')
with open(out, 'w') as f:
    json.dump(grammar, f, indent=2, ensure_ascii=False)
    f.write('\n')

# ---- .vsx: Vertex with markup (proposed_vsx.md §6, §9.1) ----
# The same grammar, with markup where the file may hold it. A `<` opens a
# tag where Vertex would read a prefix operator -- not bound on the left
# (line start, whitespace, or one of ( [ { , ; :), and followed by a name
# or `>` -- so `a < b`, `a<b`, `Array<int>` and `sorted(by: <)` stay what
# they are. A declaration's generic clause is matched by its own rule
# first. Inside markup, `{…}` is Vertex again, which may hold markup.
import copy
X = copy.deepcopy(R)

# A capitalized or dotted name is a component; a lowercase one an HTML
# element. Two groups, so each gets its scope.
COMPONENT = r'(?:[A-Z][\w$]*(?:\.[\w$]+)*|[\w$]+(?:\.[\w$]+)+)'
ELEMENT = r'[a-z_$][\w$]*(?:[:-][\w$-]+)*'
TAG = r'(?:(' + COMPONENT + r')|(' + ELEMENT + r'))'

def element(begin_prefix):
    return {
        # `<` then a name, or `<>`: a `<` before a space or a digit is
        # the operator.
        'begin': begin_prefix + r'(<)(?:' + TAG + r'(?=[\s/>{]|$)|(?=>))',
        'end': r'(/>)|(</)' + TAG + r'?\s*(>)',
        'beginCaptures': {'1': {'name': 'punctuation.definition.tag.begin.vsx'},
                          '2': {'name': 'support.class.component.vsx'},
                          '3': {'name': 'entity.name.tag.vsx'}},
        'endCaptures': {'1': {'name': 'punctuation.definition.tag.end.vsx'},
                        '2': {'name': 'punctuation.definition.tag.begin.vsx'},
                        '3': {'name': 'support.class.component.vsx'},
                        '4': {'name': 'entity.name.tag.vsx'},
                        '5': {'name': 'punctuation.definition.tag.end.vsx'}},
        'name': 'meta.tag.vsx',
        'patterns': [{'include': '#markup-attributes'}, {'include': '#markup-children'}]}

# At an expression's start: the prefix position.
X['markup'] = element(r'(?:^|(?<=[\s(\[{,;:]))')
# Among an element's children: any `<name` or `<>`.
X['markup-inner'] = element(r'')
X['markup-attributes'] = {
    'begin': r'\G', 'end': r'(?=/>)|(>)',
    'endCaptures': {'1': {'name': 'punctuation.definition.tag.end.vsx'}},
    'name': 'meta.tag.attributes.vsx',
    'patterns': [
        {'include': '#comments'},
        # `{...attrs}`
        {'begin': r'(\{)\s*(\.\.\.)', 'end': r'\}',
         'beginCaptures': {'1': {'name': 'punctuation.section.embedded.begin.vsx'},
                           '2': {'name': 'keyword.operator.spread.vsx'}},
         'endCaptures': {'0': {'name': 'punctuation.section.embedded.end.vsx'}},
         'name': 'meta.embedded.expression.vsx', 'patterns': [{'include': '#code'}]},
        # class:done, style:--kit-accent, data-p, onClick
        {'match': r'(?<![\w$-])(on[A-Z][\w$]*)(?=\s*=)', 'name': 'entity.other.attribute-name.event.vsx'},
        {'match': r'(?<![\w$-])(class|style)(:)([\w$-]+)',
         'captures': {'1': {'name': 'entity.other.attribute-name.namespace.vsx'},
                      '2': {'name': 'punctuation.separator.namespace.vsx'},
                      '3': {'name': 'entity.other.attribute-name.vsx'}}},
        {'match': r'(?<![\w$-])[A-Za-z_$][\w$]*(?:[:.-][\w$-]+)*', 'name': 'entity.other.attribute-name.vsx'},
        {'match': r'=', 'name': 'keyword.operator.assignment.vsx'},
        {'begin': r'"', 'end': r'"', 'name': 'string.quoted.double.vsx',
         'beginCaptures': {'0': {'name': 'punctuation.definition.string.begin.vsx'}},
         'endCaptures': {'0': {'name': 'punctuation.definition.string.end.vsx'}}},
        {'begin': r"'", 'end': r"'", 'name': 'string.quoted.single.vsx',
         'beginCaptures': {'0': {'name': 'punctuation.definition.string.begin.vsx'}},
         'endCaptures': {'0': {'name': 'punctuation.definition.string.end.vsx'}}},
        {'include': '#markup-code'},
    ]}
X['markup-children'] = {'patterns': [
    {'include': '#markup-code'},
    {'include': '#markup-inner'},
    {'match': r'&(?:[A-Za-z][A-Za-z0-9]*|#[0-9]+|#x[0-9A-Fa-f]+);', 'name': 'constant.character.entity.vsx'},
    {'match': r'[^<{&]+', 'name': 'meta.jsx.children.vsx'},
]}
# `{…}`: Vertex, markup included. Empty braces and `{/* … */}` are nothing.
X['markup-code'] = {'begin': r'\{', 'end': r'\}',
    'beginCaptures': {'0': {'name': 'punctuation.section.embedded.begin.vsx'}},
    'endCaptures': {'0': {'name': 'punctuation.section.embedded.end.vsx'}},
    'name': 'meta.embedded.expression.vsx',
    'patterns': [{'include': '#code'}]}
# Markup is tried before the operators, after comments and strings.
code = X['code']['patterns']
code.insert(2, {'include': '#markup'})

vsx = {
    '$schema': 'https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json',
    'name': 'Vertex Markup',
    'scopeName': 'source.vtx.vsx',
    'fileTypes': ['vsx'],
    'patterns': [{'include': '#shebang'}, {'include': '#code'}],
    'repository': X,
}
with open(os.path.join(sys.argv[1], 'vertex-vsx.tmLanguage.json'), 'w') as f:
    json.dump(vsx, f, indent=2, ensure_ascii=False)
    f.write('\n')
