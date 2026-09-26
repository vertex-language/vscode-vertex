# Generates the grammars for vs.mod, vs.work and vs.sum, after
# vsc/pkg/vsmod.go (go.mod's syntax: `verb args` lines, `verb ( ... )`
# blocks, // comments) and vsc/importer/sum.go (`module version hash`).
import json, sys, os

out = sys.argv[1]
TOK = r'[^\s/(),]+(?:/[^\s/(),]+)*'       # a module path or version: anything but space, ( ) and //
LOCAL = r'(?:\.\.?(?:/\S*)?|/\S*)'         # ./x ../x /abs . ..  (isLocalPath)
C = lambda n: {'name': n}

def comment(sfx):
    return {'begin': r'//', 'end': r'$', 'name': 'comment.line.double-slash.' + sfx,
            'beginCaptures': {'0': C('punctuation.definition.comment.' + sfx)}}

def version(sfx):
    return {'patterns': [
        {'match': r'\bv?[0-9]+(?:\.[0-9]+){0,2}(?:-[0-9A-Za-z.\-]+)?(?:\+[0-9A-Za-z.\-]+)?(?![\w./])',
         'name': 'constant.numeric.version.' + sfx},
        {'match': r'\S+', 'name': 'constant.other.version.' + sfx}]}

def arg_rules(verb, sfx):
    """The argument shapes of one directive, for its line or its block."""
    mp = 'string.unquoted.module-path.' + sfx
    if verb == 'module':
        return [{'match': r'(' + TOK + r')', 'captures': {'1': C('entity.name.namespace.module.' + sfx)}}]
    if verb == 'vertex':
        return [{'match': r'(\S+)', 'captures': {'1': {'patterns': [{'include': '#version'}]}}}]
    if verb == 'platform':
        return [{'match': r'(\S+)(?:\s+(\S+))?', 'captures': {'1': C('support.constant.platform.' + sfx),
                                                          '2': {'patterns': [{'include': '#version'}]}}}]
    if verb in ('require', 'exclude'):
        return [{'match': r'(' + TOK + r')(?:\s+(\S+))?', 'captures': {'1': C(mp), '2': {'patterns': [{'include': '#version'}]}}}]
    if verb == 'use':
        return [{'match': r'(\S+)', 'captures': {'1': C('string.unquoted.path.' + sfx)}}]
    if verb == 'replace':
        return [
            {'match': r'(' + TOK + r')(?:\s+(?!=>)(\S+))?\s+(=>)\s+(' + LOCAL + r')(?=\s*(?://|$))',
             'captures': {'1': C(mp), '2': {'patterns': [{'include': '#version'}]},
                          '3': C('keyword.operator.arrow.' + sfx), '4': C('string.unquoted.path.' + sfx)}},
            {'match': r'(' + TOK + r')(?:\s+(?!=>)(\S+))?\s+(=>)\s+(' + TOK + r')(?:\s+(\S+))?',
             'captures': {'1': C(mp), '2': {'patterns': [{'include': '#version'}]},
                          '3': C('keyword.operator.arrow.' + sfx), '4': C(mp),
                          '5': {'patterns': [{'include': '#version'}]}}},
            {'match': r'=>', 'name': 'keyword.operator.arrow.' + sfx}]
    raise ValueError(verb)

def directive_grammar(name, scope, sfx, verbs):
    R = {'comment': comment(sfx), 'version': version(sfx)}
    pats = [{'include': '#comment'}]
    for v in verbs:
        args = arg_rules(v, sfx)
        R[v] = {'patterns': [
            # verb ( ... ) block
            {'begin': r'^\s*(' + v + r')\s*(\()\s*(?=$|//)', 'end': r'^\s*(\))',
             'beginCaptures': {'1': C('keyword.other.directive.' + sfx), '2': C('punctuation.section.block.begin.' + sfx)},
             'endCaptures': {'1': C('punctuation.section.block.end.' + sfx)},
             'name': 'meta.block.' + v + '.' + sfx,
             'patterns': [{'include': '#comment'}] + args},
            # verb args
            {'begin': r'^\s*(' + v + r')\b', 'end': r'(?=//)|$',
             'beginCaptures': {'1': C('keyword.other.directive.' + sfx)},
             'name': 'meta.directive.' + v + '.' + sfx,
             'patterns': args}]}
        pats.append({'include': '#' + v})
    # vsc refuses any other directive ("unknown directive").
    pats.append({'match': r'^\s*([^\s/]\S*)', 'captures': {'1': C('invalid.illegal.unknown-directive.' + sfx)}})
    return {'$schema': 'https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json',
            'name': name, 'scopeName': scope, 'patterns': pats, 'repository': R}

mod = directive_grammar('Vertex Module', 'source.vtx.mod', 'vertex-mod',
                        ['module', 'vertex', 'platform', 'require', 'exclude', 'replace'])
work = directive_grammar('Vertex Workspace', 'source.vtx.work', 'vertex-work',
                         ['vertex', 'use', 'replace'])

# vs.sum: `module version hash`, one per line; any other shape is an error.
sfx = 'vertex-sum'
summ = {'$schema': 'https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json',
        'name': 'Vertex Checksums', 'scopeName': 'source.vtx.sum',
        'patterns': [
            {'match': r'^\s*(\S+)\s+(\S+)\s+(?:([A-Za-z][A-Za-z0-9]*)(:))?([A-Za-z0-9+/=_\-]+)\s*$',
             'captures': {'1': C('string.unquoted.module-path.' + sfx),
                          '2': {'patterns': [{'include': '#version'}]},
                          '3': C('keyword.other.hash-algorithm.' + sfx),
                          '4': C('punctuation.separator.' + sfx),
                          '5': C('constant.other.hash.' + sfx)}},
            {'match': r'^\s*\S.*$', 'name': 'invalid.illegal.line.' + sfx}],
        'repository': {'version': version(sfx)}}

for fname, g in [('vertex-mod.tmLanguage.json', mod), ('vertex-work.tmLanguage.json', work),
                 ('vertex-sum.tmLanguage.json', summ)]:
    with open(os.path.join(out, fname), 'w') as f:
        json.dump(g, f, indent=2)
        f.write('\n')
