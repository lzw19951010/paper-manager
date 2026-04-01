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
- OLMo 2 32B / 7B
- Qwen 3 32B
- Qwen 3 VL 32B Think
- Qwen 2.5 32B / 7B
- DeepSeek-R1 32B
- Gemma 3 27B
- Gemma 2 27B
- LLM360 K2-V2 70B Instruct
- Apertus 70B
- Stanford Marin 32B / 8B
- Nemotron Nano 9B v2
- OpenThinker3 7B
- DS-R1 Owen 7B / 8B
- OR Nemotron 7B
- Granite 3.3 8B Instruct
- Apertus 8B Instruct
category: llm/pretraining
citation_count: 0
citation_date: '2026-03-31'
code_url: https://github.com/allenai/OLMo-core (pretrain), https://github.com/allenai/open-instruct
  (posttrain)
core_contribution: new-framework
datasets:
- 'Dolma 3 Mix (5.93T tokens 预训练: 76.1% CommonCrawl 4.51T + 13.6% olmOCR PDFs 805B
  + 6.89% Stack-Edu 409B + 2.56% FineMath 152B + 0.86% arXiv 50.8B + 0.04% Wikipedia
  2.51B)'
- 'Dolma 3 Dolmino Mix (100B tokens 中训练: 数学+代码+通用知识QA+指令跟随+思维链)'
- 'Dolma 3 Longmino Mix (50B/100B tokens 长上下文: olmOCR science PDFs 640B pool, 22.3M
  docs >8K tokens)'
- 'Dolci Think SFT (2.27M prompts 7B / 2.25M prompts 32B: Math 95.3万 + Coding 66.9万
  + IF 49.5万 + Chat 8.3万 + Safety 8.96万 + Multilingual 9.9万 + Other 5K)'
- 'Dolci Think DPO (200K pairs: Chat 40.7K + IF 24.6K + Math 19.4K + Coding 23.4K
  + Safety 11.9K + Science 21.3K + Multilingual 4.1K + Other 21K)'
- 'Dolci Think RL (104.9K prompts 7B / 171.9K prompts Instruct: Math 30.4K + Coding
  22.1K + IF 30.2K + General Chat 21.4K)'
- Dolci Instruct SFT (2.15M prompts SFT / 259.9K prompts DPO)
- Dolci RL-Zero (13.3K math prompts, 去污后)
- OlmoBaseEval (43 tasks 开发评测 + 4 held-out tasks)
- 'Chat evaluation suite (Table 16: 20+ tasks 包含 MATH, AIME 2024/2025, HumanEval+,
  MBPP+, IFEval, IFBench, MMLU, AlpacaEval 2 LC 等)'
date: '2025-12-15'
doi: null
keywords: &id001
- open-source language model
- model flow
- pretraining data curation
- midtraining
- long-context extension
- supervised finetuning
- delta learning DPO
- reinforcement learning with verifiable rewards
- data mixing optimization
- quality-aware upsampling
metrics:
- MATH accuracy (CoT EM, temp=0.6, top-p=0.95, max_tokens=32768, N=1, 7 subtasks)
- AIME 2024 accuracy (CoT EM Flex, temp=0.6, top-p=0.95, max_tokens=32768, N=32, Minerva
  extraction)
- AIME 2025 accuracy (CoT EM Flex, temp=0.6, top-p=0.95, max_tokens=32768, N=32, Minerva
  extraction)
- OMEGA accuracy (CoT EM Flex, temp=0.6, top-p=0.95, max_tokens=32768, N=1, Custom
  Regexes, 55 subtasks)
- BigBenchHard accuracy (CoT EM Flex, temp=0.6, top-p=0.95, max_tokens=32768, N=1,
  OLMo 3 Regex)
- ZebraLogic accuracy (CoT Custom, temp=0.6, top-p=0.95, max_tokens=32768, N=1, Custom
  JSON)
- AGI Eval English accuracy (CoT Acc, temp=0.6, top-p=0.95, max_tokens=32768, N=1,
  OLMo 3 Regex, 9 subtasks)
- HumanEvalPlus pass@1 (CoT Code pass@1, temp=0.6, top-p=0.95, max_tokens=32768, N=10)
- MBPP+ pass@1 (CoT Code pass@1, temp=0.6, top-p=0.95, max_tokens=32768, N=10)
- LiveCodeBench v3 pass@1 (CoT Code pass@1, temp=0.6, top-p=0.95, max_tokens=32768,
  N=10)
- IFEval strict accuracy (CoT Custom, temp=0.6, top-p=0.95, max_tokens=32768, N=1)
- IFBench accuracy (CoT Custom, temp=0.6, top-p=0.95, max_tokens=32768, N=1)
- MMLU accuracy (CoT MC Acc, temp=0.6, top-p=0.95, max_tokens=32768, N=1, OLMo 3 Regex,
  57 subtasks)
- PopQA EM Recall (CoT MC Acc, temp=0.6, top-p=0.95, max_tokens=32768, N=1)
- GPQA accuracy (CoT MC Acc, temp=0.6, top-p=0.95, max_tokens=32768, N=1, OLMo 3 Regex,
  23 subtasks)
- AlpacaEval 2 LC win rate (CoT Winrate, temp=0.6, top-p=0.95, max_tokens=32768, N=1,
  GPT-4.1 judge)
- Safety composite (avg of DoAnythingNow, HarmBench, TrustLLM-JailbreakTrigger, WildGuard-Test,
  XSTest, BBQ, StrongReject, Toxigen, WMDP)
publication_type: preprint
tags: *id001
title: Olmo 3
tldr: OLMo 3 是最强全开放语言模型家族（7B/32B），旗舰 OLMo 3.1 Think 32B 在 MATH 达 96.2%、AIME 2024 达
  80.6%，通过三阶段后训练（SFT→DPO→RL）和 Delta Learning 偏好调优，用 6 倍少的训练 token 逼近 Qwen 3 32B 等最佳开放权重模型。
url: https://arxiv.org/abs/2512.13961
venue: null
---
#### 核心速览 (Executive Summary)

**TL;DR:** OLMo 3 是 AI2 发布的全开放语言模型家族（7B/32B），旗舰模型 OLMo 3.1 Think 32B 在 MATH 达 96.2%、AIME 2024 达 80.6%、AIME 2025 达 78.1%，是迄今最强全开放思维模型。通过三阶段后训练流水线（Dolci Think SFT → Delta Learning DPO → OlmoRL）和全新数据课程（Dolma 3 预训练 5.93T tokens + Dolmino 中训练 100B + Longmino 长上下文扩展），在仅用 Qwen 3 约 1/6 训练 token 的情况下逼近其性能。

**一图流:** 旧方法（OLMo 2）= 预训练+中训练后直接 SFT+DPO，数据仅 web text+math → OLMo 2 32B Instruct 在 Post-train Eval 约 45%。新方法（OLMo 3）= 预训练+中训练+**长上下文扩展**后，**Think 路线**经 SFT→Delta Learning DPO→OlmoRL 三阶段，**Instruct 路线**经 warm-start SFT→Delta-aware DPO→Instruct RL 三阶段 → OLMo 3.1 Think 32B Post-train Eval 约 85%，提升 ~40 个百分点。

**核心机制一句话:** 通过构建多阶段数据课程（Dolma 3→Dolmino→Longmino→Dolci）结合 Delta Learning 偏好调优（用强弱模型对比度而非绝对质量构建偏好对）和多领域可验证奖励 RL（OlmoRL），在全开放框架下实现从基座到思维模型的完整能力跃迁。

---

#### 动机与第一性原理 (Motivation & First Principles)

**痛点:**
- OLMo 2 在 Post-train Eval 上远落后于闭源和开放权重模型：OLMo 2 Instruct 32B 的 MATH 仅 49.2%，AIME 2024 仅 0.3%，而 Qwen 3 32B 的 MATH 达 95.4%、AIME 2024 达 80.8%（Table 1）。
- 现有全开放模型（公开数据+代码+中间检查点）在推理能力上存在巨大缺口：Marin 32B 的 MATH 仅 36.2%，Apertus 70B 仅 36.2%，而最佳开放权重模型（非全开放）如 Qwen 3 VL 32B Think 的 MATH 高达 96.7%。
- 开放 RLVR 研究缺乏透明基准：所有主流 RLVR 工作（DAPO、DeepSeek R1 等）都在不公开预训练/中训练数据的模型上训练，导致无法分辨 RL 提升来自真实推理学习还是数据污染。

**核心洞察（Because→Therefore 因果链）:**

1. **Because** 模型推理能力的上限由预训练和中训练阶段的数据质量和覆盖决定（Gandhi et al., 2025 展示预训练中包含 verification/backtracking 行为的模型在 RL 中表现显著更好），**Therefore** 需要构建专门的中训练数据（Dolmino Mix）来植入结构化推理能力（meta-reasoning capabilities 包括 self-awareness、backtracking、goal management 等 7 种核心能力）。

2. **Because** SFT 在强模型数据上存在饱和效应——继续在 Qwen3 32B 生成的 chosen responses 上做 SFT 实际上会 hurt 模型性能（Table 21: Cont. SFT on chosen 的 Avg 仅 64.5 vs Delta learning 的 72.9），**Therefore** 需要利用 Delta Learning 构建偏好对：关键不是 chosen/rejected 各自的绝对质量，而是两者之间的 capability delta（$y_c > y_r$ 的对比度）。

3. **Because** 单领域 RL 训练会导致过拟合——IFEval only RL 会让 AlpacaEval 从 ~45 下降到 ~10（Figure 20），**Therefore** 需要多领域混合 RL（math+code+IF+general chat），虽然单领域 train reward 更高，但混合训练的下游性能更好（Figure 21），因为混合数据防止了 reward hacking。

**物理/直觉解释:** 把训练语言模型类比为培养一个学生：预训练（5.93T tokens）是广泛阅读各类书籍建立世界知识；中训练（100B tokens）是选择性地深入学习数学、代码等专业领域（相当于选修课）；长上下文扩展（50-100B tokens）是训练阅读长篇论文的能力。进入后训练阶段，SFT 是跟着优秀范例学习解题过程（模仿学习），DPO 是通过对比好答案和差答案来培养判断力（Delta Learning 的精妙之处在于：不是简单告诉学生"这个好"，而是展示"这个比那个好在哪里"——用 Qwen3 32B 的答案 vs Qwen3 0.6B 的答案来构造最大对比度），RL 则是让学生自己做题、用答案验证器自动批改来强化推理能力。

---

#### 方法详解 (Methodology)

**直觉版:**

参考 Figure 2（模型流全景图），OLMo 3 的训练分为两大阶段：

**基座模型训练（左半）:**
- **旧（OLMo 2）：** 预训练 → 中训练，只用 4096 tokens 上下文，中训练数据较单一
- **新（OLMo 3）：** 预训练（5.93T tokens, 8192 上下文）→ 中训练（100B tokens, 引入 meta-reasoning 数据）→ **长上下文扩展**（50-100B tokens, 65K 上下文），新增 olmOCR 科学 PDF 数据源、受限数据混合优化、质量感知上采样

**后训练（右半）:**
- **旧：** SFT → DPO（UltraFeedback 式 LLM-judge）
- **新 Think 路线：** Dolci Think SFT（2.27M 样本，含 reasoning traces）→ Dolci Think DPO（Delta Learning，200K 对，Qwen3 32B vs Qwen3 0.6B）→ OlmoRL（~100K prompts, GRPO + 多领域可验证奖励）
- **新 Instruct 路线：** 从 Think SFT 模型 warm-start → Dolci Instruct SFT → Delta-aware DPO（含长度控制、多轮对话）→ Instruct RL

**精确版:**

##### 数据流全景

```
输入: CommonCrawl (8.14T tokens pool) + olmOCR PDFs (972B) + Stack-Edu (137B) + arXiv (21.4B) + FineMath (34.1B) + Wikipedia (3.69B)
                    ↓ [三阶段去重: Exact→MinHash→Suffix Array, 38.7B→9.7B docs (-75%)]
                    ↓ [WebOrganizer 24类主题分类 + fastText 质量评分 → 480 buckets (24 topics × 20 quality tiers)]
                    ↓ [受限数据混合: Swarm(30M proxy models) → Per-task regression(BPB) → Mix optimization]
                    ↓ [质量感知上采样: 截断幂指数函数 f_{p,λ}(x), 底部40%丢弃, 顶部5%上采样7倍]
Dolma 3 Mix: 5.93T tokens → Pretraining (7B@512 GPUs, 32B@1024 GPUs)
                    ↓
Dolmino Mix: 100B tokens (数学: TinyMATH+CraneMath+Dolminos Math; 代码: CraneCode+FIM; QA+IF+思维链)
                    → Midtraining (7B@128 GPUs, 32B@512 GPUs)
                    ↓
Longmino Mix: 50B(7B)/100B(32B) tokens (olmOCR long docs + 合成数据 + web text)
                    → Long-context extension (65K context, 7B@256 GPUs, 32B@1024 GPUs)
                    ↓
                  OLMo 3 Base
                    ↓
        ┌──────────────┼──────────────┐
    Think SFT     Instruct SFT    RL-Zero RLVR
    (2.27M)      (warm from Think)  (13.3K prompts)
        ↓              ↓                ↓
    Think DPO     Instruct DPO     OLMo 3 RL-Zero
    (200K pairs)  (260K pairs)
        ↓              ↓
    Think RL      Instruct RL
    (OlmoRL)      (OlmoRL)
        ↓              ↓
  OLMo 3 Think   OLMo 3 Instruct
```

##### 关键公式

**1. OlmoRL 目标函数（Eq. 1）：**

$$\mathcal{J}(\theta) = \frac{1}{\sum_{i=1}^{G} |y_i|} \sum_{i=1}^{G} \sum_{t=1}^{|y_i|} \min\left(\frac{\pi(y_{i,t} \mid x, y_{i,<t}; \theta)}{\pi_{\text{vllm}}(y_{i,t} \mid x, y_{i,<t}; \theta_{\text{old}})}, \rho\right) \min\left(r_{i,t}, \text{clip}(r_{i,t}, 1-\varepsilon_{\text{low}}, 1+\varepsilon_{\text{high}}) A_{i,t}\right)$$

其中：
- $r_{i,t} = \frac{\pi(y_{i,t} | x, y_{i,<t}; \theta)}{\pi(y_{i,t} | x, y_{i,<t}; \theta_{\text{old}})}$ 是 importance ratio
- $\varepsilon_{\text{low}} = 0.2$, $\varepsilon_{\text{high}} = 0.272$ 是非对称 clipping 参数（clip-higher 允许更大的正向更新）
- $\rho$ 是 truncated importance sampling cap（32B 为 2.0），补偿推理和训练引擎的对数概率差异
- $\pi_{\text{vllm}}(\cdot)$ 是 vLLM 返回的 token 概率（推理时的参考概率）
- $A_{i,t}$ 是 advantage，**不除以 group 标准差**（避免 difficulty bias）

**Advantage 计算（Eq. 2）：**

$$A_{i,t} = r(x, y_i) - \text{mean}\left(\{r(x, y_i)\}_{i=1}^{G}\right)$$

物理含义：对同一个 prompt $x$ 的 $G=8$ 个 rollout，每个 rollout 的 advantage = 该 rollout 的 reward 减去组均值。不做标准差归一化，因为当所有 rollout reward 方差很小时（太简单或太难的题），归一化会放大噪声。

**2. 长度归一化 DPO Loss（Appendix A.6.2）：**

$$\max_{\pi_\theta} \mathbb{E}_{(x,y_c,y_r) \sim \mathcal{D}} \left[ \log \sigma \left( \frac{\beta}{|y_c|} \log \frac{\pi_\theta(y_c|x)}{\pi_{\text{ref}}(y_c|x)} - \frac{\beta}{|y_r|} \log \frac{\pi_\theta(y_r|x)}{\pi_{\text{ref}}(y_r|x)} \right) \right]$$

$\beta = 5$ 控制偏好学习的保守程度。除以 token 数消除长度偏差。

**3. 质量感知上采样函数（Appendix A.2.4）：**

$$f_{p,\lambda}(x) = \begin{cases} 0, & \text{for } x < a \\ C(x-a)^p \cdot e^{\lambda(x-a)}, & \text{for } x \ge a \end{cases}$$

约束条件：Token yield $\int_0^1 f(x)dx = Z/X$；Maximum upsampling $\frac{1}{b}\int_{1-b}^1 f_{p,\lambda}(x)dx \le M$（$M=7$）；Monotonicity $\lambda \ge 0$。实现：$a=0.40$（丢弃底部 40%），数值搜索 $p, \lambda, C$。

##### 数值推演示例

以 DPO Delta Learning 为例，假设 prompt $x$ = "Solve $2^{10} \mod 7$"：
- Qwen3 32B (chosen) $y_c$：有 Fermat's Little Theorem 推理链，正确使用 $2^6 \equiv 1 \pmod{7}$
- Qwen3 0.6B (rejected) $y_r$：直接计算 $1024 / 7 = 146...2$，正确但推理更浅
- **Delta = 推理深度差异**，即使答案相同，模型学到的是"如何更深入地推理"
- 如果继续在 $y_c$ 上做 SFT → avg 64.5（Table 21, hurt），但配对后做 DPO → avg 72.9（+8.4）

##### 伪代码

```python
# OlmoRL Training Loop (simplified)
class OlmoRL:
    def __init__(self, model, actors, verifiers, config):
        self.model = model  # learner (DeepSpeed distributed)
        self.actors = actors  # pool of vLLM instances
        self.verifiers = {  # domain-specific reward
            'math': SymPyVerifier(),      # binary: 1 if answer matches
            'code': TestCaseVerifier(),    # percentage of passed tests OR binary (all pass)
            'if': ConstraintVerifier(),    # #satisfied / #constraints
            'chat': LLMJudgeVerifier(),   # [0,1] from Qwen3 32B judge
        }
        self.clip_low, self.clip_high = 0.2, 0.272
        self.group_size = 8  # G rollouts per prompt
        self.tis_cap = 2.0   # truncated importance sampling cap

    def active_sampling(self, batch_target: int) -> list:
        """Continuously pull completions until enough non-zero-advantage samples"""
        valid_samples = []
        while len(valid_samples) < batch_target:
            completions = self.results_queue.get_batch()  # continuous batching
            for group in completions:
                rewards = [self.verifiers[group.domain](group.prompt, y)
                          for y in group.responses]  # shape: [G]
                if std(rewards) > 0:  # zero gradient signal filtering
                    valid_samples.append((group, rewards))
                # Filtered prompts: requeue new prompts (active sampling)
        return valid_samples[:batch_target]

    def compute_advantage(self, rewards):
        """No std normalization - avoids difficulty bias"""
        return rewards - rewards.mean()  # shape: [G]

    def training_step(self):
        samples = self.active_sampling(batch_size=128)  # 64 prompts × 2 sampled
        total_loss, total_tokens = 0, 0
        for (group, rewards) in samples:
            advantages = self.compute_advantage(torch.tensor(rewards))
            for i, (response, adv) in enumerate(zip(group.responses, advantages)):
                for t, token in enumerate(response):
                    ratio = (self.model.log_prob(token) - self.old_log_probs[token]).exp()
                    tis_ratio = min(ratio / self.vllm_probs[token], self.tis_cap)
                    clipped = torch.clamp(ratio, 1-self.clip_low, 1+self.clip_high)
                    loss_t = -tis_ratio * min(ratio * adv, clipped * adv)
                    total_loss += loss_t
                    total_tokens += 1
        (total_loss / total_tokens).backward()
        # Inflight update: push weights to actors WITHOUT invalidating KV cache
        for actor in self.actors:
            actor.update_weights_thread_safe()  # up to 4x throughput gain
```

##### 超参数表

**基座模型训练超参数（Table 35）:**

| 参数 | 7B Pretraining | 7B Midtraining | 7B Long-ctx | 32B Pretraining | 32B Midtraining | 32B Long-ctx |
|---|---|---|---|---|---|---|
| LR Schedule | Modified cosine | Linear decay | Linear decay | Cosine trunc@5.5T | Linear decay | Linear decay |
| Peak LR | 3.0×10⁻⁴ | 2.074×10⁻⁴ | 2.074×10⁻⁴ | 6.0×10⁻⁴ | 2.071×10⁻⁴ | 2.071×10⁻⁴ |
| LR Warmup | 2000 steps | 0 | 200 steps | 2000 steps | 0 | 200 steps |
| Batch Size (instances) | 512 | 256 | 64 | 1,024 | 512 | 128 |
| Seq Length | 8,192 | 8,192 | 65,536 | 8,192 | 8,192 | 65,536 |
| Batch Tokens | 4.19M | 2.10M | 4.19M | 8.39M | 4.19M | 8.39M |
| Total Tokens | 5.93T | 100B | 50B | 5.5T | 100B (×2 seeds) | 100B |

**后训练超参数（Tables 47, 48, 49）:**

| 参数 | 7B Think SFT | 32B Think SFT | 7B Think DPO | 32B Think DPO | 7B Think RL | 32B Think RL | 7B RL-Zero |
|---|---|---|---|---|---|---|---|
| Data Size | 45.4B tok | 45.2B tok | 150K pairs | 200K pairs | 104,869 | 104,869 | 13,314 |
| LR | 5×10⁻⁵ | 1×10⁻⁴ souped | 8×10⁻⁸ | 7×10⁻⁸ | 1×10⁻⁶ | 2×10⁻⁶ | 1×10⁻⁶ |
| GPUs | 64 | 256 | 32 | 64-128 | 72 (16L+56A) | 224 (64L+160A) | 72 (8L+64A) |
| Max Seq | 32K | 32K | 16K | 8K | 32,768 | 32,768 | 16,384 |
| Steps/Epochs | 2 epochs | 2 epochs | 1 epoch | 1 epoch | 1,400 steps | 750 steps | 2,000 steps |
| DPO β | - | - | 5 | 5 | - | - | - |
| Clip-low/high | - | - | - | - | 0.2/0.272 | 0.2/0.272 | 0.2/0.272 |
| Group Size | - | - | - | - | 8 | 8 | 8 |

**模型架构（Table 33）:**

| 参数 | 7B | 32B |
|---|---|---|
| Layers | 32 | 64 |
| Hidden ($d_{model}$) | 4096 | 5120 |
| Q/KV heads | 32/32 (MHA) | 40/8 (GQA) |
| Activation | SwiGLU | SwiGLU |
| QKV norm | QK-Norm | QK-Norm |
| RoPE θ | 5×10⁵ | 5×10⁵ |
| SWA | 3/4 layers; 4096 window | 3/4 layers; 4096 window |
| Context | 8192→65536 | 8192→65536 |

##### 设计决策

1. **Delta Learning vs UltraFeedback-style LLM-judge DPO：** UltraFeedback 用多个模型生成+LLM judge 评分。问题：当 generator pool 全是强模型时，chosen 和 rejected 差别太小（Table 32: Updated GPT UltraF pipeline avg 55.4 vs Delta learning + GPT 的 60.4）。Delta Learning 用一个强模型和一个弱模型，最大化 capability delta。

2. **No KL in RL：** 移除 KL 惩罚项。因为 reward 来自可验证答案而非 learned reward model，不存在 reward model overoptimization 风险。

3. **Asymmetric clipping（0.272 > 0.2）：** 允许正 advantage 样本有更大策略更新幅度，来自 DAPO。

4. **Active sampling vs Dynamic sampling（DAPO）：** DAPO 过采样 3 倍。OlmoRL 持续从 actor 拉取并即时过滤，保持恒定 batch size（Figure 26: 100% non-zero advantage throughout training）。

5. **Token-level loss：** 用 batch 内所有 token 总数归一化，避免短 response 的 per-token gradient 被放大。

##### 易混淆点

❌ **错误理解：** Delta Learning 是选择"最好的"和"最差的" responses 来构建偏好对。
✅ **正确理解：** 关键是模型来源不同——chosen 来自强模型（Qwen3 32B），rejected 来自弱模型（Qwen3 0.6B），确保对比度来自 capability 差异。即使 chosen 对 SFT 已无用（继续 SFT 反而 hurt），配对后的对比信号仍然有效。

❌ **错误理解：** OLMo 3 的 RL 训练只关注数学推理。
✅ **正确理解：** OlmoRL 是多领域 RL——math（SymPy）、code（test cases）、IF（constraint check）、chat（LLM judge）四个领域同时训练。单领域训练会导致其他能力崩溃（Figure 20）。

❌ **错误理解：** 长上下文扩展只需改 RoPE θ 和增加序列长度。
✅ **正确理解：** 还引入了 SWA（3/4 层 4096 window）+ YaRN，更关键的是数据：olmOCR 科学 PDF（22.3M docs >8K tokens, 640B tokens total）是目前最大公开长上下文训练集。

---

#### 实验与归因 (Experiments & Attribution)

**主要结果表 1: OLMo 3 Think 32B 结果（Table 1 & 14）**

| 类别 | 基准 | OLMo 3.1 Think 32B | OLMo 2 Inst 32B | Qwen 3 32B | Qwen 3 VL 32B Think | DS-R1 32B | K2-V2 70B |
|---|---|---|---|---|---|---|---|
| **Math** | MATH | **96.2** | 49.2 | 95.4 | 96.7 | 92.6 | 94.5 |
| | AIME 2024 | **80.6** | 4.6 | 80.8 | 86.3 | 70.3 | 78.4 |
| | AIME 2025 | **78.1** | 0.9 | 70.9 | 78.8 | 56.3 | 70.3 |
| | OMEGA | 53.4 | 9.8 | 47.7 | 50.8 | 38.9 | 46.1 |
| **Reasoning** | BBH | 88.6 | 65.6 | 90.6 | 91.1 | 89.7 | 87.6 |
| | ZebraLogic | 80.1 | 13.3 | 88.3 | 96.1 | 69.4 | 79.2 |
| **Coding** | HumanEval+ | 91.5 | 44.4 | 91.2 | 90.6 | 92.3 | 88.0 |
| | MBPP+ | 68.3 | 49.0 | 70.6 | 66.2 | 70.1 | 66.0 |
| | LiveCodeBench | 83.3 | 10.6 | 90.2 | 84.8 | 79.5 | 78.4 |
| **IF** | IFEval | **93.8** | 85.4 | 86.5 | 85.5 | 78.7 | 68.7 |
| | IFBench | **68.1** | 26.3 | 37.3 | 55.1 | 23.8 | 46.3 |
| **Knowledge** | MMLU | 86.4 | 77.1 | 88.8 | 90.1 | 88.0 | 88.4 |
| **Chat** | AlpacaEval 2 LC | 69.1 | - | 75.6 | 80.9 | 26.2 | - |

**主要结果表 2: OLMo 3 Instruct 7B（Table 26）**

| 类别 | 基准 | OLMo 3 7B Inst | Qwen 3 8B | Qwen 3 VL 8B | Qwen 2.5 7B | OLMo 2 7B | Apertus 8B | Granite 3.3 8B |
|---|---|---|---|---|---|---|---|---|
| Math | MATH | **87.3** | 82.3 | 91.6 | 71.0 | 30.1 | 21.9 | 67.3 |
| | AIME 2024 | **44.3** | 26.2 | 55.1 | 11.3 | 1.3 | 0.5 | 7.3 |
| Coding | HumanEval+ | 77.2 | 79.8 | 82.9 | 74.9 | 25.8 | 34.4 | 64.0 |
| IF | IFEval | 85.6 | 86.3 | 87.5 | 72.2 | 71.4 | 71.4 | 77.5 |
| Chat | AlpacaEval | 40.9 | 49.8 | 73.5 | 23.0 | 18.3 | 8.1 | 28.6 |
| Tool | SimpleQA | **79.3** | 79.0 | 90.3 | 78.0 | - | - | - |
| Safety | Avg | **87.6** | 78.4 | 77.7 | 73.4 | 91.1 | 71.1 | 74.3 |

**归因排序（按贡献大小）:**

1. **Delta Learning DPO（最大贡献）：** Table 21: SFT ckpt avg 70.3 → Delta learning avg 72.9（+2.6），而 Cont. SFT on chosen avg 64.5（-5.8）。DPO 的独特价值在 SFT 饱和后仍能提供学习信号。AIME 2025: SFT 58.8 → DPO 66.3（+7.5pt）。

2. **OlmoRL 多领域 RL（第二贡献）：** Table 22: SFT+DPO avg 72.7 → SFT+DPO+RLVR avg **74.1**（+1.4）。DPO 作为 RL 起点优于 SFT。IFEval 提升最大（Table 24: DPO 82.3 → RL 93.8, +11.5pt）。

3. **Dolci Think SFT 数据（第三贡献）：** Table 18: Base + Synthetic 2 avg 47.3（最高）。Table 29: Think SFT warm-start Instruct 比冷启动高 3.3 分。

4. **中训练数据课程（第四贡献）：** Figure 25: 有推理数据的 midtrained 模型 RL-Zero 中 response length 增长到 2000 tokens + math reward 上升；推理数据不足的模型停滞。

5. **基础设施优化（第五贡献）：** Table 23: OLMo 2 → OLMo 3 基础设施 = 3.35x 加速（6.34 → 21.23 Mtok），MFU 0.30% → 1.01%。

6. **质量感知上采样（第六贡献）：** Table 39: OLMo 3 Upsampling avg BPB 0.719 vs Top 5% flat 的 0.930。

**可信度检查:**

1. **评估去污染：** 专门的 decon 工具 + RL-Zero spurious reward 实验（Figure 27: 随机 reward 训练零提升，验证无数据泄露）。

2. **Baseline 公平性：** 统一 OLMES 框架，temp=0.6, top-p=0.95, max_tokens=32768。但 Qwen 3 训练数据量远大于 OLMo 3（未公开），直接对比有不公平性。

3. **未报告的负面结果：** (a) Overlong filtering 等 RL 改进"未一致提升"（footnote 33）；(b) GPT-5 judge 不如 GPT-4.1（footnote 69）；(c) AlpacaEval 在 extended RL 后下降 5pt。

---

#### 专家批判 (Critical Review)

**隐性成本:**

1. **计算总成本：** 56 天 × 1024 H100 GPU，约 $2.75M（@$2/H100-hr）。预训练约 47 天，后训练约 9 天。OLMo 3.1 Think 32B 的扩展 RL 额外 21 天 × 224 GPU。

2. **推理主导的 RL 成本：** 32B reasoner 生成 max 32K tokens rollout，learner 75% 时间等数据。Inference 使用 20 nodes vs training 8 nodes（8:1 比例）。推理计算量约训练的 5 倍（GPU 利用率角度）。

3. **数据处理成本：** olmOCR 爬取 238M PDFs；web data heuristic filtering 花费 ~$11,300（1030 i4i.32xlarge EC2 hours）；代码执行用 AWS Lambda 跑 17.2M generated samples。SFT 数据生成依赖 QwQ-32B 生成 75.3 万条 reasoning traces（每条 up to 32K tokens）。

**最值得复用的技术:**

1. **Delta Learning DPO：** 极简有效——只需一个强模型和一个弱模型构建偏好对，在 SFT 饱和时仍提供有效学习信号。Table 21 ablation 非常有说服力，适用于任何后训练场景。

2. **Active Sampling for RL：** 比 DAPO 的 3x dynamic sampling 更高效，保持恒定 batch size。实现不复杂——异步 actor pool + 结果队列 + 连续过滤。

**最大的坑:**

1. **RL 稳定性：** 论文明确提到"至少 1 天因稳定性损失"。没有 inflight weight updates（需修改 vLLM 使其 thread-safe）throughput 低 4 倍。

2. **Model souping 的黑魔法：** SFT 最终 checkpoint = 两个不同 LR checkpoint 的线性 merge（mergekit），DPO 选择涉及"vibe test"主观评估，难以精确复现。

**关联技术:**

1. **vs DeepSeek R1：** R1 用 pure RL-Zero，OLMo 3 展示 SFT→DPO→RL 三阶段在开放模型上的优势。OLMo 3 RL-Zero 在 7B 上与 DAPO（Qwen 2.5 32B base）性能接近但更高效（Figure 38）。

2. **vs SmolLM3 (Bakouch et al., 2025)：** 同期全开放小模型但无 DPO。OLMo 3 展示 preference tuning 在 thinking model 上的独特价值。

3. **vs DAPO (Yu et al., 2025)：** OlmoRL 采纳 DAPO 多项改进但增加 active sampling + TIS + inflight updates，在 GPU hours 效率上显著优于 DAPO。

---

#### 机制迁移分析 (Mechanism Transfer Analysis)

**机制解耦表格:**

| 计算原语 | 本文用途 | 抽象描述 | 信息论直觉 |
|---|---|---|---|
| **Delta Learning 偏好构建** | 强模型(Qwen3 32B) vs 弱模型(Qwen3 0.6B)输出对构建 DPO 数据 | 利用不同能力水平信号源的差值作为学习信号 | 互信息最大化：不看"好作文"学写作，而是看"好作文 vs 差作文的差异"学判断力 |
| **Active Sampling** | RL 训练中持续拉取 completions，过滤零梯度样本，保持恒定 batch | 在线难度自适应采样：只训练模型"还没完全学会"的样本 | Entropy-guided sampling：只在 policy 不确定区域投入梯度计算 |
| **多领域可验证奖励混合** | math/code/IF/chat 四域同时 RL，混合训练 | 多目标优化中的 domain regularization | 正则化：单域 entropy 快速下降（过拟合），多域维持高 entropy → 更好 generalization |
| **质量感知上采样** | 预训练数据按质量分布用参数化曲线控制上采样率 | 连续质量权重函数替代二元过滤 | Rate-distortion tradeoff：好书多看几遍，一般书看一遍，差书不看 |

**迁移处方:**

1. **Delta Learning → 推荐系统排序模型偏好学习**
   - 目标：用强 ranker vs 弱 ranker 对同一 query 生成排序结果构建偏好对，替代人工标注
   - 怎么接：强 ranker chosen list → 弱 ranker rejected list → DPO 训练排序模型
   - 预期收益：降低标注成本，对比度更一致
   - 风险：如果强/弱 ranker 错误模式高度相关则 delta 信号不可靠

2. **Active Sampling → 自动驾驶仿真数据筛选**
   - 目标：RL 训练中只在"有学习价值"的仿真场景上计算梯度
   - 怎么接：对仿真场景做 8-rollout 采样 → 过滤 reward std=0 的场景
   - 预期收益：减少 >50% 无效仿真
   - 风险：如果仿真器本身很便宜，收益有限

3. **多领域可验证奖励 → VLM 联合 RL**
   - 目标：VQA(answer matching) + OCR(CER) + visual math(SymPy) + description(LLM judge) 混合训练
   - 怎么接：各模态独立 verifier → 混合 prompt pool
   - 预期收益：防止单模态过拟合
   - 风险：不同模态 reward scale 差异需仔细调节

4. **质量感知上采样 → 医疗 NLP 数据增强**
   - 目标：对医疗文本按质量评分用截断幂指数函数控制上采样
   - 怎么接：底部 40% 网页垃圾丢弃，顶部 5% 临床笔记上采样 7 倍
   - 预期收益：有限预算下最大化高质量医疗知识注入
   - 风险：质量分类器在专业领域可能不准确

**机制家族图谱:**

**前身(Ancestors):**
1. **RLHF/PPO (Stiennon et al., 2020)** → OlmoRL 的 GRPO 是 PPO 的 group-relative 变体
2. **DPO (Rafailov et al., 2024)** → Dolci DPO 直接使用 DPO loss + 长度归一化
3. **Tülu 3 (Lambert et al., 2024)** → 后训练 SFT→DPO→RL 三阶段框架的直接前身
4. **DCLM (Li et al., 2024a)** → Dolma 3 web data 处理 pipeline 基础
5. **OLMo 2 (OLMo et al., 2024)** → 架构和训练框架（OLMo-core）直接继承

**兄弟(Siblings):**
1. **SmolLM3 (Bakouch et al., 2025)** — 同期全开放小模型
2. **Stanford Marin (Hall et al., 2025)** — 同期全开放 32B
3. **LLM360 K2-V2 (Team et al., 2025)** — 同期全开放 70B reasoning 模型

**后代(Descendants):**
- OLMo 3.1 Think 32B（本文直接后续，extended RL 2300 steps）
- 暂无外部后续（2025年12月发布的新论文）

**创新增量：** OLMo 3 是第一个系统性地将 Delta Learning DPO + 多领域 OlmoRL + 质量感知预训练数据策略组合在一起的全开放模型，也是第一个公开 RL-Zero 基准（含去污染预训练和 RL 数据）支持可复现 RLVR 研究。

#### 后代 (Descendants) — 基于引用分析

> 截至 2026-03-31，本文共被引用 **0** 次（数据来源：OpenAlex）

暂无高影响力引用论文。

---

#### 背景知识补充 (Background Context)

1. **GRPO (Group Relative Policy Optimization):** PPO 简化版，移除 value network，用 group 内 reward 相对值作 advantage。本文作为 OlmoRL 基础算法。(Shao et al., 2024)

2. **olmOCR:** AI2 的 PDF→纯文本工具（vision language model），本文用于构建 972B tokens 科学 PDF 数据源。(Poznanski et al., 2025a)

3. **WebOrganizer:** Web 文本 24 主题分类工具，本文用于预训练数据的主题分区和混合优化。(Wettig et al., 2025)

4. **Duplodocus:** AI2 的 native-rust 大规模去重工具（exact + MinHash），处理 trillion-token 规模去重。

5. **Model Souping:** 多 checkpoint 线性加权平均获取更好模型，本文 SFT 最终 checkpoint 由两个不同 LR 的 checkpoint merge 而成。(Wortsman et al., 2022)

6. **vLLM:** 高效 LLM 推理引擎，本文作为 OlmoRL actor inference engine，支持 continuous batching 和 inflight weight updates。(Kwon et al., 2023)
