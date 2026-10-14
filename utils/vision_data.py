"""Validated static display data. Never imports Torch or the original solvers."""
import hashlib
import json
from pathlib import Path
from functools import lru_cache

ROOT=Path(__file__).resolve().parents[1]/'data_public/vision'

@lru_cache(maxsize=1)
def load():
    manifest=json.loads((ROOT/'VISION_MANIFEST.json').read_text(encoding='utf-8'))
    if len(manifest['files'])!=5 or len({e['file'] for e in manifest['files']})!=5:
        raise ValueError('视觉数据清单不完整')
    data={}
    for entry in manifest['files']:
        path=(ROOT/entry['file']).resolve()
        if not path.is_relative_to(ROOT.resolve()): raise ValueError('视觉数据路径异常')
        raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest().upper()!=entry['sha256']:
            raise ValueError('视觉展示数据完整性检查未通过')
        data[path.stem]=json.loads(raw)
    if data['result']['status']!='PASS': raise ValueError('视觉计算侧结果未通过验证')
    return data
