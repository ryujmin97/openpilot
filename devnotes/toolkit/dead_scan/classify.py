#!/usr/bin/env python3
"""dead_scan/classify.py <out_dir>  (277cha) scan.py 결과를 분류한다.
live / zero(참조 0건) / zero_dec(데코레이터 있음) / self_only(자기 본문에서만) /
test_only(테스트에서만) / dyn_only(비파이썬 파일이나 비테스트 문자열에서만). 직접 후보에서 프레임워크
오버라이드, 벤더, `_ingest_*`(getattr 디스패치)를 빼고, 후보 본문 안에서만 호출되는 정의를 고정점까지 연쇄 추가한다."""
import json, sys, os
D = sys.argv[1] if len(sys.argv) > 1 else '.'
d = json.load(open(os.path.join(D, 'defs.json'))); low = json.load(open(os.path.join(D, 'refs_low.json')))
FW = {'log_message', 'do_HEAD', 'do_POST', 'do_DELETE', 'do_GET', 'seekable', 'writable', 'handle_starttag', 'handle_startendtag', 'handle_one_request'}
def cat(x):
    if x['nt_out'] > 0: return 'live'
    if x['other'] > 0 or x['str_nt'] > 0: return 'dyn_only'
    if x['test'] > 0 or x['str_test'] > 0: return 'test_only'
    if x['nt_in'] > 0: return 'self_only'
    return 'zero_dec' if x['dec'] else 'zero'
for x in d: x['cat'] = cat(x)
import collections
print(collections.Counter(x['cat'] for x in d))
S = [x for x in d if x['cat'] in ('zero', 'zero_dec', 'test_only', 'self_only') and '.vendor/' not in x['file']
     and x['name'] not in FW and not x['name'].startswith('_ingest_')
     and not (x['cat'] == 'zero_dec' and x['kind'] != 'class')]  # 데코레이터 등록 함수(명령 핸들러 등)는 제외, 클래스만 남긴다
key = lambda x: (x['name'], x['file'], x['line'])
chosen = {key(x) for x in S}; chain = []
while True:
    spans = {}
    for x in d:
        if key(x) in chosen: spans.setdefault(x['file'], []).append((x['line'], x['end']))
    cov = lambda f, l: any(a <= l <= b for a, b in spans.get(f, []))
    new = [x for x in d if key(x) not in chosen and 0 < x['nt_out'] <= 6 and '.vendor/' not in x['file']
           and low.get(x['name']) and all(cov(f, l) for f, l in low[x['name']])]
    if not new: break
    for x in new: chosen.add(key(x)); chain.append(x)
fmt = lambda x: f"{x['file']}:{x['line']} {x['kind']} {(x['cls'] + '.') if x['cls'] else ''}{x['name']} cat={x['cat']} test={x['test']}"
print('\n== direct candidates', len(S))
for x in sorted(S, key=lambda x: (x['file'], x['line'])): print(' ', fmt(x))
print('\n== chained (고정점)', len(chain))
for x in chain: print(' ', fmt(x))
json.dump({'direct': [key(x) for x in S], 'chain': [key(x) for x in chain]}, open(os.path.join(D, 'candidates.json'), 'w'))
