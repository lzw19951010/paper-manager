# deepaper

> 一个 arxiv 链接 &rarr; 一份专家级深度分析笔记，由多智能体流水线驱动

[![PyPI](https://img.shields.io/pypi/v/deepaper)](https://pypi.org/project/deepaper/)
[![Python](https://img.shields.io/pypi/pyversions/deepaper)](https://pypi.org/project/deepaper/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)

**[English](README.md)** | **中文**

![deepaper demo](demo.gif)

deepaper 通过 Claude Code 编排的 **5-Agent 流水线**，将 arxiv 论文链接转换为结构化深度分析笔记。不是摘要，而是**可执行的研究笔记**：7 层深度分析 + 15 项自动质量门控、基于证据的机制家族图谱、跨领域迁移处方、完整超参数表和伪代码，以及针对复现者的工程陷阱预警。

笔记存储为 Obsidian 兼容的 Markdown + YAML，支持 Git 同步、自动分类（12 个子类别），由 Claude Code CLI 驱动（Max 订阅，无 API 费用）。

## 工作原理

deepaper 作为 `/deepaper` 斜杠命令在 Claude Code 中运行。输入 `/deepaper <arxiv-url>` 即可触发 5-Agent 流水线：

```
指挥者 (Claude Code)
  ├→ [1] Extractor  — 阅读全部页面，输出结构化笔记（表格、公式、相关工作）
  ├→ [2] Writer-A   — 撰写 frontmatter + 核心速览 + 动机 + 方法详解              ┐
  ├→ [3] Writer-B   — 撰写 实验与归因 + 专家批判                                 ├ 并行
  ├→ [4] Writer-C   — 撰写 机制迁移分析 + 背景知识补充                            ┘
  ├→ [5] Critic     — 15 项质量门控审计（含 API 不可用时的内联降级）
  └→ [6] Fixer      — 修复未通过的门控（如有）
```

每个 Agent 具有专用提示词、字符数门控和自动自检。最终输出通过 15 项质量门控，涵盖事实准确性、数据密度和结构完整性。

## deepaper vs 其他方案

| 功能 | Zotero | Semantic Scholar | 手动笔记 | **deepaper** |
|------|--------|------------------|---------|------------|
| **深度分析** | 书签 + 标记 | 摘要 | 手写总结 | 7 层多智能体分析 |
| **质量控制** | 无 | 无 | 自我审查 | 15 项自动质量门控 |
| **机制可视化** | 无 | 无 | 有（费时） | 自动机制家族图谱（前身/兄弟/后代） |
| **引用追踪** | 计数统计 | 引用列表 | 手工搜索 | 基于证据的后代论文（OpenAlex，无需 API key） |
| **Obsidian 原生** | 无 | 无 | 原生 | 原生（YAML + Markdown + Dataview） |
| **多设备同步** | 云同步（付费） | 无 | Git 同步（DIY） | Git 同步（内置） |
| **API 成本** | 无 | 无 | 无 | 无（Max 订阅，无按量计费） |

## 快速开始

```bash
# 安装
pip install deepaper

# 初始化项目
cd my-papers && deepaper init

# 在 Claude Code 中分析论文
/deepaper https://arxiv.org/abs/2512.13961
```

完成后在 `papers/` 目录中看到 markdown 笔记，可直接在 Obsidian 中打开。

## 安装

```bash
# 推荐：隔离安装
pipx install deepaper

# 或直接安装
pip install deepaper

# 全局安装 /deepaper 斜杠命令
deepaper install
```

> **前提：** 需要安装 [Claude Code CLI](https://claude.ai/code) 并已登录（Max 订阅）。还需要 PyMuPDF 用于 PDF 文本提取：`pip install PyMuPDF`。

## 使用方法

### 分析论文（多智能体流水线）

在 deepaper 项目内的任何 Claude Code 会话中：

```
/deepaper https://arxiv.org/abs/2512.13961
```

这将触发完整的 5-Agent 流水线。指挥者会：
1. 下载 PDF 并提取全文
2. 启动 Extractor 阅读全部页面，生成结构化笔记
3. 并行启动 3 个 Writer 生成分析
4. 运行 Critic 验证 15 项质量门控
5. 修复未通过的门控
6. 保存到 `papers/{类别}/{标题}.md`

### CLI 命令

```bash
# 下载论文 PDF + 元数据
deepaper download https://arxiv.org/abs/2512.13961

# 保存分析到知识库
deepaper save 2512.13961 --category llm/pretraining --input /tmp/analysis.md

# 查找引用论文
deepaper cite 2512.13961

# 更新已有笔记的引用数据
deepaper cite --update 2512.13961

# 同步笔记到 git
deepaper sync
```

### 引用查询

```bash
deepaper cite 1706.03762
```

从 OpenAlex 获取真实引用论文（免费，无需 API key），按引用量排序。使用 `--update` 将后代注入已有笔记的机制家族图谱。

### Git 同步

```bash
deepaper sync
deepaper sync --message "添加 OLMo 3 分析"
```

自动执行 `git pull --rebase`，然后提交并推送。

## 分析输出格式

每篇笔记包含 YAML 元数据 + 7 层深度分析，由 15 项质量门控验证：

| 部分 | 内容 | 质量门控 |
|------|------|---------|
| **Frontmatter** | Baselines（每行一个）、数据集（含 token 数）、指标（含评测配置） | Baselines 格式、指标配置、数据集计数 |
| **核心速览** | 含具体数字的 TL;DR + 新旧方法对比 + 核心机制一句话 | TL;DR 含 ≥2 个 benchmark 数字 |
| **动机与第一性原理** | Baseline 痛点（含数字）+ 3 步因果链 + 直觉类比 | 痛点引用 ≥2 个 baseline，因果链 ≥3 步 |
| **方法详解** | 数据流图 + 公式 + 数值推演 + 伪代码 + 超参数表 + 设计决策 | ≥12K 字符，设计决策 ≥3K 字符 |
| **实验与归因** | 完整对比表格（含所有 baselines）+ 消融排序 + 可信度检查 | ≥2 张完整表格，归因含 delta 数字 |
| **专家批判** | 隐性成本（含数字）+ 可复用技术 + 陷阱 + 关联技术对比 | ≥3 个隐性成本含数字 |
| **机制迁移分析** | 3-5 个计算原语 + 跨领域迁移处方 + 家族图谱（≥4 前身，≥3 兄弟） | ≥5K 字符，处方完整，家族计数 |
| **背景知识补充** | 外部技术表格（≥8 项） | -- |

### 分类体系

论文自动归入 12 个子类别：
- **LLM**：pretraining、alignment、reasoning、efficiency、agent
- **推荐系统**：matching、ranking、llm-as-rec、generative-rec、system
- **多模态**：vlm、generation、understanding
- **其他**：misc

## Obsidian 集成

将项目根目录作为 Obsidian vault 打开。使用 [Dataview](https://github.com/blacksmithgu/obsidian-dataview) 查询笔记：

```dataview
TABLE date, venue, keywords
FROM "papers"
SORT date DESC
LIMIT 20
```

## 配置参考

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `git_remote` | — | GitHub/GitLab 远端 URL（用于 `deepaper sync`） |
| `papers_dir` | `papers` | 笔记存储目录 |

引用分析使用 [OpenAlex](https://openalex.org/) 开放 API，**无需 API key**。

如需更丰富的引用影响力分析，可选配置 [Semantic Scholar API key](https://www.semanticscholar.org/product/api#api-key-form)（免费），在 `config.yaml` 或环境变量 `SEMANTIC_SCHOLAR_API_KEY` 中设置。

## 依赖项

- Python 3.10+
- [Claude Code](https://claude.ai/code) CLI（已安装并登录）
- Max 订阅（无 API 计费）
- PyMuPDF（`pip install PyMuPDF`）用于 PDF 文本提取
- Git（可选，用于 `deepaper sync`）
- Obsidian（可选，用于查看 vault）

## License

AGPL-3.0-or-later。详见 [LICENSE](LICENSE)。
