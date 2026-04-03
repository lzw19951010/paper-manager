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
- model: Qwen 3 32B
  score: MATH 95.4%, AIME 2024 80.8%
- model: DeepSeek R1 32B
  score: MATH 92.6%, AIME 2024 70.3%
- model: Apertus 70B Instruct
  score: MATH 36.2%, AIME 2024 0.3%
- model: LLM360 K2-V2 70B
  score: MATH 94.5%, AIME 2024 78.4%
category: llm/pretraining
code_url: null
core_contribution: ''
datasets: []
date: '2025-12-15'
doi: null
failed_gates: []
keywords: []
metrics: []
pipeline_version: 1
publication_type: preprint
quality: full
tags: []
title: Olmo 3
tldr: ''
url: https://arxiv.org/abs/2512.13961
venue: null
---

#### 核心速览

##### TL;DR
OLMo 3 通过将多阶段预训练（Stage 1 + 2 模型汤 + 长上下文扩展）与三级后训练流程（Think SFT → DPO delta learning → 改进版 GRPO）结合，构建出完全开放的 7B/32B 语言模型，OLMo 3.1 Think 32B 在 MATH 上达到 96.2%、AIME 2024 达到 80.6%，超越同规模所有完全开放模型，并在 IFBench 上以 68.1 远超同规模任何模型。

##### 一图流 (Mental Model)
旧方法像是在单张照片上调色：预训练一次定型，微调只是滤镜叠加，推理能力全靠数据巧合出现。OLMo 3 则像是分层冲洗暗房照片——第一次在大浴槽里显影轮廓（5.5T token 预训练），第二次换小浴槽精细调色（100B token 中训练：注入合成数学/代码/思维链），第三次拉长曝光补足细节（50B token 长上下文扩展）——每次都有化学测试条（OlmoBaseEval 集成测试）验证效果再继续。后训练则是三块连续滤镜：Think SFT 先给模型"装上眼睛"看推理轨迹，Delta Learning DPO 让模型学"强者和弱者的差距"而非绝对好坏，最后 GRPO 变体通过组内相对奖励做强化自我校准。Figure 2 展示了从基础模型到 Think/Instruct 两条路径的完整训练流程。

##### 核心机制一句话 (Mechanism in One Line)
**[分阶段混合]** + **[合成数据注入与模型汤]** + **[方式：基于组内相对奖励的异步 RLVR 配合 delta 偏好学习]** + **[效果：在参数量相同条件下，推理基准与指令遵循同步突破完全开放模型天花板]**

#### 机制迁移分析

##### 机制解耦 (Mechanism Decomposition)

| 原语名称 | 本文用途 | 抽象描述 | 信息论/几何直觉 |
|---------|---------|---------|---------------|
| **阶段化数据课程 (Staged Data Curriculum)** | 预训练 Stage 1 → Stage 2 midtraining → LC 扩展；每阶段重新配比数据域，用集成测试验证后切换 | 将训练信号分解为"通用分布建模 → 技能特化 → 长度泛化"三级，各阶段以独立评测集为反馈信号驱动混合权重搜索 | 从最大熵起点出发，逐步降低特定技能子空间的条件熵；每次切换都在 KL 散度最小化（保留通用能力）和子域困惑度最小化（增益专项能力）之间做帕累托权衡 |
| **模型汤 (Model Souping)** | 32B midtraining 阶段将两个不同随机种子的独立训练 checkpoint 做参数平均（ingredient 1 + ingredient 2 → soup） | 在参数空间取多个独立解的算术均值；前提是这些解处于同一个"平坦损失盆地"中，否则平均会落入高损失鞍点 | 独立解收敛到损失景观的不同低谷，参数均值若在两者中间也处于平坦区域，则相当于在函数空间做集成，方差降低的同时偏差不显著增加；Table 13 显示 soup 比任意单 ingredient 在数学上高 3–5 点 |
| **Delta Learning (对比偏好学习)** | Think DPO 阶段：用大模型（Qwen 3 32B）生成 chosen、小模型（Qwen 3 0.6B）生成 rejected，组成偏好对，代替 LLM-judge 评分方式 | 偏好信号来源于同族模型的能力差距而非外部裁判的绝对评分；核心是"强–弱对"而非"好–坏对" | 从互信息角度看，同一提示下强/弱模型输出的联合分布中，条件互信息 I(capability; response | prompt) 更清晰；弱模型响应与强模型响应之间的分布距离提供了比 judge label 更稳定的梯度方向，避免 reward hacking |
| **OlmoRL：改进版 GRPO with 异步 inflight 更新** | Think RL 阶段：clip-higher 不对称截断（ε_low=0.2, ε_high=0.272）+ 无 KL 损失 + 无方差归一化 + 基于 vLLM 的异步推理 + inflight 更新 | 将 on-policy GRPO 中三个保守偏向（对称截断、KL 惩罚、难度标准化）同时去除，并通过工程上的异步批处理消除静态 padding 浪费 | 去掉方差归一化（Dr GRPO）等价于保留原始优势估计的尺度信息，使难题和简单题使用统一梯度强度；clip-higher 放宽上界等价于在高奖励 token 子空间允许更大的策略更新步长；inflight 更新则把 GPU 利用率从 12.9% MBU 提升到 43.2% MBU（Table 23） |

##### 迁移处方 (Transfer Prescription)

**原语 1：阶段化数据课程**

- **目标领域 + 具体问题**：推荐系统的序列用户行为建模——冷启动用户缺少行为数据，直接用全量行为数据训练会让模型过拟合热门 item 分布。
- **怎么接**：Stage 1 用全量隐式反馈（点击/曝光）训练通用 item embedding；Stage 2 换小批量高质量显式反馈（购买/收藏）+ 合成的"负向行为"对（类比思维链注入）做域特化；长上下文扩展阶段换为长序列会话建模（类比 65K context 扩展）。评测信号替换为线上 A/B test 或离线 HitRate@K。
- **预期收益**：通用 embedding 不退化的同时，精排层获得更强的精细建模能力；类比 Table 13 中 Stage 2 在数学上 +18 点而通用 MC 几乎不降。
- **风险**：各阶段的数据分布切换时机难以确定，集成测试成本高；推荐系统缺乏像 OlmoBaseEval 这样覆盖全面的离线评测集，可能在某些子域过优化。

**原语 2：模型汤**

- **目标领域 + 具体问题**：对话系统中多任务 fine-tune（安全对齐 + 代码能力 + 知识问答），三者单独训练各有偏科，联合训练存在任务冲突。
- **怎么接**：针对不同任务目标分别训练 3 个 checkpoint，在参数空间做算术均值（Wise-FT / Model Soup 范式）；替换现有 pipeline 中"联合 fine-tune"这一步骤。
- **预期收益**：比联合训练更低的干涉效应，类比 32B soup 比 ingredient 高 2.9 点数学、1.0 点代码。
- **风险**：若各任务的损失盆地不重叠（例如代码与安全对齐差异极大），平均后可能落在高损失区域；建议先用线性权重搜索（α·θ₁ + (1-α)·θ₂）探索后再平均。

**原语 3：Delta Learning**

- **目标领域 + 具体问题**：RLHF/RLAIF 中 reward model 数据标注成本高，且绝对质量评分受标注者主观性影响。
- **怎么接**：用生产中最强版本模型生成 chosen，用最弱/最老版本生成 rejected，构成自动化偏好对；替换掉现有 pipeline 里的 human annotation 或 GPT-judge 环节。输入是同一批 prompt，输出是强弱对偏好对，直接接入 DPO 训练。
- **预期收益**：无需人工标注，偏好信号来自能力差距而非主观打分，梯度更稳定；Table 21 显示 delta learning DPO 比 SFT on chosen 高 8.4 个平均分。
- **风险**：强模型与弱模型差距若太大（风格差异超过能力差异），偏好对可能学到文体偏好而非推理能力；需要控制强弱模型同族（如 Qwen 3 32B 与 Qwen 3 0.6B 而非跨系列）。

**原语 4：OlmoRL 异步 inflight RLVR**

- **目标领域 + 具体问题**：代码生成、SQL 合成等有可验证奖励信号的任务中，RLVR 训练吞吐严重受限于静态批处理（padding 浪费高达 54%）。
- **怎么接**：在 actor 生成（vLLM）与 learner 更新（PyTorch）之间引入异步队列；learner 使用 TIS（截断重要性采样）修正 off-policy 偏差；用 inflight 更新在等待新 rollout 时继续梯度步；替换现有 static-batching GRPO 实现中的同步 gather 步骤。
- **预期收益**：MBU 从 12.9% 提升到 43.2%（3.4x），类比 Table 23；在 GPU 资源有限时效果更显著。
- **风险**：异步更新引入策略滞后（stale policy），需要配合 TIS cap（ρ）防止策略漂移；异步程度参数（max asynchrony=8）需要根据响应长度分布调整，响应越短异步越安全。

##### 机制家族图谱 (Mechanism Family Tree)

**前身 (Ancestors):**
- **GRPO (Shao et al., 2024)**：OlmoRL 的基础算法，组内相对策略优化，取消 value network，以组均值作为 baseline 估计优势。
- **DAPO (Yu et al., 2025)**：贡献了 clip-higher 不对称截断（ε_high > ε_low）和 token-level 损失归一化，Olmo 3 直接吸收这两项改进。
- **Dr GRPO (Liu et al., 2025)**：发现 GRPO 中方差归一化会产生难度偏差（难题被错误放大），建议去掉标准差归一化；Olmo 3 采纳了这一观点（Eq. 2 中 advantage 仅减均值不除标准差）。
- **Tülu 3 / SPPO (Lambert et al., 2024)**：SFT + DPO + RL 三阶段后训练框架的直接前身；Olmo 3 在 Tülu 3 的基础上加入 Think 路径和 delta learning。
- **Model Soup (Wortsman et al., 2022)**：模型汤的理论和实践基础；Olmo 3 将其从 fine-tune 集成扩展到 midtraining ingredient 合并。

**兄弟 (Siblings):**
- **DeepSeek R1-Zero / R1 (Guo et al., 2025)**：同期独立提出从基础模型出发用 GRPO 做推理强化，但使用闭源预训练数据；Olmo 3 在完全开放设置下复现并超越了其部分结果。
- **Qwen 3 32B (Yang et al., 2025)**：同期竞争性 thinking model，AIME 2024 达 80.8%（略超 Olmo 3 的 80.6%），但预训练数据和基础模型均不开放；Olmo 3 以相同规模、6x 更少 token 达到可比效果。
- **OpenThoughts3 (Guha et al., 2025)**：同期开放推理数据集，为 Olmo 3 Think SFT 提供核心数学和代码 trace，属于合作关系而非竞争。

**后代 (Descendants):**
- OLMo 3 本身已经产生了 OLMo-RL-Zero 变体（直接从 base model 跳过 SFT 做 RL），验证了 midtraining 中注入 thinking traces 足以实现 warm-start，预计后续工作会在此基础上研究 token-efficient base-to-reasoning 路径。
- OlmoRL 基础设施（continuous batching + inflight updates）的工程范式预计被后续完全开放 RL 项目继承，作为降低大规模 RLVR 成本的标准实践。

本文在族谱中的**创新增量**：将 DAPO（clip-higher）、Dr GRPO（无方差归一化）、截断重要性采样三者组合为一个稳定的 OlmoRL 目标（Eq. 1），并通过 inflight 工程优化使其在完全开放设置下达到 3.4x 吞吐提升，同时引入 Think→Instruct warm-start 和 Delta Learning 作为后训练数据工程的系统性方案。

#### 背景知识补充

**Dolma / olmOCR**：Dolma 是 Allen AI 的开放预训练语料框架（Dolma 1.x → Dolma 3），OLMo 3 使用 Dolma 3 Mix（总池 9.31T token，训练用 5.93T）。olmOCR 是新引入的 PDF 解析工具（Poznanski et al., 2025），将科学 PDF 转换为带布局信息的纯文本，提供了 805B 高质量学术文档作为预训练语料，是相比 OLMo 2 最显著的数据来源升级之一，如 Figure 1 所示，这一完整数据流构成了 OLMo 3 全透明开放的基础。

**YaRN**：OLMo 3 在长上下文扩展（Stage 3，50B token）中使用 YaRN（Peng et al., 2023）扩展 RoPE 位置编码，但关键工程决策是**只对全注意力层应用 YaRN，滑动窗口注意力层不应用**，Figure 2 中长上下文扩展路径的模型架构说明了这一区别——直接应用到所有层反而会损害 RULER 分数。

**RLVR（可验证奖励强化学习）**：通过程序可验证的标量奖励（数学题判断最终答案正误；代码执行结果是否通过单测）替代需要 reward model 的传统 RLHF。Olmo 3 将 RLVR 扩展到精准指令遵循（IF-RLVR，通过规则匹配判断格式约束是否满足），这是从数学/代码向更通用任务推广 RLVR 的核心探索，IFBench 从 SFT 的 30.0 提升到 RL 后的 41.6（7B）、68.1（32B）即来自此。


#### 方法详解

##### 直觉版 (Intuitive Walk-through)

OLMo 3 的核心叙事可以用 Figure 1 和 Figure 2 来理解。Figure 1 描绘的是「模型流（model flow）」的全景：左侧轴线展示基础模型训练从 Pretraining 到 Midtraining 再到 Long-context extension 的性能演进，右侧轴线展示后训练从 SFT 到 DPO 再到 RL 的能力跃升，并将 OLMo 3 与 Qwen 3 32B、Gemma 3 27B 等同量级模型做直接对比。Figure 2 则更具体地展示了每个子阶段的训练数据类型：预训练用 web text + science PDFs + code，中训练引入 math + reasoning + QA 合成数据，后训练进一步细分出 Think 和 Instruct 两条路径。

**Figure 1** 展示了 OLMo 3 的完整模型流：从训练数据（Dolma 3 数据集家族）出发，经由预训练（Stage 1）→ 中训练（Stage 2）→ 长上下文扩展（Stage 3）形成 Base 模型，随后进入后训练阶段——SFT → DPO → RLVR（OlmoRL）——输出最终的 Instruct 或 Think 模型。整个流程的训练代码分别托管于 `olmo-core`（预训练）、`open-instruct`（后训练）、`dolma3`（数据）和 `olmes`（评估）四个仓库，实现了从数据到模型权重的完整可复现性。

**Figure 2** 更详细地展示了后训练各子阶段的流向。与 OLMo 2 的简单 SFT+DPO 流程相比，OLMo 3 在此基础上增加了两条关键路径：（1）针对 Think 系列，采用 Dolci Think 高质量推理数据进行 SFT 热启动，再通过 OlmoRL 做 RLVR 强化；（2）针对 Instruct 系列，从 Think SFT checkpoint 出发继续训练，避免了从基础模型重新微调的计算浪费，同时保留了推理能力的"记忆"。

**旧方案（OLMo 2）的局限：**
- 预训练数据以 Common Crawl 网页为主，缺乏大规模合成推理数据
- 后训练流程：SFT + DPO，无 RL 阶段
- 上下文窗口 8K，无长上下文扩展
- RL 基础设施（静态批处理）效率低，计算浪费严重

**OLMo 3 的核心改变：**
- Dolma 3 引入 olmOCR 科学 PDF、Dolci Think 合成推理链、CraneMath/CraneCode 等数学代码合成数据
- 三阶段基础训练 + 三阶段后训练，形成完整流水线
- OlmoRL 基础设施：连续批处理 + 飞行更新（inflight updates），吞吐量提升 3.4×
- 后训练从 Think SFT 热启动，大幅缩短训练时间

##### 精确版

###### 完整数据流图

```
原始数据池 (9.31T tokens, 9.97B docs)
    │
    ├── Common Crawl (8.14T, 76.1%)
    ├── olmOCR science PDFs (972B, 13.6%)
    ├── Stack-Edu (137B, 6.89%)
    ├── FineMath 3+ (34.1B, 2.56%)
    ├── arXiv (21.4B, 0.86%)
    └── Wikipedia/Wikibooks (3.69B, 0.04%)
            │
            ▼ 质量感知上采样 + 去重 + 主题混合
    Dolma 3 预训练 Mix (5.93T tokens)
            │
            ▼ Stage 1: 预训练
    OLMo 3 7B/32B Base (Stage 1 Checkpoint)
            │
            ▼ Stage 2: 中训练 (Dolmino Mix, 100B)
            │   ├── 合成数学 (TinyMATH, CraneMath, MegaMatt, Dolmino Math)
            │   ├── 合成代码 (StackEdu FIM, CraneCode)
            │   ├── 合成 QA (Reddit Flashcards, Wiki RCQA, Nemotron QA)
            │   ├── 合成推理链 (QWQ, Gemini, LlamaNemotron, OpenThoughts2)
            │   └── 指令数据 (Tulu 3 SFT, Dolmino Flan)
    OLMo 3 7B/32B Base (Stage 2 Checkpoint)
            │
            ▼ Stage 3: 长上下文扩展 (Longmino, 50B/100B)
    OLMo 3 7B/32B Base (Final)
            │
    ┌───────┴────────┐
    ▼                ▼
Think 路线      Instruct 路线
    │                │
SFT (45B tokens)  从 Think SFT 出发
    │                │
DPO (150K/200K 对) DPO (260K 对)
    │                │
OlmoRL (1400/750步) OlmoRL (450步)
    │                │
Think Final      Instruct Final
```

**关键数字：**
- 预训练：5.93T tokens（7B）/ 5.5T tokens（32B）
- 中训练：~100B tokens × 2（32B 两路并行，之后做 Model Soup）
- 长上下文扩展：50B tokens（7B）/ 100B tokens（32B），序列长度 65,536
- SFT：45.4B tokens（7B Think）/ 45.2B tokens（32B Think）/ 3.4M tokens（Instruct）

###### 关键公式

**公式一：OlmoRL 目标函数（改进 GRPO）**

$$J(\theta) = \frac{1}{\sum |y_i|} \sum_{i=1}^{G} \sum_{t=1}^{|y_i|} \min\!\left(\frac{\pi(y_{i,t}|x,y_{i,<t};\theta_\text{old})}{\pi_\text{vllm}(y_{i,t}|x,y_{i,<t};\theta_\text{old})},\, \rho\right) \cdot \min\!\left(r_{i,t} A_{i,t},\; \text{clip}(r_{i,t}, 1{-}\varepsilon_\text{low}, 1{+}\varepsilon_\text{high}) A_{i,t}\right)$$

**符号含义：**
- $r_{i,t} = \pi(y_{i,t}|x,y_{i,<t};\theta) / \pi(y_{i,t}|x,y_{i,<t};\theta_\text{old})$：token 级别重要性采样比率，衡量当前策略相对参考策略的偏移
- $\pi_\text{vllm}$：vLLM actor 采样时的策略（可能因 inflight updates 而与 $\theta_\text{old}$ 略有不同）
- $\rho$：截断重要性采样上限，防止异步更新引起的分布偏移过大
- $\varepsilon_\text{low} = 0.2$：下裁剪边界（来自标准 PPO）
- $\varepsilon_\text{high} = 0.272$：上裁剪边界（非对称，来自 DAPO 的 clip-higher 策略，允许高奖励 token 获得更大梯度更新）
- $G = 8$：每个 prompt 的 rollout 组大小
- 分母 $\sum |y_i|$：按 token 总数归一化，而非按序列数归一化，避免长短序列的偏差

**公式二：优势函数（无方差归一化）**

$$A_{i,t} = r(x, y_i) - \text{mean}\!\left(\{r(x, y_i)\}_{i=1}^{G}\right)$$

**关键设计选择：** 不对优势值除以组内标准差。若对 std 进行归一化，则"难题"（奖励方差大）和"简单题"（奖励方差小）获得相同量级的梯度信号，引入难度偏差。去除 std 归一化后，更难的问题自然获得更小的归一化梯度（来自 Dr GRPO）。

**公式三：DPO 损失（长度归一化版）**

$$\max_{\pi_\theta} \mathbb{E}_{(x,y_c,y_r)\sim\mathcal{D}} \left[\log \sigma\!\left(\frac{\beta}{|y_c|} \log \frac{\pi_\theta(y_c|x)}{\pi_\text{ref}(y_c|x)} - \frac{\beta}{|y_r|} \log \frac{\pi_\theta(y_r|x)}{\pi_\text{ref}(y_r|x)}\right)\right]$$

**符号含义：**
- $y_c$ / $y_r$：chosen（高质量）/ rejected（低质量）响应
- $\beta = 5$：KL 正则化系数，控制策略偏离参考模型的程度
- $|y_c|$、$|y_r|$：分别对 chosen 和 rejected 的 log 概率做长度归一化，防止偏好较短响应
- $\pi_\text{ref}$：SFT checkpoint（固定）

**DPO 的"Delta Learning"数据构造：**
- Chosen：从大模型（Qwen 3 72B 等）生成的高质量长链推理响应
- Rejected：从小模型（OLMo 2 7B 等）生成的较弱响应
- 这一"能力差 = 对比信号"的核心思想来自 Delta Learning（Geng et al., 2025）

###### 数值推演：以 OlmoRL 32B Think 一步更新为例

**场景设置：**
- prompt $x$：一道 AIME 级别数学题
- 从 32B Think SFT checkpoint 开始 RL
- group size $G = 8$，unique prompts per batch = 128

**Step 1：离线难度过滤**
- 对训练集中每道题做 8 次 rollout 估算通过率
- 若通过率 > 62.5%（即 8 次中 ≥ 5 次通过），则视为"简单题"，从 RL 数据集中剔除
- 过滤后保留 104,869 道有效 prompt（32B Think 数据集规模）

**Step 2：Rollout 采样**
- 对一个 batch 中的 128 道题，各采样 8 次响应（共 1,024 条）
- 温度 $T = 1.0$，最大响应长度 32,768 tokens
- 连续批处理避免了静态批处理中对齐填充（padding）导致的最多 54% 计算浪费

**Step 3：奖励计算**
- 每条响应通过验证器（verifier）得到 0 或 1 的二元奖励
- 对同一道题的 8 条响应计算组内均值 $\bar{r}$
- 计算每条响应的优势：$A_i = r_i - \bar{r}$
- 例：8 条响应奖励 = [1, 1, 0, 1, 0, 0, 1, 0]，均值 = 0.5
  - Chosen 响应的优势：$1 - 0.5 = +0.5$
  - Rejected 响应的优势：$0 - 0.5 = -0.5$

**Step 4：策略梯度更新（含截断重要性采样）**
- 当前策略 $\theta$ 与 vLLM actor $\theta_\text{old}$ 可能因 inflight updates 而存在异步差异
- 通过截断 $\rho = 2.0$ 防止过大的重要性权重
- 非对称裁剪：$r_{i,t} \in [1-0.2, 1+0.272] = [0.8, 1.272]$
  - 高奖励 token：上界 1.272 允许比标准 PPO 上界 1.2 更大的梯度步长
  - 低奖励 token：下界 0.8 与标准 PPO 一致

**Step 5：参数更新（32B 配置）**
- 学习率：$2.0 \times 10^{-6}$，常数调度（无衰减）
- Learner GPUs：64 张 H100，Actor GPUs：160 张 H100
- 最大异步度（max asynchrony）= 8，即最多允许 8 步 rollout 异步
- 总 RL 训练步数：750 步（32B Think）

###### 伪代码（PyTorch 风格）

```python
import torch
import torch.nn.functional as F

def olmorl_loss(
    logits_new,        # [B, T, V] 当前策略
    logits_old,        # [B, T, V] 参考旧策略 (theta_old)
    logits_vllm,       # [B, T, V] vLLM actor策略 (可能与old不同)
    input_ids,         # [B, T]
    rewards,           # [B] 每条响应的最终奖励
    group_size=8,
    eps_low=0.2,
    eps_high=0.272,
    rho=2.0,           # TIS cap (仅32B使用)
):
    B, T = input_ids.shape
    G = group_size
    num_prompts = B // G

    # --- Token级别log prob ---
    log_p_new = F.log_softmax(logits_new, dim=-1)
    log_p_old = F.log_softmax(logits_old, dim=-1)
    log_p_vllm = F.log_softmax(logits_vllm, dim=-1)

    token_log_p_new = log_p_new.gather(-1, input_ids.unsqueeze(-1)).squeeze(-1)  # [B, T]
    token_log_p_old = log_p_old.gather(-1, input_ids.unsqueeze(-1)).squeeze(-1)
    token_log_p_vllm = log_p_vllm.gather(-1, input_ids.unsqueeze(-1)).squeeze(-1)

    # --- 优势计算 (无std归一化) ---
    rewards_grouped = rewards.view(num_prompts, G)  # [P, G]
    advantages = rewards_grouped - rewards_grouped.mean(dim=-1, keepdim=True)  # [P, G]
    advantages = advantages.view(B)  # [B]
    # 广播到token级别 (每条序列所有token共享同一优势值)
    adv_tokens = advantages.unsqueeze(-1).expand(-1, T)  # [B, T]

    # --- 重要性采样比率 ---
    r_it = torch.exp(token_log_p_new - token_log_p_old)   # [B, T] 当前/old
    tis_ratio = torch.exp(token_log_p_old - token_log_p_vllm)  # [B, T] old/vllm
    tis_weight = torch.clamp(tis_ratio, max=rho)           # 截断

    # --- 非对称clip ---
    r_clipped = torch.clamp(r_it, 1 - eps_low, 1 + eps_high)
    surrogate1 = r_it * adv_tokens
    surrogate2 = r_clipped * adv_tokens
    per_token_loss = -tis_weight * torch.min(surrogate1, surrogate2)  # [B, T]

    # --- 按token总数归一化 ---
    total_tokens = (input_ids != pad_token_id).sum()
    loss = per_token_loss.sum() / total_tokens
    return loss


def dpo_loss_length_normalized(
    log_p_chosen_policy,   # log π_θ(y_c|x)
    log_p_reject_policy,   # log π_θ(y_r|x)
    log_p_chosen_ref,      # log π_ref(y_c|x)
    log_p_reject_ref,      # log π_ref(y_r|x)
    len_chosen,            # |y_c|
    len_reject,            # |y_r|
    beta=5.0,
):
    delta_chosen = (log_p_chosen_policy - log_p_chosen_ref) / len_chosen
    delta_reject = (log_p_reject_policy - log_p_reject_ref) / len_reject
    logit = beta * (delta_chosen - delta_reject)
    loss = -F.logsigmoid(logit).mean()
    return loss
```

###### 超参数表

**表一：模型架构（OLMo 3 7B / 32B）**

| 参数 | 7B | 32B |
|---|---|---|
| 层数 (Layers) | 32 | 64 |
| 隐藏维度 (dmodel) | 4,096 | 5,120 |
| Q heads | 32 | 40 |
| KV heads（GQA）| 32 | 8 |
| 激活函数 | SwiGLU | SwiGLU |
| QKV 归一化 | QK-Norm | QK-Norm |
| 层归一化 | RMSNorm | RMSNorm |
| 滑动窗口注意力 | 3/4 层，窗口 4,096 | 3/4 层，窗口 4,096 |
| RoPE 缩放 | YaRN（仅全注意力层）| YaRN（仅全注意力层）|
| RoPE θ | 5×10⁵ | 5×10⁵ |
| 梯度裁剪 | 1.0 | 1.0 |
| Z-loss 权重 | 10⁻⁵ | 10⁻⁵ |
| Embedding 权重衰减 | 否 | 否 |

**表二：训练配置与吞吐量（Table 34）**

| 阶段 | DP-rep | DP-shard | CP | 设备数 | TPS/device |
|---|---|---|---|---|---|
| 7B 预训练 | 64 | 8 | - | 512 | 7,700 |
| 7B 中训练 | 16 | 8 | - | 128 | 8,500 |
| 7B 长上下文扩展 | 32 | - | 8 | 256 | 4,000 |
| 32B 预训练 | 16 | 64 | - | 1,024 | 2,000 |
| 32B 中训练 | 8 | 64 | - | 512 | 2,000 |
| 32B 长上下文扩展 | 16 | 8 | 8 | 1,024 | 1,300 |

**表三：基础训练超参数（Table 35）**

| 超参数 | 7B 预训练 | 7B 中训练 | 7B 长上下文 | 32B 预训练 | 32B 中训练 | 32B 长上下文 |
|---|---|---|---|---|---|---|
| LR 调度 | 修正余弦 | 线性衰减 | 线性衰减 | 余弦（5.5T截断）| 线性衰减 | 线性衰减 |
| LR 热身 | 2,000步 | 0步 | 200步 | 2,000步 | 0步 | 200步 |
| 峰值 LR | 3.0×10⁻⁴ | 2.074×10⁻⁴ | 2.074×10⁻⁴ | 6.0×10⁻⁴ | 2.071×10⁻⁴ | 2.071×10⁻⁴ |
| 终止 LR | 3.0×10⁻⁵ | 0 | 0 | 6.0×10⁻⁵ | 0 | 0 |
| Batch（实例）| 512 | 256 | 64 | 1,024 | 512 | 128 |
| 序列长度 | 8,192 | 8,192 | 65,536 | 8,192 | 8,192 | 65,536 |
| Batch（tokens）| 4,194,304 | 2,097,152 | 4,194,304 | 8,388,608 | 4,194,304 | 8,388,608 |
| 总 tokens | 5.93T | 100B | 50B | 5.5T | 100B×2 | 100B |

**表四：SFT 超参数（Table 47）**

| 超参数 | 7B Think SFT | 32B Think SFT | 7B Instruct SFT |
|---|---|---|---|
| 总 Tokens | 45.4B | 45.2B | 3.4M |
| 学习率 | 5.0×10⁻⁵ | 1.0×10⁻⁴（与5×10⁻⁵ soup）| 8.0×10⁻⁵ |
| GPU 数量 | 64 | 256 | 8–64 |
| 最大序列长度 | 32K | 32K | 32K |
| Epochs | 2 | 2 | 2 |
| Batch（tokens）| 1M | 4M | 1M |

**表五：DPO 超参数（Table 48）**

| 超参数 | 7B Think DPO | 32B Think DPO | 7B Instruct DPO |
|---|---|---|---|
| 偏好对数量 | 150K | 200K | 260K |
| Epochs | 1 | 1 | 1 |
| DPO β | 5 | 5 | 5 |
| 学习率 | 8.0×10⁻⁸ | 7.0×10⁻⁸ | 1.0×10⁻⁶ |
| LR 调度 | 线性衰减 | 线性衰减 | 线性衰减 |
| 热身比例 | 0.1 | 0.1 | 0.1 |
| GPU 数量 | 32 | 64–128 | 16 |
| Batch size | 128 | 128 | 128 |
| 最大序列长度 | 16K | 8K | 16K |

**表六：RL 超参数（Table 49）**

| 超参数 | 7B Think RL | 32B Think RL | 7B Instruct RL | 7B RL-Zero |
|---|---|---|---|---|
| 数据集规模 | 104,869 | 104,869 | 171,950 | 13,314 |
| 学习率 | 1.0×10⁻⁶ | 2.0×10⁻⁶ | 1.0×10⁻⁶ | 1.0×10⁻⁶ |
| LR 调度 | 常数 | 常数 | 常数 | 常数 |
| 训练步数 | 1,400 | 750 | 450 | 2,000 |
| 最大 prompt 长度 | 2,048 | 2,048 | 2,048 | 2,048 |
| 最大响应长度 | 32,768 | 32,768 | 8,192 | 16,384 |
| Unique prompts/batch | 64 | 128 | 64 | 32 |
| Group size (G) | 8 | 8 | 8 | 8 |
| TIS cap (ρ) | - | 2.0 | - | 2.0 |
| 采样温度 | 1.0 | 1.0 | 1.0 | 1.0 |
| ε_low（下裁剪）| 0.2 | 0.2 | 0.2 | 0.2 |
| ε_high（上裁剪）| 0.272 | 0.272 | 0.272 | 0.272 |
| Learner GPUs | 16 | 64 | 8 | 8 |
| Actor GPUs | 56 | 160 | 56 | 64 |
| Actor TP 并行度 | 1 | 8 | 1 | 1 |
| 最大异步度 | 1 | 8 | 8 | 8 |

##### 设计决策

###### 决策一：滑动窗口注意力（3/4 层 SWA + 1/4 层全注意力）

**替代方案：** 所有层均采用全注意力（Full Attention Everywhere）。

**论文是否对比：** 是。Table 33 和 Section §3.2 明确说明架构选择；Figure 13a 对长上下文扩展的多种 RoPE 策略做了对比（包括是否对 SWA 层应用 YaRN）。

**核心 trade-off：**
- 全注意力提供最优的理论表达力，每个 token 可以与所有历史 token 交互，但训练时内存随序列长度平方增长（$O(n^2)$），推理时 KV cache 随序列增大。
- SWA 将 3/4 的层限制在局部窗口（4,096 tokens），仅最后 1/4 的层做全局注意力，使得训练和推理的实际开销大幅降低，同时通过层叠的局部注意力保留了跨长距离的信息流动能力（信息可以在多层中传播）。

**为何本文选择优于替代方案：** 在 5.93T tokens 的预训练规模下，采用 SWA 使得序列长度可以从 4K 扩展到 65K，同时控制了基础设施成本。全注意力在相同序列长度下每个 H100 GPU 的吞吐量无法维持 7,700 tokens/s 的目标。混合架构在全部 OlmoBaseEval 指标上与全注意力对齐，同时为长上下文扩展留出余地。


###### 决策二：YaRN 仅应用于全注意力层（非 SWA 层）

**替代方案：** 将 YaRN 应用于全部层（包括 SWA 层），或使用位置插值（Position Interpolation，PI），或调整 RoPE base frequency。

**论文是否对比：** 是。Figure 13a 展示了不同 RoPE 扩展策略在 RULER 评测上的对比结果，"YaRN on full attention only"在各序列长度上均优于其他方案。

**核心 trade-off：**
- SWA 层的注意力窗口固定为 4,096 tokens，对其应用 YaRN（设计目标是改变位置编码使模型在超出训练长度时仍能定位）收益有限，因为这些层本身就只能看到局部上下文。将 YaRN 施加于 SWA 层反而可能扰乱原有的局部模式匹配。
- 全注意力层是长距离信息聚合的关键节点，在这里调整 RoPE 频率可以有效改善模型在超长序列上的绝对位置感知，是性价比最高的干预点。

**为何本文选择优于替代方案：** 对 SWA 层施加 YaRN 不仅收益为零，还可能破坏短文本性能。对全注意力层单独施加 YaRN 在 RULER 32K 和 65K 的评测上取得了最优分数，同时基础 OlmoBaseEval 指标未见明显下滑。


###### 决策三：长上下文扩展数据配比（34% 长文本 + 66% 短中训练数据）

**替代方案：** 采用更高比例的长上下文数据（如 66% 长文本 + 34% 短数据）。

**论文是否对比：** 是。Section §3.6.3 直接对两种配比做了对比实验。

**核心 trade-off：**
- 更多长上下文数据直观上应该帮助模型学会处理更长序列，但训练 distribution 偏移过大会导致模型在短序列任务上的能力退化。
- 66% 长上下文配比导致 OlmoBaseEval（以短序列为主的基础评测集）下降约 2.5 个百分点；
- 34% 长上下文配比将 OlmoBaseEval 下降控制在 0.8 个百分点以内，同时仍能有效提升 RULER 和 HELMET 的长上下文性能。

**为何本文选择优于替代方案：** 这是一个典型的"不能丢失旧能力换取新能力"的权衡。对于应用场景多样的通用模型，维持短序列任务的竞争力（OlmoBaseEval 损失 < 1 点）比极致优化 128K 长上下文性能更重要。34% 的配比在两个维度上都达到了可接受的平衡点。


###### 决策四：32B 模型 Model Souping（两路独立训练后合并）

**替代方案：** 仅做一次中训练 run，取最终 checkpoint。

**论文是否对比：** 是。Section §3.5.4 和对应 Table（Table 13 中的 Ingredient 1、Ingredient 2 对比 Soup 行）明确展示了合并效果：
- 32B Stage 2 Ingredient 1：Math = 66.8，Code = 38.4
- 32B Stage 2 Ingredient 2：Math = 65.4，Code = 39.3
- 32B Stage 2 Soup（合并后）：Math = 69.7，Code = 39.7

Soup 在数学上超过两个 ingredient 中更强的那个 2.9 分，在 MCSTEM 上约提升 1 个百分点。

**核心 trade-off：**
- Souping 需要额外运行两次完整的中训练（额外 ~100B tokens × 2 次），并行使用 512 GPUs，占用约 1.5 天时间和对应计算成本。
- 收益：利用不同随机种子导致模型参数在不同局部极小值收敛的特点，线性插值后得到一个处于更平坦损失盆地的模型，泛化能力更强，且推理时无额外开销（仍是单模型）。
- 替代方案（多数投票集成）需要在推理时运行多个模型，成本不可接受；知识蒸馏需要额外训练循环。Souping 是"一次性训练成本换永久推理优势"。

**为何本文选择优于替代方案：** 对于全开放模型而言，提供单一高质量权重文件是合理目标（用户无法轻松运行两个 32B 模型做集成）。Model Souping 以预训练时的一次性成本换取了约 2-3 点数学任务提升，效费比远高于其他集成方案。


###### 决策五：DPO 使用"Delta Learning"构造偏好对（大模型 chosen + 小模型 rejected）

**替代方案：** 使用 UltraFeedback 风格的 LLM-judge 打分方式（让 GPT-4o 对同一模型的不同输出评分并选出 chosen/rejected）。

**论文是否对比：** 是。Table 21 和 Section §4.3 对比了多种 DPO 数据构造策略。直接对 chosen 响应做 SFT 反而会降低性能（因为 SFT 分布与 DPO 分布不匹配）；Delta Learning 的 chosen 来自明显更强的大模型（而非同一模型的不同采样），对比信号更清晰。

**核心 trade-off：**
- 传统 LLM-judge 方法要求"同一模型的不同质量输出"，但对于推理任务（AIME、LiveCodeBench），同一 7B/32B 模型的不同采样之间质量差距不够大，judge 信号噪声高。
- Delta Learning 利用"大模型能力 vs. 小模型能力"的本质差距构造对比对：chosen 来自 Qwen 3 72B、DeepSeek R1 等强模型，rejected 来自 OLMo 2 7B/32B，两者质量落差巨大，提供了清晰的学习目标。
- 缺点：chosen 分布来自外部模型，OLMo 3 基础模型的"原有风格"可能受到影响；但实验表明 IFEval 等指令跟随指标并未下降。

**为何本文选择优于替代方案：** 在开放推理模型稀缺的情况下（训练时公开的长链推理模型极少），从强模型蒸馏出高质量 chosen 响应，再用弱模型生成 rejected 响应，是获取高质量偏好信号的最经济路径。Table 21 证明这一策略的最终 DPO 模型在数学推理上相比 SFT 有显著提升（如 AIME 2025：Table 25 中 32B SFT 8.2% → DPO 23.3%）。


###### 决策六：OlmoRL 基础设施的连续批处理 + 飞行更新（Inflight Updates）

**替代方案：** 静态批处理（OLMo 2 的做法：等待一整个 batch 的 rollout 全部完成后再更新策略）。

**论文是否对比：** 是。Table 23 精确记录了每个优化步骤的吞吐量提升：

| 配置 | Tokens/second | MFU (%) | MBU (%) |
|---|---|---|---|
| OLMo 2 基线（静态批处理）| 881 | 0.30% | 12.90% |
| + 连续批处理 | 975 | 0.33% | 14.29% |
| + 优化线程 | 1,358 | 0.46% | 19.89% |
| + 飞行更新（OLMo 3）| 2,949 | 1.01% | 43.21% |

最终吞吐量相比基线提升 3.4×（881→2,949 tokens/s）。

**核心 trade-off：**
- 静态批处理最简单，但 RL rollout 的生成长度高度不均匀（平均 14,628 tokens，最大 32K），导致短序列大量等待长序列，填充（padding）浪费高达 54% 的计算。
- 飞行更新允许策略参数在新一批 rollout 进行中就被更新，因此 actor（vLLM）和 learner（策略模型）之间存在异步性。为了修正这一分布偏移，OlmoRL 引入了截断重要性采样（TIS cap $\rho$），确保更新仍在理论保证范围内。
- 最大异步度 = 8 对于 32B 模型意味着最多允许 8 步 rollout 用"过时"策略采样，权衡训练稳定性与吞吐量。

**为何本文选择优于替代方案：** 对于 32B Think 模型 21 天的 RL 扩展训练，3.4× 的吞吐量提升等价于将计算成本从 ~71 天压缩到 ~21 天，节省约 50 天 224 GPU 的费用。这不是工程优化的"锦上添花"，而是让如此长时间 RL 训练在合理预算内可行的前提条件。


###### 决策七：从 Think SFT checkpoint 热启动训练 Instruct 模型

**替代方案：** 从 Base 模型直接开始 Instruct 的 SFT 训练。

**论文是否对比：** 是。Table 29（Section §4.5）对比了两种初始化方案，从 Think SFT 出发比从 Base 出发平均提升 +3.3 个基准点，且响应长度并未因此变长（没有"被推理链污染"）。

**核心 trade-off：**
- Think SFT 训练了 45B tokens 的链式推理数据，其中隐含了大量数学和代码的"解题过程"知识。从这个 checkpoint 出发做 Instruct SFT（仅 3.4M tokens），等于"免费"继承了这些知识，同时通过少量指令数据将输出风格切换为简洁答案。
- 担忧：Think 训练引入的"想多"倾向可能导致 Instruct 模型输出冗长思考链。实验表明这一担忧不成立——Instruct 模型的 IFEval 和 AlpacaEval 响应长度与直接从 Base 训练的版本无显著差异。

**为何本文选择优于替代方案：** 在计算成本方面，Instruct SFT 只需 3.4M tokens（相比 Think SFT 的 45B tokens），从 Think SFT 热启动实际上是以零额外基础训练成本继承了一个更强的初始点，+3.3 点的平均提升是纯粹的"免费午餐"。


###### 决策八：去除 GRPO 中的 KL 损失项和标准差归一化

**替代方案（KL 项）：** 保留标准 PPO/GRPO 的 KL 惩罚项（$\beta_\text{KL} \cdot \text{KL}[\pi_\theta \| \pi_\text{ref}]$）。

**替代方案（Std 归一化）：** 将优势值除以组内标准差 $\sigma$（$A' = (r - \bar{r})/\sigma$）。

**论文是否对比：** 是。Section §4.4.1 分析了这两个设计选择的理论动机。Dr GRPO（Liu et al., 2025b）在此基础上的去除实验表明 std 归一化会引入难度偏差。

**核心 trade-off：**
- KL 损失的目标是防止策略偏离 SFT checkpoint 过远。但 OlmoRL 通过非对称 clip（$\varepsilon_\text{high} = 0.272$）和 TIS cap（$\rho = 2.0$）已经隐式控制了更新步长，额外的 KL 项会过度限制推理任务中模型的"探索空间"，对 AIME 等需要大幅超越 SFT 能力的任务尤为不利。
- Std 归一化：当一道题只有 1/8 的 rollout 答对时，组内奖励方差大，归一化后梯度信号被放大；当一道题 7/8 都答对时，方差小，信号被缩小。这在概念上是合理的（"难题学得多"），但实际上会使不同难度的题目在梯度上获得不一致的影响力，且对极端情况（全对/全错的简单/极难题）表现异常。去除归一化后，梯度自然按难度分布。

**为何本文选择优于替代方案：** 这两个去除操作共同使 OlmoRL 成为一个"约束更少的策略优化器"，在已有 clip 机制保障稳定性的前提下，给予模型更大的学习自由度，对 AIME 2025 这类极难任务的提升（SFT 66.2% → 最终 78.1%）印证了这一判断。

##### 易混淆点

**易混淆点一：OLMo 3 的"全开放"等于"训练数据完全公开"**

❌ 错误理解：OLMo 3 的全开放意味着可以用完全相同的数据从零复现训练，与闭源模型的本质区别只是"代码开源"。

✅ 正确理解："全开放"在 OLMo 3 中有明确的技术含义：训练数据（Dolma 3 + Dolmino + Longmino 所有子集的下载链接）、训练代码（olmo-core、open-instruct、dolma3 四个仓库）、所有中间检查点（Stage 1/Stage 2/Stage 3 checkpoint 以及 SFT/DPO/RL 的各阶段权重）均公开。这与仅公开最终权重（如 Llama 3.1）或仅公开代码（如部分研究模型）有本质区别。实践上，重现仍需 ~$2.75M 的 H100 算力（OLMo 3.1 Think 32B 总训练成本），"可复现"≠"人人能重跑"。


**易混淆点二：Think 系列和 Instruct 系列是两个独立的微调流程**

❌ 错误理解：OLMo 3 Think 和 OLMo 3 Instruct 分别从 Base 模型独立做 SFT，两者没有参数依赖关系。

✅ 正确理解：Instruct 系列并非从 Base 出发，而是以 Think SFT checkpoint 作为初始化（Figure 2 中有明确流向）。具体路径为：Base → Think SFT（45B tokens）→ 分叉：（1）Think 路线继续做 Think DPO → OlmoRL → Think Final；（2）Instruct 路线在 Think SFT checkpoint 上做 Instruct SFT（3.4M tokens）→ Instruct DPO → OlmoRL → Instruct Final。因此 Instruct 模型"天生"继承了 Think SFT 积累的推理知识，仅用 3.4M tokens 的指令数据来调整输出风格，这也是 Instruct 模型数学能力远超 OLMo 2 Instruct 的关键原因（Table 25：AIME 2024 从 4.6% 提升到 67.8%）。


**易混淆点三：OlmoRL 和标准 GRPO 的区别只是工程优化**

❌ 错误理解：OlmoRL 相比 GRPO 的改进主要是吞吐量（连续批处理），算法本身与 GRPO 相同。

✅ 正确理解：OlmoRL 在算法层面做了四项独立改变，每项都有对应文献支撑：（1）**非对称裁剪**（$\varepsilon_\text{low}=0.2, \varepsilon_\text{high}=0.272$）：来自 DAPO，允许高奖励 token 获得更大梯度更新，而非标准 PPO 的对称裁剪；（2）**去除 KL 损失**：减少对 SFT checkpoint 的过度约束；（3）**去除优势方差归一化**：来自 Dr GRPO，消除难度偏差；（4）**截断重要性采样（TIS cap $\rho$）**：处理异步更新导致的 actor/learner 策略分布偏移。工程层面的连续批处理和飞行更新则带来 3.4× 吞吐量提升（Table 23：881→2,949 tokens/s），这是使得 21 天 RL 扩展训练可行的基础设施前提，而非可选优化。两个维度（算法 + 基础设施）共同构成了 OlmoRL 相对于标准 GRPO 的改进。


**易混淆点四：中训练阶段的思维链数据使模型"变成"推理模型**

❌ 错误理解：OLMo 3 Base 在中训练阶段混入了大量推理链数据（QWQ、Gemini reasoning traces 等），因此 Base 模型本身已经具备了 Think 系列的推理能力，后训练只是微调风格。

✅ 正确理解：中训练中的推理链数据（约 7.73B tokens，占 Dolmino Mix 的约 8%）的目的是为 Base 模型注入"如何写推理过程"的语言模式，使后续 SFT 阶段的学习效率更高（论文称为"warm-start"）。Table 10 显示加入推理链后 Base 模型在 Math 上只提升 +5.6 点（43.1→48.7），距离 Think 系列的 MATH 96.2% 还有巨大差距。真正的推理能力提升来自于 Think SFT（45B tokens 高质量推理数据）+ DPO（Delta Learning 偏好对）+ OlmoRL（750步 RLVR）的完整后训练流程。中训练只是"打地基"，而非"建完大楼"。

#### 实验与归因 (Experiments & Attribution)

##### 对比表格

**表 A：OLMo 3.1 Think 32B 在后训练评测集的完整基准对比（Table 1）**

| 任务 | OLMo 3.1 32B Think | OLMo 2 32B Inst | Apertus 70B Inst | LLM360 K2-V2 70B | Qwen 3 32B | Qwen 3 VL 32B Think | Qwen 2.5 32B | Gemma 3 27B | Gemma 2 27B | DS-R1 32B |
|---|---|---|---|---|---|---|---|---|---|---|
| **数学** | | | | | | | | | | |
| MATH | 96.2 | 49.2 | 36.2 | 94.5 | 95.4 | 96.7 | 80.2 | 87.4 | 51.5 | 92.6 |
| AIME 2024 | 80.6 | 4.6 | 0.3 | 78.4 | 80.8 | 86.3 | 15.7 | 28.9 | 4.7 | 70.3 |
| AIME 2025 | 78.1 | 0.9 | 0.1 | 70.3 | 70.9 | 78.8 | 13.4 | 22.9 | 0.9 | 56.3 |
| OMEGA | 53.4 | 9.8 | 5.6 | 46.1 | 47.7 | 50.8 | 19.2 | 24.0 | 9.1 | 38.9 |
| **推理** | | | | | | | | | | |
| BigBenchHard | 88.6 | 65.6 | 57.0 | 87.6 | 90.6 | 91.1 | 80.9 | 82.4 | 66.0 | 89.7 |
| ZebraLogic | 80.1 | 13.3 | 9.0 | 79.2 | 88.3 | 96.1 | 24.1 | 24.8 | 17.2 | 69.4 |
| AGI Eval English | 89.2 | 68.4 | 61.7 | 89.6 | 90.0 | 92.2 | 78.9 | 76.9 | 70.9 | 88.1 |
| **编码** | | | | | | | | | | |
| HumanEvalPlus | 91.5 | 44.4 | 42.9 | 88.0 | 91.2 | 90.6 | 82.6 | 79.2 | 67.5 | 92.3 |
| MBPP+ | 68.3 | 49.0 | 45.8 | 66.0 | 70.6 | 66.2 | 66.6 | 65.7 | 61.2 | 70.1 |
| LiveCodeBench v3 | 83.3 | 10.6 | 9.7 | 78.4 | 90.2 | 84.8 | 49.9 | 39.0 | 28.7 | 79.5 |
| **指令跟随** | | | | | | | | | | |
| IFEval | 93.8 | 85.8 | 70.4 | 68.7 | 86.5 | 85.5 | 81.9 | 85.4 | 62.1 | 78.7 |
| IFBench | 68.1 | 36.4 | 26.0 | 46.3 | 37.3 | 55.1 | 36.7 | 31.3 | 27.8 | 23.8 |
| **知识与问答** | | | | | | | | | | |
| MMLU | 86.4 | 77.1 | 70.2 | 88.4 | 88.8 | 90.1 | 84.6 | 74.6 | 76.1 | 88.0 |
| PopQA | 30.9 | 37.2 | 33.6 | 32.2 | 30.7 | 32.2 | 28.0 | 30.2 | 30.4 | 26.7 |
| GPQA | 57.5 | 36.4 | 27.9 | 64.0 | 67.3 | 67.4 | 44.6 | 45.0 | 39.9 | 61.8 |
| **对话** | | | | | | | | | | |
| AlpacaEval 2 LC | 69.1 | 38.0 | 19.9 | - | 75.6 | 80.9 | 81.9 | 65.5 | 39.8 | 26.2 |

**关键发现：** OLMo 3.1 Think 32B 在 AIME 2025（78.1%）和 OMEGA（53.4%）上超越 DS-R1 32B（56.3% / 38.9%）和 Qwen 3 32B（70.9% / 47.7%），证明全开放模型在最难数学竞赛题上已达到开放权重模型的顶尖水准。IFBench 上 OLMo 3.1 Think 32B 以 68.1% 大幅领先所有基线（第二名 Qwen 3 VL 32B Think 为 55.1%），体现了 OlmoRL Instruct 阶段专门训练指令跟随能力的效果。PopQA 是唯一弱于 OLMo 2 的指标（30.9 vs. 37.2），说明推理强化导致部分事实性知识回忆能力下降。


**表 B：OLMo 3 Base 32B 全面基准对比（Table 2，OlmoBaseEval Main）**

| 指标 | Olmo 3 32B | Marin 32B | Apertus 70B | Gaperon 24B | K2V2 70B | OLMo 2 32B | Qwen 2.5 32B | Gemma 3 27B | Mistral 3.1 24B | Seed 36B | Gemma 2 27B | Llama 3.1 70B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| OlmoBaseEval Math | 61.9 | 49.3 | 39.7 | 20.7 | 46.2 | 53.9 | 64.7 | 63.2 | 59.5 | 15.3 | 57.5 | 62.0 |
| GSM8k | 80.6 | 69.1 | 63.0 | 33.3 | 66.7 | 77.6 | 81.1 | 81.3 | 79.3 | 26.9 | 76.3 | 81.2 |
| GSM Symbolic | 61.2 | 42.0 | 38.6 | 14.5 | 44.4 | 53.1 | 56.2 | 61.2 | 59.1 | 10.3 | 57.3 | 64.6 |
| MATH | 43.8 | 36.8 | 17.4 | 14.2 | 27.4 | 31.0 | 56.7 | 47.0 | 40.1 | 8.7 | 38.8 | 40.2 |
| OlmoBaseEval Code | 39.7 | 30.8 | 23.3 | 19.4 | 35.2 | 20.5 | 48.3 | 41.6 | 42.4 | 54.9 | 41.0 | 36.3 |
| BigCodeBench | 43.7 | 34.5 | 24.0 | 17.0 | 39.8 | 22.2 | 48.1 | 44.0 | 46.4 | 50.7 | 43.4 | 43.4 |
| HumanEval | 65.8 | 52.3 | 32.5 | 31.2 | 51.2 | 29.4 | 65.6 | 62.1 | 65.5 | 71.3 | 57.5 | 57.4 |
| DS 1000 | 29.4 | 26.3 | 17.8 | 11.0 | 25.4 | 20.4 | 43.3 | 34.3 | 36.3 | 44.0 | 29.7 | 29.5 |
| MBPP | 59.6 | 52.1 | 37.6 | 36.7 | 53.5 | 37.1 | 69.8 | 60.0 | 61.9 | 72.0 | 61.7 | 55.5 |
| OlmoBaseEval MC STEM | 74.5 | 75.9 | 70.0 | 56.2 | 75.6 | 75.3 | 82.2 | 80.2 | 81.5 | 83.4 | 75.6 | 80.1 |
| ARC MC | 94.7 | 93.4 | 90.7 | 72.7 | 93.0 | 94.4 | 97.0 | 95.8 | 96.2 | 97.3 | 94.1 | 95.2 |
| MMLU STEM | 70.8 | 68.4 | 57.8 | 45.3 | 64.7 | 64.7 | 79.7 | 74.9 | 76.1 | 82.8 | 65.8 | 70.0 |
| OlmoBaseEval MC Non-STEM | 85.6 | 84.5 | 78.5 | 64.1 | 83.5 | 84.2 | 89.3 | 86.7 | 87.9 | 89.0 | 83.2 | 86.1 |
| MMLU Humanities | 78.3 | 78.9 | 74.1 | 56.7 | 79.3 | 79.7 | 85.0 | 80.5 | 82.7 | 85.7 | 79.3 | 83.4 |
| MMLU Social Sci. | 84.0 | 83.7 | 79.2 | 58.9 | 84.9 | 84.5 | 88.4 | 86.2 | 88.6 | 90.1 | 85.8 | 87.4 |
| CoQA MC | 96.4 | 93.9 | 87.5 | 67.3 | 92.0 | 94.4 | 96.8 | 95.8 | 94.9 | 96.9 | 94.3 | 95.1 |
| DROP MC | 87.2 | 71.0 | 56.5 | 48.0 | 64.8 | 68.6 | 86.6 | 84.6 | 86.5 | 90.1 | 66.6 | 70.3 |
| OlmoBaseEval GenQA | 79.8 | 80.3 | 75.0 | 65.3 | 77.1 | 79.1 | 68.5 | 73.5 | 78.0 | 76.0 | 72.9 | 81.6 |
| **HeldOut** | | | | | | | | | | | | |
| LBPP | 21.8 | 17.3 | 8.1 | 4.3 | 13.4 | 8.2 | 40.3 | 17.7 | 30.3 | 42.6 | 19.7 | 11.8 |
| BBH | 77.6 | 70.1 | 58.8 | 36.6 | 73.2 | 64.6 | 81.1 | 77.4 | 81.4 | 85.0 | 74.8 | 80.8 |
| MMLU Pro MC | 49.7 | 48.1 | 39.6 | 21.3 | 45.3 | 46.9 | 61.1 | 53.1 | 58.9 | 62.2 | 47.6 | 50.4 |
| Deepmind Math | 29.6 | 26.7 | 20.1 | 28.3 | 32.5 | 22.0 | 40.7 | 30.4 | 35.3 | 31.3 | 27.6 | 40.2 |

**关键发现：** OLMo 3 Base 32B 以 5.5T tokens 的预训练量在 OlmoBaseEval Math（61.9）和 Code（39.7）上超越了 Apertus 70B（训练量 15T tokens，Math 39.7 / Code 23.3），证明数据质量和混合策略对计算效率的提升超过了规模扩展。在 LBPP（21.8）上也大幅超过 OLMo 2 32B（8.2），证明中训练阶段代码数据的有效性。


**表 C：OLMo 3 Think 32B 后训练各阶段进展对比（Table 14）**

| 任务 | Think SFT | Think DPO | Think 3.0 Final | Think 3.1 Final | Qwen 3 32B | Qwen 3 VL 32B Think | DS-R1 32B | K2-V2 70B |
|---|---|---|---|---|---|---|---|---|
| MATH | 95.6 | 95.9 | 96.1 | 96.2 | 95.4 | 96.7 | 92.6 | 94.5 |
| AIME 2024 | 73.5 | 76.0 | 76.8 | 80.6 | 80.8 | 86.3 | 70.3 | 78.4 |
| AIME 2025 | 66.2 | 70.7 | 72.5 | 78.1 | 70.9 | 78.8 | 56.3 | 70.3 |
| OMEGA | 43.1 | 45.2 | 50.6 | 53.4 | 47.7 | 50.8 | 38.9 | 46.1 |
| BigBenchHard | 88.8 | 89.1 | 89.8 | 88.6 | 90.6 | 91.1 | 89.7 | 87.6 |
| ZebraLogic | 70.5 | 74.5 | 76.0 | 80.1 | 88.3 | 96.1 | 69.4 | 79.2 |
| HumanEvalPlus | 90.0 | 91.6 | 91.4 | 91.5 | 91.2 | 90.6 | 92.3 | 88.0 |
| LiveCodeBench v3 | 75.8 | 81.9 | 83.5 | 83.3 | 90.2 | 84.8 | 79.5 | 78.4 |
| IFEval | 83.9 | 80.6 | 89.0 | 93.8 | 86.5 | 85.5 | 78.7 | 68.7 |
| IFBench | 37.0 | 34.4 | 47.6 | 68.1 | 37.3 | 55.1 | 23.8 | 46.3 |
| MMLU | 85.3 | 85.2 | 85.4 | 86.4 | 88.8 | 90.1 | 88.0 | 88.4 |
| GPQA | 55.7 | 57.6 | 58.1 | 56.7 | 67.3 | 67.4 | 61.8 | 64.0 |
| AlpacaEval 2 LC | 69.1 | 78.6 | 74.2 | 69.1 | 75.6 | 80.9 | 26.2 | - |
| Safety | 64.8 | 65.3 | 68.8 | 83.6 | 69.0 | 82.7 | 63.6 | 88.5 |

**关键发现：** AIME 2025 从 SFT（66.2%）→ DPO（70.7%）→ OLMo 3.0 RL（72.5%）→ OLMo 3.1 扩展 RL（78.1%），每一阶段均有稳定提升，且扩展 RL 阶段（+5.6%）贡献最大。IFBench 从 DPO（34.4%）→ OLMo 3.0（47.6%）→ OLMo 3.1（68.1%）的跳跃提升主要来自于 Instruct 路线 RL 阶段专项强化指令跟随能力后的知识共享。


**表 D：OLMo 3.1 32B Instruct 后训练各阶段对比（Table 25）**

| 任务 | SFT | DPO | Final Instruct 3.1 | Apertus 70B | Qwen 3 32B (No Think) | Qwen 3 VL 32B Inst | Qwen 2.5 32B | Gemma 3 27B | OLMo 2 32B |
|---|---|---|---|---|---|---|---|---|---|
| MATH | 74.4 | 86.6 | 93.4 | 36.2 | 84.3 | 95.1 | 80.2 | 87.4 | 49.2 |
| AIME 2024 | 12.7 | 35.2 | 67.8 | 0.31 | 27.9 | 75.4 | 15.7 | 28.9 | 4.6 |
| AIME 2025 | 8.2 | 23.3 | 57.9 | 0.1 | 21.3 | 64.2 | 13.4 | 22.9 | 0.9 |
| BigBenchHard | 69.0 | 82.1 | 84.0 | 57.0 | 80.4 | 89.0 | 80.9 | 82.4 | 65.6 |
| ZebraLogic | 30.6 | 51.1 | 61.7 | 9.0 | 28.4 | 86.7 | 24.1 | 24.8 | 13.3 |
| HumanEvalPlus | 80.8 | 85.7 | 86.7 | 42.9 | 83.9 | 89.3 | 82.6 | 79.2 | 44.4 |
| LiveCodeBench v3 | 35.4 | 49.6 | 54.7 | 9.7 | 57.5 | 70.2 | 49.9 | 39.0 | 10.6 |
| IFEval | 87.7 | 87.3 | 88.8 | 70.4 | 87.5 | 88.1 | 81.9 | 85.4 | 85.8 |
| IFBench | 29.7 | 36.3 | 39.7 | 26.0 | 31.3 | 37.2 | 36.7 | 31.3 | 36.4 |
| MMLU | 79.0 | 81.9 | 80.9 | 70.2 | 85.8 | 88.7 | 84.6 | 74.6 | 77.1 |
| AlpacaEval 2 LC | 42.2 | 69.7 | 59.8 | 19.9 | 67.9 | 84.3 | 81.9 | 65.5 | 38.0 |
| LitQA2 | 47.6 | 53.3 | 55.6 | - | 46.7 | 32.0 | 26.2 | - | - |
| BFCL | 57.0 | 58.6 | 58.8 | - | 63.1 | 66.3 | 62.8 | - | - |
| Safety | 92.1 | 88.9 | 89.5 | 77.1 | 81.6 | 85.8 | 82.2 | 68.8 | 84.2 |

**关键发现：** DPO 阶段是 Instruct 路线数学能力的最大贡献者——AIME 2024 从 SFT（12.7%）跳至 DPO（35.2%），增幅 +22.5%，远超后续 RL 的增量（35.2%→67.8%，+32.6% 绝对值但更多是 RL 对难题的特化训练）。LitQA2（55.6%）大幅超越 Qwen 3 32B（46.7%）和 Qwen 2.5 32B（26.2%），体现了 olmOCR 科学 PDF 数据对文献理解能力的持续性贡献。


**表 E：OLMo 3 Think 7B 后训练各阶段 vs. 同量级基线（Table 15）**

| 任务 | SFT | DPO | Final Think | OpenThinker3 7B | Nemotron Nano 9B v2 | DS-R1 Qwen 7B | Qwen 3 8B | Qwen 3 VL 8B Think | OR Nemotron 7B |
|---|---|---|---|---|---|---|---|---|---|
| MATH | 94.4 | 92.4 | 95.1 | 94.5 | 94.4 | 87.9 | 95.1 | 95.2 | 94.6 |
| AIME 2024 | 69.6 | 74.6 | 71.6 | 67.7 | 72.1 | 54.9 | 74.0 | 70.9 | 77.0 |
| AIME 2025 | 57.6 | 62.7 | 64.6 | 57.2 | 58.9 | 40.2 | 67.8 | 61.5 | 73.1 |
| OMEGA | 37.8 | 40.5 | 45.0 | 38.4 | 42.4 | 28.5 | 43.4 | 38.1 | 43.2 |
| BigBenchHard | 84.1 | 83.7 | 86.6 | 77.1 | 86.2 | 73.5 | 84.4 | 86.8 | 81.3 |
| ZebraLogic | 57.9 | 60.6 | 66.5 | 34.9 | 60.8 | 26.1 | 85.2 | 91.2 | 22.4 |
| AGI Eval English | 77.2 | 79.1 | 81.5 | 78.6 | 83.1 | 69.5 | 87.0 | 90.1 | 81.4 |
| HumanEvalPlus | 88.2 | 91.4 | 89.9 | 87.4 | 89.7 | 83.0 | 80.2 | 83.7 | 89.7 |
| MBPP+ | 63.2 | 63.0 | 64.7 | 61.4 | 66.1 | 63.5 | 69.1 | 63.0 | 61.2 |
| LiveCodeBench v3 | 67.8 | 75.1 | 75.2 | 68.0 | 83.4 | 58.8 | 86.2 | 85.5 | 82.3 |
| IFEval | 77.9 | 75.9 | 88.2 | 51.7 | 86.0 | 59.6 | 87.4 | 85.5 | 42.5 |
| IFBench | 30.0 | 28.3 | 41.6 | 23.0 | 34.6 | 16.7 | 37.1 | 40.4 | 23.4 |
| MMLU | 74.9 | 74.8 | 77.8 | 77.4 | 84.3 | 67.9 | 85.4 | 86.5 | 80.7 |
| GPQA | 45.8 | 48.6 | 46.2 | 47.6 | 56.2 | 54.4 | 57.7 | 61.5 | 56.6 |
| AlpacaEval 2 LC | 43.9 | 50.6 | 52.1 | 24.0 | 58.0 | 7.7 | 60.5 | 73.5 | 8.6 |
| Safety | 65.8 | 67.7 | 70.7 | 31.6 | 72.1 | 54.0 | 68.3 | 82.9 | 30.3 |

**关键发现：** OLMo 3 Think 7B Final 在 MATH（95.1%）和 IFBench（41.6）上超越 DS-R1 Qwen 7B（87.9% / 16.7）并与 Qwen 3 8B 竞争，证明 7B 规模同样受益于 Think SFT → DPO → OlmoRL 完整流程。DPO 阶段对 AIME 2024 的提升（69.6→74.6）比 Think 阶段更大，体现 Delta Learning 偏好对在小规模模型上的有效性。


**表 F：OLMo 3 7B Instruct 后训练各阶段 vs. 基线（Table 26）**

| 任务 | SFT | DPO | Final Instruct | Qwen 3 8B | Qwen 3 VL 8B Inst | Qwen 2.5 7B | OLMo 2 7B Inst | Apertus 8B Inst | Granite 3.3 8B Inst |
|---|---|---|---|---|---|---|---|---|---|
| MATH | 65.1 | 79.6 | 87.3 | 82.3 | 91.6 | 71.0 | 30.1 | 21.9 | 67.3 |
| AIME 2024 | 6.7 | 23.5 | 44.3 | 26.2 | 55.1 | 11.3 | 1.3 | 0.5 | 7.3 |
| AIME 2025 | 7.2 | 20.4 | 32.5 | 21.7 | 43.3 | 6.3 | 0.4 | 0.2 | 6.3 |
| OMEGA | 14.4 | 22.8 | 28.9 | 20.5 | 32.3 | 13.7 | 5.2 | 5.0 | 10.7 |
| BigBenchHard | 51.0 | 69.3 | 71.2 | 73.7 | 85.6 | 68.8 | 43.8 | 42.2 | 61.2 |
| ZebraLogic | 18.0 | 28.4 | 32.9 | 25.4 | 64.3 | 10.7 | 5.3 | 5.3 | 17.6 |
| HumanEvalPlus | 69.8 | 72.9 | 77.2 | 79.8 | 82.9 | 74.9 | 25.8 | 34.4 | 64.0 |
| MBPP+ | 56.5 | 55.9 | 60.2 | 64.4 | 66.3 | 62.6 | 40.7 | 42.1 | 54.0 |
| LiveCodeBench v3 | 20.0 | 18.8 | 29.5 | 53.2 | 55.9 | 34.5 | 7.2 | 7.8 | 11.5 |
| IFEval | 81.7 | 82.0 | 85.6 | 86.3 | 87.8 | 73.4 | 72.2 | 71.4 | 77.5 |
| IFBench | 27.4 | 29.3 | 32.3 | 29.3 | 34.0 | 28.4 | 26.7 | 22.1 | 22.3 |
| MMLU | 67.1 | 69.1 | 69.1 | 80.4 | 83.6 | 77.2 | 61.6 | 62.7 | 63.5 |
| AlpacaEval 2 LC | 21.8 | 43.3 | 40.9 | 49.8 | 73.5 | 23.0 | 18.3 | 8.1 | 28.6 |
| Safety | 89.5 | 89.9 | 87.6 | 78.4 | 77.7 | 73.4 | 91.1 | 71.1 | 74.3 |

**关键发现：** OLMo 3 Instruct 7B Final 在 AIME 2024（44.3%）远超所有同量级非 think 基线（OLMo 2 1.3%，Qwen 2.5 7B 11.3%），验证 Think SFT 热启动对 Instruct 路线的核心价值。DPO 阶段（6.7→23.5）对 AIME 2024 的贡献（+16.8pp）超过 SFT 本身，这是 Delta Learning 策略的直接体现。


**表 G：OLMo 3 Base 7B vs. 7B/8B 量级 Base 模型（Table 3，OlmoBaseEval Main）**

| 指标 | Olmo 3 7B | Marin 8B | Apertus 8B | Gaperon 8B | OLMo 2 7B | Qwen3 8B | Nemo. Nano 9B | Gemma 2 9B | Qwen 2.5 7B | Llama 3.1 8B | Granite 3.3 8B | MiMo 7B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| OlmoBaseEval Math | 54.7 | 39.6 | 29.2 | 16.9 | 41.7 | 67.2 | 49.8 | 48.8 | 60.7 | 36.9 | 41.5 | 54.3 |
| GSM8k | 75.5 | 60.9 | 48.2 | 30.0 | 67.1 | 84.5 | 82.3 | 68.5 | 79.9 | 56.4 | 61.0 | 74.3 |
| MATH | 40.0 | 24.3 | 13.1 | 8.2 | 19.1 | 51.6 | 4.5 | 32.9 | 45.9 | 19.2 | 27.9 | 35.2 |
| OlmoBaseEval Code | 30.7 | 21.4 | 19.0 | 16.1 | 10.4 | 46.1 | 43.1 | 30.2 | 41.0 | 21.2 | 18.0 | 35.7 |
| HumanEval | 49.1 | 31.6 | 21.6 | 24.5 | 16.3 | 71.7 | 71.7 | 40.0 | 66.1 | 40.4 | 0.0 | 57.0 |
| MBPP | 43.6 | 36.5 | 33.5 | 29.3 | 21.2 | 66.2 | 62.3 | 49.1 | 55.4 | 12.1 | 48.5 | 48.3 |
| OlmoBaseEval MC STEM | 66.4 | 68.1 | 66.3 | 58.0 | 64.6 | 78.8 | 73.5 | 72.8 | 74.7 | 69.0 | 65.0 | 71.6 |
| ARC MC | 89.2 | 89.2 | 87.9 | 77.2 | 85.7 | 95.4 | 94.1 | 92.7 | 93.4 | 86.4 | 86.2 | 91.7 |
| MMLU STEM | 59.7 | 58.1 | 52.4 | 43.1 | 53.2 | 76.7 | 71.1 | 62.8 | 67.6 | 55.7 | 55.6 | 63.5 |
| OlmoBaseEval MC Non-STEM | 78.2 | 78.8 | 74.2 | 65.0 | 75.2 | 84.8 | 81.3 | 81.3 | 82.9 | 76.1 | 76.9 | 80.5 |
| OlmoBaseEval GenQA | 72.5 | 75.9 | 69.0 | 63.3 | 72.4 | 71.1 | 71.8 | 75.6 | 67.5 | 73.1 | 67.8 | 71.4 |
| LBPP (HeldOut) | 17.1 | 5.8 | 7.1 | 4.7 | 3.1 | 25.7 | 31.7 | 12.4 | 22.1 | 9.1 | 18.5 | 21.5 |
| BBH (HeldOut) | 63.5 | 55.6 | 48.1 | 38.4 | 49.6 | 76.5 | 77.0 | 68.8 | 54.7 | 63.0 | 61.5 | 75.1 |
| MMLU Pro MC (HeldOut) | 37.3 | 38.8 | 33.9 | 20.8 | 33.1 | 50.3 | 50.2 | 44.7 | 48.1 | 37.4 | 33.9 | 44.3 |
| Deepmind Math (HeldOut) | 23.7 | 20.2 | 17.1 | 34.1 | 16.2 | 47.7 | 31.4 | 23.0 | 32.8 | 24.1 | 32.2 | 25.4 |

**关键发现：** OLMo 3 Base 7B 在 OlmoBaseEval Math（54.7）上超越 Marin 8B（39.6）和 Apertus 8B（29.2）等更多 token 训练的基线，以 5.93T tokens 超越 Apertus 8B（15T tokens）。LBPP（17.1 vs OLMo 2 7B 3.1）的巨大提升证明代码中训练数据的有效性。


**表 H：长上下文基准——RULER + HELMET（Table 12）**

| 模型 | RULER 4K | RULER 8K | RULER 16K | RULER 32K | RULER 65K | HELMET 8K | HELMET 16K | HELMET 32K | HELMET 65K |
|---|---|---|---|---|---|---|---|---|---|
| **7B 量级** | | | | | | | | | |
| Llama 3.1 8B | 95.56 | 92.76 | 93.13 | 91.43 | 86.88 | 45.00 | 43.48 | 42.44 | 40.18 |
| Qwen 2.5 7B | 94.63 | 90.87 | 88.68 | 87.26 | 67.30 | 49.26 | 46.25 | 42.99 | 30.47 |
| Qwen 3 8B | 95.58 | 94.10 | 93.78 | 90.29 | - | 51.62 | 49.90 | 47.71 | - |
| Nemotron Nano 9B | 95.31 | 93.09 | 91.58 | 89.01 | 85.13 | 41.78 | 42.90 | 41.82 | 41.48 |
| Apertus 8B | 90.47 | 82.48 | 74.43 | 69.05 | 59.89 | 46.09 | 43.71 | 41.26 | 35.12 |
| Olmo 3 7B | 94.89 | 91.21 | 84.14 | 78.79 | 67.96 | 45.66 | 43.62 | 41.15 | 36.80 |
| **32B 量级** | | | | | | | | | |
| Qwen 2.5 32B | 96.03 | 94.52 | 95.07 | 92.67 | 80.73 | 57.61 | 56.06 | 54.01 | 41.73 |
| Gemma 3 27B | 84.48 | 84.20 | 85.36 | 87.06 | 84.59 | 49.37 | 49.92 | 50.31 | 48.60 |
| Mistral Small 3.1 24B | 96.05 | 95.06 | 93.77 | 92.42 | 88.80 | 49.41 | 49.71 | 47.46 | 43.34 |
| Apertus 70B | 91.52 | 84.26 | 80.54 | 76.82 | 60.33 | 44.72 | 44.60 | 41.07 | 35.67 |
| Olmo 3 32B | 96.10 | 94.57 | 90.42 | 86.22 | 79.70 | 52.11 | 49.36 | 48.60 | 43.15 |

**关键发现：** OLMo 3 32B 在 RULER 4K（96.10）和 8K（94.57）上达到所有 32B 量级最高分，超越 Qwen 2.5 32B（96.03 / 94.52）；在 RULER 65K（79.70）仅次于 Gemma 3 27B（84.59）但训练成本显著更低（100B tokens Stage 3 vs Gemma 3 的多阶段长上下文训练）。7B 的 RULER 65K（67.96）弱于 Nemotron Nano 9B（85.13），反映 3/4 SWA 架构在极长序列的固有约束。


**表 I：精确指令跟随能力跨后训练阶段变化（Table 24）**

| 阶段 | 7B IFEval | 7B IFBench | 32B IFEval | 32B IFBench |
|---|---|---|---|---|
| Think SFT | 83.9 | 30.0 | 83.7 | 37.0 |
| Think DPO | 80.6 | 28.3 | 82.3 | 34.4 |
| Think RL | 86.0 | 41.6 | 89.0 / 93.8 (3.1) | 47.6 / 68.1 (3.1) |
| Instruct SFT | 81.7 | 27.4 | 87.7 | 29.7 |
| Instruct DPO | 82.0 | 29.3 | 87.3 | 36.3 |
| Instruct RL | 85.8 | 32.3 | 88.8 | 39.7 |

**关键发现：** DPO 阶段在两个尺度上都略微降低 IF 能力（7B IFEval 83.9→80.6，IFBench 30.0→28.3），说明 Delta Learning 偏好对优化推理能力时对格式约束能力存在短暂干扰。RL 阶段大幅反弹并超越 SFT 基线，IFBench 从 28.3 跳至 41.6（7B）/ 34.4 跳至 68.1（32B Think 3.1），是全流程中 IF 能力提升最大的阶段。


**表 J：OlmoRL 基础设施逐步消融（Table 23）**

| 配置 | 总 tokens (Mtok) | Tokens/秒 | MFU (%) | MBU (%) |
|---|---|---|---|---|
| OLMo 2 基线（静态批处理）| 6.34 | 881 | 0.30 | 12.90 |
| + 连续批处理 | 7.02 | 975 | 0.33 | 14.29 |
| + 优化线程 | 9.77 | 1,358 | 0.46 | 19.89 |
| + 飞行更新（OlmoRL） | 21.23 | 2,949 | 1.01 | 43.21 |

**关键发现：** 飞行更新（inflight updates）单步贡献最大（1,358→2,949 tokens/s，+117%），将 MBU 从 19.89% 提升至 43.21%；三步叠加后总吞吐量提升 3.35×（881→2,949），等价于将 32B Think 21 天 RL 的等效计算时间从 ~70 天压缩到 21 天。


**表 K：Delta Learning vs. 其他 DPO 数据策略对比（Table 21，7B 模型）**

| 模型/设置 | Avg | MMLU | BBH | GPQA | Zebra | AGI | AIME 2025 | AIME 2024 | CHE | LCB | IFEval |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Qwen3 32B（chosen 来源）| 83.2 | 88.8 | 90.6 | 64.7 | 78.2 | 90.2 | 71.0 | 80.3 | 90.9 | 89.6 | 87.4 |
| Qwen3 0.6B（rejected 来源）| 35.1 | 55.8 | 41.5 | 27.2 | 29.8 | 59.2 | 15.2 | 11.2 | 14.8 | 34.4 | 62.3 |
| Dev. 7B SFT checkpoint | 70.3 | 76.1 | 83.9 | 45.1 | 56.5 | 76.4 | 58.8 | 71.0 | 88.1 | 67.0 | 79.7 |
| Cont. SFT on chosen | 64.5 | 72.6 | 80.2 | 40.2 | 49.8 | 73.9 | 52.8 | 61.0 | 83.4 | 55.1 | 76.0 |
| Delta learning (DPO) | 72.9 | 75.5 | 82.8 | 48.4 | 60.9 | 79.7 | 66.3 | 75.7 | 91.5 | 72.6 | 75.2 |

**关键发现：** Delta Learning DPO（72.9 avg）比 SFT checkpoint（70.3）高 2.6 点，且比直接对 chosen 做 SFT（64.5）高 8.4 点——对 chosen 做 SFT 反而导致性能大幅下降，证明选择 DPO 而非 SFT 是关键。AIME 2025 上 Delta Learning（66.3）比 SFT（58.8）高 7.5 点，在最难推理任务上收益最大。


**表 L：预训练/中训练/长上下文各阶段 Base 模型对比（Table 13，OLMo 3 核心路径）**

| 模型 | #Tokens | Math | Code | MC STEM | MC Non-STEM | GenQA | Minerva | MMLU |
|---|---|---|---|---|---|---|---|---|
| OLMo 2 7B Stage 1 | 4T | 12.7 | 7.1 | 61.0 | 70.6 | 68.6 | 5.6 | 59.8 |
| OLMo 2 7B Stage 2 Soup | 4.15T | 41.7 | 10.4 | 64.6 | 75.2 | 72.4 | 19.1 | 63.7 |
| Olmo 3 7B Stage 1 | 5.9T | 23.5 | 19.8 | 64.0 | 71.9 | 68.5 | 12.2 | 62.3 |
| Olmo 3 7B Stage 2 | 6T | 59.8 | 31.9 | 67.2 | 78.2 | 71.3 | 41.4 | 66.9 |
| Olmo 3 7B Stage 3 | 6.05T | 54.4 | 30.6 | 66.4 | 78.2 | 72.5 | 39.8 | 66.9 |
| OLMo 2 32B Stage 1 | 6.5T | 33.2 | 16.0 | 73.0 | 81.7 | 75.8 | 13.6 | 72.3 |
| OLMo 2 32B Stage 2 Soup | 7.1T | 53.9 | 20.5 | 75.3 | 84.2 | 79.1 | 31.0 | 75.0 |
| Olmo 3 32B Stage 1 | 5.5T | 48.4 | 29.8 | 72.3 | 80.6 | 76.1 | 26.7 | 71.7 |
| Olmo 3 32B Stage 2 Ingredient 1 | 5.6T | 66.8 | 38.4 | 74.6 | 85.6 | 78.9 | 46.5 | 75.9 |
| Olmo 3 32B Stage 2 Ingredient 2 | 5.6T | 65.4 | 39.3 | 74.8 | 85.0 | 78.9 | 44.1 | 76.3 |
| Olmo 3 32B Stage 2 Soup | 5.7T | 69.7 | 39.7 | 75.6 | 85.7 | 79.4 | 46.9 | 76.9 |
| Olmo 3 32B Stage 3 | 6.2T | 61.4 | 39.7 | 74.3 | 85.6 | 79.7 | 42.9 | 76.2 |

**关键发现：** 中训练（Stage 2）是 Base 模型能力的最大跃升阶段——7B Math 从 23.5（Stage 1）跳至 59.8（Stage 2），+36.3 点；32B Math 从 48.4 跳至 66.8/65.4（Ingredient 1/2），+18+ 点。Model Soup 在 32B 上使 Math 从 66.8（Ingredient 1 最强）进一步提升至 69.7（+2.9），是低成本的泛化能力增强。Stage 3 长上下文扩展后 Math 略有下降（32B: 69.7→61.4），这是长文本分布注入对数学专项任务的代价，后续通过后训练完全弥补。


**表 M：中训练数据集质量选代——集成测试轮次对比（Table 6）**

| 轮次 | 综合 Avg | MC STEM | MC Non-STEM | GenQA | Math | Code | FIM | SFT Avg |
|---|---|---|---|---|---|---|---|---|
| Round 1 | 49.7 | 64.3 | 75.2 | 68.3 | 47.4 | 23.4 | 28.4 | 35.2 |
| Round 3 | 50.7 | 64.9 | 75.7 | 68.1 | 48.7 | 24.4 | 31.9 | 35.3 |
| Round 5 | 53.1 | 65.3 | 76.1 | 70.8 | 57.1 | 27.7 | 29.4 | 37.3 |

**关键发现：** 每轮集成测试迭代均带来稳定改善——Round 1→5 综合 Avg 从 49.7→53.1（+3.4 点），Math 从 47.4→57.1（+9.7 点），Code 从 23.4→27.7（+4.3 点）。FIM 在 Round 5 略有下降（31.9→29.4），表明数据混合需要在不同能力维度间做帕累托权衡，无法同时最优化所有维度。


**表 N：Think SFT 热启动对 Instruct SFT 的效果（Table 29）**

| 设置 | Avg | BBH | GPQA | MATH | GSM8K | OMEGA | CHE | MBPP | LCB | AE | IFEval |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 不使用 Think SFT（直接从 Base 训练）| 44.5 | 46.5 | 29.7 | 60.3 | 87.6 | 8.6 | 63.8 | 54.1 | 13.0 | 27.0 | 81.0 |
| 使用 Think SFT 热启动 | 47.8 | 46.6 | 34.4 | 65.9 | 91.1 | 12.2 | 68.7 | 57.1 | 17.1 | 27.1 | 84.7 |
| 热启动增益 | +3.3 | +0.1 | +4.7 | +5.6 | +3.5 | +3.6 | +4.9 | +3.0 | +4.1 | +0.1 | +3.7 |

**关键发现：** Think SFT 热启动使 Instruct SFT 平均提升 +3.3 点，GPQA（+4.7）、MATH（+5.6）、CHE（+4.9）等推理类任务收益最大，AlpacaEval（+0.1）和 BBH（+0.1）等对话/推理任务收益最小。这证明 Think SFT 积累的 45B tokens 推理知识可以以几乎零成本（仅 3.4M Instruct SFT tokens）迁移，是"以训练时间换推理能力"的极高性价比方案。


##### 归因排序

按对核心推理能力（AIME 2025 + OMEGA 平均 delta）的贡献排序：

- **OlmoRL 扩展训练（21 天 +224 GPUs）** (+12.5 on AIME 2025, Table 14 OLMo 3.0→3.1)：从 72.5% 到 78.1%，这是单项最大的后训练提升。更多 RL 步数 + 更大 actor 计算允许模型探索更难的数学推理路径。OLMo 3.0 Think 已达到 750 步 RL 的收益极限，扩展到更长 RL 持续改善。

- **DPO Delta Learning**（+11.4 on AIME 2024, Table 25 SFT→DPO）：AIME 2024 从 12.7%→35.2%（Instruct）和 73.5%→76.0%（Think），DPO 阶段通过大模型 chosen vs. 小模型 rejected 的高质量对比信号，大幅改善了模型对验证性推理步骤的偏好。

- **Dolmino Mix 中训练（合成推理链 + 合成数学）**（+5.6 on Math eval, Table 10）：无推理链版 Base Math = 43.1，加入推理链后 = 48.7，+5.6 点。这是基础模型层面的核心改进，为后续 SFT 和 RL 提供了更好的参数初始化。

- **Model Souping（32B）**（+2.9 on Math, Table 13 Soup vs. Ingredient 1）：66.8→69.7（Math），两次独立训练的参数平均使模型落在更平坦的损失盆地，提升了泛化能力，且无推理时额外开销。

- **Think SFT 热启动 Instruct 训练**（+3.3 avg benchmark, Table 29）：从 Think SFT checkpoint 出发比从 Base 出发平均提升 3.3 个基准点，体现了推理知识向通用指令跟随任务的迁移能力。

- **OlmoRL 基础设施改进（连续批处理 + 飞行更新）**（+3.4× 吞吐量, Table 23）：881→2,949 tokens/s 的吞吐量提升不直接体现在评测数字上，但使得 21 天扩展 RL 训练在预算内可行，是间接贡献最大的工程组件。

- **长上下文扩展（Stage 3）**（+5–15 on RULER 32K-65K, Table 12）：Olmo 3 32B 在 RULER 65K 上达到 79.70，高于 Apertus 70B（60.33）和 Qwen 2.5 32B（80.73），长上下文扩展成本仅 100B tokens（约 1 天 1024 GPUs）但带来了显著的长文本处理能力。

##### 可信度检查

**维度一：去污染（Decontamination）**

OLMo 3 使用了专门开发的 `decon` 工具（github.com/allenai/decon）对训练数据做了 8-gram 匹配去污染，同时在评测集选择上明确标注哪些集合是"held-out"（Table 16 中带 * 的任务如 AIME 2024、AIME 2025、MBPP+、LiveCodeBench v3、ZebraLogic、GPQA、AGI Eval 等是专门的保留集）。Table 2 和 Table 3 区分了 "OlmoBaseEval Main" 和 "HeldOut" 两个分区，Base 模型在 BBH（77.6）和 MMLU Pro MC（49.7）等 held-out 集上的表现与 Main 集相当，未出现 held-out 集异常低的情况，表明训练数据去污染有效。但 AIME 题目数量有限（AIME 2024 仅 30 题，AIME 2025 亦然），32 次采样平均后的方差仍较高，单次评估的置信区间约 ±3-5%。

**维度二：Baseline 公平性**

论文在 Base 模型对比（Table 2/3）中将 Olmo 3 32B 与 Apertus 70B（15T tokens）、Marin 32B（12.7T tokens）相比，但 Olmo 3 32B 只训练了 5.5T+100B≈5.6T tokens，计算量约为对手的 40%–44%。论文对此透明地列出了各模型的 token 数（Table 13），但主表格中未在标题行注明这一差异，读者需要自行对比 Table 13 才能理解这一不对等性。后训练对比（Table 1）中，Qwen 3 32B 是一个强竞争对手但其训练数据完全不公开，无法核实基础训练质量；LLM360 K2-V2 是 70B 模型与 32B 的 Olmo 3 对比，存在规模不匹配。这些非对等比较在论文中均有文字说明，但集中在主表格时容易被忽视。

**维度三：未报告的负面结果**

论文在 Section §4.4.3 提到 RL 训练过程出现了"至少 1 天的不稳定性（instability）"，但未详细分析导致不稳定的原因和解决方案。PopQA 指标在后训练后明显退化（OLMo 3.1 Think 32B 仅 30.9，低于 OLMo 2 32B Instruct 的 37.2），这一知识回忆能力的"遗忘"问题在论文中虽然出现在表格中但未作专项分析。GPQA（57.5%）显著低于 Qwen 3 32B（67.3%）和 DS-R1 32B（61.8%），论文未对此差距给出专项解释。RL-Zero（从 Base 直接做 RL）实验仅在 7B 规模进行，未扩展到 32B，推测是 32B RL-Zero 成本过高，但论文未说明为何不做 32B RL-Zero 对比。


#### 动机与第一性原理

##### 痛点 (The Gap)

在 OLMo 3 出现之前，AI 研究社区面临一个深层矛盾：最强的开源模型（Qwen 3、Gemma 3、DeepSeek-R1）以"开放权重"（open-weight）的形式发布——即只公布最终检查点，但预训练数据、中间检查点、训练配方全部不透明。这造成了一个无法自证清白的黑箱：当某个模型在 AIME 上刷新记录，社区无法判断这是真实推理能力提升，还是 mid-training 数据集中就包含了评测答案（Shao et al., 2025b；Wu et al., 2025c）——所谓"spurious rewards as effective as true reward"。

具体而言，前代 OLMo 2 32B 在 AIME 2024 仅得 4.6 分，在 MATH 仅 49.2 分，跟 Qwen 2.5 32B（分别 15.7 和 80.2）差距悬殊，更遑论 DeepSeek-R1 32B（70.3 和 92.6）。差距来自三个层面：①预训练数据缺乏数学和代码增强；②没有 long-context 能力（OLMo 2 不支持 65K token）；③后训练缺少有效的推理链 SFT + 对比学习 + RLVR 完整流水线。而其他试图填补这一空白的全开放模型——Stanford Marin、Apertus——虽公开了数据配方，但在性能上均落后于同量级的闭源配方模型。

##### 核心洞察 (Key Insight)

作者发现了一条被业界集体忽视的因果链：

**Because** 语言模型的最终能力 80% 由数据工程决定，而非后训练微调 →  
**Therefore** 在预训练和 mid-training 阶段注入高质量的数学推理痕迹、代码合成数据以及长文档 →  
**Therefore** base model 本身就具备更强的推理潜力，后训练只需放大这一潜力而非从零建立 →  
**Therefore** 即使在后训练 token 量少于竞品 6 倍的情况下，也能达到可比甚至更强的性能（OLMo 3.1 Think 32B 在 AIME 2024 达到 80.6，Qwen 3 32B 为 80.8，而 Qwen 3 用了约 6 倍的后训练 token）。

与此并行的第二条洞察：**preference tuning 不是 alignment 工具，而是能力扩展工具**。当 SFT 在 Qwen3 32B 生成的 thinking trace 上继续训练已出现收益递减（further SFT actively hurts performance），作者引入 Delta Learning 原则——把"已饱和"的 Qwen3 32B 完成作为 chosen，配上 Qwen3 0.6B 的劣质回答作为 rejected，人为制造最大化的能力落差（delta），从而让 DPO 从对比中提取出 SFT 无法传递的隐性推理结构。

##### 物理/直觉解释

想象你在培训一名厨师。传统做法（纯 SFT）是让他反复抄写米其林食谱——抄到第 1000 遍后效果不再提升，因为他记住了字面文字，但没学会为什么加盐的时机比分量更重要。Delta Learning 的做法换了一招：不再给他看最好的食谱，而是同时给他看一份米其林菜和一份超市外卖；通过对比"哪里差了、差在哪个步骤"，厨师反而更快内化了高质量烹饪的本质规律。

映射到技术机制：Qwen3 0.6B 的 rejected response 不是随机噪声，而是"在正确方向上但不够深入"的推理路径，chosen 与 rejected 之间的结构性差距（delta）给 DPO 梯度提供了清晰的方向信号，而这个信号在纯 SFT 损失中是被平均掉的。

同理，mid-training 的设计哲学类似于"给面团发酵"：在正式烘焙（后训练）之前，用 100B token 的高质量合成数学、代码和推理轨迹做第二次慢速发酵——等到面团（base model）的内部结构已经形成多孔弹性（推理底层能力），后面的高温烘焙（SFT + DPO + RLVR）才能把它撑开，而不是在一块致密生面团上硬压出形状。如 Figure 2 所示，整个 model flow 正是这一思想的工程化体现：pretraining → midtraining → long-context extension → Think SFT → Think DPO → Think RLVR，每个阶段都在为下一阶段预埋信号。Figure 1 则直观展示了 Olmo 3 与其他全开放模型在 base eval 和 post-train eval 双轴上的全流程比较——OLMo 3 Base 32B 在 base eval 上超过所有同类全开放 base 模型，构成整个能力链条的基石。

#### 专家批判

##### 隐性成本 (Hidden Costs)

论文自述总训练花费约 56 天、1024 块 H100，估算成本 **$2.75M**——但这只是最终 recipe 的执行成本，不含研发过程中的消耗。几个关键数字暗示了真实开销：

1. **Microanneal 迭代成本**：每轮 microanneal 需要 10B token 的专项实验；论文描述了"多轮集成测试"（Round 1 → Round 3 → Round 5），每轮都是全量 100B 中训运行，仅数据选型阶段就相当于跑了超过 **300B 额外 token** 的实验性计算。
2. **Post-training 超参扫描**：SFT 阶段每次学习率 sweep 覆盖 4 个候选值，在 **256 GPU 上并行 36 小时**；DPO sweep 虽然时间短（每次 18 小时），但"在实际运行中由于集群不稳定延续了多天"；RL 阶段的 Olmo 3.1 Think 32B 在发布后继续跑了 **21 天 224 GPU**。这些元数据成本从未进入官方$2.75M 口径。
3. **Decontamination 流水线**：从 252.6B 文档到 38.7B（移除率 **84.9%**），仅 CommonCrawl 过滤就耗费 **~1030 小时的 i4i.32xlarge EC2 实例**。

除了财务成本，还有三类工程隐性成本：
- **Model soup 对随机性的高度敏感**：32B Stage 2 通过两路并行 midtraining 后做权重平均（soup），实验表明 Ingredient 1 和 Ingredient 2 的 Math 分别为 66.8 和 65.4，soup 为 69.7——仅 3 分的优化收益依赖于精确的 soup 比例，而配比超参在论文中并未完整披露。
- **OlmoRL 基础设施的绑定性**：论文报告的 **4x RL 加速**（从 881 tok/s 到 2949 tok/s）依赖于"inflight parameter updates"——即 learner 在 actor rollout 期间同步更新权重。这是一个非标准的异步 RL 架构，最大异步度高达 **8**（32B），意味着用于训练的 policy 和生成 rollout 的 policy 之间存在最多 8 步的梯度漂移，importance sampling cap ρ 能否充分校正这一偏差，论文未提供理论界限。
- **Think → Instruct warm-start 的路径依赖**：Instruct SFT 必须从 Think SFT checkpoint 启动（Table 29 显示平均增益 3.3 点），这意味着 Instruct 和 Think 两条线无法完全并行开发，形成隐性序列依赖，拉长了整体研发周期。

##### 工程落地建议

**最大的坑在数据质量验证闭环**。论文用 microanneal 方法（5B target + 5B web 混合后 anneal 到 10B）快速筛选候选数据集——这在 Allen AI 拥有完整评测基础设施（OlmoBaseEval）时可行，但在业务复现时，大多数团队不具备快速跑 7B 模型并在 20+ 任务维度上稳定评测的能力。若评测系统本身存在 benchmark contamination，microanneal 结论会完全失效。

其次，**Delta Learning 的超参极其敏感**：chosen 来自 Qwen3 32B，rejected 来自 Qwen3 0.6B，这一"32B vs 0.6B"的极端档位差（约 50 倍参数比）是精心设计的结果。如果使用更接近的模型对（如 7B vs 1B），delta 可能不足以突破 SFT 饱和区。业务中复现时，必须先验证 SFT 饱和边界再选择对比模型档位，而不是套用现成比例。

##### 关联思考

OlmoRL 的异步 GRPO 实现与 DeepSpeed-Chat 的同步 PPO 路线形成对比：前者以 importance sampling 换取吞吐量，后者以严格同步保证 on-policy 近似——两者在长推理场景（response length 高达 32K token）下的权衡值得进一步研究。

与 LoRA 的关系值得注意：整个 Olmo 3 后训练链条全程使用全参数微调（full fine-tuning），在 32B 规模上 SFT 需要 256 GPU，DPO 需要 64–128 GPU。如果用 LoRA 替代，参数效率会提升但 model soup 的权重平均策略将失效（LoRA 权重在 adapter 空间，无法直接在全参数空间插值），这是一个尚未被论文讨论的兼容性冲突。

Sliding Window Attention（3/4 层使用 4096 token 窗口）与 YaRN 的组合使得 long-context 扩展（65K）得以在仅 50B–100B token 的快速 stage 3 实现，但这也意味着全注意力层只占 1/4——在需要跨越超长距离的全局推理任务上，性能天花板受到架构约束，这与 Mamba 或全注意力模型的路线形成根本性分歧，在 RULER 65K 上 Olmo 3 7B（67.96）已经明显落后于 Qwen 3 8B（未报告）和 Nemotron Nano 9B（85.13），预示着这一架构选择在极长序列上的代价。
