# 设置与运行

零第三方依赖，无需安装任何包。

## 环境要求

- Python 3.8+（标准库：json / os / sys / re）

## 快速验证

```bash
# 在项目根目录
python run_tests.py        # 24 项验收断言，期望 PASS 24 / FAIL 0
python demo.py             # 八类演示，期望退出码 0
```

## 在自己的代码中使用

```python
from knowledge_taxonomy import KnowledgeTaxonomyRegistry

reg = KnowledgeTaxonomyRegistry()          # 自动加载 taxonomy + schema

# taxonomy 检查
print(reg.categories())                    # 八类 id 列表
errs = reg.validate_taxonomy_consistency() # 自检（空=通过）

# 校验一条知识条目（schema + 八类归并 + 来源合规）
entry = {
    "entry_id": "kb-fq-new-09",
    "knowledge_type": "faq",
    "title": "新增 FAQ 样例",
    "status": "draft",
    "domain": "operations",
    "owner_role": "ops",
    "summary": "这是一个新的 FAQ 条目。",
    "tags": ["faq"],
    "created_at": "2026-10-30",
    "version": 1,
    "source_trace": {
        "origin": "internal_project",
        "provenance": [{
            "source_id": "s1", "reference": "内部团队实践",
            "accessed_at": "2026-10-30",
            "excerpt": "验证示例" }],
        "classification_reason": "内部沉淀"
    }
}
errs = reg.validate_entry(entry)
print(errs or "✅ 通过")

# 批量加载目录（跳过 invalid 反例）
ok, rejected = reg.load_dir("examples")    # (8, [])
```

## 来源追踪规则（合规红线）

- 每条知识必须带 `source_trace.origin`（来源类型）+ `provenance`（引用清单）
- `origin = customer_material`（客户材料）**必须**带 `classification_reason`
  授权理由，否则拒绝
- 推荐：`internal_project` / `public_reference` / `synthesized`

## 常见问题

- **新增一条知识要改 schema 吗？** 不需要——统一基座已含八类；
  类型专属字段放 `type_specific` 对象里。
- **样例必须八个类都有吗？** 验收要求"八类 taxonomy"，样例覆盖全部
  类别能证明分类法可落地（测试 7 断言全覆盖）。
- **Windows 中文乱码？** 脚本已内置 UTF-8 重配置。