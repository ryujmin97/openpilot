#!/usr/bin/env python3
"""dead_scan/scan.py <repo_dir> <out_dir>  (277cha)
first-party 범위(SCOPE)의 파이썬 정의(함수/메서드/클래스)마다 이름 기준 참조를 센다.
파일마다 ast를 한 번만 파싱한다(키마다 전체 재스캔하면 300초 제한에 걸린다, 273cha).
출력: <out_dir>/defs.json (정의별 참조 개수), <out_dir>/refs_low.json (참조 6개 이하 이름의 위치).
이름 기준이라 '참조 0건'은 확실하고 '참조 있음'은 상한이다(동명 메서드, getattr 동적 호출).
`__all__` 안의 문자열은 사용으로 세지 않는다. 저장소 밖 소비자는 보지 못한다."""
import ast, os, re, json, subprocess, sys, collections
R = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/repo'
OUT = sys.argv[2] if len(sys.argv) > 2 else '.'
os.makedirs(OUT, exist_ok=True)
files = subprocess.check_output(['git', '-C', R, 'ls-files'], text=True).splitlines()
def is_test(p):
    # `*_test.py` 접미사는 테스트로 보지 않는다: server/**/vision_test.py, youtube_test.py는 `carrot` 명령이 쓰는 운영 유틸이다(277cha 정정)
    b = os.path.basename(p)
    return '/tests/' in p or '/test/' in p or b.startswith('test_') or b == 'conftest.py'
SCOPE = ('openpilot/selfdrive/carrot/', 'carrot/', 'openpilot/selfdrive/controls/lib/')
def in_scope(p): return p.endswith('.py') and p.startswith(SCOPE) and not is_test(p)
SKIP = ('tinygrad_repo/', 'docs/')
TXT = ('.py', '.json', '.js', '.mjs', '.sh', '.yaml', '.yml', '.toml', '.cfg', '.scons', '.cc', '.h', '.pyx', '.pxd', '.html', '.css', '.ini', '.txt')
tok = re.compile(r'[A-Za-z_][A-Za-z0-9_]*')
refs = collections.defaultdict(lambda: collections.defaultdict(set))
defs = []
for p in files:
    if p.startswith(SKIP) or '/generated/' in p or '/third_party/' in p: continue
    if not (p.endswith(TXT) or os.path.basename(p) in ('SConscript', 'SConstruct')): continue
    fp = os.path.join(R, p)
    try:
        if os.path.getsize(fp) > 2_000_000: continue
        src = open(fp, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    if not p.endswith('.py'):
        for t in set(tok.findall(src)): refs[t]['other'].add((p, 0))
        continue
    grp = 'py_test' if is_test(p) else 'py_nontest'
    try:
        tree = ast.parse(src)
    except Exception:
        for t in set(tok.findall(src)): refs[t]['other'].add((p, 0))
        continue
    skip_ids = set()
    for n in ast.walk(tree):  # __all__ 항목 문자열은 제외
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '__all__' for t in n.targets):
            for c in ast.walk(n.value): skip_ids.add(id(c))
    for n in ast.walk(tree):
        if isinstance(n, ast.Name): refs[n.id][grp].add((p, n.lineno))
        elif isinstance(n, ast.Attribute): refs[n.attr][grp].add((p, n.lineno))
        elif isinstance(n, ast.keyword) and n.arg: refs[n.arg][grp].add((p, n.value.lineno))
        elif isinstance(n, ast.ImportFrom):
            for a in n.names: refs[a.name][grp].add((p, n.lineno))
        elif isinstance(n, ast.Import):
            for a in n.names: refs[a.name.split('.')[-1]][grp].add((p, n.lineno))
        elif isinstance(n, ast.Constant) and isinstance(n.value, str) and len(n.value) < 400 and id(n) not in skip_ids:
            for t in tok.findall(n.value): refs[t]['str_' + grp].add((p, n.lineno))
    if in_scope(p):
        def visit(body, cls):
            for n in body:
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    defs.append((n.name, 'method' if cls else 'func', p, n.lineno, n.end_lineno, cls, bool(n.decorator_list)))
                elif isinstance(n, ast.ClassDef):
                    defs.append((n.name, 'class', p, n.lineno, n.end_lineno, cls, bool(n.decorator_list)))
                    visit(n.body, n.name)
        visit(tree.body, None)
out = []; low = {}
for (name, kind, p, l, e, cls, dec) in defs:
    if name.startswith('__') and name.endswith('__'): continue
    r = refs.get(name, {})
    nt = r.get('py_nontest', set())
    nt_out = {x for x in nt if not (x[0] == p and l <= x[1] <= e)}
    out.append(dict(name=name, kind=kind, file=p, line=l, end=e, cls=cls, dec=dec,
                    nt_out=len(nt_out), nt_in=len(nt) - len(nt_out), test=len(r.get('py_test', ())),
                    other=len(r.get('other', ())), str_nt=len(r.get('str_py_nontest', ())), str_test=len(r.get('str_py_test', ()))))
    if len(nt_out) <= 6: low[name] = sorted(nt)
json.dump(out, open(os.path.join(OUT, 'defs.json'), 'w'), ensure_ascii=False)
json.dump(low, open(os.path.join(OUT, 'refs_low.json'), 'w'))
print(len(defs), 'defs;', len(out), 'scored ->', OUT)
