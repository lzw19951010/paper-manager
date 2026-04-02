---
abstract: We introduce Olmo 3, a family of state-of-the-art, fully-open language models
  at the 7B and 32B parameter scales. Olmo 3 model construction targets long-context
  reasoning, function calling, coding, instruction following, general chat, and knowledge
  recall. This release includes the entire model flow, i.e., the full lifecycle of
  the family of models, including every stage, checkpoint, data point, and dependency
  used to build it. Our flagship model, Olmo 3 Think 32B, is the strongest fully-open
  thinking model released to-date.
arxiv_categories:
- cs.CL
arxiv_id: '2512.13961'
authors:
- Team Olmo
- ':'
- Allyson Ettinger
- Amanda Bertsch
- Bailey Kuehl
- David Graham
- David Heineman
- Dirk Groeneveld
- Faeze Brahman
- Finbarr Timbers
- Hamish Ivison
- Jacob Morrison
- Jake Poznanski
- Kyle Lo
- Luca Soldaini
- Matt Jordan
- Mayee Chen
- Michael Noukhovitch
- Nathan Lambert
- Pete Walsh
- Pradeep Dasigi
- Robert Berry
- Saumya Malik
- Saurabh Shah
- Scott Geng
- Shane Arora
- Shashank Gupta
- Taira Anderson
- Teng Xiao
- Tyler Murray
- Tyler Romero
- Victoria Graf
- Akari Asai
- Akshita Bhagia
- Alexander Wettig
- Alisa Liu
- Aman Rangapur
- Chloe Anastasiades
- Costa Huang
- Dustin Schwenk
- Harsh Trivedi
- Ian Magnusson
- Jaron Lochner
- Jiacheng Liu
- Lester James V. Miranda
- Maarten Sap
- Malia Morgan
- Michael Schmitz
- Michal Guerquin
- Michael Wilson
- Regan Huff
- Ronan Le Bras
- Rui Xin
- Rulin Shao
- Sam Skjonsberg
- Shannon Zejiang Shen
- Shuyue Stella Li
- Tucker Wilde
- Valentina Pyatkin
- Will Merrill
- Yapei Chang
- Yuling Gu
- Zhiyuan Zeng
- Ashish Sabharwal
- Luke Zettlemoyer
- Pang Wei Koh
- Ali Farhadi
- Noah A. Smith
- Hannaneh Hajishirzi
baselines:
- Qwen 3 32B
- Qwen 2.5 32B
- Gemma 3 27B
- Gemma 2 27B
- DeepSeek R1 32B
- Llama 3 70B
- Apertus 70B
- LLM360 K2-V2 70B
- Stanford Marin 32B
- OpenThinker 7B
- Nemotron Nano 9B
category: llm/pretraining
code_url: https://github.com/allenai/OLMo-core
core_contribution: First fully-open model family to release the complete model flow
  while achieving state-of-the-art performance among fully-open models, with novel
  contributions in data mixing (constrained/conditional mixing), preference tuning
  via Delta Learning, multi-domain RLVR with OlmoRL infrastructure, and long-context
  extension using olmOCR science PDFs.
datasets:
- Dolma 3 Mix (6T pretraining)
- Dolma 3 Dolmino Mix (100B midtraining)
- Dolma 3 Longmino Mix (600B long-context)
- Dolci Think SFT
- Dolci Think DPO
- Dolci Think RL
- Dolci Instruct SFT
- Dolci Instruct DPO
- Dolci Instruct RL
- Dolci RL-Zero
date: '2025-12-15'
doi: null
failed_gates: []
keywords:
- open-source LLM
- language model pretraining
- reinforcement learning
- thinking models
- data curation
- long-context extension
- instruction tuning
- GRPO
- model flow
- fully-open models
metrics:
- MATH
- AIME 2024/2025
- OMEGA
- BigBenchHard
- ZebraLogic
- AGI Eval
- HumanEvalPlus
- MBPP+
- LiveCodeBench v3
- IFEval
- IFBench
- MMLU
- PopQA
- GPQA
- AlpacaEval 2 LC
- RULER
- HELMET
- BFCLv3
- SimpleQA
- LitQA2
pipeline_version: 1
publication_type: preprint
quality: full
tags:
- open-source
- LLM
- pretraining
- reinforcement-learning
- thinking-models
- data-curation
- GRPO
- long-context
- instruction-tuning
title: Olmo 3
tldr: OLMo 3 is a family of fully-open 7B/32B language models releasing the entire
  model flow (data, code, checkpoints) with competitive performance to closed-weight
  models, featuring OLMo 3 Think (reasoning), Instruct (chat/tool-use), and RL-Zero
  variants.
url: https://arxiv.org/abs/2512.13961
venue: arXiv preprint
---

# OLMo 3: Fully-Open State-of-the-Art Language Models

## 1. 论文概述

OLMo 3 是 Allen Institute for AI (AI2) 发布的一族完全开放的语言模型，包含 7B 和 32B 两种参数规模。与其他开源模型不同，OLMo 3 发布了**完整的模型流程 (model flow)**——包括每个训练阶段的数据、代码、中间检查点和依赖项，而不仅仅是最终权重。

模型家族包含四个变体：
- **OLMo 3 Base**: 基础预训练模型
- **OLMo 3 Think**: 推理型思考模型（旗舰，最强全开放思考模型）
- **OLMo 3 Instruct**: 非推理型指令跟随模型（优化延迟和可用性）
- **OLMo 3 RL-Zero**: 直接从基础模型进行 RL 训练的变体（用于研究 RL 效果）

## 2. 核心技术贡献

### 2.1 三阶段基础模型训练

**预训练 (Stage 1)**: 在 Dolma 3 Mix 上训练约 5.9T tokens
- 数据源: Common Crawl (76.1%), olmOCR 科学 PDF (13.6%), Stack-Edu 代码 (6.89%), arXiv, FineMath, Wikipedia
- **创新的数据混合方法**: 基于 swarm 的受约束数据混合 (constrained data mixing) + 条件混合 (conditional mixing)，可增量适应新数据域
- **质量感知上采样**: 相比简单的质量过滤，采用连续上采样曲线，高质量数据被多次采样，最高上采样因子为 7x
- **三阶段去重**: 精确去重 (67% 去除) → MinHash 模糊去重 (23% 去除) → 子串去重 (14% 文本字节去除)，总共从 38.7B 文档减少到 9.7B
- 使用新的 **Duplodocus** 工具（原生 Rust）进行大规模去重

**中训练 (Stage 2)**: 在 Dolma 3 Dolmino Mix 上训练 100B tokens
- **两阶段方法框架**: 轻量级分布式微退火 (microanneal) 测试 + 集中式整合测试
- 微退火: 选择目标数据集 → 采样 5B tokens → 与 5B web tokens 混合 → 在 10B mix 上退火 → 对比 web-only 基线
- 涵盖数学（TinyMATH, CraneMath, MegaMatt）、代码（Stack-Edu FIM, CraneCode）、QA（Reddit-to-Flashcards, Wiki-to-RCQA）、思考轨迹、指令数据
- **关键发现**: 包含后训练数据类型（指令和思考轨迹）在中训练阶段就能带来基础模型性能提升

**长上下文扩展 (Stage 3)**: 在 Dolma 3 Longmino Mix 上训练 50B (7B) / 100B (32B) tokens
- 将上下文从 8,192 扩展到 65,536 tokens
- 数据来源: olmOCR 科学 PDF（600B+ tokens），最大的公开长上下文研究数据集
- 技术配方: YaRN (仅应用于全注意力层) + 文档打包 (best-fit) + 文档内掩码 + 合成数据增强 (CWE + REX 聚合任务)
- 混合 34% 长上下文数据 + 66% 短上下文数据，避免短上下文能力退化

### 2.2 后训练三阶段流程

所有后训练变体（Think 和 Instruct）都遵循 **SFT → DPO → RL** 三阶段：

**OLMo 3 Think** (推理模型):
- **SFT**: ~2.3M 示例，涵盖数学、代码、精确指令跟随、聊天、安全；使用 QwQ-32B 和 DeepSeek R1 生成推理轨迹
- **DPO (Delta Learning)**: 200K 对比对；**核心创新**——当 SFT 已饱和（继续在高质量数据上做 SFT 反而伤害性能），通过配对不同能力水平模型的输出（Qwen3 32B chosen vs Qwen3 0.6B rejected）构建有用的对比信号
- **RLVR (OlmoRL)**: ~105K prompts 跨数学、代码、IF、通用聊天四个域

**OLMo 3 Instruct** (指令模型):
- 从 Think SFT 检查点"热启动"，显著提升性能
- DPO 引入多轮对话偏好、长度控制（限制 chosen-rejected 长度差在 100 tokens 内）
- 新增函数调用训练数据（Science QA + Web Search QA + SimFC 模拟数据）
- 工具调用格式使用 OpenAPI 规范 + XML 标签，并扩展 tokenizer 词汇表

### 2.3 OlmoRL: 强化学习基础设施

基于 GRPO 的改进版本，关键优化：
- **零梯度信号过滤**: 移除奖励全同的组（类似 DAPO）
- **主动采样**: 持续从 actor 拉取完成品并重新采样，保持批量大小一致
- **Token 级损失**: 避免长度偏差
- **去除 KL 损失**: 允许更自由的策略更新
- **截断重要性采样** + **非标准差归一化优势** + **更高剪裁上界**
- **基础设施突破**: 完全异步训练 + 连续批处理 + 飞行中权重更新（不失效 KV cache），吞吐量从 OLMo 2 的 881 tokens/s 提升到 2949 tokens/s（3.3x）

### 2.4 OlmoBaseEval: 基础模型评估套件

- 任务聚类: 将 70 个外部模型的 23K benchmark 分数进行层次聚类，得到 MC_STEM、MC_Non-STEM、GenQA、Math、Code、Code FIM 六个集群
- 缩放分析: 使用 Base Easy 套件（bits-per-byte 代理指标）在小规模做数据决策
- 信噪比分析: 系统移除噪声过大的 benchmark（如 BoolQ）
- 包含 43 个任务（是 OLMo 2 的 4 倍以上），加 4 个 held-out benchmark

## 3. 实验结果

### 3.1 OLMo 3 Think 32B (旗舰模型)

| 类别 | 指标 | OLMo 3.1 Think 32B | Qwen 3 32B | DS-R1 32B |
|------|------|---------------------|------------|-----------|
| 数学 | MATH | 96.2 | 95.4 | 92.6 |
| 数学 | AIME 2025 | 78.1 | 70.9 | 56.3 |
| 推理 | BigBenchHard | 88.6 | 90.6 | 89.7 |
| 编码 | HumanEvalPlus | 91.5 | 91.2 | 92.3 |
| 编码 | LiveCodeBench v3 | 83.3 | 90.2 | 79.5 |
| IF | IFEval | 93.8 | 86.5 | 78.7 |
| 知识 | MMLU | 86.4 | 88.8 | 88.0 |
| 聊天 | AlpacaEval 2 LC | 69.1 | 75.6 | 26.2 |

- **最强全开放思考模型**，超越 Qwen 2.5 Instruct、Gemma 2/3 27B、DS-R1
- 接近 Qwen 3 32B（非全开放），且训练 tokens 少 6 倍
- OLMo 3.1 Think 32B 通过延长 RL 训练（750→2300 步）进一步提升，AIME 2025 +4, ZebraLogic +4, IFEval +4, IFBench +20

### 3.2 OLMo 3 Instruct

- 7B: 超越 Qwen 2.5-7B Instruct、OLMo 2 Instruct 7B、Apertus 8B Instruct
- 32B: 超越 Qwen 2.5 32B、Gemma 3 27B、Apertus 70B；IFBench 达 39.7（超 Qwen 3/3VL）
- 32B AIME 2025: 57.9（超越 Qwen 3 32B No-Thinking 的 21.3 达 36.6 分之差）

### 3.3 长上下文

| 模型 | RULER 65K | HELMET 65K |
|------|-----------|------------|
| OLMo 3 7B | 67.96 | 36.80 |
| Qwen 2.5 7B | 67.30 | 30.47 |
| OLMo 3 32B | 79.70 | 43.15 |
| Qwen 2.5 32B | 92.67 | 41.73 |

### 3.4 训练成本

- 总计约 56 天（1024 H100 GPU 集群）
- 预训练 ~47 天（含中训练和长上下文扩展）
- 后训练 ~9 天（SFT + DPO + RL）
- 按 $2/H100-hour 计算，总成本约 $2.75M

## 4. 关键发现与洞察

### 4.1 Delta Learning 的有效性
- 当 SFT 在高质量数据上已饱和时，继续 SFT 会伤害性能
- 但将同样的"已无效"数据配对更弱模型的输出做 DPO，可以继续提升模型
- **关键**: 偏好数据的质量取决于 chosen 和 rejected 之间的质量差距 (delta)，而非任一方的绝对质量

### 4.2 DPO 是 RL 的更好起点
- SFT + DPO + RLVR > SFT + RLVR（全面优于跳过 DPO）
- DPO 模型在 RL 中保持优势，特别是在 AlpacaEval 等非 RL 目标任务上
- DPO 模型展示更高的 pass@K 性能，说明 RL 从 DPO 出发更有效地将 pass@K 转化为 pass@1

### 4.3 混合域 RL 训练防止过拟合
- 单域 RL 训练获得更高的训练奖励，但混合域训练获得更好的下游性能
- 混合数据降低了模型在训练中过度优化的倾向，减少奖励作弊

### 4.4 中训练中的特殊 token 问题
- 在中训练数据中包含 `<|im_start|>` 等特殊 token 会严重破坏基础模型的评估表现
- 原因: 模型在推理时倾向输出这些未在预训练中见过的 token
- 解决方案: 移除特殊 token，使用简单换行分隔

### 4.5 模型合并 (Model Souping) 的效果
- 32B 中训练: 合并两个不同种子的运行，MC_STEM +1, GenQA +0.4, Math +2.9/+1.6
- 32B 长上下文: 合并三个检查点作为最终模型
- 7B 中训练: 未观察到合并收益

### 4.6 去污染的影响
- 开发了新的 `decon` 去污染工具（n-gram 匹配 + 簇扩展）
- 污染在 Flan 和 Nemotron 等现有数据集中普遍存在
- 污染不一定导致性能膨胀（如 DeepSeek LeetCode 有无污染都接近 0，GSM8K 去污后反而更好）

## 5. 开放工件

| 类别 | 工件 |
|------|------|
| 训练代码 | OLMo-core (预训练), Open Instruct (后训练) |
| 数据代码 | datamap-rs, duplodocus, dolma3 |
| 评估代码 | OLMES, decon |
| 训练数据 | Dolma 3 Mix, Dolmino Mix, Longmino Mix, Dolci 全系列 |
| 模型权重 | 所有中间检查点 + 最终模型 |
| 训练日志 | 完整 wandb 日志 |

## 6. 局限性与未来方向

- 长上下文性能仍落后于 Qwen 2.5 32B 的 RULER 分数
- 知识任务表现不如 Qwen 3 系列（推测 Qwen 通过从最大模型蒸馏获益）
- RL 训练的超参数搜索仍然昂贵且理论不成熟
- OLMo 3.1 Think 32B 的 RL 训练在 2300 步时性能仍未完全饱和，暗示更长训练可能继续提升
- 后训练评估占用 10-20% 的计算预算（长推理生成的开销）

## 7. 机制迁移分析

### 可迁移的核心机制

1. **受约束条件混合 (Constrained Conditional Mixing)**: 适用于任何多源数据混合场景。通过 swarm 基础过程 + 条件混合，可增量适应新数据域而无需从头重新搜索。
2. **Delta Learning DPO**: 当 SFT 数据饱和时，配对强弱模型输出做 DPO 仍可提升。适用于任何后训练流程。
3. **微退火评估框架**: 用 5-10B token 的小规模退火实验快速评估数据集价值，比完整训练高效 10-20 倍。
4. **OlmoRL 异步基础设施**: 连续批处理 + 飞行中更新的组合使 RL 训练吞吐提升 3.3x。
5. **从 Think SFT 热启动 Instruct**: Instruct 模型从 Think SFT 检查点开始训练，获得推理能力的残余收益而不增加推理时延。
6. **质量感知上采样曲线**: 相比简单质量过滤（阶跃函数），使用连续上采样曲线更有效利用数据分布。
