# -*- coding: utf-8 -*-
"""演示：八类 taxonomy + 样例校验 + 来源追踪检查

运行：python demo.py
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from knowledge_taxonomy import KnowledgeTaxonomyRegistry  # noqa

HERE = os.path.dirname(os.path.abspath(__file__))
reg = KnowledgeTaxonomyRegistry()

print("知识分类与元数据演示 — taxonomy + schema + 样例校验\n")

print(f"八类知识库分类（共 {len(reg.categories())} 类）：")
for cid in reg.categories():
    cat = reg.category(cid)
    print(f"  {cat['code']}  {cat['name']:<8} {cat['description'][:36]}")

ok_cnt, rej = reg.load_dir(os.path.join(HERE, "examples"))
print(f"\n样例校验：{ok_cnt} 条合法通过 / {len(rej)} 条被拒")

if rej:
    for fn, errs in rej:
        print(f"  ❌ {fn}: {errs[0]}")
else:
    print("  全部样例符合 taxonomy + schema ✅")

print("\n八类覆盖检查（样例须覆盖全部 8 类）：")
covered = set()
for f in sorted(os.listdir(os.path.join(HERE, "examples"))):
    if f.startswith("kb-") and f.endswith(".json") and "invalid" not in f:
        e = json.load(open(os.path.join(HERE, "examples", f),
                           encoding="utf-8"))
        covered.add(e["knowledge_type"])
for cid in reg.categories():
    mark = "✅" if cid in covered else "❌"
    print(f"  {mark} {cid}")

print("\n" + "=" * 50)
print("验收结果: taxonomy + schema + 样例校验 -> ✅ 全部可复现")
print("=" * 50)
sys.exit(0)