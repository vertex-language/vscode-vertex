# Generates syntaxes/vertex-ir.tmLanguage.json: the grammar for Vertex IR
# (.vir), after ir/spec/grammar.md and what ir/text prints (registers such
# as %bb1.0 carry dots; the i128 namespace exists though the spec lists it
# nowhere yet).
import json, os, sys

SYM = r'@[A-Za-z_$?@.<>][A-Za-z0-9_$?@.<>]*'
REG = r'%[A-Za-z0-9_.]+'
NS = r'(?:i1|i8|i16|i32|i64|i128|f16|bf16|f32|f64|f80|f128|ptr|v128)'

def words(ws): return r'\b(?:' + '|'.join(ws) + r')\b'

TERMINATORS = 'br brif br_table brind return trap resume tail_call tail_callind invoke invokeind'.split()
CALLS = 'call callind'.split()
BARE = 'memcpy memmove memset memcmp fence barrier va_start va_end va_copy'.split()
MODULE_KW = 'module use layout'.split()
DECL_KW = 'type global import func alias asm'.split()
LINKAGE = 'export internal hidden protected dllimport dllexport weak common'.split()
DOMAIN = 'ro rw tls shared'.split()
PLACEMENT = ('section comdat align tlsmodel nounwind personality returns_twice naked noreturn '
             'packed at zeroed volatile goto clobber').split()
TLS_MODELS = 'global-dynamic local-dynamic initial-exec local-exec'.split()
PARAM_ATTR = ('byval sret zext sext noalias swiftself swiftasync swiftindirect swifterror '
              'narrow8s narrow8u narrow16s narrow16u').split()
CALLCONV = ('ccc fastcc preserve_most preserve_all stdcall fastcall thiscall vectorcall '
            'ms_abi sysv_abi kernel').split()
ORDERING = 'unordered monotonic acquire release acq_rel seq_cst singlethread'.split()
SCOPE = 'workgroup device system'.split()
PAD = 'pad cleanup catch filter to unwind'.split()
CONSTRAINT = 'reg mem imm'.split()
SYMCONST = 'sizeof alignof offsetof'.split()
LAYOUT_ATTR = 'abi endian ptrbits stackalign extfloat vector halffloat'.split()

R = {}
R['comments'] = {'begin': r'//', 'end': r'$', 'name': 'comment.line.double-slash.vir',
                 'beginCaptures': {'0': {'name': 'punctuation.definition.comment.vir'}}}
R['strings'] = {'begin': r'"', 'end': r'"|$', 'name': 'string.quoted.double.vir',
    'beginCaptures': {'0': {'name': 'punctuation.definition.string.begin.vir'}},
    'endCaptures': {'0': {'name': 'punctuation.definition.string.end.vir'}},
    'patterns': [{'match': r'\\(?:[nrtabfv0\\"]|x[0-9A-Fa-f]{2})', 'name': 'constant.character.escape.vir'},
                 {'match': r'\\.', 'name': 'invalid.illegal.escape.vir'}]}

R['module-header'] = {'patterns': [
    {'match': r'^\s*(module)\s+([A-Za-z_][A-Za-z0-9_]*)',
     'captures': {'1': {'name': 'keyword.other.module.vir'}, '2': {'name': 'entity.name.namespace.vir'}}},
    {'match': r'^\s*(use)\b', 'captures': {'1': {'name': 'keyword.other.use.vir'}}},
    {'begin': r'^\s*(layout)\s*(\{)', 'end': r'\}', 'name': 'meta.layout.vir',
     'beginCaptures': {'1': {'name': 'keyword.other.layout.vir'}, '2': {'name': 'punctuation.section.block.begin.vir'}},
     'endCaptures': {'0': {'name': 'punctuation.section.block.end.vir'}},
     'patterns': [
         {'include': '#comments'},
         {'match': r'\b(' + '|'.join(LAYOUT_ATTR) + r')\b', 'name': 'variable.other.property.layout.vir'},
         {'match': r'\b' + NS + r'\b', 'name': 'storage.type.vir'},
         {'match': r'\b[0-9]+\b', 'name': 'constant.numeric.integer.vir'},
         {'match': r'\b[A-Za-z_][A-Za-z0-9_]*\b', 'name': 'constant.language.layout.vir'},
         {'match': r',', 'name': 'punctuation.separator.comma.vir'}]},
]}

R['definitions'] = {'patterns': [
    # type @T struct { ... }
    {'match': r'\b(type)\s+(' + SYM + r')', 'captures': {'1': {'name': 'storage.type.type.vir'}, '2': {'name': 'entity.name.type.vir'}}},
    # global ro @g ..., import global @g ...
    {'match': r'\b(global)\s+(?:(ro|rw|tls|shared)\s+)?(' + SYM + r')',
     'captures': {'1': {'name': 'storage.type.global.vir'}, '2': {'name': 'storage.modifier.domain.vir'},
                  '3': {'name': 'entity.name.variable.global.vir'}}},
    {'match': r'\b(func)\s+(' + SYM + r')', 'captures': {'1': {'name': 'storage.type.function.vir'}, '2': {'name': 'entity.name.function.vir'}}},
    {'match': r'\b(alias)\s+(func|global)\s+(' + SYM + r')\s+(' + SYM + r')',
     'captures': {'1': {'name': 'storage.type.alias.vir'}, '2': {'name': 'storage.type.vir'},
                  '3': {'name': 'entity.name.function.vir'}, '4': {'name': 'variable.other.symbol.vir'}}},
    {'match': r'^\s*(!' + r'[A-Za-z_][A-Za-z0-9_]*)\s*(=)',
     'captures': {'1': {'name': 'entity.name.tag.metadata.vir'}, '2': {'name': 'keyword.operator.assignment.vir'}}},
    # block labels: @entry:  @bb1(%x i64):  @pad pad (...) cleanup:
    {'match': r'^\s*(' + SYM + r')(?=\s*(?::|\(|\s+pad\b))', 'captures': {'1': {'name': 'entity.name.label.vir'}}},
]}

R['references'] = {'patterns': [
    {'match': r'\b(call|tail_call|invoke|ptr\.getaddr)\s+(' + SYM + r')',
     'captures': {'1': {'patterns': [{'include': '#instructions'}]}, '2': {'name': 'entity.name.function.call.vir'}}},
    {'match': r'\b(br|to|unwind|ptr\.blockaddr)\s+(' + SYM + r')',
     'captures': {'1': {'patterns': [{'include': '#instructions'}, {'include': '#keywords'}]}, '2': {'name': 'entity.name.label.vir'}}},
    {'match': r'\b(sret|byval|ptr\.alloc|ptr\.va_arg_ref\s+' + REG + r'\s*,|sizeof|alignof|offsetof)\s+(' + SYM + r')',
     'captures': {'1': {'patterns': [{'include': '#instructions'}, {'include': '#keywords'}, {'include': '#registers'}, {'include': '#punctuation'}]},
                  '2': {'name': 'entity.name.type.vir'}}},
    # callind %f : @FnType (...)
    {'match': r'(' + REG + r')\s*(:)\s*(' + SYM + r')',
     'captures': {'1': {'name': 'variable.other.register.vir'}, '2': {'name': 'punctuation.separator.vir'},
                  '3': {'name': 'entity.name.type.vir'}}},
    # a field declaration inside a struct body: name ftype
    {'match': SYM, 'name': 'variable.other.symbol.vir'},
]}

R['instructions'] = {'patterns': [
    {'match': r'\b(' + NS + r')(\.)([a-z][a-z0-9_]*)\b',
     'captures': {'1': {'name': 'storage.type.namespace.vir'}, '2': {'name': 'punctuation.accessor.vir'},
                  '3': {'name': 'support.function.instruction.vir'}}},
    {'match': words(TERMINATORS), 'name': 'keyword.control.terminator.vir'},
    {'match': words(CALLS), 'name': 'keyword.control.call.vir'},
    {'match': words(BARE), 'name': 'support.function.instruction.vir'},
]}

R['keywords'] = {'patterns': [
    {'match': words(DECL_KW), 'name': 'storage.type.vir'},
    {'match': r'\b(struct|union)\b', 'name': 'storage.type.$1.vir'},
    {'match': words(LINKAGE), 'name': 'storage.modifier.linkage.vir'},
    {'match': words(DOMAIN), 'name': 'storage.modifier.domain.vir'},
    {'match': r'(?<![\w-])(' + '|'.join(TLS_MODELS) + r')(?![\w-])', 'name': 'constant.language.tls-model.vir'},
    {'match': words(PLACEMENT), 'name': 'storage.modifier.vir'},
    {'match': words(PARAM_ATTR), 'name': 'storage.modifier.attribute.vir'},
    {'match': words(CALLCONV), 'name': 'storage.modifier.callconv.vir'},
    {'match': words(ORDERING), 'name': 'constant.language.ordering.vir'},
    {'match': words(SCOPE), 'name': 'constant.language.scope.vir'},
    {'match': words(PAD), 'name': 'keyword.other.vir'},
    {'match': words(CONSTRAINT), 'name': 'constant.language.constraint.vir'},
    {'match': words(SYMCONST), 'name': 'keyword.operator.symconst.vir'},
    {'match': r'\bnull\b', 'name': 'constant.language.null.vir'},
    {'match': words(MODULE_KW), 'name': 'keyword.other.vir'},
]}

R['types'] = {'match': r'(\[)([0-9]+)(\])|\b(' + NS + r')\b(?!\.)',
    'captures': {'1': {'name': 'punctuation.definition.array.vir'}, '2': {'name': 'constant.numeric.integer.vir'},
                 '3': {'name': 'punctuation.definition.array.vir'}, '4': {'name': 'storage.type.vir'}}}
R['registers'] = {'match': REG, 'name': 'variable.other.register.vir'}
R['metadata'] = {'match': r'![A-Za-z_][A-Za-z0-9_]*', 'name': 'entity.other.attribute-name.metadata.vir'}
R['numbers'] = {'patterns': [
    {'match': r'(?<![\w.%@])-?(?:inf|nan(?::0x[0-9A-Fa-f]+)?)\b', 'name': 'constant.numeric.float.special.vir'},
    {'match': r'(?<![\w.%@])-?0x[0-9A-Fa-f]+(?:\.[0-9A-Fa-f]*)?[pP][+-]?[0-9]+\b', 'name': 'constant.numeric.float.hexadecimal.vir'},
    {'match': r'(?<![\w.%@])-?0x[0-9A-Fa-f]+\b', 'name': 'constant.numeric.integer.hexadecimal.vir'},
    {'match': r'(?<![\w.%@])-?[0-9]+(?:\.[0-9]*(?:[eE][+-]?[0-9]+)?|[eE][+-]?[0-9]+)\b', 'name': 'constant.numeric.float.decimal.vir'},
    {'match': r'(?<![\w.%@])-?[0-9]+\b', 'name': 'constant.numeric.integer.decimal.vir'},
]}
R['axis'] = {'match': r'(?<=workitem_id|workgroup_id|workgroup_size|num_workgroups)\s+\b([xyz])\b',
             'captures': {'1': {'name': 'constant.language.axis.vir'}}}
R['punctuation'] = {'patterns': [
    {'match': r'\.\.\.', 'name': 'keyword.operator.variadic.vir'},
    {'match': r'=', 'name': 'keyword.operator.assignment.vir'},
    {'match': r'[+-]', 'name': 'keyword.operator.arithmetic.vir'},
    {'match': r',', 'name': 'punctuation.separator.comma.vir'},
    {'match': r':', 'name': 'punctuation.separator.colon.vir'},
    {'match': r'[{}]', 'name': 'punctuation.section.braces.vir'},
    {'match': r'[()]', 'name': 'punctuation.section.parens.vir'},
    {'match': r'[\[\]]', 'name': 'punctuation.section.brackets.vir'},
    {'match': r'\.', 'name': 'punctuation.accessor.vir'},
]}
# Every symbol on a branch's line is a label: brif %c, @a(%x), @b and
# br_table %i, [ @a, @b ], @default.
R['branch'] = {'begin': r'\b(br|brif|br_table|brind)\b|\b(asm)\s+(goto)\b', 'end': r'(?=//)|$',
    'beginCaptures': {'1': {'name': 'keyword.control.terminator.vir'},
                      '2': {'name': 'support.function.instruction.vir'},
                      '3': {'name': 'keyword.control.terminator.vir'}},
    'patterns': [{'include': '#strings'}, {'include': '#keywords'},
                 {'match': SYM, 'name': 'entity.name.label.vir'},
                 {'include': '#metadata'}, {'include': '#types'}, {'include': '#registers'},
                 {'include': '#numbers'}, {'include': '#punctuation'}]}
R['struct-body'] = {'begin': r'\b(struct|union)\s*(\{)', 'end': r'\}',
    'beginCaptures': {'1': {'name': 'storage.type.$1.vir'}, '2': {'name': 'punctuation.section.braces.vir'}},
    'endCaptures': {'0': {'name': 'punctuation.section.braces.vir'}},
    'patterns': [{'include': '#comments'},
                 {'match': r'(?:^|(?<=[{,]))\s*([A-Za-z_][A-Za-z0-9_]*)\s+(?=' + NS + r'\b|@|\[)',
                  'captures': {'1': {'name': 'variable.other.property.vir'}}},
                 {'match': r'\b(at)\b', 'name': 'storage.modifier.vir'},
                 {'include': '#types'}, {'include': '#references'}, {'include': '#numbers'}, {'include': '#punctuation'}]}
R['field-init'] = {'match': r'(?<=[{,])\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?==(?!=))',
    'captures': {'1': {'name': 'variable.other.property.vir'}}}

grammar = {
    '$schema': 'https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json',
    'name': 'Vertex IR',
    'scopeName': 'source.vtxir',
    'fileTypes': ['vir'],
    'patterns': [{'include': '#' + k} for k in [
        'comments', 'strings', 'module-header', 'struct-body', 'definitions', 'metadata', 'axis', 'branch',
        'references', 'instructions', 'field-init', 'keywords', 'types', 'registers', 'numbers', 'punctuation']],
    'repository': R,
}
out = os.path.join(sys.argv[1], 'vertex-ir.tmLanguage.json')
with open(out, 'w') as f:
    json.dump(grammar, f, indent=2)
    f.write('\n')
