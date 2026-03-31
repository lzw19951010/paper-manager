# deepaper

> 一个 arxiv 链接 → 一份专家级深度分析笔记

[![PyPI](https://img.shields.io/pypi/v/deepaper)](https://pypi.org/project/deepaper/)
[![Python](https://img.shields.io/pypi/pyversions/deepaper)](https://pypi.org/project/deepaper/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)

**[English](README.md)** | **中文**

![deepaper demo](demo.gif)

deepaper 将 arxiv 论文链接转换为结构化的深度分析笔记。不是摘要，而是**可执行的研究笔记**：包含 7 层深度分析、证实的机制家族图谱、基于真实引用的后代论文追踪（零配置，无需 API key）、完整的伪代码走查，以及针对复现者的工程陷阱预警。

笔记存储为 Obsidian 兼容的 Markdown + YAML，支持语义搜索、多设备 Git 同步、自动分类（12 个子类别），并利用 Claude Code CLI（Max 订阅，无 API 费用）完成 AI 分析。

## deepaper vs 其他方案

| 功能 | Zotero | Semantic Scholar | 手动笔记 | **deepaper** |
|------|--------|------------------|---------|------------|
| **深度分析** | 书签 + 标记 | 摘要 | 手写总结 | 7 层专家级剖析 |
| **机制可视化** | 无 | 无 | 有（费时） | 自动机制家族图谱 + 前身/兄弟/后代 |
| **引用分析** | 计数统计 | 引用列表 | 手工搜索 | 证实的后代论文（OpenAlex，无需 API key） |
| **Obsidian 原生** | 无 | 无 | 原生 | 原生（YAML + Markdown + Dataview 兼容） |
| **语义搜索** | 无 | 有（但闭源） | 无 | 本地 RAG（ChromaDB） |
| **多设备同步** | 云同步（付费） | 无 | Git 同步（DIY） | Git 同步（内置） |
| **API 成本** | 无 | 无 | 无 | 无（Max 订阅，无按量计费） |

## 快速开始

```bash
# 安装
pip install deepaper

# 初始化本地库
deepaper init

# 添加一篇论文
deepaper add https://arxiv.org/abs/1706.03762
```

完成后在 `papers/` 目录中看到 markdown 笔记，可直接在 Obsidian 中打开。

## 与 Claude Code 集成

deepaper 设计为与 [Claude Code](https://claude.ai/code) 协同使用。Claude Code CLI 负责 AI 分析，deepaper 负责论文管理。

### 安装方式

在 Claude Code 会话中直接安装：

```bash
# 推荐：隔离安装（不影响系统 Python）
pipx install deepaper

# 或直接安装
pip install deepaper

# 零安装运行（需要 uv）
uvx deepaper add https://arxiv.org/abs/1706.03762
```

### 在 Claude Code 中使用

安装后，在 Claude Code 中可以直接调用：

```bash
# 添加论文并获得深度分析
! deepaper add https://arxiv.org/abs/2301.00001

# 搜索已有笔记
! deepaper search "attention mechanism"

# 查看论文引用图谱
! deepaper cite 1706.03762
```

> **前提：** 需要安装 [Claude Code CLI](https://claude.ai/code) 并已登录（Max 订阅）。

## 核心功能

### 添加论文

```bash
# 单篇论文
deepaper add https://arxiv.org/abs/2301.00001

# 多篇论文（ID 或 URL）
deepaper add 2301.00001 2301.00002 2301.00003

# HuggingFace 论文页面也支持
deepaper add https://huggingface.co/papers/2301.00001

# 重新分析已有论文
deepaper add --force https://arxiv.org/abs/2301.00001
```

处理流程：获取元数据 → 下载 PDF → 提取关键图表 → Claude Code 深度分析 → 自动分类标签 → 生成 Markdown 笔记 → ChromaDB 索引 → 清理临时文件。

### 语义搜索

在 16 个月前的 50 篇笔记中找不到论文名字，但还记得"长序列的注意力机制"？

```bash
deepaper search "attention mechanism for long sequences"
deepaper search "contrastive learning vision" --n 10
```

返回相似度分数、论文标题、匹配的笔记片段和 arxiv ID。

### Git 同步

在多台机器间同步笔记：

```bash
# 推送更新
deepaper sync

# 自定义提交信息
deepaper sync --message "Add three NLP papers"
```

自动执行 `git pull --rebase`，然后提交并推送。从远端拉取的新文件自动建立索引。

### 标签和分类

```bash
# 重新分类所有论文
deepaper tag

# 仅最近添加的论文
deepaper tag --since 2024-01-01

# 限制数量
deepaper tag --limit 10
```

自动识别 12 个子类别：
- **LLM**：pretraining、alignment、reasoning、efficiency、agent
- **推荐系统**：matching、ranking、llm-as-rec、generative-rec、system
- **多模态 & CV**：vlm、generation、understanding
- **其他**：misc

### 重建搜索索引

```bash
deepaper reindex
```

重新扫描 `papers/` 目录，更新 ChromaDB 索引。在批量导入或修改笔记后运行。

### 查看配置

```bash
deepaper config
```

显示所有设置，验证 Claude Code CLI 可用性。

## 分析输出格式

每篇笔记包含 Zotero 兼容的 YAML 元数据 + 7 层深度分析：

| 部分 | 内容 |
|------|------|
| **Executive Summary** | TL;DR（≤100字）+ 心智模型类比 + 核心机制一句话 |
| **动机与第一性原理** | 之前方案的痛点 + 核心洞察（因果链） + 物理直觉 |
| **方法详解** | 直觉版（含图解） + 形式化规范（流程图/公式/数值推演/伪代码） + 设计决策 + 易混淆点 |
| **实验与归因** | 定量收益 + 消融分析（按贡献排序） + 可信度检查 |
| **批判性评审** | 隐性成本 + 工程落地陷阱 + 与现有技术的关联 |
| **机制迁移分析** | 机制解耦 + 跨域迁移处方 + **机制家族图谱**（前身/兄弟/后代） |
| **背景知识** | 论文依赖的技术和常见实践（可选） |

### 机制家族图谱示例

以《Scaling Laws for Neural Language Models》为例，机制家族图谱展示如下：

```
Ancestors (前身):
  - Grangier & Auli (2018): 早期对 Transformer 尺度的探索
  - Baevski & Auli (2019): 预训练模型的幂律行为初步观察

Siblings (兄弟):
  - Kaplan et al. (2020, 本文): 语言模型的幂律（同步独立发现）
  - Hoffmann et al. (2022): Chinchilla 最优计算分配方案

Descendants (后代，基于 Semantic Scholar 引用数据):
  - Hoffmann et al. (2022): Chinchilla — 重新优化计算分配比例
  - Wei et al. (2022): Emergent Abilities of Large Language Models — 幂律应用
  - Frye et al. (2023): Scaling Laws for Transfer — 迁移学习中的幂律扩展
```

## 图表提取

分析器自动：

1. 扫描 PDF，识别包含图表/表格的页面（位图、矢量图、标题）
2. 优先提取正文页面，跳过附录
3. 渲染最多 20 页为 JPEG 图像
4. 传递给 Claude Code 进行视觉分析
5. 分析完成后清理临时文件

## 笔记存储格式

笔记存储为 `papers/{分类}/{年份}/{论文标题}.md`，包含 YAML 元数据：

```yaml
---
title: "Attention Is All You Need"
authors: [Ashish Vaswani, ...]
date: "2017-06-12"
arxiv_id: "1706.03762"
url: "https://arxiv.org/abs/1706.03762"
venue: "NeurIPS 2017"
keywords: [transformer, attention, NLP, sequence-to-sequence]
tags: [NLP, deep-learning, transformer]
status: complete
---
```

## Obsidian 集成

将项目根目录作为 Obsidian vault 打开。使用 [Dataview](https://github.com/blacksmithgu/obsidian-dataview) 插件查询笔记：

```dataview
TABLE date, venue, tags
FROM "papers"
WHERE contains(tags, "NLP")
SORT date DESC
```

其他常见查询：

```dataview
# 最近添加的前沿论文
TABLE date, venue, arxiv_id
FROM "papers"
WHERE status = "complete"
SORT date DESC
LIMIT 20

# 特定领域的所有论文
TABLE authors, venue
FROM "papers/llm/pretraining"
SORT date DESC
```

## 多设备同步

在不同机器间无缝同步笔记：

```bash
# 机器 A：添加论文并推送
deepaper add 2301.00001
deepaper sync

# 机器 B：拉取并自动索引
deepaper sync
```

`deepaper sync` 自动：
1. 拉取远端最新更改
2. 提交本地新笔记
3. 推送到远端
4. 对新文件建立 ChromaDB 索引

## 配置参考

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `git_remote` | — | GitHub/GitLab 远端 URL（用于 `deepaper sync`） |
| `model` | `claude-opus-4-6` | 用于分析的模型名称（仅用于日志显示） |
| `tag_model` | `claude-opus-4-6` | 用于标签生成的模型（仅用于日志显示） |
| `papers_dir` | `papers` | 笔记存储目录 |
| `template` | `default` | 分析提示模板（`templates/` 目录中无扩展名） |
| `chromadb_dir` | `.chromadb` | 向量数据库目录 |

引用分析（`deepaper cite` 和 `deepaper add` 中的后代论文追踪）使用 [OpenAlex](https://openalex.org/) 开放 API，**无需任何 API key**，开箱即用。

如需更丰富的引用影响力标记，可选配置 [Semantic Scholar API key](https://www.semanticscholar.org/product/api#api-key-form)（免费）：

```yaml
# config.yaml
semantic_scholar_api_key: "your_key_here"
```

也可通过环境变量设置：`export SEMANTIC_SCHOLAR_API_KEY=your_key`

配置文件 `config.yaml` 被 gitignore——你的设置不会被提交。

## 自定义分析提示

编辑 `templates/default.md` 自定义分析结构。也可创建新模板（如 `templates/my-style.md`），然后在 `config.yaml` 中设置 `template: "my-style"`。

模板是 Markdown 文件，包含详细的分析指导。例如：

```markdown
# 论文深度剖析

Role: 你是一位拥有深厚数学功底的 LLM 领域资深算法专家...

## 输出要求

请输出一个 JSON 对象，包含以下字段...
```

## 依赖项

- Python 3.10+
- [Claude Code](https://claude.ai/code) CLI（已安装并登录）
- Max 订阅（无 API 计费）
- Git（可选，用于 `deepaper sync`）
- Obsidian（可选，用于查看 vault）

## 安装

```bash
pip install deepaper
```

## 初始化

1. 创建配置和目录：

```bash
deepaper init --git-remote https://github.com/you/my-papers.git
```

创建 `config.yaml`、`papers/` 和 `.obsidian/app.json`。

2. 编辑 `config.yaml`（可选，大多数默认值即可生效）：

```yaml
git_remote: "https://github.com/you/my-papers.git"
```

## License

AGPL-3.0-or-later。详见 [LICENSE](LICENSE) 文件。
