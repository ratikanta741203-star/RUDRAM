"""Snapshot existing presentation/data into importable assets for server bundling.
Run after editing Django templates or the geographic reference data.
"""
import json
import runpy
from pathlib import Path
root = Path(__file__).resolve().parent.parent
(root / 'web/templates.json').write_text(json.dumps({str(p.relative_to(root / 'templates')): p.read_text() for p in (root / 'templates').rglob('*.html')}, ensure_ascii=False))
locations = runpy.run_path(str(root / 'apps/core/locations.py'))
(root / 'web/locations.json').write_text(json.dumps({k: v for k, v in locations.items() if k.isupper()}, ensure_ascii=False))
knowledge = runpy.run_path(str(root / 'apps/disasters/knowledge_data.py'))
(root / 'web/knowledge.json').write_text(json.dumps({k: v for k, v in knowledge.items() if k.isupper()}, ensure_ascii=False))
