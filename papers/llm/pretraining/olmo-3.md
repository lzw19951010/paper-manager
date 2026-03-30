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
- Llama 3.1 70B
- Mistral Small 3.1 24B
- DeepSeek R1 Distilled Qwen 32B
- OLMo 2 32B
- Stanford Marin 32B
- Apertus 70B
- LLM360 K2-V2 70B
- Gaperon 24B
- IBM Granite 3.3 8B
- Nemotron Nano 9B
- Xiaomi MiMo 7B
category: llm/pretraining
code_url: https://github.com/allenai/OLMo-core
core_contribution: new-framework/new-method/new-benchmark/empirical-study
datasets:
- Dolma 3 Mix
- Dolma 3 Dolmino Mix
- Dolma 3 Longmino Mix
- Dolci Think SFT/DPO/RL
- Dolci Instruct SFT/DPO/RL
- Dolci RL-Zero
- olmOCR science PDFs
- CommonCrawl
- Stack-Edu
- FineMath
- arXiv Proof-Pile-2
- Wikipedia
- DCLM-Baseline
- OpenHermes-2.5
- UltraChat-200k
- WildChat-1M
date: '2025-12-15'
doi: null
keywords:
- fully-open language model
- model flow
- data curation
- thinking model
- reinforcement learning with verifiable rewards
- long-context extension
- data mixing optimization
- deduplication at scale
- midtraining
- olmOCR
metrics:
- pass@1
- Accuracy
- Bits-per-byte (BPB)
- AlpacaEval 2 LC win rate
- RULER score
- HELMET score
- Signal-to-Noise Ratio (SNR)
- MFU (Model FLOP Utilization)
publication_type: preprint
status: complete
tags:
- open-source LLM
- data curation pipeline
- thinking model
- reinforcement learning
- long-context extension
- multi-stage training
- data mixing optimization
title: Olmo 3
tldr: OLMo 3是一个完全开放的7B/32B语言模型家族，通过全新的数据管线（Dolma 3）、三阶段基座训练、Delta Learning偏好调优和OlmoRL强化学习框架，构建出当前最强的完全开放思维模型，在推理基准上接近Qwen
  3 32B，同时仅使用其1/6的训练token。
url: https://arxiv.org/abs/2512.13961
venue: null
---

## 核心速览 (Executive Summary)

## TL;DR (≤100字)

OLMo 3通过完全开放的三阶段基座训练（预训练5.9T→中训练100B→长上下文扩展100B）配合SFT/DPO/RLVR后训练，构建7B/32B思维模型家族。旗舰模型OLMo 3.1 Think 32B在MATH上达96.2%、AIME 2025达78.1%，是最强完全开放思维模型，接近Qwen 3 32B但仅用1/6 token。

## 一图流 (Mental Model)

如果开源模型是只给你一道成品菜（最终权重），那OLMo 3就是给你完整的厨房——从食材采购清单（Dolma 3数据管线）、刀工技法（去重/混合/上采样工具链）、烹饪过程的每一步温度记录（所有中间checkpoint）到最终成品（Think/Instruct/RL-Zero模型）。你不仅可以品尝成品，还可以在任何环节修改配方重新烹饪。

## 核心机制一句话 (Mechanism in One Line)

**[组合优化]** 多阶段数据课程中的每个阶段 **[对象]** 通过 **[分布式探索+集中式评估]** 的双循环框架 **[方式]** 在质量、多样性和规模间寻找最优数据配比 **[效果]**，使小规模模型的数据决策可靠地迁移到大规模训练。

---

## 动机与第一性原理 (Motivation & First Principles)

## 痛点 (The Gap)

### 1. 开放性缺口
现有的强推理模型（Qwen 3、DeepSeek R1）都是"open-weight"而非"fully-open"——它们只发布最终权重，不公开预训练数据、中间checkpoint或训练配方。这严重阻碍了研究社区对以下问题的研究：
- 预训练数据如何影响RL性能？（因为无法追溯推理链到原始训练数据）
- 中训练数据是否包含评测集导致benchmark污染？
- 不同训练阶段各贡献了什么能力？

### 2. 技术瓶颈
- **OLMo 2的局限**：上下文窗口仅4096 token，缺乏长上下文能力；数学和代码能力落后于Qwen 2.5等模型
- **数据工程瓶颈**：万亿token规模的全局去重缺乏高效工具；数据混合比例优化在数据源不断变化时需要从头重做
- **评估信号不足**：小规模模型在数学、代码等任务上表现为随机水平，难以用于高效的数据决策
- **RL训练效率低**：此前的RLVR训练缺乏跨领域泛化能力，训练速度慢

### 3. 具体Baseline差距
- OLMo 2 32B在MATH上仅49.2%（vs Qwen 2.5 32B的80.2%）
- OLMo 2 32B在HumanEval+上仅44.4%（vs Qwen 2.5的82.6%）
- 完全开放的base model（Marin 32B、Apertus 70B）在代码和数学上远落后于open-weight模型

## 核心洞察 (Key Insight)

**因果链推导：**

1. **Because** 模型能力高度依赖于训练数据的质量和配比（不仅是数量） → **Therefore** 需要精细化数据工程而非简单扩大规模
2. **Because** 数据管线在开发过程中持续演化（新数据源到来、过滤器改进） → **Therefore** 需要"条件混合"(conditional mixing)方法，让新数据增量融入已有最优配比，而非每次从零开始
3. **Because** 小规模模型在难任务上表现为噪声 → **Therefore** 需要proxy metrics（BPB-based Easy suites）来在小计算预算下获得可靠的数据决策信号
4. **Because** midtraining阶段引入思维链和指令数据可以为post-training"预热" → **Therefore** base model不应仅仅是通用语言模型，而应定向地为下游能力铺路
5. **Because** RL从fully-open base model出发可以消除数据泄露的混淆因素 → **Therefore** RL-Zero变体提供了首个干净的RLVR研究基准

## 物理/直觉解释

想象你在调配鸡尾酒：
- **原料选择**（数据源）：你有酒、果汁、冰块等原料，但每种原料的品质参差不齐
- **配比优化**（constrained mixing）：不是随便混合，而是通过大量小杯试饮（30M参数的proxy模型swarm）找到最佳比例
- **品质分层**（quality-aware upsampling）：最好的果汁多放几倍，一般的少放，太差的不要
- **分阶段调制**（三阶段训练）：先打底味（pretraining 5.9T token），再加精华提味（midtraining 100B高质量token），最后加长饮管方便饮用（long-context extension）
- **最后装饰**（post-training）：根据用途不同做最终调整——加伞签（Think=思维链）、加吸管（Instruct=简洁响应）、或纯饮（RL-Zero=直接从base做RL）

关键洞察是：鸡尾酒的品质80%取决于原料配比而非最后的装饰。OLMo 3的大部分创新集中在数据工程上。

---

## 方法详解 (Methodology)

## 直觉版 (Intuitive Walk-through)

### 参考Figure 2：模型流全景图

Figure 2展示了OLMo 3的完整模型流，分为左侧的Base Model Training和右侧的Post-training两大阶段。

**旧方法（OLMo 2）的数据流：**
1. 预训练（4096 context, ~5T tokens, Dolma 2数据）→ 中训练（Dolmino Mix, 主要是数学）→ 直接进入post-training
2. 中训练只关注数学领域，缺乏代码和QA数据
3. 无长上下文扩展阶段
4. 评估套件覆盖面窄（~10个benchmark）

**OLMo 3改了哪里？为什么？**

1. **预训练数据管线革新**（Figure 8）：
   - 新增olmOCR science PDFs（972B tokens）→ 因为学术文档是高质量长文档的天然来源
   - 三阶段去重（精确→模糊→子串）→ 因为去重后才能通过quality-aware upsampling精确控制重复
   - 约束条件下的数据混合优化（Figure 9）→ 因为不同主题的最优配比不是自然分布

2. **中训练大幅扩展**（Figure 11）：
   - 从纯数学扩展到Math+Code+QA+Thinking四个领域
   - 引入"分布式探索+集中式评估"双循环（distributed feedback + centralized integration tests）
   - 有意引入instruction和thinking trace数据为post-training铺路

3. **新增长上下文扩展阶段**（Figure 13）：
   - 利用olmOCR PDFs的天然长文档特性
   - 从8K扩展到65K context window
   - 关键组件：YaRN注意力缩放 + olmOCR PDFs + 合成数据增强 + 文档打包 + 充足token预算

4. **Post-training分化为三条路径**：
   - Think：SFT→DPO（Delta Learning）→RLVR，目标是强推理
   - Instruct：SFT→DPO（含长度控制）→RLVR，目标是简洁高效
   - RL-Zero：直接从Base做RLVR，目标是干净的研究基准

### 用简单例子走一遍差异

假设我们有一个3层网络要处理3篇文档：
- **旧方法（OLMo 2）**：把3篇文档直接混合训练，每篇只看4K token。中训练时只加数学题。评估时用10个benchmark取均值。
- **新方法（OLMo 3）**：先对3篇文档做质量评分和主题分类。最好的那篇重复训练7次，中等的2次，最差的丢弃。训练时扩展到8K token。中训练时除了数学还加入代码题、QA和思维链。评估时用43个benchmark，按能力聚类取6个cluster均值，且先用proxy metric确认小模型的信号可靠。最后扩展到65K context。

## 精确版 (Formal Specification)

### 流程图 (Text-based Flow)

```
Input: Raw Web (252.6B docs) + PDFs (238M docs) + Code + Math + Wiki
    ↓
[Stage 0: Data Pipeline]
    ├─ Web: HTML extraction → Heuristic filtering (→38.8B docs)
    │       → Exact dedup (→12.8B) → Fuzzy dedup (→9.8B) → Substr dedup (→9.7B)
    │       → Topic classification (24 topics) → Quality classification (20 tiers)
    │       → 480 buckets → Quality-aware upsampling → Constrained mixing
    ├─ PDFs: olmOCR extraction → PII filtering → Heuristic filtering (→108M docs)
    │       → Topic classification → Mixing
    ├─ Code: Stack-Edu → Language partitioning → Constrained mixing
    └─ Math/Wiki: FineMath(3+), arXiv LaTeX, Wikipedia
    ↓
    Dolma 3 Mix: 5.93T tokens (76.1% web, 13.6% PDFs, 6.9% code, 2.6% math, 0.9% arXiv, 0.04% wiki)
    ↓
[Stage 1: Pretraining] 8192 ctx, SWA (3/4 layers)
    7B: 5.93T tokens, 512→1024 GPUs, ~44 days
    32B: 5.5T tokens, 512→1024 GPUs, peak LR=6e-4
    ↓
[Stage 2: Midtraining] 100B tokens, linear decay LR
    Dolma 3 Dolmino Mix: Math(19.2%) + Code(20%) + QA(13.9%) + Thinking(7.1%) + ...
    ↓
[Stage 3: Long-context Extension] 50B(7B) or 100B(32B) tokens
    Dolma 3 Longmino Mix: Long PDFs + Synthetic aggregation tasks
    Context: 8K → 65K via YaRN RoPE scaling
    ↓
    Olmo 3 Base (7B/32B, 65K context)
    ↓
[Post-training branches]
    ├─ Think: SFT(Dolci Think SFT) → DPO(Delta Learning) → RLVR(OlmoRL)
    │         → Olmo 3 Think / Olmo 3.1 Think
    ├─ Instruct: SFT(Dolci Instruct SFT) → DPO(+length control) → RLVR
    │         → Olmo 3 Instruct
    └─ RL-Zero: RLVR directly from Base (Math/Code/IF/General/Mix)
             → Olmo 3 RL-Zero
```

### 关键公式与变量

#### 1. Quality-Aware Upsampling

给定质量百分位 $q \in [0, 100]$，上采样因子函数 $f(q)$ 满足：
- $f(q) = 0$ for $q < q_{\text{cutoff}}$（底部40%被丢弃）
- $f(q)$ 单调递增
- $\max(f(q)) = 7$（经验确定的最大重复次数）
- $\int_0^{100} f(q) dq = R_{\text{target}}$（目标token数约束）

其中 $R_{\text{target}}$ 由混合优化确定的目标topic比例和总训练token数共同决定。

**符号物理含义：**
- $q$：文档在其topic内的质量排名百分位（由fastText质量分类器确定）
- $f(q)$：该质量等级的文档在训练中被重复使用的次数
- $q_{\text{cutoff}}$：质量截断阈值，低于此的文档不参与训练
- $R_{\text{target}}$：从该topic桶中提取的目标token总量与桶内总token的比值

#### 2. Constrained Data Mixing（三阶段优化）

**Stage 1: Swarm Construction**
训练N个proxy模型（30M参数，3B tokens），每个使用不同的混合比例 $\mathbf{w}_i \sim \text{Dir}(\alpha \cdot \mathbf{w}_{\text{natural}})$

**Stage 2: Per-task Regression**
对每个任务 $t$，拟合广义线性模型：
$$\text{BPB}_t = g(\mathbf{w}) = \beta_0 + \sum_j \beta_j w_j + \epsilon$$

**Stage 3: Mix Optimization**
$$\mathbf{w}^* = \arg\min_{\mathbf{w}} \frac{1}{|T|} \sum_{t \in T} \widehat{\text{BPB}}_t(\mathbf{w})$$
$$\text{s.t.} \quad \sum_j w_j = 1, \quad w_j \leq w_j^{\max} \quad \forall j$$

其中 $w_j^{\max}$ 由该domain可用token数和最大重复次数（4-7x）确定。

**Conditional Mixing扩展：** 将已优化的mix冻结为单一虚拟domain，仅在新增/修改的domain上重新运行base procedure。

#### 3. Signal-to-Noise Ratio for Benchmark Selection
$$\text{SNR} = \frac{\text{Signal}}{\text{Noise}} = \frac{\text{Var}_{\text{between-models}}(s)}{\text{Var}_{\text{within-model}}(s)}$$

通过评估OLMo 2 13B的最后50个checkpoint和10个外部base model计算。SNR过低（如HumanEval单任务SNR=3.2）的benchmark被从macro-average中移除或通过增大n（pass@k中的k）改善。

### 数值推演 (Numerical Example)

**Quality-Aware Upsampling示例：**

假设一个topic桶有1000个文档，目标是产出3000个文档的训练量（即平均上采样率3x）：
- 质量bottom 40%（400文档）：f(q)=0，全部丢弃
- 质量40-80%（400文档）：f(q)=1，各出现1次 → 400文档
- 质量80-95%（150文档）：f(q)=3，各重复3次 → 450文档
- 质量95-100%（50文档）：f(q)=7，各重复7次 → 350文档
- 总计：0 + 400 + 450 + 350 = 1200文档（需调整参数使积分等于目标值）

**Constrained Mixing示例：**

假设有3个domain（Web、Code、PDF），自然分布为[0.8, 0.1, 0.1]：
1. 训练30M×15个proxy模型（5x domain数），每个用不同的Dirichlet采样比例
2. 评估每个模型在Base Easy上的BPB
3. 拟合回归模型发现：增大Code到0.25和PDF到0.15能最大化综合性能
4. 考虑约束：Code总池只有137B tokens，在6T mix中最多重复7x → w_code_max ≈ 137B×7/6T ≈ 16%
5. 最终优化结果可能是[0.70, 0.15, 0.15]，考虑质量上采样后Web实际使用4.5T tokens

### 伪代码 (Pseudocode)

```python
# === Constrained Data Mixing ===
def constrained_mixing(domains, target_tokens, eval_suite):
    """Swarm-based data mix optimization"""
    n_domains = len(domains)
    n_swarm = 5 * n_domains  # 5x rule of thumb
    
    # Stage 1: Swarm Construction
    natural_weights = [d.tokens / sum(d.tokens for d in domains) for d in domains]
    swarm_results = []
    for i in range(n_swarm):
        w_i = dirichlet_sample(alpha=1.0, center=natural_weights)  # [n_domains]
        proxy_model = train_proxy(arch='30M', tokens=3e9, mix_weights=w_i)
        scores = evaluate(proxy_model, eval_suite)  # {task: BPB}
        swarm_results.append((w_i, scores))
    
    # Stage 2: Per-task Regression
    regressors = {}
    for task in eval_suite.tasks:
        X = [r[0] for r in swarm_results]          # [n_swarm, n_domains]
        y = [r[1][task] for r in swarm_results]     # [n_swarm]
        regressors[task] = fit_glm(X, y)
    
    # Stage 3: Constrained Optimization
    w_max = [min(d.tokens * 7 / target_tokens, 1.0) for d in domains]
    w_star = guided_search(
        objective=lambda w: mean([reg.predict(w) for reg in regressors.values()]),
        constraints={'sum_to_one': True, 'upper_bounds': w_max},
        init=natural_weights
    )
    return w_star  # [n_domains]

# === Conditional Mixing (incremental update) ===
def conditional_mixing(frozen_mix, new_domains, target_tokens, eval_suite):
    """Treat frozen_mix as a single virtual domain, re-optimize over new domains"""
    virtual_domain = Domain(name='frozen', weights=frozen_mix)
    all_domains = [virtual_domain] + new_domains
    return constrained_mixing(all_domains, target_tokens, eval_suite)

# === Quality-Aware Upsampling ===
def quality_aware_upsample(topic_bucket, target_tokens, max_factor=7):
    """Generate upsampling curve for a topic bucket"""
    # topic_bucket: list of (doc, quality_percentile) sorted by quality
    # Organize into 20 vigintile bins (5-percentile intervals)
    bins = partition_into_vigintiles(topic_bucket)  # 20 bins
    
    # Search for parametric curve f(q) satisfying constraints:
    # 1. integral = target_tokens / bucket_total_tokens
    # 2. f(q) <= max_factor
    # 3. f(q) monotonically increasing
    curve = fit_upsampling_curve(
        target_integral=target_tokens / sum(b.tokens for b in bins),
        max_factor=max_factor
    )
    
    # Apply upsampling per bin
    result = []
    for bin in bins:
        rate = integrate(curve, bin.percentile_range) / bin.width
        result.extend(repeat_documents(bin.docs, factor=round(rate)))
    return result
```

## 设计决策 (Design Decisions)

### 1. 滑动窗口注意力 (SWA) vs 全注意力
- **选择**：3/4层使用SWA（窗口4096），1/4层使用全注意力，最后一层始终全注意力
- **替代方案**：全部全注意力（OLMo 2方式）、全部SWA、稀疏注意力（Longformer）
- **论文对比**：Figure 13a显示YaRN + full attention在所有层（而非仅SWA层）给出最佳RULER分数
- **核心trade-off**：训练/推理效率 vs 长程依赖捕获能力。SWA在预训练8K context时节省计算，但在长上下文扩展后需配合YaRN RoPE scaling来补偿

### 2. 三阶段去重策略
- **选择**：精确哈希去重 → MinHash模糊去重 → 后缀数组子串去重
- **替代方案**：仅做精确去重（更快但留下近似重复）、SimHash、SemDeDup（语义去重）
- **论文讨论**：该策略目标是先激进去重（75%文档被移除），再通过quality-aware upsampling有控制地重新引入重复。这与传统"去重后直接训练"不同
- **核心trade-off**：去重激进度 vs 信息保留。激进去重虽丢弃了重复计数作为质量信号，但换来了对重复的精确控制

### 3. 中训练数据中引入Thinking Traces
- **选择**：在midtraining阶段就引入QWQ推理轨迹、元推理等thinking数据（占~7%）
- **替代方案**：仅在post-training SFT阶段引入thinking数据（传统做法）
- **论文对比**：Table 10显示thinking和instruction数据在midtraining中的引入为post-training提供了显著提升
- **核心trade-off**：midtraining数据纯度 vs post-trainability。早期引入thinking数据可能"污染"base model的通用性，但显著改善了下游Think模型的性能

### 4. Conditional Mixing vs 全局重优化
- **选择**：冻结已有最优mix，仅对新增domain做增量优化
- **替代方案**：每次数据变更后重新训练整个swarm（成本高N倍）
- **论文讨论**：论文验证了conditional mixing方法有效（引用Chen et al., 2026获取更多细节），三轮增量优化分别处理Web topics、Code languages、PDF topics
- **核心trade-off**：优化全局性 vs 计算成本。conditional mixing可能找到局部最优而非全局最优，但计算成本大幅降低

### 5. RL-Zero：从Base直接做RLVR
- **选择**：跳过SFT/DPO，直接从base model用verifiable rewards做RL
- **替代方案**：标准pipeline（SFT→DPO→RL），或仅SFT→RL
- **论文对比**：Section 6详细对比了RL-Zero在Math/Code/IF/General四个domain的表现
- **核心trade-off**：研究纯净性 vs 最终性能。RL-Zero性能不如完整pipeline，但提供了无数据泄露干扰的干净RL研究基准

## 易混淆点 (Potential Confusions)

### 1. "Fully-Open" vs "Open-Weight"
- ❌ 错误理解：OLMo 3和Qwen 3都是"开源模型"，区别不大
- ✅ 正确理解："Fully-open"意味着发布所有训练数据、数据处理代码、中间checkpoint、训练配方；"Open-weight"仅发布最终权重。OLMo 3的核心价值不仅在于模型性能，而在于可以在model flow的任何环节进行干预和研究

### 2. Midtraining vs Fine-tuning
- ❌ 错误理解：Midtraining就是早期的SFT/fine-tuning
- ✅ 正确理解：Midtraining是base model训练的第二阶段（在预训练之后），仍然使用next-token prediction目标，但数据从大规模多样数据转向100B高质量token（含代码、数学、QA）。它不改变训练目标（不是instruction tuning），而是通过数据课程提升特定能力。关键区别在于学习率schedule是线性衰减而非重新warm-up

### 3. Quality-Aware Upsampling vs 质量过滤
- ❌ 错误理解：高质量数据上采样就是设定质量阈值过滤低质量数据
- ✅ 正确理解：质量过滤是step function（阈值以上保留，以下丢弃）；质量上采样是monotonically increasing curve（最好的重复7x，中等的1-3x，最差的丢弃）。上采样是在去重后的干净数据集上有控制地"重新引入"重复，与传统的flat filtering本质不同（见Figure 10对比）

---

## 实验与归因 (Experiments & Attribution)

## 核心收益

### Base Model (OLMo 3 Base 32B vs 最强fully-open对手)

| 指标 | OLMo 3 32B | Marin 32B | Apertus 70B | OLMo 2 32B | 提升幅度(vs Marin) |
|------|-----------|-----------|-------------|------------|-------------------|
| Math composite | 61.9 | 49.3 | 39.7 | 53.9 | **+12.6** |
| Code composite | 39.7 | 30.8 | 23.3 | 20.5 | **+8.9** |
| MC STEM | 74.5 | 75.9 | 70.0 | 75.6 | -1.4 |
| MC Non-STEM | 85.6 | 84.5 | 78.5 | 84.2 | +1.1 |
| GenQA | 79.8 | 80.3 | 75.0 | 79.1 | -0.5 |

**关键发现**：Math和Code有双位数提升（+12.6和+8.9），这是midtraining数据扩展（从纯数学到Math+Code+QA+Thinking）和constrained mixing优化的直接成果。MCQA和GenQA基本持平或略有提升。

### Think Model (OLMo 3.1 Think 32B vs open-weight模型)

| 指标 | OLMo 3.1 Think 32B | Qwen 3 32B Think | Qwen 2.5 32B | DeepSeek R1 Distill 32B |
|------|-------------------|-----------------|-------------|------------------------|
| MATH | 96.2 | 95.4 | 80.2 | 92.6 |
| AIME 2024 | 80.6 | 80.8 | 15.7 | 70.3 |
| AIME 2025 | 78.1 | 70.9 | 13.4 | 56.3 |
| HumanEval+ | 91.5 | 91.2 | 82.6 | 92.3 |
| LiveCodeBench v3 | 83.3 | 90.2 | 49.9 | 79.5 |
| IFEval | 93.8 | 86.5 | 81.9 | 78.7 |
| MMLU | 86.4 | 88.8 | 84.6 | 88.0 |
| AlpacaEval 2 LC | 69.1 | 75.6 | 81.9 | 26.2 |

**关键发现**：
- 在MATH (96.2 vs 95.4)和AIME 2025 (78.1 vs 70.9)上超越Qwen 3 32B
- 在IFEval上大幅领先 (93.8 vs 86.5)
- 在LiveCodeBench (83.3 vs 90.2)和AlpacaEval (69.1 vs 75.6)上仍有差距
- **关键约束**：OLMo 3仅使用~6x fewer tokens训练（6T vs Qwen的36T pretrain tokens估计）

### Long-context Performance (Table 12)

| 模型 | RULER 4K | RULER 32K | RULER 65K | HELMET 4K | HELMET 32K | HELMET 65K |
|------|---------|----------|----------|----------|-----------|----------|
| OLMo 3 7B | 94.89 | 84.14 | 67.96 | 45.66 | 43.62 | 36.80 |
| OLMo 3 32B | 96.10 | 90.42 | 79.70 | 52.11 | 49.36 | 43.15 |
| Qwen 2.5 32B | 96.03 | 90.42 | 80.73 | 52.11 | 56.06 | 51.73 |
| Gemma 3 27B | 94.45 | 84.26 | 60.33 | 47.74 | 44.60 | 35.67 |

**关键发现**：OLMo 3 32B在RULER上与Qwen 2.5 32B几乎持平，在HELMET上稍有差距。考虑到这是OLMo首次支持长上下文且扩展阶段仅100B tokens，这是一个强劲的结果。

### 阶段性贡献（Table 13，从page 36）

从预训练→中训练→长上下文的逐阶段提升：
- Math: 预训练贡献基础能力，midtraining带来大幅跳跃（~+10 points）
- Code: midtraining的代码数据带来显著提升
- 长上下文: 在不损失短上下文性能的前提下解锁65K能力

## 归因分析 (Ablation Study)

### 按贡献大小排序的关键组件：

1. **Midtraining数据扩展**（贡献最大）：从OLMo 2的纯数学midtraining扩展到Math+Code+QA+Thinking，是base model数学和代码能力跃升的主要来源。Table 7-9展示了各数据源的独立贡献。

2. **Constrained Data Mixing**（次大贡献）：Figure 9显示，优化后的web数据混合比例（大幅上调STEM主题）在1B模型上平均BPB提升0.056。

3. **Quality-Aware Upsampling**（显著贡献）：在数据受限设置下，quality-aware upsampling比flat filtering表现更好（Appendix中的实验）。

4. **olmOCR Science PDFs**（中等贡献）：Figure 13b显示olmOCR PDFs比其他长文档数据源更有效地支持长上下文能力。作为预训练的13.6%数据，也提升了科学领域知识。

5. **长上下文扩展五要素**（Figure 13）：
   - (a) YaRN + full attention at all layers → 最佳RULER score
   - (b) olmOCR PDFs > 其他数据 → 学术PDF是长文档的最佳来源
   - (c) Synthetic data augmentation → 在自然PDFs基础上进一步提升
   - (d) Document packing → 提升长序列的RULER分数
   - (e) 更长的extension budget → 持续改善

6. **Delta Learning (DPO阶段)**：扩展推理模型的能力边界，超越SFT单独能达到的水平，并为RL做好准备。

7. **OlmoRL效率优化**：4x训练加速，使得21天的extended RL run（从OLMo 3 Think到OLMo 3.1 Think）成为可能。

### Midtraining数据源归因（Tables 7-9）：
- Math synthetic数据（CraneMath, MegaMatt等）→ 数学能力的主要驱动力
- CraneCode → 代码能力的主要驱动力
- QA数据（Reddit To Flashcards, Nemotron Synth QA）→ GenQA提升
- Thinking traces → post-trainability提升（Table 10显示thinking+instruction数据在midtraining中为post-training铺路）

## 可信度检查

### 积极方面：
- **评估设计严谨**：43个benchmark分6个cluster，有SNR分析过滤噪声benchmark，有held-out set防止过拟合
- **数据去污染**：Section 3.5.5和Appendix A.5详细描述了去污染流程，包括对RL-Zero数据的额外去污染
- **完全可复现**：所有数据、代码、checkpoint开放
- **诚实报告弱点**：承认在LiveCodeBench和AlpacaEval上落后于Qwen 3

### 需要注意的方面：
- **Baseline选择**：fully-open类别中主要竞争对手（Marin、Apertus）规模偏小或训练不足，OLMo 3在该类别中"赢"的门槛相对较低
- **与Qwen 3的比较**：声称用"6x fewer tokens"，但Qwen 3的确切预训练token数未被官方确认，这个倍数是估计值
- **Post-training评估**：Table 1中AlpacaEval 2 LC对Qwen 3显示为"-"（缺失），但Qwen 3的实际分数可能更高
- **RULER vs 实际长上下文能力**：RULER是合成benchmark，HELMET虽更接近实际但仍有差距。OLMo 3在HELMET上的65K分数（43.15 vs Qwen 2.5的51.73）差距明显大于RULER

---

## 专家批判 (Critical Review)

## 隐性成本 (Hidden Costs)

### 1. 数据工程的巨大人力成本
论文描述的数据管线极其复杂：三阶段去重、PII过滤（需人工迭代文档类型分类法）、质量分类器训练、WebOrganizer topic分类、constrained mixing的多轮swarm训练、conditional mixing的三轮增量优化、quality-aware upsampling曲线拟合……每一步都需要大量的工程投入和专家判断。$2.75M的GPU成本只是冰山一角，人力成本可能远超GPU成本。

### 2. 评估的隐性计算负担
论文提到"checkpoint evaluation consumes a larger proportion of compute resources"——43个benchmark × 多个中间checkpoint × 多个候选模型的评估开销在post-training阶段尤其显著。SFT需要sweep 4个learning rate × 256 GPUs × 36小时，DPO需要多天。这些"非训练"成本在报告pretraining hours时被低估。

### 3. Midtraining的合成数据依赖
中训练数据中大量使用合成数据（标记为*和**的源）：CraneMath、MegaMatt、CraneCode等均为合成生成。这意味着OLMo 3的能力部分依赖于其他闭源模型（QWQ、Gemini、Llama Nemotron、GPT等用于生成合成数据），这在某种程度上削弱了"fully-open"的纯粹性。

### 4. 模型合并的不确定性
Midtraining使用两个并行run后进行model merging（"followed by model merging and evaluations to decide on final checkpoints"），长上下文扩展阶段也涉及merging。Model merging的效果有不确定性，论文未详细讨论merge策略的选择和敏感性。

### 5. RL训练的稳定性问题
论文坦承"at least a day of training time lost due to stability issues"，且post-training的理论"less developed"需要"multiple experiments to identify the optimal hyperparameters"。这暗示RL训练阶段的robustness仍是问题。

## 工程落地建议

### 最大的"坑"：

1. **数据管线复现难度极高**：虽然代码开源，但完整跑通需要处理9T+ tokens的数据，涉及多个工具链（Duplodocus去重、WebOrganizer分类、olmOCR提取、constrained mixing优化）。建议从150B sample mix开始实验。

2. **Conditional mixing的path dependency**：三轮增量优化的结果取决于优化顺序（先Web→Code→PDF）。如果你的数据组成不同，可能需要重新设计优化路径。

3. **长上下文扩展的数据需求**：OLMo 3的长上下文能力强烈依赖olmOCR science PDFs（640B tokens，22.3M文档超8K tokens）。如果缺乏类似规模的长文档数据，长上下文扩展效果可能大打折扣。

4. **OlmoRL框架的domain-specific tuning**：RLVR在不同domain（Math/Code/IF/General）需要不同的reward设计和超参数。论文提供了RL-Zero作为benchmark，但"the theory for post-training, particularly RL, is less developed"。

5. **SWA与长上下文的交互**：预训练时使用SWA（窗口4096）但长上下文扩展后需要在所有层使用full attention才能获得最佳效果（Figure 13a），这种架构转换的具体实现细节需要仔细参考OLMo-core代码。

### 推荐的落地路径：
1. 直接使用发布的OLMo 3 Base作为起点，跳过pretraining
2. 在自有domain数据上做midtraining（参考Dolmino Mix的配比思路）
3. 使用Open Instruct框架做post-training（SFT→DPO→RL）
4. 如需长上下文，参考Longmino Mix的配方但可能需要自行准备长文档数据

## 关联思考

### 与现有技术的联系：

1. **与MoE的关系**：OLMo 3是dense模型（7B/32B），未使用MoE。在同等推理成本下，MoE（如DeepSeek V3的671B总参数/37B活跃参数）可能在知识容量上有优势。OLMo 3的设计选择是简单性和可复现性优先。

2. **与FlashAttention的关系**：论文使用custom attention kernels（引用Dao 2024），即FlashAttention，作为训练效率优化的一部分。SWA pattern进一步减少了attention计算。

3. **与LoRA的关系**：论文未使用LoRA进行post-training（全参数fine-tuning），但发布的base model和中间checkpoint为LoRA微调提供了优质起点。

4. **与数据mixing literature的关系**：Constrained mixing方法建立在RegMix、Data Mixing Laws、CLIMB的基础上，核心创新是conditional mixing（增量适配数据变化）和swarm-based optimization的工程化实现。

5. **与RLHF/RLVR的关系**：OLMo 3的post-training使用RLVR（verifiable rewards）而非传统RLHF（human feedback），这与DeepSeek R1的路线一致。Delta Learning是DPO的改进变体，通过精心构造contrastive pairs扩展推理边界。

6. **与Scaling Laws的关系**：论文大量使用scaling analysis（Figure 6）做决策，但没有提出新的scaling law。proxy metrics（BPB-based Easy suites）是对Chinchilla-style scaling law的实用扩展。

7. **与DCLM的关系**：OLMo 3的web数据处理深度依赖DCLM pipeline（Resiliparse提取、DCLM-Baseline作为初始mix），但在去重、分类和mixing上做了大幅改进。

---

## 机制迁移分析 (Mechanism Transfer Analysis)

## 机制解耦 (Mechanism Decomposition)

| 原语名称 | 本文用途 | 抽象描述 | 信息论/几何直觉 |
|---------|---------|---------|---------------|
| **Conditional Mixing** | 数据源不断变化时增量优化训练数据配比 | 将已优化的混合策略冻结为单一虚拟节点，在降维子空间中对新增元素做增量优化 | 高维优化空间中的子空间投影：将已解决的维度"冻结"，仅在新增维度上搜索，以O(k)代替O(n)复杂度 |
| **Quality-Stratified Resampling** | 按文档质量百分位差异化重复训练次数 | 对样本集按质量评分分层，用monotonic upsampling curve差异化采样频率 | 信息增益加权采样：高信息密度样本获得更多梯度更新机会，等价于在loss landscape中对高价值区域做更密集的搜索 |
| **Proxy Metric Bridging** | 用BPB-based Easy suite在小模型上预测大模型的benchmark排序 | 将离散指标转化为连续代理指标，在低资源regime下获得高资源regime的决策信号 | 流形上的局部-全局对应：如果两个指标在某个尺度范围内保持单调关系，则在低尺度的代理指标排序可以可靠地迁移到高尺度 |
| **Distributed Exploration + Centralized Assessment** | Midtraining中各数据源团队独立优化，集中做integration test评估 | 多目标优化中的分层搜索：独立单元在各自子空间探索，周期性汇聚到全局评估点做Pareto筛选 | 类似进化算法的island model：各岛独立进化（exploration），定期migration（centralized assessment）实现全局收敛 |

## 迁移处方 (Transfer Prescription)

### 原语1: Conditional Mixing

**场景A：推荐系统的特征工程迭代**
- **目标领域**：推荐系统中，特征数据源（用户行为、内容属性、上下文信号）不断新增和迭代
- **怎么接**：将已有的特征组合权重冻结为虚拟特征组，仅对新增特征源做配比优化。输入是各特征源的embedding，输出是组合后的user/item representation
- **替换组件**：替代传统的全局特征重要性搜索（如AutoFE中的全量NAS）
- **预期收益**：特征工程迭代速度提升数倍（swarm size从O(n_features)降到O(n_new_features)）
- **风险**：如果新特征与已冻结特征有强交互效应，conditional mixing可能错过最优解

**场景B：多模态模型的数据配比**
- **目标领域**：Vision-Language Model训练中，图文数据源种类不断扩展（新的caption数据集、新的VQA数据等）
- **怎么接**：冻结已优化的text-only mix，仅对新增的图文配对数据做增量比例优化
- **预期收益**：避免每次新增数据源时重跑expensive proxy model swarm
- **风险**：跨模态交互可能使冻结假设失效

### 原语2: Quality-Stratified Resampling

**场景A：推荐系统训练数据的质量分层采样**
- **目标领域**：电商推荐中，用户隐式反馈（点击/购买）的质量差异巨大
- **怎么接**：用行为置信度（如session深度、重复购买）作为质量分数，对高质量交互做3-7x过采样，低质量（misclick等）做降采样或丢弃。输入是(user, item, interaction)三元组，输出是重采样后的训练集
- **替换组件**：替代传统的uniform sampling或简单的hard negative mining
- **预期收益**：在数据量有限时更高效地利用高质量信号
- **风险**：如果质量评分器有偏差，会放大bias

**场景B：代码生成模型的训练数据策展**
- **目标领域**：代码LLM训练中，GitHub代码质量参差不齐
- **怎么接**：用代码质量评分器（star count、linter score、test coverage等）分层，高质量代码多次训练
- **预期收益**：在相同token预算下获得更好的代码生成能力
- **风险**：过度上采样high-star repos可能偏向特定编程范式

### 原语3: Proxy Metric Bridging

**场景A：大规模推荐模型的快速A/B决策**
- **目标领域**：推荐系统中，线上A/B测试昂贵且耗时
- **怎么接**：找到与线上GMV/CTR保持单调关系的离线代理指标（如calibrated loss on held-out set），用小流量实验结果预测大流量表现
- **替换组件**：替代需要完整A/B cycle的传统评估
- **预期收益**：模型迭代决策速度提升5-10x
- **风险**：代理指标与真实指标的相关性可能随模型改进而漂移

### 原语4: Distributed Exploration + Centralized Assessment

**场景A：多团队协作的推荐系统优化**
- **目标领域**：大型推荐系统中，内容理解、用户画像、排序策略等由不同团队负责
- **怎么接**：各团队独立优化各自模块（distributed exploration），周期性汇聚到统一的端到端评测pipeline（centralized assessment）做整体性能验证
- **预期收益**：团队并行度最大化，同时保证端到端质量
- **风险**：各模块的优化方向可能在集成时冲突

## 机制家族图谱 (Mechanism Family Tree)

### Conditional Mixing
- **前身 (Ancestors)**：
  - RegMix (Liu et al., 2024a)：用回归模型预测data mix性能的先驱
  - Data Mixing Laws (Ye et al., 2025)：data mix与性能的理论关系
  - CLIMB (Diao et al., 2025)：类似的swarm-based mixing优化
- **兄弟 (Siblings)**：
  - DoReMi (Xie et al., 2024)：用domain reweighting优化训练分布
  - SlimPajama mixing experiments：类似的数据配比搜索
- **后代 (Descendants)**：论文引用Chen et al. (2026)作为conditional mixing的完整方法论文
- **创新增量**："条件化"思想——将已优化的mix冻结为虚拟domain做增量更新，这是对RegMix/CLIMB的关键工程化扩展

### Quality-Stratified Resampling
- **前身 (Ancestors)**：
  - Curriculum Learning (Bengio et al., 2009)：按难度/质量排序训练
  - DCLM Flat Filtering (Li et al., 2024a)：用质量阈值做二元过滤
  - Importance Sampling in RL：按样本重要性加权采样
- **兄弟 (Siblings)**：
  - FineWeb quality filtering：类似的质量分层策略
  - Fang et al. (2025a)：发现重复计数是质量信号的工作
- **后代 (Descendants)**：预期会有更多结合quality scoring和adaptive sampling的数据策展方法
- **创新增量**：将去重和质量上采样解耦——先激进去重消除自然重复，再通过参数化曲线有控制地重新引入高质量重复。这比flat filtering更灵活，比curriculum learning更系统化

### Proxy Metric Bridging (OlmoBaseEval)
- **前身 (Ancestors)**：
  - Scaling Laws (Kaplan et al., 2020; Hoffmann et al., 2022)：用小模型预测大模型性能
  - Schaeffer et al. (2023)：证明"emergent abilities"是指标选择的artifact
  - Magnusson et al. (2025)：不同评估在不同scale敏感的发现
- **兄弟 (Siblings)**：
  - Bhagia et al. (2024)：OLMo 2的scaling model suite
  - Heineman et al. (2025)：benchmark SNR分析方法
- **后代 (Descendants)**：OlmoBaseEval作为开源套件，预期被后续fully-open模型开发采用
- **创新增量**：系统化地将SNR分析、scaling analysis、task clustering和proxy metrics组合成一个完整的评估框架，使数据决策可以在小计算预算下可靠进行

### 多阶段数据课程 (Pretrain → Midtrain → Long-context)
- **前身 (Ancestors)**：
  - GPT-4 training pipeline：多阶段训练的工业实践
  - OLMo 2 (2024)：两阶段（pretrain + midtrain）的先驱
  - Llama 3 (2024)：类似的多阶段数据课程
- **兄弟 (Siblings)**：
  - Qwen 2.5/3：类似的多阶段训练但不公开细节
  - Gemma 3：类似的长上下文扩展策略
- **后代 (Descendants)**：Stanford Marin等后续fully-open模型已在采用类似的多阶段框架
- **创新增量**：(1) 中训练阶段的目标从"提升基础能力"扩展到"为post-training铺路"（引入thinking traces和instruction data）；(2) 长上下文扩展作为独立阶段，利用olmOCR PDFs作为天然长文档来源

---

## 背景知识补充 (Background Context)

## 背景知识补充

### 1. Fully-Open vs Open-Weight 模型分类
在当前LLM生态中，"开放"有不同层次：
- **Open-weight**（如Qwen、Llama、Gemma）：发布模型权重，允许使用和fine-tuning，但不公开训练数据和完整配方
- **Fully-open**（如OLMo、Marin、Apertus）：发布所有内容——训练数据、数据处理代码、所有中间checkpoint、训练超参数、评估代码

OLMo系列是fully-open阵营的旗舰，其核心价值主张是"model flow"的完全透明，而非仅仅是最终模型性能。

### 2. DCLM (DataComp for Language Models)
DCLM (Li et al., 2024a) 是一个标准化的LLM训练数据评估框架，提供了从CommonCrawl提取的标准化web数据池（DCLM-pool）和经质量过滤的基准数据（DCLM-Baseline）。OLMo 3的web数据管线以DCLM为起点，但做了大幅改进（三阶段去重、WebOrganizer分类、quality-aware upsampling）。

### 3. olmOCR
olmOCR (Poznanski et al., 2025a) 是Allen AI开发的PDF-to-text转换工具，可以将学术PDF转化为线性化的纯文本。它是OLMo 3引入的一个关键新数据源——将238M份学术PDF转为可训练的文本格式。这些PDF天然地提供了大量长文档（22.3M文档超8K tokens），使得OLMo 3的长上下文扩展成为可能。

### 4. Delta Learning
Delta Learning (Geng et al., 2025) 是一种改进的偏好数据构造方法，用于DPO阶段。核心思想是通过精心设计的contrastive pairs（chosen vs rejected responses），将模型的推理能力边界推到超越SFT所能达到的水平。OLMo 3将其用于Think和Instruct模型的DPO阶段。

### 5. RLVR (Reinforcement Learning with Verifiable Rewards)
RLVR是RLHF的替代方案，使用自动可验证的reward（如数学题的正确性、代码的执行通过率）替代人类偏好信号。DeepSeek R1率先证明了RLVR在训练thinking model中的有效性。OLMo 3的OlmoRL框架扩展了RLVR到代码和一般聊天领域。

### 6. YaRN (Yet another RoPE extensioN)
YaRN是一种RoPE位置编码的扩展方法，允许在训练后（或通过少量额外训练）将模型的有效上下文长度扩展到超过训练时使用的长度。OLMo 3使用YaRN将context从8K扩展到65K。

### 7. WebOrganizer
WebOrganizer (Wettig et al., 2025) 是一个基于transformer的web文档分类工具，可将文档分为24个主题类别。OLMo 3将其蒸馏为fastText模型以加速处理，用于数据的主题分区和后续的per-topic混合优化。

### 8. Sliding Window Attention (SWA)
SWA (Beltagy et al., 2020) 限制每个token只关注前方固定窗口内的token，将attention的复杂度从O(n²)降为O(n×w)。OLMo 3在3/4层使用SWA（窗口4096），1/4层使用full attention，这是效率和长程建模能力的折中。Mistral系列模型也采用了类似策略。
