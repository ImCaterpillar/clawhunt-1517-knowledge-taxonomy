# 知识分类与元数据 — 八类 taxonomy + schema + 样例校验

对应 ClawHunt 任务 **#1517**（企业 Agent 系统 30/50｜知识分类与元数据）。

**验收标准**：提交 **taxonomy、schema 与样例校验**。

## 一条命令验证全部

```bash
python run_tests.py      # -> PASS 24 / FAIL 0
python demo.py           # -> 八类 taxonomy 演示
```

## 验收三要素（与验收标准逐条对应）

**① taxonomy（八类知识分类法）路径**
`taxonomy/enterprise_taxonomy.json` —— 企业知识库八类分类法
（agent_role / methodology / case_study / template / standard /
reference_data / evidence / faq），每类含编码、说明、必填元数据，
并与系列既有拆分单关联。

**② schema（元数据规范）路径**
`schema/knowledge_entry.schema.json` —— 知识条目元数据 schema
（draft-07）：统一基座（entry_id / knowledge_type / title / status /
owner_role / created_at / source_trace）**+ 来源追踪字段**（origin /
provenance / classification_reason），类型专属扩展字段。

**③ 样例校验：运行命令 + 正/反例预期输出**

```bash
python run_tests.py
# ✅ 2. exactly eight categories -- count=8
# ✅ 7. samples cover all eight types -- covered=8/8
# ✅ 9. all 8 samples pass validation -- ok=8 rejected=0
# ✅ 10. invalid entry rejected -- 4 errors
# ✅ 11. customer_material without reason rejected
# Result: PASS 24   FAIL 0
```

## 快速开始

```bash
# 零第三方依赖（纯 Python 标准库）
python run_tests.py          # 全部验收验证
python demo.py               # 八类 taxonomy 演示
```

## 目录

```
.
├── knowledge_taxonomy.py    # taxonomy 加载 + 条目校验 + 来源追踪（核心）
├── run_tests.py             # 验收验证
├── demo.py                  # 八类演示
├── taxonomy/
│   └── enterprise_taxonomy.json  # 八类知识分类法
├── schema/
│   └── knowledge_entry.schema.json  # 条目元数据 schema
├── examples/
│   ├── kb-ar-onboard-01.json   # agent_role
│   ├── kb-me-scrum-02.json     # methodology
│   ├── kb-cs-rework-03.json    # case_study
│   ├── kb-tp-checklist-04.json # template
│   ├── kb-st-desensitization-05.json # standard
│   ├── kb-rd-industry-enum-06.json   # reference_data
│   ├── kb-ev-fingerprint-07.json     # evidence
│   ├── kb-fq-codeload-08.json        # faq
│   └── kb-invalid-99.json     # 反例（校验拒绝路径）
├── docs/（验收对照 / 实现说明 / 验证记录）
├── SETUP.md
└── README.md
```

## 设计要点

1. **八类覆盖企业知识形态**：角色、流程、案例、模板、标准、数据、
   证据、问答——与系列 50 拆分单的沉淀一一对应。
2. **统一元数据基座 + 来源追踪**：每条知识必须声明来源类型
   （internal_project / public_reference / customer_material /
   synthesized）与可追溯的 provenance 引用——这是"来源追踪规范"的落点。
3. **合规红线**：`customer_material` 必须携带 classification_reason
   （授权理由），否则校验拒绝（测试 11）——对齐"只能使用获授权或脱敏资料"。
4. **八类全覆盖样例**：8 个合法样例各归一类，证明分类法可落地。
5. **反例覆盖**：未知类型/缺字段/额外字段/空来源 → 全部被拒。
6. **零第三方依赖**：纯标准库，买家一键可复现。

## 环境

- Python 3.8+
- **零第三方依赖**（纯标准库）

## 边界说明

本单范围 = 知识库**分类法 + 元数据规范 + 来源追踪**；以下不在本单范围：
- 具体知识内容的检索/引用实现 —— 属「知识接线」类拆分单（#1508 等）
- 知识库运行时/多 Agent 检索 —— 属「知识库」类拆分单
- 真实客户内部资料 —— 按原文要求仅用脱敏/授权材料