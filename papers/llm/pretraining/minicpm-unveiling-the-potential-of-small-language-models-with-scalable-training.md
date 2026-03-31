---
abstract: The burgeoning interest in developing Large Language Models (LLMs) with
  up to trillion parameters has been met with concerns regarding resource efficiency
  and practical expense, particularly given the immense cost of experimentation. This
  scenario underscores the importance of exploring the potential of Small Language
  Models (SLMs) as a resource-efficient alternative. In this context, we introduce
  MiniCPM, specifically the 1.2B and 2.4B non-embedding parameter variants, not only
  excel in their respective categories but also demonstrate capabilities on par with
  7B-13B LLMs. While focusing on SLMs, our approach exhibits scalability in both model
  and data dimensions for future LLM research. Regarding model scaling, we employ
  extensive model wind tunnel experiments for stable and optimal scaling. For data
  scaling, we introduce a Warmup-Stable-Decay (WSD) learning rate scheduler (LRS),
  conducive to continuous training and domain adaptation. We present an in-depth analysis
  of the intriguing training dynamics that occurred in the WSD LRS. With WSD LRS,
  we are now able to efficiently study data-model scaling law without extensive retraining
  experiments on both axes of model and data, from which we derive the much higher
  compute optimal data-model ratio than Chinchilla Optimal. Additionally, we introduce
  MiniCPM family, including MiniCPM-DPO, MiniCPM-MoE and MiniCPM-128K, whose excellent
  performance further cementing MiniCPM&#39;s foundation in diverse SLM applications.
  MiniCPM models are available publicly at this https URL .
arxiv_categories:
- cs.CL
arxiv_id: '2404.06395'
authors:
- Shengding Hu
- Yuge Tu
- Xu Han
- Chaoqun He
- Ganqu Cui
- Xiang Long
- Zhi Zheng
- Yewei Fang
- Yuxiang Huang
- Weilin Zhao
- Xinrong Zhang
- Zheng Leng Thai
- Kaihuo Zhang
- Chongyi Wang
- Yuan Yao
- Chenyang Zhao
- Jie Zhou
- Jie Cai
- Zhongwu Zhai
- Ning Ding
- Chao Jia
- Guoyang Zeng
- Dahai Li
- Zhiyuan Liu
- Maosong Sun
baselines:
- Llama2-7B
- Llama2-13B
- Mistral-7B
- Gemma-7B
- Phi-2 (2B)
- Qwen-7B
- TinyLlama-1.1B
- Qwen-1.8B
- Gemma-2B
- StableLM-Zephyr-3B
- Deepseek-7B
- Llama2-34B
- Deepseek-MoE (16B)
- Yarn-Mistral-7B-128K
- ChatGLM3-6B-128K
category: llm/pretraining
code_url: https://github.com/OpenBMB/MiniCPM
core_contribution: new-method/new-framework/empirical-study
datasets:
- C4
- MMLU
- CMMLU
- C-Eval
- HumanEval
- MBPP
- GSM8K
- MATH
- BBH
- ARC-e
- ARC-c
- HellaSwag
- MTBench
- InfiniteBench
- UltraFeedback
- Dolma
- Pile
date: '2024-04-09'
doi: null
keywords:
- Small Language Models
- Scaling Law
- Learning Rate Scheduler
- Warmup-Stable-Decay
- Tensor Program
- Continuous Pre-training
- Mixture-of-Experts
- Model Wind Tunnel
- Compute-Optimal Training
- Data-Model Ratio
metrics:
- Accuracy
- Pass@1 (HumanEval/MBPP)
- C4 Loss (byte-level)
- MTBench Score
- Perplexity (PPL)
publication_type: preprint
tags:
- Small Language Models
- Scaling Law
- Learning Rate Scheduler
- Warmup-Stable-Decay
- Continuous Pre-training
- Compute-Optimal Training
- Data-Model Ratio
title: 'MiniCPM: Unveiling the Potential of Small Language Models with Scalable Training
  Strategies'
tldr: 提出WSD学习率调度器和模型风洞实验方法，使1.2B/2.4B小模型MiniCPM达到7B-13B大模型的性能，同时发现远高于Chinchilla Optimal的数据-模型最优比例。
url: https://arxiv.org/abs/2404.06395
venue: null
---

## 核心速览 (Executive Summary)

- **TL;DR (≤100字):** MiniCPM通过Tensor Program稳定超参跨尺度迁移、WSD学习率调度器实现持续训练与高效scaling law测量、以及两阶段预训练策略混入高质量数据，使2.4B/1.2B小模型在多数基准上匹配甚至超越Mistral-7B和Llama2-13B，并揭示了远高于Chinchilla Optimal（约192×而非20×）的最优数据-模型比。

- **一图流 (Mental Model):** 如果传统Cosine LRS训练像是一次性铸造一把固定长度的剑——你必须预先决定剑的长度（训练步数），铸造完成后无法再延长。那么WSD LRS就像是锻造一根可以无限延伸的钢条（Stable阶段），任何时候你都可以选择淬火（Decay阶段）来获得锋利的刀刃，而且淬火只需要极短的时间（10%的步数）。这意味着你永远不需要提前决定"这根钢条要多长"。

- **核心机制一句话 (Mechanism in One Line):** 将学习率调度显式拆分为高学习率稳定探索阶段和短时衰减收敛阶段，使得任意中间检查点都可快速退火至最优损失，从而实现持续训练与O(m)复杂度的scaling law测量。

---

## 动机与第一性原理 (Motivation & First Principles)

- **痛点 (The Gap):**
  1. **Cosine LRS的致命缺陷：** 当前主流的Cosine LRS（被Kaplan 2020、Chinchilla等广泛采用）要求提前指定总训练步数T，且必须T=S（总步数=cosine周期）才能获得最优性能。这意味着如果你想延长训练，必须从头重训——这对LLM来说成本惊人。
  2. **Scaling law测量的二次成本：** 传统scaling law实验需要在m个模型规模×m个数据规模上训练，成本是O(m²)C，对于资源有限的研究者来说不可承受。
  3. **SLM能力不足：** 现有SLM（Phi系列、TinyLlama等）要么缺乏LLM级别的综合能力，要么训练方法不透明且不可迁移到更大规模。

- **核心洞察 (Key Insight):**
  Because Cosine LRS的优良性能实际上来源于两个独立的机制（长时间高学习率探索全局最优 + 充分的学习率衰减找到局部最优）→ 这两个阶段可以被显式解耦 → 解耦后Stable阶段可以无限延长而Decay阶段只需10%的步数即可收敛 → 因此任何Stable阶段的检查点都可以被快速"退火"到接近Cosine(T=S)的最优损失 → 这同时解锁了持续训练和高效scaling law测量两个能力。

- **物理/直觉解释:** 想象一个人在山地中寻找最低谷。高学习率就像大步跨越山脊，帮你到达正确的大盆地（全局探索）；低学习率就像在盆地里小步微调，精确找到最低点（局部收敛）。Cosine LRS把这两件事混在一起：学习率从头到尾慢慢降低。WSD则说："先尽情大步走，你觉得探索够了，再花10%的时间小步找最低点就行。" 关键洞察是：大步走的过程中虽然loss看起来没降多少，但模型其实已经把自己"搬"到了一个好的盆地里——退火只是帮它"坐下来"而已。

---

## 方法详解 (Methodology)

#### 直觉版 (Intuitive Walk-through)

论文的方法由三个互相支撑的部分组成，参考Figure 1-6和Figure 15可以理解全貌：

**Part 1: 模型风洞实验 (Model Wind Tunnel Experiments)**

旧方法：每个新模型规模都需要重新搜索超参数（学习率、batch size等），对于LLM这是不可承受的。

新方法：使用Tensor Program（µP）技术，在0.009B的微型模型上搜索最优超参数（scale_depth=1.4, scale_emb=12, init_std=0.1, lr=0.01），然后直接迁移到2.4B。实验验证模型从0.04B到2.1B，最优学习率始终稳定在0.01附近（Figure 3）。同时通过三个尺度（0.009B, 0.03B, 0.17B）的实验，建立了batch size与C4 loss的关系：bs = 1.21×10⁶ / L^{6.2140}。

**Part 2: WSD学习率调度器**

旧方法（Cosine LRS）：学习率从高到低画一个完整的cosine曲线，必须提前知道总步数T，且T=S时最优（Figure 4）。如果你想继续训练，之前的cosine衰减就浪费了。

新方法（WSD LRS）：如Figure 15所示，显式分三段：
- Warmup：短暂的学习率爬升
- Stable：以恒定的最高学习率η持续训练（可以无限延长）
- Decay：短暂的学习率衰减（只需总步数的~10%）

Figure 5展示了关键现象：在Stable阶段loss下降缓慢，但进入Decay阶段后loss急剧下降，最终达到与Cosine(T=S)相当甚至更低的loss。更重要的是，你可以在任意Stable检查点执行Decay，而不需要从头训练。

**Part 3: 两阶段预训练策略**

旧方法：预训练全程使用粗粒度数据，然后SFT阶段才引入高质量数据。

新方法：在WSD的Decay阶段混入高质量SFT数据，利用Decay阶段loss急剧下降的特性，让模型在"退火"过程中同时吸收高质量知识。Table 1的消融实验显示，A-2（Decay阶段混入SFT数据）在所有指标上大幅超越A-1（仅预训练数据Decay + 相同SFT），例如C-Eval从40.0→52.6，MMLU从44.6→50.9。

#### 精确版 (Formal Specification)

**流程图 (Text-based Flow):**

```
[Raw Text Corpus, ~1T tokens]
    │
    ▼
┌─────────────────────────────────────────────┐
│ Stage 1: Stable Training                     │
│ LR = η = 0.01 (constant after warmup)       │
│ Batch size = 3.93M tokens                    │
│ Data: large-scale coarse pre-training data   │
│ Optimizer: Adam                              │
│ Duration: ~1T tokens                         │
│ Output: Multiple intermediate checkpoints    │
└─────────────┬───────────────────────────────┘
              │ Pick any checkpoint
              ▼
┌─────────────────────────────────────────────┐
│ Stage 2: Decay (Annealing)                   │
│ LR: exponential decay f(s-T) = 0.5^{(s-S)/T}│
│ T = 5000 steps (~20B tokens, ~10% of total) │
│ Data: pre-train + high-quality SFT data mix  │
│ Output: Annealed checkpoint                  │
└─────────────┬───────────────────────────────┘
              ▼
┌─────────────────────────────────────────────┐
│ Stage 3: SFT                                 │
│ LR: aligned with end of annealing + WSD     │
│ Data: SFT data only (no pre-train data)     │
│ Duration: ~6B tokens                        │
│ Output: Final base model                    │
└─────────────┬───────────────────────────────┘
              ▼
┌─────────────────────────────────────────────┐
│ [Optional] Stage 4: DPO Alignment           │
│ LR: 1e-5, Cosine LRS                        │
│ Data: UltraFeedback + proprietary pref data │
│ Output: MiniCPM-DPO                         │
└─────────────────────────────────────────────┘
```

**关键公式与变量：**

1. **WSD调度器核心公式：**

$$\text{WSD}(T; s) = \begin{cases} \frac{s}{W}\eta, & s < W \\ \eta, & W < s < T \\ f(s - T) \cdot \eta, & T < s < S \end{cases}$$

- $s$: 当前训练步数（物理含义：训练进度的时间坐标）
- $W$: warmup结束步数（物理含义：学习率爬升阶段的终点，影响很小）
- $T$: stable阶段结束步数（物理含义：开始退火的时间点，可以任意选择）
- $S$: 总训练步数（物理含义：训练终止点）
- $\eta$: 最大学习率（物理含义：探索强度，MiniCPM中为0.01）
- $f(s-T)$: 衰减函数，满足$0 < f \leq 1$且单调递减。论文使用指数衰减$f(s-T) = 0.5^{(s-S)/T}$

2. **Scaling Law拟合公式：**

$$L(N, D) = C_N N^{-\alpha} + C_D D^{-\beta} + L_0$$

- $N$: 非嵌入参数量（物理含义：模型容量）
- $D$: 训练数据量（物理含义：知识输入量）
- $\alpha, \beta$: 模型/数据的缩放指数（物理含义：每增一倍N或D对loss的贡献率）
- $L_0$: 不可约损失（物理含义：数据本身的固有熵，无论模型多大都无法消除）

3. **计算最优模型/数据规模：**

给定计算预算 $C = 6ND$：

$$N_{\text{opt}} = K_2 \left(\frac{C}{6}\right)^{\eta}, \quad \eta = \frac{\beta}{\alpha + \beta}$$

论文实测：$\alpha = 0.29, \beta = 0.23$, 平均$D_{\text{opt}}/N_{\text{opt}} = 192$，远高于Chinchilla的20。

4. **Batch Size与Loss的关系：**

$$bs = \frac{1.21 \times 10^6}{L^{6.2140}}$$

- $bs$: 最优batch size（token数）
- $L$: 当前C4 loss

**数值推演 (Numerical Example):**

假设我们有一个0.036B模型，训练80N（约2.88B）tokens的数据：

- **Cosine LRS方案：** 必须设T=80N，从头训练到80N tokens。假设最终C4 loss = 3.60。
- **WSD LRS方案：**
  - Stable阶段：lr=0.01常数，训练到80N tokens。此时C4 loss ≈ 3.80（比Cosine同步数时高，因为没有衰减）。
  - Decay阶段：从80N检查点开始，以指数衰减训练额外8N tokens（10%）。loss从3.80急剧下降到≈3.58，等于甚至略低于Cosine(80N)的3.60。
  - 复用能力：如果之前在40N保存过检查点，可以直接从40N执行4N的Decay，得到Cosine(40N)的最优loss≈3.80，无需重训。

对于scaling law测量：
- 传统方法：6个模型×6个数据量 = 36次完整训练 = O(36C)
- WSD方法：6个模型各训练一次到最大数据量，然后从中间检查点Decay = 6次完整训练 + 36次短Decay = O(6C + 36×0.1C) ≈ O(10C)

**伪代码 (Pseudocode):**

```python
# WSD Learning Rate Scheduler
class WSDScheduler:
    def __init__(self, eta=0.01, warmup_steps=W, stable_end=T, total_steps=S):
        self.eta = eta
        self.W = W
        self.T = T  # stable阶段结束步
        self.S = S  # 总步数
        self.decay_steps = S - T  # decay阶段长度, 约0.1 * T
    
    def get_lr(self, step):
        if step < self.W:
            return (step / self.W) * self.eta          # Warmup: 线性增长
        elif step < self.T:
            return self.eta                              # Stable: 恒定最大lr
        else:
            # Exponential decay: f(s-T) = 0.5^((s-S)/decay_steps)
            return (0.5 ** ((step - self.S) / self.decay_steps)) * self.eta

# 持续训练 + Scaling Law 测量
def continuous_training_with_scaling(model, data_stream, checkpoints=[10N, 20N, 40N, 60N]):
    """
    一次Stable训练 → 多次Decay → 多个最优loss测量点
    """
    # Phase 1: Stable training (恒定高学习率)
    scheduler = WSDScheduler(eta=0.01, stable_end=max(checkpoints))
    saved_checkpoints = {}
    
    for step, batch in enumerate(data_stream):
        lr = scheduler.get_lr(step)  # 在stable阶段，lr始终=0.01
        loss = train_step(model, batch, lr)
        
        if step in checkpoints:
            saved_checkpoints[step] = save_checkpoint(model)
    
    # Phase 2: 从每个检查点执行短暂Decay
    optimal_losses = {}
    for ckpt_step, ckpt in saved_checkpoints.items():
        model_copy = load_checkpoint(ckpt)
        decay_steps = int(0.1 * ckpt_step)  # 10% 的decay
        
        # 用混合数据(预训练+SFT)进行decay
        decay_scheduler = WSDScheduler(
            eta=0.01, stable_end=0, total_steps=decay_steps
        )
        for s in range(decay_steps):
            lr = decay_scheduler.get_lr(s)  # 指数衰减
            batch = sample_mixed_data(pretrain_data, sft_data)
            loss = train_step(model_copy, batch, lr)
        
        optimal_losses[ckpt_step] = evaluate(model_copy)
    
    return optimal_losses  # 用于拟合 L(N, D) scaling law
```

#### 设计决策 (Design Decisions)

| 设计选择 | 替代方案 | 论文是否对比 | 结果 | 核心trade-off |
|---------|---------|-----------|------|-------------|
| WSD LRS | Cosine LRS, Linear LRS, CosineLoop LRS | ✅ Figure 4, 5 | WSD匹配Cosine(T=S)，且支持持续训练 | 灵活性 vs. 简洁性：WSD多一个"何时开始decay"的决策，但换来不需要预定义总步数 |
| 指数衰减 f(s)=0.5^{(s-S)/T} | 线性衰减、cosine衰减 | ⚠️ 未充分对比 | 论文仅提到使用指数衰减，未系统对比其他衰减函数 | 论文未讨论 |
| Decay步数=10% | 2.5%, 5%, 更多 | ✅ Figure 5 | 10%足够收敛，2.5%不够 | 效率 vs. 充分性：太少收敛不够，太多浪费stable训练的复用优势 |
| Decay阶段混入SFT数据 | 仅预训练数据Decay + 更多SFT | ✅ Table 1 | Decay混入SFT远优于单纯增加SFT量 | 数据利用时机：decay阶段的loss急剧下降是一个特殊的学习窗口 |
| Tensor Program (µP) | 手动调参、grid search | ✅ Figure 3, 14 | lr=0.01从0.04B到2.1B保持稳定 | 前期投入（理解µP）vs. 后期收益（不需要为每个尺度调参） |
| Deep-and-thin架构 | 标准比例（如Phi-2的32层） | 部分（与Phi-2隐式对比） | 2.4B用40层（vs Phi-2的32层），1.2B更极端用52层 | 更深更窄 = 更好的表征能力，但可能更难并行化 |
| GQA（仅1.2B） | 标准MHA | 论文未直接对比 | 用于减少参数量 | 参数量 vs. 注意力表达能力 |
| 嵌入层共享 | 不共享 | 128K版本取消共享以支持并行 | 节省0.2-0.3B参数 | 参数效率 vs. 训练灵活性 |

#### 易混淆点 (Potential Confusions)

1. **关于Stable阶段的loss停滞**
   - ❌ 错误理解: Stable阶段loss不降说明模型没在学习，是在浪费计算。
   - ✅ 正确理解: Stable阶段模型权重在剧烈变化（Figure 7），模型正在高学习率下探索更好的loss basin。虽然loss表面上停滞，但"势能"在积累——Decay时的急剧下降就是证据。这类似于模拟退火中高温阶段的作用。

2. **关于WSD与Cosine的性能对比**
   - ❌ 错误理解: WSD在同等计算量下比Cosine LRS获得更低的loss。
   - ✅ 正确理解: WSD的核心优势不是更低的loss，而是**灵活性**——它在任意步数都能达到与Cosine(T=S)相当的loss，而不需要预知总步数。性能上WSD ≈ Cosine(T=S)，但WSD支持持续训练和高效scaling law测量。

3. **关于D_opt/N_opt=192的含义**
   - ❌ 错误理解: 这意味着Chinchilla的scaling law是错的，我们应该用192倍数据训练。
   - ✅ 正确理解: 192倍是**计算最优**（compute-optimal）比例，而Chinchilla的20倍是在不同配置下得出的结果。差异主要来源于配置差异（数据质量、tokenizer、模型架构等）。但趋势一致——应该比Chinchilla建议的更侧重数据缩放。这也意味着小模型可以吸收远比之前认为的更多数据，对推理效率有利。

---

## 实验与归因 (Experiments & Attribution)

- **核心收益：**

  | 对比 | 指标 | 提升 |
  |------|------|------|
  | MiniCPM-2.4B vs Llama2-7B | Avg | 52.33 vs 35.40 (+16.93) |
  | MiniCPM-2.4B vs Mistral-7B | Avg | 52.33 vs 48.97 (+3.36) |
  | MiniCPM-2.4B vs Llama2-13B | Avg | 52.33 vs 41.48 (+10.85) |
  | MiniCPM-1.2B vs TinyLlama-1.1B | Avg | 45.67 vs 25.36 (+20.31) |
  | MiniCPM-1.2B vs Qwen-1.8B | Avg | 45.67 vs 34.72 (+10.95) |
  | MiniCPM-DPO vs Mistral-7B-Inst-v0.2 | MTBench | 7.25 vs 6.84 |
  | MiniCPM-MoE(4B activated) vs Llama2-34B | 多数指标 | 持平或超越 |
  | MiniCPM-128K vs ChatGLM3-6B-128K | ∞Bench Avg | 37.68 vs 36.57 |

- **归因分析 (Ablation Study):**

  根据Table 1的消融实验，按贡献从大到小排序：

  1. **Decay阶段混入高质量SFT数据**（贡献最大）：A-1→A-2，C-Eval +12.6, CMMLU +9.6, MMLU +6.3, GSM8K +14.6, MBPP +5.9。这是单一最大提升来源。
  2. **WSD调度器本身**：使持续训练成为可能，0.036B模型通过持续训练可以匹配0.17B模型的性能（Figure 6），以约4倍训练计算换5倍推理加速。
  3. **Tensor Program超参迁移**：Figure 3显示lr=0.01从0.04B到2.1B保持稳定，确保了风洞实验结论的可迁移性。
  4. **Deep-and-thin架构**：40层/52层的深窄架构，与MobileLLM的发现一致，但论文未提供直接的架构对比消融。
  5. **增加SFT数据量（无Decay混入）** 效果有限：B-1 vs B-2（6B vs 12B SFT），几乎无提升，说明关键不在SFT数量而在引入时机。

- **可信度检查：**
  - ✅ **正面**：评估工具UltraEval开源，评估脚本公开；对每个模型取PPL和生成两种方式中的最高分，公平对比；模型和代码完全开源。
  - ⚠️ **需注意**：(1) GeminiNano-3B数据直接引用其论文，缺少部分指标；(2) Phi-2在学术导向数据集上表现与MiniCPM持平，说明训练数据分布对基准性能有显著影响——MiniCPM的优势部分来自更广泛的数据覆盖而非纯粹的方法创新；(3) BBH上SLM普遍弱于LLM，论文坦诚指出推理能力更依赖模型规模；(4) HellaSwag上MiniCPM-2.4B得分68.25，显著低于Mistral-7B的80.43，说明在某些常识推理任务上小模型仍有差距。
  - ⚠️ **Scaling law的局限**：论文承认scaling law实验仅在SLM上进行，未在LLM上验证。192倍的D/N比可能受特定配置影响。

---

## 专家批判 (Critical Review)

- **隐性成本 (Hidden Costs):**
  1. **Decay阶段的调优成本**：虽然10%步数"足够"，但Figure 5显示2.5%就不够了——这意味着在实际应用中需要仔细选择Decay长度和衰减函数，这本身是一个需要实验验证的超参数。
  2. **Stable阶段的效率假象**：虽然Stable阶段可以无限延长，但Figure 6的power-law拟合显示收益递减明显。0.036B模型要达到0.17B的性能需要约4倍计算，这在训练端并不便宜。
  3. **数据工程的隐藏工作量**：Decay阶段需要精心设计数据混合（Figure 11右图），包含多种SFT数据和预训练数据的配比，论文未详细讨论这些比例的敏感性。
  4. **Tensor Program的学习门槛**：µP技术（width scaling + depth scaling）的正确实现需要对每个tensor的初始化、学习率、输出scaling都做特定修改（Table 7），实现复杂度不低。
  5. **Vocabulary embedding的参数占比**：2.4B模型的122K词表增加0.3B参数（占总参数12.5%），对SLM来说是显著开销。

- **工程落地建议：**
  1. **最大的坑——Decay阶段数据混合**：Table 1显示Decay数据质量对最终效果影响巨大，但论文未给出数据配比的敏感性分析。建议先在小规模模型上做配比消融。
  2. **µP实现的验证**：Table 7的操作容易出错（特别是学习率按d_m/d_base缩放），建议先在9M模型上验证lr=0.01确实是最优，再扩大规模。
  3. **batch size调度**：MiniCPM-1.2B使用了2M→4M的batch size增长（Figure 12左图loss的第一次下降），这与learning rate decay有类似效果，需要特别注意两者的交互。
  4. **128K长上下文版本**：需要禁用embedding共享以支持vocabulary parallelism，这是一个架构级别的改动，需要从训练初期就规划好。

- **关联思考：**
  - **与DeepSeek LRS的关系**：论文提到DeepSeek "bears the closest resemblance to our proposed WSD LRS"。DeepSeek也采用了类似的分阶段学习率策略，说明WSD类思路已被独立验证。
  - **与LoRA/PEFT的互补**：WSD的Decay阶段天然适合作为domain adaptation的入口。结合LoRA，可以在Stable检查点上用LoRA+Decay做领域适应，比全参数fine-tuning更高效。
  - **与MoE的协同**：MiniCPM-MoE使用Sparse Upcycling从dense检查点初始化，这依赖WSD的Stable阶段检查点质量。WSD确保了Stable检查点在各训练步数上的一致性。
  - **与FlashAttention的正交性**：WSD是训练策略，FlashAttention是计算优化，两者完全兼容。MiniCPM的deep-and-thin架构（更多层、更小hidden dim）可能在FlashAttention下有不同的效率特征。
  - **与Chinchilla的核心分歧**：192x vs 20x的差异暗示"compute-optimal"是一个高度配置依赖的概念。论文对Llama2的分析（Figure 18）估计Llama2的实际比例在70-100x，与MiniCPM更接近。

---

## 机制迁移分析 (Mechanism Transfer Analysis)

#### 机制解耦 (Mechanism Decomposition)

| 原语名称 | 本文用途 | 抽象描述 | 信息论/几何直觉 |
|---------|---------|---------|---------------|
| **Explore-then-Exploit调度** | WSD的Stable+Decay两阶段 | 在优化过程中，先以高扰动强度探索参数空间的全局结构，再以低扰动快速收敛到最近的局部最优 | 几何直觉：高学习率=在loss landscape上做大步随机游走，覆盖更多basin；低学习率=在当前basin内做梯度下降。信息论：高lr阶段最大化"已访问basin的信息熵"，低lr阶段最小化"与最近最优点的KL散度" |
| **检查点复用与退火** | 从任意Stable检查点Decay得到最优模型 | 将一次昂贵的长程训练转化为多个短程优化问题的共享前缀，通过"分支-退火"复用计算 | 几何直觉：Stable训练是一条主干路径，Decay是从路径上任意一点出发的"下坡捷径"。类似分支定界法中的公共前缀优化 |
| **退火阶段数据注入** | Decay阶段混入高质量SFT数据 | 在优化轨迹的快速收敛窗口中注入目标分布数据，利用高梯度响应率引导模型向目标分布收敛 | 信息论：Decay阶段的loss curvature增大（Figure 8），模型对数据分布变化的"感受野"变窄但"灵敏度"提高，此时注入目标分布数据的学习效率最高 |
| **跨尺度超参迁移** | Tensor Program使lr=0.01跨模型尺度稳定 | 通过理论指导的参数化方案，使优化超参数与模型宽度/深度解耦 | 几何直觉：µP使不同宽度的网络具有"几何相似"的loss landscape，因此相同的步长（lr）在不同尺度上有等效的探索效率 |

#### 迁移处方 (Transfer Prescription)

**原语1: Explore-then-Exploit调度**

- **目标：推荐系统的在线学习**
  - 具体问题：推荐模型需要持续学习新用户行为，但Cosine LRS要求预定义训练周期
  - 接入方式：将推荐模型的在线训练替换为WSD：Stable阶段用高lr持续学习用户行为流，定期（如每周）执行短Decay得到部署版本
  - 预期收益：无需重训即可持续吸收新数据，部署模型始终是当前数据的最优版本
  - 风险：推荐系统的数据分布漂移（concept drift）可能使Stable阶段累积的"探索"失效

- **目标：强化学习的策略优化**
  - 具体问题：PPO等算法的学习率调度通常是线性衰减，但最优训练步数难以预知
  - 接入方式：将PPO的lr scheduler替换为WSD，Stable阶段保持高探索，评估指标不再提升时执行Decay
  - 预期收益：自适应训练长度，避免过早衰减导致的性能损失
  - 风险：RL的非平稳性可能使Stable阶段的梯度统计不稳定

**原语2: 检查点复用与退火**

- **目标：NAS（神经架构搜索）中的权重共享**
  - 具体问题：超网络训练后子网络需要重训练才能获得最终性能
  - 接入方式：超网络用Stable训练，每个候选架构通过短Decay评估真实性能
  - 预期收益：将NAS评估成本从O(n×full_train)降低到O(1×stable + n×0.1×decay)
  - 风险：不同架构可能需要不同的Decay长度

**原语3: 退火阶段数据注入**

- **目标：多语言/多领域模型的领域适应**
  - 具体问题：通用模型适应特定领域（如医学、法律）时，全程混入领域数据可能导致通用能力退化
  - 接入方式：通用预训练用Stable阶段，领域适应数据仅在Decay阶段混入
  - 预期收益：最大化领域知识吸收效率，同时保留通用能力（因为Stable阶段是纯通用数据）
  - 风险：领域数据量过小时，10%的Decay步数可能不足以充分吸收

#### 机制家族图谱 (Mechanism Family Tree)

**WSD学习率调度的技术族谱：**

- **前身 (Ancestors):**
  - **Cosine LRS** (Loshchilov & Hutter, 2016)：将warmup和衰减统一在一个cosine周期内，是WSD的直接灵感来源
  - **SGDR (Warm Restarts)** (Loshchilov & Hutter, 2016)：CosineLoop的前身，提出学习率周期性重启，WSD的Stable阶段可以看作是一个"无限长的plateau"
  - **1cycle Policy** (Howard & Ruder, 2018)：Super-convergence中的warmup-high-decay三阶段，与WSD结构相似但目的不同（1cycle是为了快速收敛，WSD是为了持续训练）
  - **Kaplan Scaling Law** (2020)：建立了loss、model size、data size的幂律关系，是WSD用于scaling law测量的理论基础
  - **Chinchilla** (Hoffmann et al., 2022)：建立了compute-optimal的D/N比，WSD的实验直接挑战了其具体比例

- **兄弟 (Siblings):**
  - **DeepSeek LRS** (Bi et al., 2024)：同时期独立提出的类似分阶段学习率策略，论文明确提到"bears the closest resemblance"
  - **Yi-9B的batch size调度** (Young et al., 2024)：通过增大batch size替代降低学习率，与WSD的理念互补

- **后代 (Descendants):**
  - **DeepSeek-V2/V3**：后续工作延续并完善了WSD类学习率策略
  - **持续预训练范式**：WSD使得"训练一个base模型然后持续喂数据"成为标准流程，影响了后续多个开源模型的训练策略

**创新增量：** WSD的核心创新不是"分阶段学习率"这个idea本身（1cycle早已存在），而是**将其与持续训练和高效scaling law测量这两个实际需求连接起来**，并通过系统实验（Figure 5-8）揭示了Decay阶段的训练动力学（梯度方向一致性增强、loss curvature增大等），提供了理论支撑。

---

#### 后代 (Descendants) — 基于引用分析

> 截至 2026-03-31，本文共被引用 **19** 次（数据来源：OpenAlex）


##### 核心后续工作

- **EuroLLM: Multilingual Language Models for Europe** (Martins et al., 2025) — 被引 12
  - 🟡 组件引用
  - 训练欧洲多语言LLM时采用了MiniCPM提出的WSD学习率调度策略。
- **Efficient GPT-4V level multimodal large language model for deployment on edge devices** (Yao et al., 2025) — 被引 11
  - 🟠 扩展应用
  - 将MiniCPM的小模型高效训练思路扩展到多模态领域，构建可部署于边缘设备的多模态大模型。

##### 其他引用

| 论文 | 年份 | 被引数 | 关系 |
|------|------|--------|------|
| Empowering large language models to edge intelli... (Wang et al.) | 2025 | 15 | — |
| IMFND: In-context multimodal fake news detection... (Jiang et al.) | 2025 | 4 | — |
| MEDSQ: Towards personalized medical education vi... (Ouyang et al.) | 2024 | 4 | — |
| Ethical Risks and Future Direction in Building T... (Lee et al.) | 2024 | 3 | — |
| Empowering large language models to edge intelli... (Wang et al.) | 2025 | 15 | — |
| IMFND: In-context multimodal fake news detection... (Jiang et al.) | 2025 | 4 | — |
| MEDSQ: Towards personalized medical education vi... (Ouyang et al.) | 2024 | 4 | — |
| Ethical Risks and Future Direction in Building T... (Lee et al.) | 2024 | 3 | — |

##### 引用趋势
- 2024: 2 篇 | 2025: 9 篇

## 背景知识补充 (Background Context)

- **Tensor Program (µP)** (Yang et al., 2022; 2023)：一个理论框架，通过对网络各层的初始化标准差、学习率、输出缩放进行与宽度/深度相关的调整，使得超参数在不同模型规模间可迁移。MiniCPM使用了width scaling和depth scaling两种技术。在LLM社区中，CerebrasGPT是最早采用µP的知名模型。µP的核心思想是让不同宽度的网络在infinite-width极限下行为一致。

- **Chinchilla Scaling Law** (Hoffmann et al., 2022)：由DeepMind提出，主张模型参数和训练数据应以相同速率缩放（D_opt ≈ 20×N），是当前LLM训练预算分配的基准参考。但后续实践（Llama2用2T tokens训练70B模型，远超20×70B=1.4T）表明实际最优比例可能更高。

- **Sparse Upcycling** (Komatsuzaki et al., 2022)：将dense模型转化为MoE模型的技术——复制每层MLP为多个专家，随机初始化router。MiniCPM-MoE即采用此方法从dense检查点初始化。

- **DPO (Direct Preference Optimization)** (Rafailov et al., 2024)：一种无需reward model的人类偏好对齐方法，直接在policy上优化Bradley-Terry偏好模型。相比RLHF更简单稳定，已成为SLM对齐的主流选择。
