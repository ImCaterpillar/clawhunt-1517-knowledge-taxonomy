# -*- coding: utf-8 -*-
"""知识分类与元数据校验器（taxonomy + schema + 样例校验）

对应 ClawHunt 任务 #1517（企业 Agent 系统 30/50｜知识分类与元数据），
验收标准：**提交 taxonomy、schema 与样例校验**。

设计：
  - `taxonomy/enterprise_taxonomy.json`：八类知识分类法（类别/编码/说明/关联交付物）
  - `schema/knowledge_entry.schema.json`：条目元数据 schema（统一基座 + 来源追踪）
  - `KnowledgeTaxonomyRegistry`：
      · 加载 taxonomy 八类
      · 校验知识条目是否「合法归入某类」且元数据完整
      · 来源追踪检查（source_trace.origin / provenance 必填，
        customer_material 必须带分类理由，防未授权材料）
  - 一次命令跑验收 = 结构模板/taxonomy + schema + 样例校验全验证
"""
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


class TaxonomyError(Exception):
    pass


def _type_ok(value, t):
    if t == "object":
        return isinstance(value, dict)
    if t == "array":
        return isinstance(value, list)
    if t == "string":
        return isinstance(value, str)
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if t == "boolean":
        return isinstance(value, bool)
    if t == "null":
        return value is None
    return True


def validate(instance, schema, path="$"):
    errors = []
    if "type" in schema and not _type_ok(instance, schema["type"]):
        return [f"{path}: 期望 {schema['type']} 实为 {type(instance).__name__}"]
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: 值 {instance!r} 不在允许集合 {schema['enum']}")
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: 值 {instance!r} != 常量 {schema['const']}")
    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: 长度 {len(instance)} < {schema['minLength']}")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{path}: 长度 {len(instance)} > {schema['maxLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"{path}: 值 {instance!r} 不匹配模式 {schema['pattern']}")
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: {instance} < {schema['minimum']}")
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: 元素数 {len(instance)} < {schema['minItems']}")
        if "items" in schema:
            for i, item in enumerate(instance):
                errors += validate(item, schema["items"], f"{path}[{i}]")
    if isinstance(instance, dict):
        if "required" in schema:
            for k in schema["required"]:
                if k not in instance:
                    errors.append(f"{path}: 缺少必填字段 {k!r}")
        if schema.get("additionalProperties") is False \
                and "properties" in schema:
            for k in instance:
                if k not in schema["properties"]:
                    errors.append(f"{path}: 不允许的额外字段 {k!r}")
        if "properties" in schema:
            for k, sub in schema["properties"].items():
                if k in instance:
                    errors += validate(instance[k], sub, f"{path}.{k}")
    return errors


class KnowledgeTaxonomyRegistry:
    """八类知识分类法 + 条目元数据校验 + 来源追踪检查"""

    def __init__(self, taxonomy_path=None, schema_path=None):
        here = os.path.dirname(os.path.abspath(__file__))
        self.taxonomy_path = taxonomy_path or os.path.join(
            here, "taxonomy", "enterprise_taxonomy.json")
        self.schema_path = schema_path or os.path.join(
            here, "schema", "knowledge_entry.schema.json")
        self.taxonomy = json.load(open(self.taxonomy_path, encoding="utf-8"))
        self.schema = json.load(open(self.schema_path, encoding="utf-8"))
        self._categories = {}
        for cat in self.taxonomy.get("categories", []):
            self._categories[cat["id"]] = cat

    def categories(self):
        return list(self._categories)

    def category(self, cid):
        return self._categories.get(cid)

    def validate_taxonomy_consistency(self):
        """taxonomy 自检：八类齐全、id 唯一、编码唯一、必填元数据非空"""
        errors = []
        cats = self.taxonomy.get("categories", [])
        ids = [c.get("id") for c in cats]
        codes = [c.get("code") for c in cats]
        if len(ids) != 8:
            errors.append(f"taxonomy 类别数 != 8（{len(ids)}）")
        if len(set(ids)) != len(ids):
            errors.append("taxonomy id 重复")
        if len(set(codes)) != len(codes):
            errors.append("taxonomy code 重复")
        for c in cats:
            if not c.get("required_metadata"):
                errors.append(f"类别 {c.get('id')} 缺 required_metadata")
        return errors

    def validate_entry(self, entry):
        """校验一条知识条目：schema + 八类归并 + 来源合规"""
        errs = validate(entry, self.schema)
        if errs:
            return errs
        kt = entry.get("knowledge_type")
        if kt not in self._categories:
            return [f"knowledge_type {kt!r} 不在 taxonomy 八类中"]
        # 来源追踪合规：customer_material 必须带授权/分类理由
        st = entry.get("source_trace", {})
        if st.get("origin") == "customer_material":
            if not st.get("classification_reason"):
                return ["customer_material 必须带 classification_reason（授权理由）"]
        return []

    def load_dir(self, d):
        """加载目录下所有 kb-*.json 条目（跳过 invalid），返回 (合法数, 拒绝列表)"""
        if not os.path.isdir(d):
            return 0, []
        files = sorted(f for f in os.listdir(d)
                       if f.startswith("kb-") and f.endswith(".json")
                       and "invalid" not in f)
        ok = 0
        rejected = []
        for fn in files:
            entry = json.load(open(os.path.join(d, fn), encoding="utf-8"))
            errs = self.validate_entry(entry)
            if errs:
                rejected.append((fn, errs))
            else:
                ok += 1
        return ok, rejected


def load_taxonomy(path=None):
    """便捷入口：加载 taxonomy 及其类目"""
    r = KnowledgeTaxonomyRegistry(path)
    return r.taxonomy