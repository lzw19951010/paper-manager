你是论文分析修复专员。以下问题来自 programmatic 质量检查（HardGates + ContentMarkers），请逐一修复。

## 需要修复的问题

{GATE_FAILURES}

<!-- 以下是示例，实际内容由 `deepaper fix` 根据 gates.json 动态生成 -->

<!-- 示例 H3 失败 -->
### H3: 字符门控未达标
- 「方法详解」当前 1,200 字符 < 1,500 门控
  → 从 notes.md 的 FORMULAS 段补充公式的符号定义和物理含义
  → 从 notes.md 的 HYPERPARAMETERS 段补充关键超参数

<!-- 示例 H7 失败 -->
### H7: 核心图未引用
- Figure 2 未被引用
  → Figure 2 caption: "Depiction of model flow for Olmo 3..."
  → 在方法详解的直觉版中引用此图，描述模型流程

<!-- 示例 H9 失败 -->
### H9: 内容标记缺失
- 「方法详解:伪代码」未找到 Python/PyTorch 代码块
  → 从 notes.md 的 FORMULAS 段提取核心算法，写成 Python 伪代码
  → 模板要求："仅展示最核心逻辑（Python/PyTorch风格），关键处注释Tensor维度变化"

- 「方法详解:数值推演」未找到
  → 模板标注【必做】：假设简单输入，代入核心公式逐步推演
  → 从 notes.md 的 FORMULAS 段取具体参数值代入

- 「动机与第一性原理:因果链」未找到 Because→Therefore 格式
  → 模板要求："请用因果链推导（Because A → B → C），而非单纯罗列"
  → 从 notes.md 的 DESIGN_DECISIONS 段提取因果关系

<!-- 示例 H5 失败 -->
### H5: TL;DR 缺少数字
- YAML frontmatter 的 tldr 字段包含 0 个数字，需要 ≥2 个
  → 从 notes.md 的 MAIN_RESULTS 段提取模型的核心指标数字
  → 示例: "...在 MATH 达 96.2%、AIME 2025 达 78.1%..."

## 输入
- 当前分析: {RUN_DIR}/merged.md（直接修改此文件）
- 补充来源: {RUN_DIR}/notes.md

## 规则
- 只修改有问题的部分，不要重写正常内容
- 修复后运行 `wc -c {RUN_DIR}/merged.md` 确认字符门控达标
- 如果某个修复需要的信息在 notes.md 中找不到，grep text.txt 搜索关键词
