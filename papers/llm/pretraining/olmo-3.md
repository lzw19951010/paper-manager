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
- Qwen 3 32B Think
- Qwen 3 VL 32B
- Qwen 2.5 32B Instruct
- Gemma 3 27B
- Gemma 2 27B
- Llama 3.1 70B
- Mistral Small 3.1 24B
- DeepSeek R1 Distilled Qwen 32B
- Stanford Marin 32B
- Apertus 70B
- LLM360 K2-V2 70B Instruct
- OLMo 2 32B Instruct
- Gaperon 24B
- IBM Granite 3.3 8B
- Nemotron Nano 9B v2
- Xiaomi MiMo 7B
- OpenThinker 7B
- Qwen 3 8B
- Qwen 2.5 7B
category: llm/pretraining
code_url: https://github.com/allenai/OLMo-core
core_contribution: new-framework/new-method/empirical-study
datasets:
- Dolma 3 Mix (5.93T tokens：76.1% CommonCrawl + 13.6% olmOCR PDFs + 6.89% Stack-Edu
  + 2.56% FineMath + 0.86% arXiv + 0.04% Wikipedia)
- Dolma 3 Dolmino Mix (100B tokens：Math 19.2% + Code 20% + QA 13.9% + Thinking 7.1%
  + Web 22.5% + PDF 5%)
- Dolma 3 Longmino Mix (50-100B tokens long-context extension)
- Dolci Think SFT (~2.3M examples：Math/Code/Chat/Safety/Multilingual)
- Dolci Think DPO (Delta Learning, chosen=Qwen3-32B, rejected=Qwen3-0.6B)
- Dolci Think RL (~105K prompts：Math 30K + Code 23K + IF 30K + General 21K)
- Dolci Instruct SFT (~2.15M examples)
- Dolci Instruct DPO (~260K pairs, with length control)
- Dolci Instruct RL (~172K prompts)
- Dolci RL-Zero (decontaminated：Math 13.3K + Code/IF/General)
- olmOCR science PDFs (108M documents after filtering, 972B tokens)
- CommonCrawl (104 dumps, 252.6B docs → 9.7B after 3-stage dedup)
- Stack-Edu rebalanced (137B tokens)
- FineMath 3+ (34.1B tokens)
- arXiv Proof-Pile-2
- Wikipedia & Wikibooks
- CraneMath (5.62B synthetic, Qwen3生成, MATH提升18.5pt)
- MegaMatt (3.88B synthetic, Qwen3生成)
- TinyMATH Mind/PoT (1.14B synthetic)
- OpenThoughts3 (math/code prompts)
- SYNTHETIC-2 (PrimeIntellect)
- OpenHermes-2.5 (quality classifier positive examples)
- UltraChat-200k (quality classifier positive examples)
- WildChat-1M / WildChat-4.8M
date: '2025-12-15'
doi: null
keywords: &id001
- Fully-Open Language Model
- Model Flow
- Thinking Model
- RLVR
- Data Curation
- Midtraining
- Long-Context Extension
- Delta Learning
- OlmoRL
- Constrained Data Mixing
- Quality-Aware Upsampling
- Deduplication at Scale
metrics:
- MATH accuracy (Minerva extraction)
- AIME 2024 accuracy (Avg@32, pass@1)
- AIME 2025 accuracy (Avg@32, pass@1)
- OMEGA accuracy
- HumanEval+ pass@1 (Avg@10)
- MBPP+ pass@1 (Avg@10)
- LiveCodeBench v3 pass@1 (Avg@10)
- IFEval accuracy
- IFBench accuracy
- MMLU accuracy
- GPQA accuracy
- PopQA accuracy
- AlpacaEval 2 LC win rate
- BigBenchHard accuracy
- ZebraLogic accuracy
- AGIEval English accuracy
- SimpleQA accuracy (function-calling)
- LitQA2 accuracy (function-calling)
- BFCL v3 accuracy (function-calling)
- Bits-per-byte (BPB, Base Easy proxy metric)
- RULER score (long-context, 4K/32K/65K)
- HELMET score (long-context, 4K/32K/65K)
- Signal-to-Noise Ratio (SNR, benchmark selection)
- MFU (Model FLOP Utilization, 43% for 7B, 41% for 32B)
- Safety score
publication_type: preprint
tags: *id001
title: Olmo 3
tldr: OLMo 3是完全开放的7B/32B模型家族，通过三阶段基座训练（5.9T预训练+100B中训+长上下文扩展）和SFT/Delta Learning DPO/OlmoRL后训练，旗舰模型OLMo
  3.1 Think 32B在MATH达96.2%、AIME 2025达78.1%，是最强完全开放思维模型，接近Qwen 3 32B但训练token仅为其1/6，总成本约$2.75M（56天1024×H100）。
url: https://arxiv.org/abs/2512.13961
venue: null
---

## 核心速览 (Executive Summary)

- **TL;DR (≤100字):** OLMo 3通过完全开放的三阶段基座训练（5.9T预训练→100B中训→长上下文扩展至65K）配合SFT/Delta Learning DPO/OlmoRL多域RLVR后训练，使OLMo 3.1 Think 32B在MATH达96.2%、AIME 2025达78.1%、HumanEval+达91.5%，成为最强完全开放思维模型，接近Qwen 3 32B(MATH 96.7%, AIME 86.3%)且训练token仅为其1/6，总成本$2.75M/56天/1024×H100。

- **一图流 (Mental Model):** 如果开源模型只给你成品菜（最终权重），OLMo 3给你完整的厨房——从食材采购清单（Dolma 3, 9T token数据池）、配方优化实验记录（swarm-based constrained mixing, 30M proxy models × 5倍domain数）、刀工技法（三阶段去重工具Duplodocus, 75%文档被精确裁减）、每步烹饪温度记录（所有中间checkpoint）、到最终菜品（Think/Instruct/RL-Zero三条产品线）。你可以在任何环节介入——换食材、改配方、调火候。

- **核心机制一句话:** `[多阶段数据课程 + conditional mixing + quality-aware upsampling] + [7B/32B密集Transformer] + [分布式探索 + 集中式集成测试的双循环数据优化] + [构建可介入全流程的完全开放模型家族]`

---

## 动机与第一性原理 (Motivation & First Principles)

- **痛点 (The Gap):**
  1. **"伪开源"困境：** Qwen 3、DeepSeek R1只发布最终权重，不公开预训练数据和中间checkpoint。研究社区无法追溯推理链到训练数据，无法判断RLVR性能来自RL算法还是数据泄露（Shao et al., 2025b实证了这一问题）。
  2. **OLMo 2的能力短板：** OLMo 2 32B在MATH仅49.2%（vs Qwen 2.5的80.2%），HumanEval+仅44.4%（vs 82.6%），上下文窗口仅4096 token，无长上下文能力。在完全开放模型中排名第一但与open-weight模型差距巨大。
  3. **数据工程瓶颈：** 万亿token规模全局去重缺乏高效工具（OLMo 2用的工具无法处理38.8B文档）；数据混合优化在数据源不断变化时需要从头重做整个swarm（成本与domain数平方成正比）。
  4. **评估信号不足：** 小规模模型（≤1B参数, 100B tokens）在MATH、HumanEval等难任务上表现为随机水平（Wei et al., 2022），无法用于高效的数据决策。OLMo 2仅用~10个benchmark评估，覆盖面窄。

- **核心洞察 (Key Insight):**
  Because 数据源在开发过程中持续演化（新数据到来、过滤器改进、质量分类器更新）→ Therefore 需要conditional mixing：将已有最优mix冻结为单一虚拟domain，仅对新增domain增量优化，将O(n²)搜索降为O(n) → Because 小规模模型在难任务上是纯噪声 → Therefore 需要proxy metrics（BPB-based Base Easy suites），在小计算预算下获得可靠信号（Figure 6证明BPB在1B规模即有信号而pass@1无信号）→ Because midtraining阶段引入thinking traces和instruction数据可以为post-training"预热"（Table 10实证）→ Therefore base model不应仅是通用语言模型，应定向为下游能力铺路 → Because Delta Learning对比当前SFT检查点（而非初始base model）→ Therefore 在偏好边界附近获得更高信噪比的对比信号（Table 21：直接SFT on chosen反而掉分，而DPO with weak rejected显著提升）。

- **物理/直觉解释:**
  想象你在调配鸡尾酒：
  - **原料选择**（数据源）：你有酒、果汁、冰块等原料（CommonCrawl 8.14T、PDFs 972B、Code 137B），但每种品质参差不齐
  - **配比优化**（constrained mixing）：不是随便混，而是通过大量小杯试饮（30M参数proxy模型swarm，5×domain数）找到最佳比例。STEM类topic被大幅上调，Java代码被下调让位Python
  - **品质分层**（quality-aware upsampling）：最好的果汁多放7倍（top 5%），一般的少放（1x），太差的丢弃（bottom 40%）
  - **分阶段调制**（三阶段训练）：先打底味（pretraining 5.9T广度覆盖），再加精华提味（midtraining 100B高质量数学/代码/推理数据），最后加长吸管（long-context extension到65K）
  - **最后装饰**（post-training）：根据用途不同做最终调整——加伞签（Think=思维链推理）、加吸管（Instruct=简洁高效）、或纯饮（RL-Zero=直接从base做RLVR）
  
  关键洞察：品质80%取决于原料配比（数据工程），而非最后的装饰（post-training）。OLMo 3的大部分创新集中在数据工程上。

---

## 方法详解 (Methodology)

#### 直觉版 (Intuitive Walk-through)

参考Figure 2（模型流全景图），OLMo 3的训练分为左侧Base Model Training和右侧Post-training两大阶段。

**旧方法（OLMo 2）的数据流：**
1. 预训练（4096 context, ~5T tokens, Dolma 2数据）→ 中训练（Dolmino Mix, 主要是数学）→ 直接进入post-training
2. 中训练只关注数学领域，缺乏代码和QA数据
3. 无长上下文扩展阶段
4. 评估套件覆盖面窄（~10个benchmark）

**OLMo 3改了哪里？为什么？**

1. **预训练数据管线革新**（Figure 8）：
   - 新增olmOCR science PDFs（238M→108M docs→972B tokens）→ 因为学术文档是高质量长文档的天然来源
   - 三阶段去重（精确→模糊→子串，252.6B docs→9.7B docs, 移除75%）→ 因为去重后才能通过quality-aware upsampling精确控制重复
   - Swarm-based constrained mixing（30M proxy×5倍domain数→回归→约束优化）→ 因为不同topic/language的最优配比不是自然分布（Figure 9：STEM被大幅上调）
   - Conditional mixing（冻结已有最优mix为虚拟domain，仅搜索新增维度）→ 因为数据源持续变化，三轮增量优化(Web topics→Code languages→PDF topics)

2. **中训练大幅扩展**（Table 5, Figure 11）：
   - 从纯数学扩展到Math(19.2%)+Code(20%)+QA(13.9%)+Thinking(7.1%)+Web(22.5%)+PDF(5%)
   - 引入"分布式微退火探索+集中式集成测试"双循环方法论
   - 有意引入thinking traces(QWQ推理轨迹等)和instruction数据为post-training铺路（Table 10验证有效）

3. **新增长上下文扩展阶段**（Section 3.6）：
   - 利用olmOCR PDFs天然长文档（22.3M docs > 8K tokens, 4.5M > 32K tokens）
   - RoPE theta从1M→100M，YaRN注意力缩放
   - 从8K扩展到65K context window，仅需50B(7B)或100B(32B)额外tokens

4. **Post-training分化三条路径**：
   - Think：SFT(Dolci Think SFT) → DPO(Delta Learning) → RLVR(OlmoRL, 750→2300步for 3.1)
   - Instruct：SFT(含function-calling) → DPO(含length control) → RLVR
   - RL-Zero：直接从Base做RLVR（去污染后的Dolci RL-Zero），目标是干净的研究基准

### 用简单例子走一遍差异

假设我们有1000篇文档要处理：
- **旧方法（OLMo 2）**：把1000篇混合训练，每篇只看4K token。中训时只加数学题。用10个benchmark取均值评估。
- **新方法（OLMo 3）**：先对1000篇做质量评分(fastText质量分类器)和主题分类(WebOrganizer 24类)。最好的50篇重复训练7次，中间500篇1-3次，最差400篇丢弃。训练时扩展到8K token。用30M proxy模型×150个(5×30 topic+language buckets)找最优配比。中训时除了数学还加入CraneMath(+18.5pt MATH)、代码、QA和思维链。用43个benchmark评估，按能力聚类为6个cluster，且用BPB proxy metric确认小模型信号可靠（SNR分析移除噪声benchmark如BoolQ）。最后扩展到65K context。

#### 精确版 (Formal Specification)

**流程图 (Text-based Flow):**

```
Input: Raw Web (252.6B docs) + PDFs (238M docs) + Code (137B tok) + Math (34.1B tok) + Wiki
    ↓
[Stage 0: Data Pipeline]
    ├─ Web: HTML extraction → Heuristic filtering (→38.8B docs, -84.6%)
    │       → Exact dedup (→12.8B, -67%) → MinHash fuzzy dedup (→9.8B, -23%)
    │       → Suffix array substr dedup (→9.7B, -14% bytes) → [9.7B docs / 36.5T bytes]
    │       → Topic classification (WebOrganizer 24 categories, FastText distilled)
    │       → Quality classification (FastText, 20 vigintile buckets)
    │       → 480 buckets (24 topics × 20 quality tiers)
    │       → Quality-aware upsampling (bottom 40% discard, top 5% at 7x)
    │       → Constrained mixing (swarm 30M×5N → regression → optimization)
    │       → Conditional mixing (3 rounds: Web topics → Code langs → PDF topics)
    ├─ PDFs: olmOCR v0.1 extraction → Language filter → PII filter (Gemma 3 12B + 4B)
    │       → Heuristic filter (→108M docs) → MinHash dedup → Topic classification → Mixing
    ├─ Code: Stack-Edu → Language partition (C/C++/Go/Java/JS/Python/Ruby/Rust/...)
    │       → Constrained mixing per language
    └─ Math: FineMath3+ (34.1B) + arXiv LaTeX (21.4B) + Wikipedia (3.69B)
    ↓
    Dolma 3 Mix: 5.93T tokens
    [76.1% web | 13.6% PDFs | 6.89% code | 2.56% math | 0.86% arXiv | 0.04% wiki]
    ↓
[Stage 1: Pretraining] context=8192, SWA (3/4 layers window=4096, last layer full attn)
    7B: 5.93T tokens, peak LR=3×10⁻⁴, batch=4M tokens, 512 GPUs
    32B: 5.5T tokens, peak LR=6×10⁻⁴, batch=8M tokens, 512→1024 H100 GPUs
    LR schedule: Cosine (stretched to match 1 epoch for 7B, truncated at 5.5T for 32B)
    Throughput: 7B@7700 tok/s/GPU (43% MFU), 32B@1960 tok/s/GPU (41% MFU)
    ↓
[Stage 2: Midtraining] 100B tokens, linear LR decay
    Dolma 3 Dolmino Mix composition (Table 5):
      Math(19.2%): CraneMath 5.62B + Dolmino Math 10.7B + TinyMATH 1.14B + MegaMatt 1.73B
      Code(20%): Stack-Edu FIM 10B + CraneCode 10B
      QA(13.9%): Nemotron Synth QA 5B + Reddit Flashcards 5.9B + Wiki RCQA 3B
      Thinking(7.1%): QWQ Traces 1.87B + General Reasoning 1.87B + Meta-Reasoning 0.84B + ...
      Web(22.5%): CommonCrawl HQ subset
      PDF(5%): olmOCR science PDFs HQ subset
      Instruction(6.1%): Tulu 3 SFT 1.1B + Dolmino Flan 5B
    Framework: Distributed microanneals (5B+5B tokens) → Integration tests (full 100B) → SFT tests
    ↓
[Stage 3: Long-context Extension]
    7B: 50B tokens, 32B: 100B tokens
    Dolma 3 Longmino Mix: Long PDFs (olmOCR, 22.3M docs > 8K tokens) + synthetic aggregation
    RoPE: theta 1M→100M, YaRN scaling
    Context: 8K → 65K
    ↓
    Olmo 3 Base (7B/32B, 65K context)
    ↓
[Post-training: THREE branches]
    ├─ Think: SFT(~2.3M examples, QwQ-32B生成) → DPO(Delta Learning, ref=SFT ckpt)
    │         → RLVR(OlmoRL: math+code+IF+chat, ~105K prompts, 750→2300 steps for 3.1)
    │         → Olmo 3 Think / Olmo 3.1 Think
    ├─ Instruct: SFT(~2.15M examples, including function-calling with MCP trajectories)
    │         → DPO(Delta Learning + multi-turn + length control: ≤100 token delta)
    │         → RLVR(OlmoRL, max 8K/16K tokens, ~172K prompts)
    │         → Olmo 3 Instruct / Olmo 3.1 Instruct
    └─ RL-Zero: RLVR directly from Base (decontaminated Dolci RL-Zero)
             → Math/Code/IF/General/Mix domains
             → Olmo 3 RL-Zero (研究用：干净的RLVR基准)
```

**关键公式与变量：**

**1. Constrained Data Mixing（三阶段优化, Section 3.4.4）：**

Stage 1 - Swarm Construction:
训练 $N = 5 \times |\text{domains}|$ 个 proxy 模型（30M参数, 3B tokens, 5×Chinchilla），每个使用不同混合比例：
$$\mathbf{w}_i \sim \text{Dir}(\alpha \cdot \mathbf{w}_{\text{natural}})$$
- $\mathbf{w}_i \in \mathbb{R}^{|\text{domains}|}$：第i个proxy的domain混合权重
- $\mathbf{w}_{\text{natural}}$：自然分布（各domain按token数比例）
- $\alpha$：Dirichlet浓度参数，控制采样离散程度

Stage 2 - Per-task Regression:
对每个评估任务 $t \in T$（Base Easy suite, BPB-based），拟合广义线性模型：
$$\text{BPB}_t(\mathbf{w}) = \beta_0^{(t)} + \sum_{j=1}^{|\text{domains}|} \beta_j^{(t)} w_j + \epsilon$$
- $\text{BPB}_t$：任务t上的bits-per-byte（越低越好，proxy metric for downstream performance）
- $\beta_j^{(t)}$：domain j对任务t的回归系数（正=有害，负=有益）

Stage 3 - Constrained Optimization:
$$\mathbf{w}^* = \arg\min_{\mathbf{w}} \frac{1}{|T|} \sum_{t \in T} \widehat{\text{BPB}}_t(\mathbf{w})$$
$$\text{s.t.} \quad \sum_j w_j = 1, \quad w_j \geq 0, \quad w_j \leq w_j^{\max} \quad \forall j$$
- $w_j^{\max} = \min\left(\frac{X_j \cdot M}{Z}, 1\right)$：domain j的上界，$X_j$为可用tokens，$M$为最大重复次数（4-7x），$Z$为总目标tokens

**Conditional Mixing扩展：** 冻结已有最优mix为虚拟domain $d_{\text{frozen}}$，仅对新增domain $\{d_{\text{new}_1}, ...\}$重跑base procedure。搜索空间从 $|\text{all domains}|$ 维降至 $1 + |\text{new domains}|$ 维。OLMo 3进行了三轮：(1)DCLM 24 topics, (2)Stack-Edu 15 programming languages, (3)PDF 24 topics。

**2. Quality-Aware Upsampling（Section 3.4.4, Appendix A.2.4）：**

给定topic桶内 $Q$ 个质量等级（vigintile, 5-percentile intervals），第 $q$ 个等级有 $X_q$ tokens：
- 上采样函数 $f: [0, 1] \to [0, M]$ 须满足：
  - $f$ 凸且单调递增
  - $f(q) = 0$ for $q < q_{\text{cutoff}}$（实际bottom 40%被丢弃）
  - $\max f = M = 7$（经验确定的最大重复次数）
  - $\sum_q f(q) \cdot X_q = Z$（积分约束：总token数匹配目标）

Figure 10展示曲线形状：bottom 40%丢弃 → 40-95%以1-4x线性增长 → top 5%以7x重复。

**3. Signal-to-Noise Ratio for Benchmark Selection（Section 3.3.3）：**
$$\text{SNR} = \frac{\text{Var}_{\text{between-models}}(s)}{\text{Var}_{\text{within-model}}(s)}$$
通过评估OLMo 2 13B的最后50个checkpoint和10个外部base model计算。SNR低的benchmark（如单任务HumanEval SNR=3.2）被从macro-average中移除或通过增大n（pass@k中的k）改善到SNR=10.0（Figure 7）。

**4. GRPO Loss (OlmoRL, Section 4.4.1):**
$$\mathcal{L} = -\mathbb{E} \left[ \min\left( r_{i,t} \cdot A_{i,t}, \; \text{clip}(r_{i,t}, 1-\varepsilon_{\text{low}}, 1+\varepsilon_{\text{high}}) \cdot A_{i,t} \right) \right]$$
$$r_{i,t} = \frac{\pi(y_{i,t} | x, y_{i,<t}; \theta)}{\pi(y_{i,t} | x, y_{i,<t}; \theta_{\text{old}})}$$
$$A_{i,t} = r(x, y_i) - \text{mean}\left(\{r(x, y_i)\}_{i=1}^{G}\right)$$

符号物理含义：
- $r_{i,t}$：策略比率（新策略/旧策略的token概率比）
- $A_{i,t}$：组内相对优势（该响应比同组$G$个采样的平均好多少）
- $\varepsilon_{\text{low}}, \varepsilon_{\text{high}}$：非对称clipping参数，防止策略更新过大
- $r(x, y_i)$：来自各域验证器的奖励（Math: SymPy验证, Code: test-case通过率, IF: 约束满足, Chat: LM judge打分[0,1]）
- 加入truncated importance sampling cap $\rho$（Yao et al., 2025）

**数值推演 (Numerical Example)：**

**Quality-Aware Upsampling 推演：**

假设"Science, Math and Technology" topic桶有100M文档（8T pool中的某一个topic），分为20个质量等级（vigintile）：
- 目标：constrained mixing规定从该topic取1.2T tokens（优化后上调了STEM权重）
- 桶内总tokens：800B → 平均上采样率 = 1.2T/800B = 1.5x
- 质量分布：
  - Bottom 40%（8个vigintile，共320B tokens）：$f(q)=0$，全部丢弃 → 0 tokens
  - 40-80%（8个vigintile，共320B tokens）：$f(q) \approx 1.2$，各重复1.2x → 384B tokens
  - 80-95%（3个vigintile，共120B tokens）：$f(q) \approx 3.5$，各重复3.5x → 420B tokens
  - 95-100%（1个vigintile，共40B tokens）：$f(q) = 7$，各重复7x → 280B tokens
  - 总计：0 + 384B + 420B + 280B = 1.084T（接近目标1.2T，需微调参数）

**Constrained Mixing 推演：**

假设3个domain（Web, Code, PDF），自然分布[0.85, 0.07, 0.08]，目标6T tokens：
1. 训练15个proxy（5×3），各用Dirichlet采样比例，每个30M参数训练3B tokens
2. 评估每个在Base Easy（BPB）：回归发现增大Code和PDF权重降低math/code BPB
3. 约束：Code池=137B tokens，max 7x → $w_{\text{code}}^{\max} = 137B × 7 / 6T ≈ 16\%$
4. 优化结果可能：[0.76, 0.07, 0.14, 0.03]（STEM topic大幅上调，Entertainment下调）
5. Conditional mixing：冻结[0.76, 0.07, 0.14, 0.03]为虚拟domain，新增olmOCR PDFs的24个topic子分类，仅搜索PDF内部topic比例

**Delta Learning DPO 推演（Table 21 的直觉）：**

标准DPO：reference = base model (能力远低于SFT模型)
- chosen = Qwen3-32B (很强) vs rejected = Qwen3-0.6B (很弱)
- 对比信号："极好 vs 极差"，但两者都远离SFT模型的决策边界 → 信号冗余

Delta Learning：reference = SFT checkpoint (当前水平)
- 同样的chosen/rejected，但参考系变了
- 对比信号："在当前水平基础上好 vs 在当前水平基础上差" → 信号聚焦在决策边界附近
- 结果（Table 21）：直接SFT on chosen掉分（Avg 70.3→64.5），Delta Learning提升（70.3→72.9）

**伪代码 (Pseudocode)：**

```python
# === Constrained Data Mixing (Section 3.4.4) ===
def constrained_mixing(domains: list[Domain], target_tokens: int, eval_suite):
    """Swarm-based data mix optimization with constraints."""
    n_swarm = 5 * len(domains)  # 5x domains rule of thumb
    natural_w = normalize([d.tokens for d in domains])  # [n_domains]

    # Stage 1: Train proxy swarm (30M params, 3B tokens each)
    results = []
    for i in range(n_swarm):
        w = dirichlet_sample(alpha=1.0, center=natural_w)  # [n_domains]
        model = train_proxy(arch='30M', tokens=3e9, mix_weights=w)
        scores = eval_bpb(model, eval_suite)  # {task_name: BPB_float}
        results.append((w, scores))

    # Stage 2: Per-task regression (BPB = f(weights))
    regressors = {
        task: fit_glm(
            X=[r[0] for r in results],   # [n_swarm, n_domains]
            y=[r[1][task] for r in results]  # [n_swarm]
        ) for task in eval_suite.tasks
    }

    # Stage 3: Constrained optimization
    w_max = [min(d.tokens * 7 / target_tokens, 1.0) for d in domains]
    return optimize(
        obj=lambda w: mean(reg.predict(w) for reg in regressors.values()),
        constraints={'sum_to_1': True, 'non_negative': True, 'upper_bounds': w_max},
        init=natural_w,
    )  # Returns optimal weights [n_domains]

# === Conditional Mixing (incremental update) ===
def conditional_mixing(frozen_mix: dict, new_domains: list[Domain], target_tokens, eval_suite):
    """Treat frozen_mix as single virtual domain, only search new dimensions."""
    virtual = Domain(name='frozen', weights=frozen_mix, tokens=sum(frozen_mix.values()))
    return constrained_mixing([virtual] + new_domains, target_tokens, eval_suite)
    # OLMo 3: 3 rounds: Web(24 topics) → Code(15 langs) → PDF(24 topics)

# === Quality-Aware Upsampling (per topic bucket) ===
def quality_aware_upsample(topic_docs, target_tokens, max_factor=7):
    """Apply monotonic upsampling curve based on quality percentile."""
    bins = partition_into_vigintiles(topic_docs, n=20)  # 5-percentile intervals
    avg_rate = target_tokens / sum(b.tokens for b in bins)

    # Search for parametric convex monotonic curve f(q):
    # constraints: integral = avg_rate, max = max_factor, convex, monotonic
    curve = fit_convex_monotonic_curve(
        target_integral=avg_rate, max_factor=max_factor
    )  # See Appendix A.2.4 for parameterization

    result = []
    for bin in bins:
        rate = integrate(curve, bin.percentile_range) / bin.width
        if rate < 0.01:  # bottom cutoff (e.g., bottom 40%)
            continue  # discard
        result.extend(repeat_documents(bin.docs, factor=round(rate)))
    return result

# === Delta Learning DPO ===
def delta_learning_dpo(sft_model, preference_data, beta=0.1):
    """DPO with reference model = current SFT checkpoint (NOT base model)."""
    ref_model = copy(sft_model)  # 关键：reference是SFT模型本身
    ref_model.freeze()

    for batch in preference_data:
        # batch.chosen: Qwen3-32B responses, batch.rejected: Qwen3-0.6B responses
        logp_chosen = sft_model.log_prob(batch.chosen)      # [B, T]
        logp_rejected = sft_model.log_prob(batch.rejected)  # [B, T]
        ref_chosen = ref_model.log_prob(batch.chosen)       # [B, T]
        ref_rejected = ref_model.log_prob(batch.rejected)   # [B, T]

        # DPO loss: reward difference relative to CURRENT checkpoint
        reward_diff = beta * (
            (logp_chosen.sum(-1) - ref_chosen.sum(-1)) -
            (logp_rejected.sum(-1) - ref_rejected.sum(-1))
        )  # [B]
        loss = -F.logsigmoid(reward_diff).mean()
        loss.backward()
        optimizer.step()

# === OlmoRL with continuous batching (Section 4.4.3) ===
def olmorl_train_step(learner, actors, prompt_queue, result_queue):
    """Async RL with continuous batching and inflight weight updates."""
    # 1. Dispatch prompts to vLLM actors
    for actor in actors:
        if actor.has_capacity():
            prompt = prompt_queue.get()
            actor.generate_async(prompt, max_tokens=32768)  # continuous batching

    # 2. Collect completed generations (async, no waiting for full batch)
    batch = []
    while len(batch) < target_batch_size:
        result = result_queue.get()  # blocks until any actor finishes
        reward = verify(result)       # domain-specific: SymPy/test-case/constraint-check/LM-judge
        advantage = reward - group_mean(result.group)  # GRPO: group relative advantage
        if abs(advantage) > 0:  # active sampling: skip zero-gradient samples
            batch.append((result, advantage))

    # 3. Update learner (GRPO loss with asymmetric clipping)
    loss = grpo_loss(learner, batch, eps_low=0.2, eps_high=0.28)
    loss.backward()
    optimizer.step()

    # 4. Inflight weight update (no KV cache invalidation!)
    for actor in actors:
        actor.update_weights_async(learner.state_dict())  # thread-safe, no pause
    # Result: 4x faster than OLMo 2 (Table 23: 881→2949 tok/s)
```

#### 设计决策 (Design Decisions)

**1. 滑动窗口注意力(SWA) vs 全注意力**
- **选择**：3/4层使用SWA（window=4096），1/4层+最后一层使用全注意力
- **替代方案**：全部全注意力（OLMo 2方式）、全部SWA、稀疏注意力（Longformer方式）
- **论文对比**：Figure 13a显示YaRN + full attention在所有层最优RULER分数
- **核心trade-off**：训练/推理效率 vs 长程依赖捕获。SWA在预训练8K context时省计算，但在长上下文扩展后需配合YaRN RoPE scaling补偿

**2. 三阶段去重策略**
- **选择**：精确哈希去重(→12.8B,-67%) → MinHash模糊去重(→9.8B,-23%) → 后缀数组子串去重(→9.7B,-14% bytes)
- **替代方案**：仅精确去重（更快但留近似重复）、SimHash（更快但精度低）、SemDeDup（语义去重，计算昂贵）
- **论文讨论**：策略目标是先激进去重（75%文档被移除），再通过quality-aware upsampling有控制地重新引入重复。与传统"去重后直接训练"不同
- **核心trade-off**：去重激进度 vs 信息保留。激进去重虽丢弃了重复计数作为质量信号，但换来了对重复的精确控制（"先打扫干净，再选择性放回"）
- **工具**：Duplodocus（Rust实现，支持万亿token规模分布式去重）

**3. Midtraining引入Thinking Traces**
- **选择**：midtraining阶段就引入QWQ推理轨迹+元推理等thinking数据（占~7.1%）
- **替代方案**：仅在post-training SFT阶段引入thinking数据（传统做法）
- **论文对比**：Table 10显示thinking和instruction数据在midtraining中的引入为post-training提供了显著提升。Table 29进一步证明从Think SFT起步训练Instruct模型也能获益
- **核心trade-off**：base model通用性 vs post-trainability。早期引入thinking数据可能"污染"base model评估指标，但显著改善了下游Think模型性能

**4. Conditional Mixing vs 全局重优化**
- **选择**：冻结已有最优mix为虚拟domain，仅对新增/修改的domain做增量优化
- **替代方案**：每次数据变更后重新训练整个swarm（成本与domain数平方成正比）
- **论文验证**：三轮增量优化有效（Web topics→Code languages→PDF topics），详见Chen et al., 2026
- **核心trade-off**：全局最优性 vs 计算成本。conditional mixing可能找到局部最优，但计算成本大幅降低，且实际中数据源变更频繁，全局优化的"保质期"很短

**5. Delta Learning vs 标准DPO**
- **选择**：DPO的参考模型 = 当前SFT检查点（而非base model）
- **替代方案**：标准DPO（参考模型=base）、SimPO、KTO、IPO
- **论文对比**：Table 21证明：直接SFT on chosen responses反而掉分(70.3→64.5)，而DPO with weak rejected显著提升(70.3→72.9)。Table 22进一步证明DPO后再做RL比SFT后直接做RL效果更好
- **核心trade-off**：信号针对性 vs 偏好数据利用率。Delta Learning使对比信号集中在当前决策边界附近

**6. Continuous Batching + Inflight Updates vs Static Batching**
- **选择**：vLLM continuous batching + 不暂停推理的异步权重更新
- **替代方案**：OLMo 2的static batching + 同步权重更新
- **论文对比**：Table 23量化了改进效果：881→2949 tok/s（3.3x），MBU从12.9%→43.2%。32K生成长度下static batching浪费54%计算（因为平均生成长度14628 vs 最大32K）
- **核心trade-off**：工程复杂度 vs 训练效率。需要线程安全的vLLM引擎和精心设计的异步架构

#### 易混淆点 (Potential Confusions)

- ❌ 错误理解: OLMo 3 Think是通过蒸馏Qwen/DeepSeek R1获得思维链能力的
- ✅ 正确理解: Think能力来自自主训练的SFT+DPO+RL流程。Dolci数据集虽包含合成数据，但由QwQ-32B等模型生成reasoning traces，不是直接蒸馏。chosen/rejected responses来自Qwen3-32B和Qwen3-0.6B的生成，用于构造对比信号，而非蒸馏知识。

- ❌ 错误理解: "完全开放"只是多发布了权重
- ✅ 正确理解: 完全开放包括整个model flow——每个训练阶段的数据mix（实际训练用的token序列）、数据池（9T+2T+640B完整源数据）、代码（OLMo-core训练 + Open Instruct后训练 + datamap-rs处理 + duplodocus去重 + OLMES评估）、所有中间检查点和评估日志。可以从任意节点介入修改。

- ❌ 错误理解: Quality-aware upsampling就是简单的top-K质量过滤
- ✅ 正确理解: 它是连续的凸单调递增曲线，通过积分约束确保总token数匹配目标。底部丢弃 + 中间平滑增长 + 顶部最大重复，是"filtering"和"upsampling"的统一框架。与DCLM的step function过滤本质不同（Appendix A.2.4有形式化描述）。

---

## 实验与归因 (Experiments & Attribution)

### 核心收益

**Base Model (OLMo 3 Base 32B, Table 2):**

| 指标 | OLMo 3 32B | Marin 32B | Apertus 70B | OLMo 2 32B | Qwen 2.5 32B | 提升(vs Marin) |
|------|-----------|-----------|-------------|------------|-------------|---------------|
| Math composite | 61.9 | 49.3 | 39.7 | 53.9 | 64.7 | **+12.6** |
| Code composite | 39.7 | 30.8 | 23.3 | 20.5 | 48.3 | **+8.9** |
| MC STEM | 74.5 | 75.9 | 70.0 | 75.6 | 79.5 | -1.4 |
| MC Non-STEM | 85.6 | 84.5 | 78.5 | 84.2 | 87.2 | +1.1 |
| GenQA | 79.8 | 80.3 | 75.0 | 79.1 | 68.5 | -0.5 |

→ 完全开放模型中Math和Code双位数领先，接近Qwen 2.5(open-weight)。

**Think Model (OLMo 3.1 Think 32B, Table 1/14):**

| 指标 | OLMo 3.1 Think 32B | Qwen 3 32B Think | Qwen 3 VL 32B | DeepSeek R1 Distill 32B | Qwen 2.5 32B |
|------|-------------------|-----------------|---------------|------------------------|-------------|
| MATH | **96.2** | 95.4 | **96.7** | 92.6 | 80.2 |
| AIME 2024 | 80.6 | 80.8 | **86.3** | 70.3 | 15.7 |
| AIME 2025 | **78.1** | **70.9** | **78.8** | 56.3 | 13.4 |
| HumanEval+ | 91.5 | 91.2 | 90.6 | 92.3 | 82.6 |
| LiveCodeBench v3 | 83.3 | **90.2** | 84.8 | 79.5 | 49.9 |
| IFEval | **93.8** | 86.5 | 85.5 | 78.7 | 81.9 |
| IFBench | **68.1** | 37.3 | 55.1 | 23.8 | 36.7 |
| MMLU | 86.4 | 88.8 | 90.1 | 88.0 | 84.6 |
| AlpacaEval 2 LC | 69.1 | 75.6 | 80.9 | 26.2 | 81.9 |

→ 在MATH(96.2)和IFEval(93.8)上超越或持平Qwen 3，AIME 2025(78.1)接近Qwen 3 VL(78.8)。**训练token仅为Qwen 3的~1/6。**

**Post-training阶段性贡献 (Table 14, 32B Think):**

| 阶段 | MATH | AIME 2024 | AIME 2025 | HumanEval+ | IFEval | IFBench |
|------|------|----------|----------|-----------|--------|---------|
| SFT | 95.6 | 73.5 | 66.2 | 90.0 | 83.9 | 37.0 |
| +DPO | 95.9(+0.3) | 76.0(+2.5) | 70.7(+4.5) | 91.6(+1.6) | 80.6(-3.3) | 34.4(-2.6) |
| +RL(3.0) | 96.1(+0.2) | 76.8(+0.8) | 72.5(+1.8) | 91.4(-0.2) | 89.0(+8.4) | 47.6(+13.2) |
| +RL(3.1) | 96.2(+0.1) | **80.6(+3.8)** | **78.1(+5.6)** | 91.5 | **93.8(+4.8)** | **68.1(+20.5)** |

→ RL阶段贡献最大的是AIME(+10.6/+11.9 from SFT)和IF(+9.9/+31.1 from SFT)。延长RL(3.0→3.1)在IFBench上+20.5pt的巨大提升。

**Instruct Model (OLMo 3.1 Instruct 32B, Table 25):**

| 指标 | OLMo 3.1 Inst 32B | Qwen 3 32B(NoThink) | Qwen 3 VL 32B Inst | Qwen 2.5 32B |
|------|-------------------|-------------------|-------------------|-------------|
| MATH | 93.4 | 84.3 | 95.1 | 80.2 |
| AIME 2025 | 57.9 | 21.3 | 64.2 | 13.4 |
| IFEval | 88.8 | 87.5 | 88.1 | 81.9 |
| IFBench | **39.7** | 31.3 | 37.2 | 36.7 |
| BFCL v3 | 58.8 | 63.1 | 66.3 | 62.8 |
| LitQA2 | **55.6** | 46.7 | 32.0 | 26.2 |
| AlpacaEval 2 LC | 59.8 | 67.9 | 84.3 | 81.9 |

→ IFBench(39.7)超越所有同尺度模型，LitQA2(55.6)大幅领先（MCP tool-use能力）。

**Long-context (Table 12):**

| 模型 | RULER 4K | RULER 32K | RULER 65K | HELMET 32K | HELMET 65K |
|------|---------|----------|----------|-----------|----------|
| OLMo 3 32B | 96.10 | 90.42 | 79.70 | 49.36 | 43.15 |
| Qwen 2.5 32B | 96.03 | 90.42 | 80.73 | 56.06 | 51.73 |
| Gemma 3 27B | 94.45 | 84.26 | 60.33 | 44.60 | 35.67 |

→ RULER上与Qwen 2.5持平，HELMET上稍有差距。考虑到扩展阶段仅100B tokens，这是强结果。

**训练成本：** ~$2.75M，1024 H100 GPUs，56天（预训练47天 + 后训练9天），$2/H100-hour计算。

### 归因分析 (Ablation Study)

**按贡献大小排序的关键组件：**

1. **Midtraining数据扩展**（贡献最大）：从OLMo 2的纯数学扩展到Math+Code+QA+Thinking四领域100B tokens，是base model数学和代码能力跃升的主要来源。其中：
   - CraneMath(5.62B tokens)：微退火测试MATH+18.5pt, GSM8K+27.4pt（最有效的单一数据源）
   - TinyMATH(1.14B tokens)：MATH+13.2pt, GSM8K+13.9pt
   - Dolmino-1 Math(10.7B tokens, 延续OLMo 2)：MATH+10.4pt, GSM8K+38.2pt

2. **Constrained Data Mixing**（次大贡献）：Figure 9显示优化后的web数据混合比例（大幅上调STEM主题）在1B模型上平均BPB提升0.056，max提升0.209。仅13/54任务有轻微退化（均<0.035）。

3. **Delta Learning DPO → RL的串联效果**：Table 22证明DPO+RL(Avg 74.1) > SFT+RL(71.9) > SFT+DPO(72.7) > SFT only(70.1)。DPO为RL提供了更好的起点。

4. **OlmoRL基础设施优化**：Table 23量化：continuous batching+inflight updates使训练从881→2949 tok/s(3.3x加速)，MBU从12.9%→43.2%。这使得长RL训练（750→2300步）在实际中可行。

5. **Think SFT → Instruct SFT的warm-start**（Table 29）：从Think SFT起步训练Instruct模型平均提升3.3pt（MATH+5.6, Code+4.9, IFEval+3.7），成本接近零。

### 可信度检查

- ✅ **评估去污染**：Section 3.5.3详述了基于n-gram和语义匹配的去污染方法。Section 6.2用spurious reward实验验证了去污染有效性（Figure 27：随机奖励训练不产生任何提升）。
- ✅ **标准评估框架**：使用公开的OLMES框架，所有评估代码开源。
- ✅ **方差报告**：Section 4.1.1报告了每个评估指标的方差分析（3次运行×14个模型），将benchmark分为high-variance(GPQA 1.48, AlpacaEval 1.24)、stable(ZebraLogic 0.56)、very-stable(MATH 0.25)三档。
- ✅ **OlmoBaseEval设计**：43个benchmark（OLMo 2的4倍），SNR分析移除噪声benchmark，Base Easy proxy metric在小规模即有信号。
- ⚠️ **与Qwen 3的对比需谨慎**：Qwen 3未公开base model和训练数据，无法判断其36T tokens中是否包含评测数据。
- ⚠️ **AlpacaEval 2 LC上OLMo 3.1 Think(69.1)低于Qwen 3(75.6)**，延长RL(3.0→3.1)导致AlpacaEval下降5pt，说明reasoning-chat存在trade-off。
- ⚠️ **MMLU/GPQA/Knowledge任务上持续落后Qwen**：论文推测因为Qwen通过蒸馏大模型获得知识，而OLMo 3完全自主训练。

---

## 专家批判 (Critical Review)

### 隐性成本（论文未明说的代价）

1. **配方探索成本远超"应用配方"成本：** 报告的$2.75M/56天只计算了最终配方的执行。实际探索成本包括：midtraining进行了5轮集成测试（每轮100B tokens on 512 GPUs）；仅math domain就做了80+次微退火实验（每次10B tokens on 256 GPUs, 数小时）；SFT扫4个learning rate×256 GPUs并行36小时；DPO多次sweep因集群不稳定延长到多天。保守估计探索成本至少是执行成本的2-3倍。

2. **RL推理开销极度不对称：** 32B Think的OlmoRL中，20个H100节点用于vLLM推理 vs 仅8个用于训练，推理占总计算的5x。7B更极端：7节点推理 vs 2节点训练=14x比例。原因是thinking模型平均生成长度14,628 tokens（最大32K），推理是绝对瓶颈。即使有continuous batching，static batching下54%的计算会被浪费（32K max vs 14.6K mean）。

3. **7B首次RL运行耗时15天（无基础设施优化），优化后降到6天。** 但优化本身（continuous batching + inflight updates + better threading）是重大工程投入。Table 23量化：OLMo 2到OLMo 3的基础设施改进使throughput从881→2949 tok/s（3.3x），MBU从12.9%→43.2%。

4. **评估消耗总计算的10-20%（Section 4.1.1）。** Thinking模型每个benchmark需生成最长32K tokens×32 samples（如AIME的Avg@32）。高方差评估（GPQA std=1.48, AlpacaEval std=1.24）需要3次运行取平均，进一步放大评估成本。

5. **DPO数据量是敏感超参且存在反直觉现象。** Figure 23显示：AlpacaEval和ZebraLogic在75-100K样本时达峰值，更多数据反而hurt。AIME则不饱和。不同task的最优DPO数据量不同，需要逐task sweep——但论文的做法是"sweep learning rate和dataset size作为超参"，本质是暴力搜索。

6. **延长RL训练(3.0→3.1)产生trade-off。** AIME 2025 +5.6pt、IFBench +20.5pt，但AlpacaEval -5pt。reasoning和chat存在跷跷板效应，论文选择了偏向reasoning。

### 最值得复用的技术

1. **Delta Learning（实现成本: 改1行代码, 收益: 显著）。** 仅需将DPO的reference model从base model改为当前SFT checkpoint。Table 21证明：直接SFT on chosen反而掉分(70.3→64.5)，而Delta Learning DPO提升到72.9。Table 22进一步证明DPO+RL(74.1) > SFT+RL(71.9)。任何做偏好调优的团队都应该立即采用。

2. **Active Sampling（实现成本: 中等, 收益: RL训练稳定性质变）。** 持续从actor pool拉取结果并过滤零梯度样本，替代传统的3x oversampling。Figure 26显示batch中非零梯度样本比例从持续下降变为稳定在100%，训练loss方差大幅降低。对任何GRPO/PPO训练都有价值。

### 最大的坑

1. **Constrained mixing的swarm方法需要几十个30M模型并行训练。** 5×domain数意味着24个web topics需要120个proxy models。没有大规模集群难以复现。**变通方案：** 减少到3x domain数，或用更小的proxy(10M)，或仅对最重要的few domains做swarm。

2. **DPO的"高对比"要求容易被忽视。** Table 32显示：用高质量模型池生成的chosen/rejected（对比度低）反而不如OLMo 2的旧数据。必须刻意用弱模型（如Qwen3-0.6B）生成rejected，或用delta-aware GPT judge刻意选最差response。"用最新最强的模型生成训练数据"这个直觉在DPO中是错的。

### 关联技术对比

1. **vs DeepSeek R1：** OLMo 3证明不需蒸馏即可获得强思维链能力（MATH 96.2% vs R1-Distill 92.6%），但代价是更长的RL训练（750→2300步）。R1的优势是直接从base model做RL-Zero就能emergent reasoning，OLMo 3需要SFT+DPO+RL三阶段。OLMo 3 RL-Zero提供了首个完全开放的R1-Zero风格基准，且用spurious reward实验（Figure 27）验证了无数据泄露——这是R1/DAPO都无法做到的。

2. **vs MiniCPM的WSD LRS：** OLMo 3用传统Cosine LRS（7B一个epoch完整跑完）和截断Cosine（32B在5.5T处截断），未采用WSD。原因可能是：OLMo 3已经通过midtraining的阶段化设计实现了WSD的核心价值（"从任意checkpoint出发退火获得最优模型"），不需要WSD的"无预设终点"特性。但WSD在midtraining内部可能仍有价值——论文未讨论。

3. **vs Llama 3的数据工程：** 两者都在midtraining中注入高质量数据，但OLMo 3的差异化在于：(a) 完全公开了constrained mixing的优化过程和最终配比（Llama 3不公开）；(b) olmOCR提供了独特的学术PDF数据源（972B tokens，Llama 3无此数据）；(c) quality-aware upsampling替代了flat filtering（DCLM/Llama的做法），在数据受限场景下更优。

4. **vs SmolLM3/Marin/Apertus（同期完全开放模型）：** OLMo 3的关键优势是post-training管线的完整性（SFT+DPO+RL三阶段 vs 其他模型通常只有SFT或SFT+DPO）。Table 1显示OLMo 3.1 Think 32B在MATH上96.2% vs Marin的49.2%(Instruct)——差距主要来自post-training的深度，而非base model。

---

## 机制迁移分析 (Mechanism Transfer Analysis)

#### 机制解耦 (Mechanism Decomposition)

| 原语名称 | 本文用途 | 抽象描述 | 信息论/几何直觉 |
|---------|---------|---------|---------------|
| Swarm-based Constrained Mixing | 9T数据池→5.93T训练mix的最优配比搜索 | 小规模proxy集群采样配比空间→回归建模→约束优化 | 用低维代理(30M)的BPB作为高维配比空间的"温度计"，回归建立配比→性能的可微映射，在token数约束的可行域内做梯度下降 |
| Conditional Mixing | 数据源变更时的增量配比更新 | 冻结已有最优为不动点→仅在新增维度搜索 | 高维优化的子空间分解：假设已有最优解在新增维度的投影仍然近似最优，只搜索正交补空间 |
| Quality-Aware Upsampling | 同topic内按质量差异化重复训练数据 | 连续凸单调曲线控制的数据重采样（底部丢弃→中间线性→顶部饱和） | 在数据流形上按信息密度倾斜采样——高质量区域entropy低但signal高，低质量区域entropy高但signal低（噪声），用参数化曲线平滑控制采样密度 |
| Delta Learning | DPO的reference model用当前SFT checkpoint替代base model | 自适应对比基准：在当前策略的决策边界附近构造对比信号 | 最大化Fisher信息：在参数空间中，当前策略附近的对比梯度信息最大（局部曲率最高），远离决策边界的对比冗余 |
| Active Sampling | RL训练中持续补充非零梯度样本到batch | 在线难例挖掘：持续监测样本梯度信号，动态替换已"解决"的样本 | 随策略改进，更多样本的reward方差→0→梯度消失。主动重采样等价于在非平稳分布上维持恒定的信息增益率 |

#### 迁移处方 (Transfer Prescription)

**原语1: Constrained Mixing → 推荐系统多源特征/数据配比**
- **目标领域+问题：** 推荐模型训练中多源数据（用户行为日志、商品属性、上下文特征、UGC文本）的配比优化。当前通常凭经验设定。
- **怎么接：** 每个数据源作为一个domain。训练轻量proxy推荐模型（如简化双塔, 100K参数）作为swarm，每个用不同配比采样训练数据。用AUC/GAUC作为回归目标（替代BPB）。约束条件=各源可用数据量×最大重复次数。
- **预期收益：** 从启发式权重升级为数据驱动最优配比。OLMo 3中Figure 9显示优化后的mix比自然分布平均BPB改善0.056。推荐场景中CTR的微小提升（0.1%）即有商业价值。
- **风险：** 推荐场景的反馈信号（点击率）比BPB噪声大得多，proxy模型和全量模型的排序一致性需要验证（即1M参数proxy的配比偏好是否迁移到100M模型）。

**原语2: Conditional Mixing → 持续学习/在线特征工程**
- **目标领域+问题：** 推荐/搜索系统中特征源不断新增（新业务线数据、新用户信号），每次全量重训配比搜索成本太高。
- **怎么接：** 冻结已有最优特征配比为虚拟源，仅对新增特征源做proxy swarm搜索。搜索维度从N降为1+M（M为新增源数）。
- **预期收益：** OLMo 3用3轮conditional mixing避免了对24+15+24=63个domain的全量swarm（需315个proxy），改为3轮分别搜索。同理，推荐系统新增3个特征源时，只需15个proxy（5×3）而非5×(原有源数+3)。
- **风险：** 假设"已有最优在新维度的投影仍近似最优"——如果新特征源与已有源有强交互（如新数据源改变了已有源的最优比例），conditional mixing可能找到次优解。需要定期做全量校验。

**原语3: Quality-Aware Upsampling → 数据增强/课程学习**
- **目标领域+问题：** CV数据集中标注质量不均匀（crowd-sourced标注有噪声），或推荐系统中不同时间段的行为数据质量不同。
- **怎么接：** 用数据质量评估器（如标注一致性分数、时效性权重）替代fastText质量分类器。将数据分为质量分位桶（如20等分）。用凸单调曲线定义每个桶的采样率。底部X%丢弃，顶部以max_factor重复，中间平滑过渡。通过积分约束确保总采样量匹配目标。
- **预期收益：** 比hard threshold（top-K过滤）保留更多中等质量数据的信息量。OLMo 3 Appendix中提到在data-constrained setting（250B from 1T pool），quality-aware upsampling优于flat DCLM filtering。
- **风险：** 质量评估器的系统偏差会被放大——top 5%被重复7次意味着偏差被放大7倍。必须验证质量评估器在不同topic/domain上无系统性偏见。

**原语4: Delta Learning → 任意偏好调优场景**
- **目标领域+问题：** 对话系统RLHF、推荐系统的reward model训练、内容安全分类器的迭代优化。
- **怎么接：** 将DPO/RLHF中的reference model从初始base model替换为当前训练checkpoint（一行代码改动：`ref_model = current_sft_model` 而非 `ref_model = base_model`）。Chosen/rejected数据不变。
- **预期收益：** Table 21证明：对OLMo 3 7B SFT模型，直接SFT on Qwen3-32B chosen responses反而掉分(70.3→64.5)，而Delta Learning DPO提升(70.3→72.9)。信号集中在当前决策边界附近，避免"太好vs太差"的低效对比。
- **风险：** 如果chosen/rejected本身质量差异极大（如human expert vs random noise），Delta Learning退化为标准DPO——因为当前checkpoint的概率分布对两者的区分度已经很高。更适合chosen/rejected都相对高质量但有细微差异的场景。

**原语5: Active Sampling → 任何策略梯度RL**
- **目标领域+问题：** 机器人控制RL、游戏AI训练、推荐系统的在线策略优化中，随着策略改进，大部分训练样本的梯度趋近于零。
- **怎么接：** 在GRPO/PPO训练循环中，持续从replay buffer / environment中拉取新completions，过滤掉组内方差为零（即所有responses都正确或都错误）的样本组。替代传统的固定oversampling率（如DAPO的3x）。
- **预期收益：** Figure 26显示batch中有效样本比例从逐步下降（vanilla GRPO）变为稳定100%。训练loss方差大幅降低。OLMo 3在此基础上实现了更长更稳定的RL训练（2300步 without collapse）。
- **风险：** 只训练"难例"可能导致过拟合于难例分布，忽略简单但重要的general能力维持。需要与diversity constraint结合（如保留一定比例的random样本）。

#### 机制家族图谱 (Mechanism Family Tree)

**前身 (Ancestors):**
- **Chinchilla (Hoffmann et al., 2022):** compute-optimal训练理论基础。OLMo 3的数据配比优化本质是在Chinchilla框架下寻找"给定compute budget的最优data mix"，但超越了Chinchilla只考虑数据总量的局限，引入了数据质量和domain维度。
- **DCLM (Li et al., 2024):** web数据质量过滤框架。OLMo 3的第一轮constrained mixing基于DCLM-Baseline数据做优化，且quality classifier的训练正负例来自DCLM方法论。但OLMo 3用quality-aware upsampling替代了DCLM的flat filtering。
- **RegMix (Liu et al., 2024):** swarm-based数据混合方法先驱，用小模型集群探索混合空间。OLMo 3直接继承了swarm构造和回归优化的两阶段框架，新增了conditional mixing和质量约束。
- **OLMo 2 (OLMo et al., 2024):** 直接前代，贡献了midtraining概念、Dolmino数据、microanneal方法论。OLMo 3在此基础上扩展了midtraining domain（从纯math到四领域）、新增了长上下文阶段、升级了post-training管线（加入Delta Learning和多域RLVR）。
- **DeepSeek R1 (Guo et al., 2025):** 证明RLVR可以从base model bootstrap reasoning能力。OLMo 3的RL-Zero直接受启发于R1-Zero，但提供了完全开放的数据和去污染验证。
- **SwallowMath (Fujii et al., 2025):** 发现对FineMath进行LLM重写可以大幅提升数学能力。OLMo 3的CraneMath是其独立复现（用Qwen3替代Llama以规避license限制），在microanneal中MATH+18.5pt。

**兄弟 (Siblings):**
- **Stanford Marin 32B (Hall et al., 2025):** 同期完全开放，base model GenQA能力略强(80.3 vs 79.8)但Math(49.3 vs 61.9)和Code(30.8 vs 39.7)显著弱于OLMo 3。缺乏thinking能力的post-training管线。
- **Apertus 70B (Apertus Team, 2025):** 同期完全开放，参数更多(70B)但所有评估指标均不及OLMo 3 32B，说明数据质量和训练方法论的重要性超过模型规模。
- **LLM360 K2-V2 70B (Team et al., 2025):** 同期开放训练日志，但Think Instruct版本在Table 1中AlpacaEval评估失败（token解析错误），说明post-training工程成熟度不足。
- **DAPO (Yu et al., 2025):** RLVR算法改进（dynamic sampling等），OLMo 3 RL-Zero在类似设置下达到接近DAPO的性能，但用更少的训练步数（Figure 38），且无数据泄露风险。

**后代 (Descendants):** 暂无（2025年12月发布）

**创新增量：** OLMo 3在族谱中的独特位置是**"系统级集成创新"**——它没有发明constrained mixing（来自RegMix）、没有发明Delta Learning（来自Geng et al.）、没有发明GRPO（来自DeepSeek），但首次将这些技术系统性集成到一个完全开放的端到端管线中，并证明这种集成可以在推理能力上接近最强半开源模型（MATH 96.2% vs Qwen 3的96.7%）。同时，conditional mixing和quality-aware upsampling是原创的数据工程方法，RL-Zero提供了首个无数据泄露的RLVR研究平台。

---

## 背景知识补充 (Background Context)

- **Sliding Window Attention (SWA)** [Beltagy et al., 2020]：每个token只注意力前window个token的稀疏注意力模式。**本文角色：** OLMo 3在3/4层使用SWA(window=4096)以降低预训练8K序列的计算开销，最后一层保持全注意力确保信息聚合。与Flash Attention兼容。

- **YaRN (Yet another RoPE extensioN)** [Peng et al., 2023]：通过修改RoPE的频率参数（提高base theta）和引入温度缩放，将训练在短上下文上的模型扩展到更长序列。**本文角色：** OLMo 3用YaRN将上下文从8K扩展到65K，theta从1M→100M。选择YaRN而非PI或NTK-aware scaling的原因是其在RULER benchmark上表现最优（Figure 13a）。

- **GRPO (Group Relative Policy Optimization)** [Shao et al., 2024, DeepSeek]：策略梯度RL算法，不需要单独的critic/value model。对每个prompt生成G个responses，用组内相对reward作为advantage估计（公式2）。**本文角色：** OlmoRL的核心算法基础，OLMo 3在其上加入truncated importance sampling cap ρ（Yao et al., 2025）和asymmetric clipping（ε_low ≠ ε_high）。

- **olmOCR** [Poznanski et al., 2025a]：Allen AI开发的PDF→线性化纯文本转换工具，能处理含数学公式、表格、图片的学术PDF。**本文角色：** 提供972B tokens的学术文档数据（108M documents after filtering），是长上下文扩展阶段的核心数据源（22.3M docs > 8K tokens, 4.5M > 32K tokens）。版本v0.1.49-0.1.53用于批量处理238M原始PDFs。

- **Microanneal方法论** [OLMo et al., 2024]：快速数据评估方法——从预训练checkpoint出发，取5B目标数据+5B web数据混合退火10B tokens，对比仅web数据的baseline。**本文角色：** midtraining数据筛选的核心工具，每次microanneal只需数小时（vs 集成测试的数天）。仅math domain就进行了80+次microanneal，评估了25个候选数据源。

- **WebOrganizer** [Wettig et al., 2025]：web文档的主题分类器，将文档分为24个topic类别（如Science/Tech、Entertainment、Politics等）。**本文角色：** 用于Dolma 3 Mix的topic-level数据分区，是constrained mixing的domain定义基础。OLMo 3用FastText蒸馏了一个轻量版（Table 37：overall P/R=0.762），处理万亿token规模的分类。

- **Duplodocus** [Allen AI]：Rust实现的大规模分布式去重工具，支持精确哈希去重和MinHash模糊去重。**本文角色：** 处理OLMo 3的三阶段去重管线中的前两阶段（精确+MinHash），将38.8B文档缩减到9.8B。是万亿token规模去重的关键基础设施。

- **Model Flow概念** [本文提出]：指语言模型的完整生命周期——从数据收集、处理、每个训练阶段、到评估的全流程。**本文角色：** OLMo 3的核心理念——"不仅发布终点（最终权重），更发布路径（数据+代码+中间检查点+评估日志）"，使社区可以从任意节点介入修改。这是OLMo 3与Qwen/Llama等"open-weight"模型的本质区别。

- **Delta Learning** [Geng et al., 2025]：偏好学习中用当前模型检查点（而非原始base model）作为DPO的reference model的方法。**本文角色：** OLMo 3 Think和Instruct的DPO阶段都采用此方法。Table 21实证其价值：直接SFT on chosen掉分，Delta Learning DPO提升。Table 22进一步证明DPO→RL的串联优于SFT→RL。
