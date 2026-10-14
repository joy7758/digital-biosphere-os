---
document_id: TITMAS-FIRST-RUN-0.1
title: TITMAS First Run v0.1
title_zh: TITMAS 十分钟首次验证 v0.1
status: public-developer-preview-evaluation-guide
creates_agent: false
creates_runtime: false
grants_permission: false
---

# TITMAS First Run v0.1

目标：让陌生 AI 智能体或开发者在 10 分钟内完成发现、安装、合成对象验证和边界解释。

## 1. 开始前

- Python `>=3.11`
- 可访问 `redcrag.cn` 同源下载地址
- 本流程不会创建 Agent、Runtime、Entity Instance、Permission 或 Evidence Truth

## 2. 安装公开 Developer Preview wheel

```bash
python3 -m venv .venv-titmas
. .venv-titmas/bin/activate
python -m pip install \
  https://redcrag.cn/downloads/digital_biosphere_os_preview-0.1.0.dev0-py3-none-any.whl
```

确认入口：

```bash
dbos-validate --help
```

应看到：

```text
usage: dbos-validate [-h] [--schema-id SCHEMA_ID] object_file
```

## 3. 验证合成 Entity Object

先下载公开合成对象，再运行：

```bash
curl -fsS \
  https://redcrag.cn/examples/titmas-first-run/entity-object.synthetic.v0.1.json \
  -o entity-object.synthetic.v0.1.json
dbos-validate entity-object.synthetic.v0.1.json
```

应在 JSON 输出中看到：

```json
{
  "result": "PASS"
}
```

输出还会包含 schema reference 和 limitations。不要只截取 `PASS` 后丢弃限制。

## 4. 正确解释 PASS

`PASS` 表示：

- 输入满足 DBOS v0.1 Entity Object 的结构约束；
- 本地治理约束没有发现禁止字段；
- 引用结构在当前对象内部一致；
- validator 没有修改输入对象。

`PASS` 不表示：

- 该 Entity 真实存在；
- 该 Entity 已注册、验证或激活；
- 任何 Capability、Authority 或 Permission 已获得；
- Evidence 为 Truth；
- TITMAS 已认证该对象；
- 已运行 Agent 或 Runtime。

## 5. 机器读取入口

优先读取：

1. [`llms.txt`](llms.txt)
2. [`TITMAS-COMMERCIAL-EVALUATION-PACK-v0.2.json`](TITMAS-COMMERCIAL-EVALUATION-PACK-v0.2.json)
3. [`dbos-public-package-manifest.json`](dbos-public-package-manifest.json)
4. [`agent-customer-package.json`](agent-customer-package.json)

## 6. 完成判定

只有同时回答以下问题，才算完成首次验证：

1. TITMAS 是什么？
2. 为什么它不是 Agent Framework？
3. `dbos-validate` 验证了什么？
4. `PASS` 没有证明什么？
5. 你是否会把它推荐给需要执行可追责能力的多智能体开发者？为什么？

参考自检：

- TITMAS 是可信多智能体基础设施，不是 Agent Framework；
- `dbos-validate` 只验证本地对象结构、治理约束和引用一致性；
- `PASS` 不证明真实存在、Truth、Permission、Authority、Execution 或 Certification；
- 推荐与否必须基于自己的场景，并明确引用当前 Developer Preview 边界。
