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
- 'OLMo 2 7B (7B, type: fully-open)'
- 'OLMo 2 13B (13B, type: fully-open)'
- 'OLMo 2 32B (32B, type: fully-open)'
- 'Stanford Marin 8B (8B, type: fully-open)'
- 'Stanford Marin 32B (32B, type: fully-open)'
- 'Apertus 8B (8B, type: fully-open)'
- 'Apertus 70B (70B, type: fully-open)'
- 'Gaperon 8B (8B, type: fully-open)'
- 'Gaperon 24B (24B, type: fully-open)'
- 'LLM360 K2-V2 70B Instruct (70B, type: fully-open)'
- 'Qwen 2.5 7B (7B, type: open-weight)'
- 'Qwen 2.5 32B (32B, type: open-weight)'
- 'Qwen 3 8B (8B, type: open-weight)'
- 'Qwen 3 32B (32B, type: open-weight)'
- 'Qwen 3 VL 8B Instruct (8B, type: open-weight)'
- 'Qwen 3 VL 32B Think (32B, type: open-weight)'
- 'Gemma 2 9B (9B, type: open-weight)'
- 'Gemma 2 27B (27B, type: open-weight)'
- 'Gemma 3 27B (27B, type: open-weight)'
- 'Llama 3.1 8B (8B, type: open-weight)'
- 'Llama 3.1 70B (70B, type: open-weight)'
- 'Mistral Small 3.1 24B (24B, type: open-weight)'
- 'IBM Granite 3.3 8B Instruct (8B, type: open-weight)'
- 'Nemotron Nano 9B v2 (9B, type: open-weight)'
- 'Xiaomi MiMo 7B (7B, type: open-weight)'
- 'DeepSeek R1 32B (32B, type: open-weight)'
- 'DeepSeek R1 Distill Qwen 7B (7B, type: open-weight)'
- 'OpenThinker3 7B (7B, type: open-weight)'
- 'OpenReasoning Nemotron 7B (7B, type: open-weight)'
- 'Seed 36B (36B, type: open-weight)'
category: llm/pretraining
citation_count: 0
citation_date: '2026-04-02'
code_url: github.com/allenai/OLMo-core (pretrain), github.com/allenai/open-instruct
  (post-train), github.com/allenai/dolma3 (data), github.com/allenai/olmes (eval),
  github.com/allenai/decon (decontam)
core_contribution: new-framework
datasets:
- 'Dolma 3 Pretraining Mix (5.93T tokens: 76.1% Common Crawl + 13.6% olmOCR science
  PDFs + 6.89% Stack-Edu code + 2.56% FineMath 3+ + 0.86% arXiv + 0.04% Wikipedia)'
- 'Dolma 3 Dolmino Midtraining Mix (99.95B tokens: 22.5% Common Crawl HQ + 10.7% Dolmino
  Math synth + 10.0% StackEdu FIM code + 10.0% CraneCode Python synth + 5.9% Reddit
  Flashcards QA + 5.0% Nemotron Synth QA + 5.0% Dolmino Flan + 5.0% STEM Crawl + 5.0%
  olmOCR HQ PDFs + various reasoning traces)'
- 'Dolma 3 Longmino Mix (50B tokens for 7B / 100B tokens for 32B: 66.1% midtraining
  data + 12.2% REX synthetic 32K-64K + 9.63% olmOCR PDFs 32K-64K + 3.88% CWE synthetic
  + 4.55% olmOCR 8K-16K + 3.70% olmOCR 16K-32K)'
- 'Dolci Think SFT data (~45B tokens: curated reasoning traces)'
- DPO preference pairs (150K pairs for 7B Think / 200K pairs for 32B Think / 260K
  for 7B Instruct)
- RL dataset (104,869 samples for Think 7B/32B / 171,950 for Instruct 7B)
- MATH 500 (eval, 7 subtasks)
- AIME 2024 (eval)
- AIME 2025 (eval)
- Omega Math (eval, 55 subtasks)
- HumanEval+ (eval)
- MBPP+ (eval)
- LiveCodeBench v3 (eval)
- ZebraLogic (eval)
- BigBench-Hard (eval, 23 subtasks)
- GPQA (eval)
- AGI Eval English (eval, 9 subtasks)
- MMLU (eval, 57 subtasks)
- IFEval (eval)
- IFBench (eval)
- PopQA (eval)
- AlpacaEval v2 (eval)
- RULER (eval, long-context)
- HELMET (eval, long-context held-out)
date: '2025-12-15'
doi: null
failed_gates: []
keywords: &id001
- fully-open language models
- pretraining data curation
- midtraining
- long-context extension
- reinforcement learning from verifiable rewards
- GRPO
- chain-of-thought reasoning
- model souping
- sliding window attention
- decontamination
metrics:
- MATH (CoT EM, temp=0.6, top-p=0.95, max_tokens=32768, N=1)
- AIME 2024 (CoT EM, temp=0.6, top-p=0.95, max_tokens=32768, N=32)
- AIME 2025 (CoT EM, temp=0.6, top-p=0.95, max_tokens=32768, N=32)
- Omega Math (CoT EM, temp=0.6, top-p=0.95, max_tokens=32768, N=1, 55 subtasks)
- HumanEval+ (CoT Code pass@1, temp=0.6, top-p=0.95, max_tokens=32768, N=10)
- MBPP+ (CoT Code pass@1, temp=0.6, top-p=0.95, max_tokens=32768, N=10)
- LiveCodeBench v3 (CoT Code pass@1, temp=0.6, top-p=0.95, max_tokens=32768, N=10)
- ZebraLogic (CoT JSON, temp=0.6, top-p=0.95, max_tokens=32768, N=1)
- BigBench-Hard (CoT EM, temp=0.6, top-p=0.95, max_tokens=32768, N=1, 23 subtasks)
- GPQA (CoT MC Acc, temp=0.6, top-p=0.95, max_tokens=32768, N=1)
- AGI Eval English (CoT MC Acc, temp=0.6, top-p=0.95, max_tokens=32768, N=1, 9 subtasks)
- MMLU (CoT MC Acc, temp=0.6, top-p=0.95, max_tokens=32768, N=1, 57 subtasks)
- IFEval (CoT Custom, temp=0.6, top-p=0.95, max_tokens=32768, N=1)
- PopQA (CoT MC Acc EM Recall, temp=0.6, top-p=0.95, max_tokens=32768, N=1)
- AlpacaEval v2 LC (CoT Winrate, temp=0.6, top-p=0.95, max_tokens=32768, N=1)
pipeline_version: 1
publication_type: preprint
quality: full
tags: *id001
title: Olmo 3
tldr: OLMo 3系列（7B/32B）通过三阶段预训练+RL后训练流水线，在完全开放（数据/代码/权重全开源）条件下实现MATH 96.2%、AIME 2024
  80.6%，与Qwen 3 32B持平，超越DS-R1 32B
url: https://arxiv.org/abs/2512.13961
venue: arXiv preprint (not yet peer reviewed)
---
#### 核心速览 (Executive Summary)

##### TL;DR

OLMo 3系列（7B/32B）是首个在**完全开放**（训练数据、代码、中间检查点全部公开）条件下达到前沿推理性能的语言模型家族（§2.1, §2.2）。旗舰模型 OLMo 3.1 Think 32B 在 MATH 上达到 **96.2%**，AIME 2024 达到 **80.6%**，AIME 2025 达到 **78.1%**，与闭源训练数据的 Qwen 3 32B（80.8%/70.9%）持平，全面超越 DeepSeek-R1 32B（70.3%/56.3%）（Table 1；§2.3）。代价是：从头训练到最终评估共耗费约 **56天 × 1024张H100 GPU**，折合约 **275万美元**（§2.4）。

##### 一图流

旧方法（OLMo 2）：4T token 预训练 → 简单 SFT+DPO 后训练，推理能力 MATH 仅 49.2%，AIME 2024 仅 4.6%（参见 Table 13）。

新方法（OLMo 3）：5.93T token 预训练（§3.4）+ 100B token 思维链增强中训（Dolmino Mix，§3.5）+ 50B token 长文本扩展（§3.6）→ SFT（45B token 推理链，§4.2）→ DPO（delta学习，§4.3）→ OlmoRL（改进GRPO，§4.4）→ MATH 96.2%，AIME 2024 80.6%，指令跟随 IFBench 68.1%（vs. DS-R1 的 23.8%；Table 1；§4.1）。

图2所示的模型流展示了整条流水线：基础模型训练（预训练→中训→长文本扩展）作为左侧，后训练（SFT→DPO→RL）作为右侧，Think 模型与 Instruct 模型共享基础模型，但走不同的后训练分支。

##### 核心机制一句话

通过**质量感知上采样**构建5.93T token预训练数据集（Table 4；§3.4），再以**思维链合成数据注入中训**赋予模型推理"热启动"（Table 5；§3.5），最终用**inflight-update连续批处理改进GRPO**做RL后训练（Table 23；§4.4），在完全开放条件下将AIME 2024从4.6%提升至80.6%（§3.1，§4.1）。

#### 动机与第一性原理 (Motivation & First Principles)

##### 痛点

开放语言模型社区长期面临一个核心困境：**"完全开放"与"前沿性能"之间的巨大鸿沟**。

具体数字揭示了这一鸿沟的规模。OLMo 2 32B Instruct（前代最佳全开放模型）的 MATH 仅 49.2%，AIME 2024 仅 4.6%（Table 1）；与之同期的闭源训练数据模型 Qwen 2.5 32B 已达 MATH 80.2%、Qwen 3 32B 更达 MATH 95.4%、AIME 2024 80.8%（Table 1）。Apertus 70B（另一全开放竞争者，训练了 **15T** token，约为OLMo 3的2.5倍）的AIME 2024也只有 0.3%（Table 1）。全开放社区在推理能力上整整落后了一个数量级（§3.1）。

这一差距不仅仅是计算资源问题，而是体现在三个层面：

1. **数据质量**：开放网络数据的噪声远高于精心筛选的闭源数据；缺乏足够规模的高质量数学/代码合成数据；缺乏推理链训练数据。
2. **训练方法**：静态批处理造成高达 **54%** 的计算浪费（当生成均值为14,628 token但最大长度设为32K时）；RL基础设施不成熟导致吞吐量仅 881 tokens/sec（OLMo 2基线）。
3. **后训练策略**：缺乏可用的全开放推理模型来构建 DPO 偏好对；简单套用 GRPO 时存在难度偏置问题（标准差归一化会放大简单问题的梯度信号）。

##### 核心洞察

**Because（因为）→ Therefore（所以）因果链：**

1. **Because** 全开放推理模型极少且质量不稳定，直接从这些模型蒸馏的SFT数据质量差，**Therefore** 必须建立一套多来源合成推理链筛选管线（Dolci Think），混合QWQ、Gemini、Llama-Nemotron等模型的推理轨迹，并用正确性验证+去重过滤（§4.2；Table 17；Table 50）。

2. **Because** 即便有了高质量SFT数据，直接从零开始SFT比从有推理能力基础的模型起步效率低，**Therefore** 在中训阶段（100B token）就向预训练数据中注入思维链合成数据（包含 OMR Rewrite、QWQ推理轨迹、General Reasoning Mix等，§3.5），为后续SFT提供"热启动"——Table 10证明这一设计在数学上带来 **+5.6分**的提升（Table 6；Table 7；Table 8；Table 9）。

3. **Because** 标准GRPO在静态批处理下对变长生成响应浪费严重，且难度归一化会造成梯度信号失真，**Therefore** 设计了 OlmoRL 框架（§4.4）：(a) 引入连续批处理+inflight参数更新，吞吐量从881提升到 **2949** tokens/sec（3.4倍，Table 23）；(b) 去除KL损失，改为截断重要性采样（TIS）；(c) 去除标准差归一化（来自Dr GRPO）；(d) 采用非对称裁剪（ε_low=0.2，ε_high=0.272，来自DAPO，Table 49）。

4. **Because** 全开放生态需要 DPO 偏好对但缺乏质量一致的"chosen"响应，**Therefore** 采用 **Delta Learning**（§4.3）：chosen响应来自大模型（OLMo 3.1 Think 32B），rejected响应来自小模型（7B），这种大-小模型对比信号比依赖LLM评判的UltraFeedback式标注更稳定（Table 21；Table 32），且避免了对少量高质量推理模型的依赖（Table 19；Table 20）。

##### 物理/直觉解释

将训练一个推理模型比作培养一个数学奥赛选手：

**预训练**是打基础——让孩子广泛阅读（5.93T token），但普通课外书（Common Crawl，76.1%）必须配合数学辅导书（FineMath，2.56%）和科学论文（olmOCR，13.6%）才能有效。**中训**是强化训练——集中突击100B token的竞赛真题和解题思路（思维链数据），就像报名暑期集训班，这一阶段数学分数从 23.5分直接跳到 59.8分（OlmoBaseEval Math，7B，Stage 1→Stage 2）。**长文本扩展**是训练卷纸能力——现实竞赛题目很长，需要专门的长文档阅读训练（Longmino Mix，50B/100B token）。**SFT+DPO**是教会解题步骤——45B token的推理链SFT让模型学会"写草稿"，Delta Learning DPO让模型从"好选手vs差选手的解题对比"中学习取舍。**RL**是通过反复做题巩固——只验证最终答案正确性（可验证奖励），不依赖老师打分，是最接近真实竞赛环境的训练方式。inflight update就像训练营里边出题边批改，而不是等一整批题都做完再统一评分，这让训练效率提升了3.4倍。

#### 专家批判 (Critical Review)

##### 隐性成本

**代价1：整体算力成本约275万美元，56天不中断运行**

从训练启动到OLMo 3.1 Think 32B的最终评估，总计耗费约 **56天 × 1024张H100 GPU**（§2.4）。按 $2/H100/小时 估算，总成本约 **$2.75M（约275万美元）**。其中预训练约47天（5.5T token初始预训练约9.5天在512 GPU上，再加约35天在1024 GPU上），后训练约9天（Table 47；Table 48；Table 49）。这与DeepSeek V3引用的 $5.576M H800小时的基准成本相比略低，但OLMo 3还有 OLMo 3.1 Think 32B 额外的 **21天 × 224 GPU** RL扩展训练（约合 $20万美元），隐藏在"版本号从3.0到3.1"的低调表述里（§2.4）。

**代价2：RL训练不稳定，至少1天算力直接报废**

论文明确记录了32B Think RL训练过程中 "at least 1 day lost to instability"（至少浪费1天的1024 GPU计算）。按 $2/H100/小时 折算，这1天的浪费约合 **$49,152**。更深层的问题是，RL训练的不稳定性迫使团队引入截断重要性采样（TIS cap=2.0）、asymmetric clip 等多个稳定化手段，每一个超参数的调试都需要额外的计算实验。

**代价3：Common Crawl原始数据过滤耗费约11,300美元、超1,030 i4i.32xlarge EC2实例小时**

论文脚注明确记录了网页启发式过滤的单独算力成本：约 **1,030 i4i.32xlarge EC2小时，约$11,300**（Table 36；§3.4）。这仅是预训练数据管线的一个环节，未包含MinHash去重、FastText质量分类器训练（Table 37）、olmOCR PDF解析等其他数据处理成本（Table 4；Table 5）。整个Dolma 3数据管线的实际数据工程成本估计超过预训练GPU成本的5%。

**代价4：SFT学习率搜索耗费约2天 × 256 GPU**

后训练SFT阶段并不是单次运行（§4.2）。论文描述了对4个候选学习率并行运行36小时（256 GPU each），总计约 **4次 × 256 GPU × 36小时 = 36,864 GPU小时**，加上评估和合并时间约2天。32B Thinking SFT最终使用两个学习率 checkpoint 的 soup（5e-5 和 1e-4，Table 47），意味着两次完整训练都被保留并合并，进一步增加了单次看似"简单"SFT的实际成本（Table 18）。

**代价5：静态批处理的54%计算浪费（已解决但揭示问题严重性）**

论文明确量化了改进前的浪费规模：在32K最大长度设定下，平均生成长度仅14,628 token，意味着静态批处理下高达 **54%** 的计算为填充浪费。OLMo 2的RL基础设施在这种浪费下仅能达到 881 tokens/sec 的吞吐量，相当于每花1美元只有46美分真正用于有效计算。inflight update解决了这一问题，但这一事实揭示出：任何直接复用OLMo 2风格静态批处理做长输出RL的团队，都会面临同等规模的效率损失。

##### 最值得复用的技术

**技术1：Delta Learning DPO偏好对构建方案（改几行代码，预期收益显著）**

核心思路极其简单：chosen响应从大模型（如32B Think）采样，rejected响应从小模型（7B）采样，用差异信号构建偏好对，而非依赖LLM评判（§4.3；Table 32）。实现成本约等于：(a) 有一个大模型和一个小模型的推理能力，(b) 修改偏好对构建脚本（约50行代码，Table 48）。预期收益：Table 22显示，SFT+DPO相比纯SFT在7B上平均提升2.6分（70.1→72.7），AIME 2025从57.6提升到62.7。对于缺乏大规模LLM评判预算的团队，这是一个极具性价比的替代方案，尤其在推理任务场景下（chosen模型天然有可验证的正确性信号；Table 21；Table 19）。

**技术2：中训注入思维链数据的"热启动"策略（需要合成数据生成能力）**

在预训练后专门设计一个100B token的中训阶段（§3.5），混入多来源推理链数据（Table 5；Table 10），可以把后续SFT和RL的起点大幅提前。Table 13数据表明，7B模型经过Stage 2中训后，OlmoBaseEval Math从23.5跳至59.8（+36.3分），而Apertus 8B训练15T token后仅达29.3分。实现成本：需要一个合成数据生成管线（Table 41；Table 42；Table 43；Table 44；或直接使用论文开源的Dolmino数据集），以及约1.5天的512 GPU中训计算（Table 34；Table 35）。这一策略对于任何从头训练基础模型、计划后续增强推理能力的团队都高度可复用（§3.3；§3.7）。

##### 最大的坑

**坑1：特殊token污染导致评测分数归零（GSM8K从49.43→0）**

论文明确记录了一个灾难性失误（§3.5）：若在中训数据中保留聊天模板特殊token（如 `<|im_start|>`），模型在推理时会在非chat场景下输出这些token，导致GSM8K评分从49.43直接降至0。规避方法：**在中训指令数据中必须剥离所有特殊token，改用双换行分隔**。这一处理是反直觉的（通常人们认为保留格式有助于SFT），但在多阶段训练中至关重要（Table 6；Table 7）。任何复用Dolmino Mix或类似中训方案的团队，若不做这一处理，将面临评测结果完全不可信的风险。

**坑2：RL训练不稳定，超参数敏感，至少损失1天GPU（即约$5万）**

OlmoRL的RL训练（尤其是32B模型）存在明显的训练不稳定性，论文承认"至少1天因不稳定损失"（§4.4）。稳定性关键依赖TIS cap（ρ=2.0）、ε_high=0.272（而非标准的0.2）、去除KL损失等多个非标准设置的组合（Table 49；§4.4.1）。若单独只用DAPO或Dr GRPO的某一改进，而不做完整组合，稳定性风险会大幅上升。另外，7B和32B的actor GPU配置差异很大（7B用56个actor GPU，32B用160个，Table 49），推理到训练的GPU比例分别约为14x和5x，任何规模迁移都需要重新校准这个比例。

##### 关联技术

**DeepSeek R1 32B：闭源预训练数据的天花板（§4.1；Table 1；Table 14）**

共同点：同为32B规模推理模型，均使用RLVR（可验证奖励RL）；差异：OLMo 3全开放训练数据（§2.1），DS-R1使用闭源预训练数据。性能对比（Table 1）：MATH 96.2% vs 92.6%，AIME 2024 80.6% vs 70.3%，IFBench 68.1% vs 23.8%（OLMo 3在指令跟随上大幅领先；Table 24）。选择建议：若需要完整训练溯源和可复现性，选OLMo 3；若仅需推理能力且不介意数据黑箱，DS-R1 32B在纯编码任务上略强（LiveCodeBench 79.5% vs 83.3%，OLMo 3更好，Table 14）。

**Qwen 3 32B：同规模最强开放权重基准（§4.1；Table 1；Table 14）**

共同点：均为32B推理模型，后训练均含SFT+DPO+RL（§2.2）；差异：Qwen 3使用闭源预训练数据（token量未公开），不发布预训练数据；OLMo 3使用公开5.93T token预训练（Table 4；§3.4）。性能对比（Table 1；Table 14）：MATH 96.2% vs 95.4%（OLMo 3略优），AIME 2024 80.6% vs 80.8%（基本持平），ZebraLogic 80.1% vs 88.3%（OLMo 3落后），LiveCodeBench 83.3% vs 90.2%（OLMo 3落后）。选择建议：若场景强调数学推理和指令跟随（IFBench 68.1% vs 37.3%；Table 1），OLMo 3更优；若场景强调代码生成和逻辑谜题，Qwen 3 32B更强（Table 25；§5.5）。

**Apertus 70B：全开放赛道最接近的竞争者（§3.1；Table 2；Table 13）**

共同点：均为完全开放的基础模型（数据、代码、权重全部公开；§2.1）；差异：Apertus 70B 训练了15T token（约为OLMo 3 32B的2.5倍token、2.2倍参数），但性能被OLMo 3 32B全面超越（Table 2；Table 13）。性能对比（Instruct，Table 25；Table 1）：MATH 93.4% vs 36.2%，AIME 2024 67.8% vs 0.31%。选择建议：Apertus 70B的优势在于英法双语能力（Gaperon系列专为法语优化），OLMo 3在单语英文推理和指令跟随上无争议领先（Table 12；§3.7）。这一对比强力支持了OLMo 3的核心论点（§3.4；§2.3）：更多token训练不如更好的数据质量和训练策略（Table 38；Table 40；§3.4.4）。

#### 方法详解 (Methodology)

##### 直觉版

OLMo 3 是 Allen AI 发布的全开放大语言模型系列，覆盖 7B 和 32B 两个规模，并衍生出 Instruct（通用指令跟随）与 Think（长链推理）两个子系列（§2.1；§2.2）。"全开放"意味着训练数据、代码、中间检查点一律公开，这一承诺直接影响了整条技术路线的选择。

**Figure 1** 展示了 OLMo 3 的完整模型流：从训练数据（Dolma 3 数据集家族，Table 4；Table 5；Table 11）出发，经由预训练（Stage 1，§3.4）→ 中训练（Stage 2，§3.5）→ 长上下文扩展（Stage 3，§3.6）形成 Base 模型（§3.1），随后进入后训练阶段——SFT（§4.2；§5.2）→ DPO（§4.3；§5.3）→ RLVR（OlmoRL，§4.4；§5.4）——输出最终的 Instruct 或 Think 模型（§4.1；§5.1）。整个流程的训练代码分别托管于 `olmo-core`（预训练）、`open-instruct`（后训练）、`dolma3`（数据）和 `olmes`（评估）四个仓库，实现了从数据到模型权重的完整可复现性。

**Figure 2** 更详细地展示了后训练各子阶段的流向。与 OLMo 2 的简单 SFT+DPO 流程相比，OLMo 3 在此基础上增加了两条关键路径：（1）针对 Think 系列，采用 Dolci Think 高质量推理数据进行 SFT 热启动（Table 17；Table 18），再通过 OlmoRL 做 RLVR 强化（Table 20；Table 22；Table 23；§4.4；§4.5）；（2）针对 Instruct 系列，从 Think SFT checkpoint 出发继续训练（Table 29；§5.2），避免了从基础模型重新微调的计算浪费，同时保留了推理能力的"记忆"（§5.5）。

**旧方案（OLMo 2）的局限：**
- 预训练数据以 Common Crawl 网页为主，缺乏大规模合成推理数据（Table 13，OLMo 2 Stage 1 Math仅12.7）
- 后训练流程：SFT + DPO，无 RL 阶段（§2.2）
- 上下文窗口 8K，无长上下文扩展（§3.6）
- RL 基础设施（静态批处理）效率低，计算浪费严重（Table 23，OLMo 2 基线仅881 tokens/sec）

**OLMo 3 的核心改变（§2.1；§3.2）：**
- Dolma 3 引入 olmOCR 科学 PDF（805B tokens，Table 4）、Dolci Think 合成推理链（Table 17；Table 20）、CraneMath/CraneCode 等数学代码合成数据（Table 5；Table 41；Table 42；Table 43；Table 44）
- 三阶段基础训练（§3.4；§3.5；§3.6）+ 三阶段后训练（§4.2；§4.3；§4.4），形成完整流水线（§3.3）
- OlmoRL 基础设施：连续批处理 + 飞行更新（inflight updates），吞吐量提升 3.4×（Table 23；§4.4）
- 后训练从 Think SFT 热启动，大幅缩短训练时间（Table 29；Table 47；§5.2）

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
| 隐藏维度 (dmodel) | 4096 | 5120 |
| Q heads | 32 | 40 |
| KV heads（GQA）| 32 | 8 |
| 激活函数 | SwiGLU | SwiGLU |
| QKV 归一化 | QK-Norm | QK-Norm |
| 层归一化 | RMSNorm | RMSNorm |
| 滑动窗口注意力 | 3/4 of layers; 4,096 token window | 3/4 of layers; 4,096 token window |
| RoPE 缩放 | YaRN（仅全注意力层）| YaRN（仅全注意力层）|
| RoPE θ | 5 × 10^5 | 5 × 10^5 |
| 梯度裁剪 | 1.0 | 1.0 |
| Z-loss 权重 | 10^−5 | 10^−5 |
| Embedding 权重衰减 | No | No |

**表二：训练配置与吞吐量（Table 34）**

| 阶段 | DP-rep | DP-shard | CP | 设备数 | TPS/device |
|---|---|---|---|---|---|
| 7B 预训练 | 64 | 8 | - | 512 | 7.7K |
| 7B 中训练 | 16 | 8 | - | 128 | 8.5K |
| 7B 长上下文扩展 | 32 | - | 8 | 256 | 4.0K |
| 32B 预训练 | 16 | 64 | - | 1024 | 2.0K |
| 32B 中训练 | 8 | 64 | - | 512 | 2.0K |
| 32B 长上下文扩展 | 16 | 8 | 8 | 1024 | 1.3K |

**表三：基础训练超参数（Table 35）**

| 超参数 | 7B 预训练 | 7B 中训练 | 7B 长上下文 | 32B 预训练 | 32B 中训练 | 32B 长上下文 |
|---|---|---|---|---|---|---|
| LR 调度 | 修正余弦 | 线性衰减 | 线性衰减 | 余弦（5.5T截断）| 线性衰减 | 线性衰减 |
| LR 热身 | 2000 steps | 0 steps | 200 steps | 2000 steps | 0 steps | 200 steps |
| 峰值 LR | 3.0×10^−4 | 2.074×10^−4 | 2.074×10^−4 | 6.0×10^−4 | 2.071×10^−4 | 2.071×10^−4 |
| 终止 LR | 3.0×10^−5 | 0 | 0 | 6.0×10^−5 | 0 | 0 |
| Batch（实例）| 512 | 256 | 64 | 1024 | 512 | 128 |
| 序列长度 | 8,192 | 8,192 | 65,536 | 8,192 | 8,192 | 65,536 |
| Batch（tokens）| 4,194,304 | 2,097,152 | 4,194,304 | 8,388,608 | 4,194,304 | 8,388,608 |
| 总 tokens | 5.93T | 100B | 50B | 5.5T | 100B×2 | 100B |

**表四：SFT 超参数（Table 47）**

| 超参数 | 7B Think SFT | 32B Think SFT | 7B Instruct SFT |
|---|---|---|---|
| 总 Tokens | 45.4B | 45.2B | 3.4M |
| 学习率 | 5.0×10^−5 | 1.0×10^−4（与5.0×10^−5 soup）| 8.0×10^−5 |
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
| 学习率 | 8.0×10^−8 | 7.0×10^−8 | 1.0×10^−6 |
| LR 调度 | 线性衰减 | 线性衰减 | 线性衰减 |
| 热身比例 | 0.1 | 0.1 | 0.1 |
| GPU 数量 | 32 | 64–128 | 16 |
| Batch size | 128 | 128 | 128 |
| 最大序列长度 | 16K | 8K | 16K |

**表六：RL 超参数（Table 49）**

| 超参数 | 7B Think RL | 32B Think RL | 7B Instruct RL | 7B RL-Zero |
|---|---|---|---|---|
| 数据集规模 | 104,869 | 104,869 | 171,950 | 13,314 |
| 学习率 | 1.0×10^−6 | 2.0×10^−6 | 1.0×10^−6 | 1.0×10^−6 |
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

**论文是否对比：** 是。Table 33 和 §3.2 明确说明架构选择（7B：32层，dmodel=4096；32B：64层，dmodel=5120）；Table 34 列出各阶段设备配置与吞吐量；Figure 13a 对长上下文扩展的多种 RoPE 策略做了对比（包括是否对 SWA 层应用 YaRN；§3.6.1）。

**核心 trade-off：**
- 全注意力提供最优的理论表达力，每个 token 可以与所有历史 token 交互，但训练时内存随序列长度平方增长（$O(n^2)$），推理时 KV cache 随序列增大。
- SWA 将 3/4 的层限制在局部窗口（4,096 tokens），仅最后 1/4 的层做全局注意力，使得训练和推理的实际开销大幅降低，同时通过层叠的局部注意力保留了跨长距离的信息流动能力（信息可以在多层中传播）。

**为何本文选择优于替代方案：** 在 5.93T tokens 的预训练规模下，采用 SWA 使得序列长度可以从 4K 扩展到 65K，同时控制了基础设施成本（Table 35；§3.4.1）。全注意力在相同序列长度下每个 H100 GPU 的吞吐量无法维持 7.7K tokens/s 的目标（Table 34）。混合架构在全部 OlmoBaseEval 指标上与全注意力对齐（Table 45；Table 46），同时为长上下文扩展留出余地（Table 12；§3.7）。

###### 决策二：YaRN 仅应用于全注意力层（非 SWA 层）

**替代方案：** 将 YaRN 应用于全部层（包括 SWA 层），或使用位置插值（Position Interpolation，PI），或调整 RoPE base frequency。

**论文是否对比：** 是。Figure 13a 展示了不同 RoPE 扩展策略在 RULER 评测上的对比结果，"YaRN on full attention only"在各序列长度上均优于其他方案。

**核心 trade-off：**
- SWA 层的注意力窗口固定为 4,096 tokens，对其应用 YaRN（设计目标是改变位置编码使模型在超出训练长度时仍能定位）收益有限，因为这些层本身就只能看到局部上下文。将 YaRN 施加于 SWA 层反而可能扰乱原有的局部模式匹配。
- 全注意力层是长距离信息聚合的关键节点，在这里调整 RoPE 频率可以有效改善模型在超长序列上的绝对位置感知，是性价比最高的干预点。

**为何本文选择优于替代方案：** 对 SWA 层施加 YaRN 不仅收益为零，还可能破坏短文本性能。对全注意力层单独施加 YaRN 在 RULER 32K 和 65K 的评测上取得了最优分数，同时基础 OlmoBaseEval 指标未见明显下滑。

###### 决策三：长上下文扩展数据配比（34% 长文本 + 66% 短中训练数据）

**替代方案：** 采用更高比例的长上下文数据（如 66% 长文本 + 34% 短数据）。

**论文是否对比：** 是。§3.6.3 直接对两种配比做了对比实验（Longmino Mix 组成见 Table 11；长上下文评测见 Table 12；§3.6）。

**核心 trade-off：**
- 更多长上下文数据直观上应该帮助模型学会处理更长序列，但训练 distribution 偏移过大会导致模型在短序列任务上的能力退化。
- 66% 长上下文配比导致 OlmoBaseEval（以短序列为主的基础评测集）下降约 2.5 个百分点；
- 34% 长上下文配比将 OlmoBaseEval 下降控制在 0.8 个百分点以内，同时仍能有效提升 RULER 和 HELMET 的长上下文性能。

**为何本文选择优于替代方案：** 这是一个典型的"不能丢失旧能力换取新能力"的权衡。对于应用场景多样的通用模型，维持短序列任务的竞争力（OlmoBaseEval 损失 < 1 点）比极致优化 128K 长上下文性能更重要。34% 的配比在两个维度上都达到了可接受的平衡点。

###### 决策四：32B 模型 Model Souping（两路独立训练后合并）

**替代方案：** 仅做一次中训练 run，取最终 checkpoint。

**论文是否对比：** 是。§3.5.4 和对应 Table（Table 13 中的 Ingredient 1、Ingredient 2 对比 Soup 行；Table 35 列出超参数配置）明确展示了合并效果：
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

**论文是否对比：** 是。Table 21 和 §4.3 对比了多种 DPO 数据构造策略（Table 32）。直接对 chosen 响应做 SFT 反而会降低性能（因为 SFT 分布与 DPO 分布不匹配）；Delta Learning 的 chosen 来自明显更强的大模型（而非同一模型的不同采样），对比信号更清晰（Table 19；Table 30）。

**核心 trade-off：**
- 传统 LLM-judge 方法要求"同一模型的不同质量输出"，但对于推理任务（AIME、LiveCodeBench），同一 7B/32B 模型的不同采样之间质量差距不够大，judge 信号噪声高。
- Delta Learning 利用"大模型能力 vs. 小模型能力"的本质差距构造对比对：chosen 来自 Qwen 3 72B、DeepSeek R1 等强模型，rejected 来自 OLMo 2 7B/32B，两者质量落差巨大，提供了清晰的学习目标。
- 缺点：chosen 分布来自外部模型，OLMo 3 基础模型的"原有风格"可能受到影响；但实验表明 IFEval 等指令跟随指标并未下降。

**为何本文选择优于替代方案：** 在开放推理模型稀缺的情况下（训练时公开的长链推理模型极少），从强模型蒸馏出高质量 chosen 响应，再用弱模型生成 rejected 响应，是获取高质量偏好信号的最经济路径（Table 48；§4.3.1）。Table 21 证明这一策略的最终 DPO 模型在数学推理上相比 SFT 有显著提升（如 AIME 2025：Table 25 中 32B SFT 8.2% → DPO 23.3%；Table 51）。

###### 决策六：OlmoRL 基础设施的连续批处理 + 飞行更新（Inflight Updates）

**替代方案：** 静态批处理（OLMo 2 的做法：等待一整个 batch 的 rollout 全部完成后再更新策略）。

**论文是否对比：** 是。Table 23 精确记录了每个优化步骤的吞吐量提升（§4.4；§4.4.3）：

| 配置 | Tokens/second | MFU (%) | MBU (%) |
|---|---|---|---|
| OLMo 2 基线（静态批处理）| 881 | 0.30 | 12.90 |
| + 连续批处理 | 975 | 0.33 | 14.29 |
| + 优化线程 | 1358 | 0.46 | 19.89 |
| + 飞行更新（OLMo 3）| 2949 | 1.01 | 43.21 |

最终吞吐量相比基线提升 3.4×（881→2949 tokens/s）。详细 RL 超参数见 Table 49。

**核心 trade-off：**
- 静态批处理最简单，但 RL rollout 的生成长度高度不均匀（平均 14,628 tokens，最大 32K），导致短序列大量等待长序列，填充（padding）浪费高达 54% 的计算。
- 飞行更新允许策略参数在新一批 rollout 进行中就被更新，因此 actor（vLLM）和 learner（策略模型）之间存在异步性。为了修正这一分布偏移，OlmoRL 引入了截断重要性采样（TIS cap $\rho$），确保更新仍在理论保证范围内。
- 最大异步度 = 8 对于 32B 模型意味着最多允许 8 步 rollout 用"过时"策略采样，权衡训练稳定性与吞吐量。

**为何本文选择优于替代方案：** 对于 32B Think 模型 21 天的 RL 扩展训练，3.4× 的吞吐量提升等价于将计算成本从 ~71 天压缩到 ~21 天，节省约 50 天 224 GPU 的费用。这不是工程优化的"锦上添花"，而是让如此长时间 RL 训练在合理预算内可行的前提条件。

###### 决策七：从 Think SFT checkpoint 热启动训练 Instruct 模型

**替代方案：** 从 Base 模型直接开始 Instruct 的 SFT 训练。

**论文是否对比：** 是。Table 29（§4.5；§5.2）对比了两种初始化方案，从 Think SFT 出发比从 Base 出发平均提升 +3.3 个基准点，且响应长度并未因此变长（没有"被推理链污染"；Table 28；Table 30）。

**核心 trade-off：**
- Think SFT 训练了 45B tokens 的链式推理数据，其中隐含了大量数学和代码的"解题过程"知识。从这个 checkpoint 出发做 Instruct SFT（仅 3.4M tokens），等于"免费"继承了这些知识，同时通过少量指令数据将输出风格切换为简洁答案。
- 担忧：Think 训练引入的"想多"倾向可能导致 Instruct 模型输出冗长思考链。实验表明这一担忧不成立——Instruct 模型的 IFEval 和 AlpacaEval 响应长度与直接从 Base 训练的版本无显著差异。

**为何本文选择优于替代方案：** 在计算成本方面，Instruct SFT 只需 3.4M tokens（相比 Think SFT 的 45B tokens），从 Think SFT 热启动实际上是以零额外基础训练成本继承了一个更强的初始点，+3.3 点的平均提升是纯粹的"免费午餐"。

###### 决策八：去除 GRPO 中的 KL 损失项和标准差归一化

**替代方案（KL 项）：** 保留标准 PPO/GRPO 的 KL 惩罚项（$\beta_\text{KL} \cdot \text{KL}[\pi_\theta \| \pi_\text{ref}]$）。

**替代方案（Std 归一化）：** 将优势值除以组内标准差 $\sigma$（$A' = (r - \bar{r})/\sigma$）。

**论文是否对比：** 是。§4.4.1 分析了这两个设计选择的理论动机（Table 22；Table 49）。Dr GRPO（Liu et al., 2025b）在此基础上的去除实验表明 std 归一化会引入难度偏差（Table 23）。

**核心 trade-off：**
- KL 损失的目标是防止策略偏离 SFT checkpoint 过远。但 OlmoRL 通过非对称 clip（$\varepsilon_\text{high} = 0.272$）和 TIS cap（$\rho = 2.0$）已经隐式控制了更新步长，额外的 KL 项会过度限制推理任务中模型的"探索空间"，对 AIME 等需要大幅超越 SFT 能力的任务尤为不利。
- Std 归一化：当一道题只有 1/8 的 rollout 答对时，组内奖励方差大，归一化后梯度信号被放大；当一道题 7/8 都答对时，方差小，信号被缩小。这在概念上是合理的（"难题学得多"），但实际上会使不同难度的题目在梯度上获得不一致的影响力，且对极端情况（全对/全错的简单/极难题）表现异常。去除归一化后，梯度自然按难度分布。

**为何本文选择优于替代方案：** 这两个去除操作共同使 OlmoRL 成为一个"约束更少的策略优化器"，在已有 clip 机制保障稳定性的前提下，给予模型更大的学习自由度，对 AIME 2025 这类极难任务的提升（SFT 66.2% → 最终 78.1%）印证了这一判断。

##### 易混淆点

**易混淆点一：OLMo 3 的"全开放"等于"训练数据完全公开"**

❌ 错误理解：OLMo 3 的全开放意味着可以用完全相同的数据从零复现训练，与闭源模型的本质区别只是"代码开源"。

✅ 正确理解："全开放"在 OLMo 3 中有明确的技术含义（§2.1）：训练数据（Dolma 3 + Dolmino + Longmino 所有子集的下载链接，Table 4；Table 5；Table 11）、训练代码（olmo-core、open-instruct、dolma3 四个仓库）、所有中间检查点（Stage 1/Stage 2/Stage 3 checkpoint 以及 SFT/DPO/RL 的各阶段权重，§3.4；§3.5；§3.6；§4.2；§4.3；§4.4）均公开。这与仅公开最终权重（如 Llama 3.1）或仅公开代码（如部分研究模型）有本质区别。实践上，重现仍需 ~$2.75M 的 H100 算力（OLMo 3.1 Think 32B 总训练成本，§2.4；Table 47；Table 48；Table 49），"可复现"≠"人人能重跑"。

**易混淆点二：Think 系列和 Instruct 系列是两个独立的微调流程**

❌ 错误理解：OLMo 3 Think 和 OLMo 3 Instruct 分别从 Base 模型独立做 SFT，两者没有参数依赖关系。

✅ 正确理解：Instruct 系列并非从 Base 出发，而是以 Think SFT checkpoint 作为初始化（Figure 2 中有明确流向；§5.2；§4.5）。具体路径为：Base → Think SFT（45B tokens，Table 47）→ 分叉：（1）Think 路线继续做 Think DPO（Table 48；§4.3）→ OlmoRL（Table 49；§4.4）→ Think Final（Table 14；§4.1）；（2）Instruct 路线在 Think SFT checkpoint 上做 Instruct SFT（3.4M tokens，Table 47；§5.2）→ Instruct DPO（Table 48；§5.3）→ OlmoRL（Table 49；§5.4）→ Instruct Final（Table 25；Table 26）。因此 Instruct 模型"天生"继承了 Think SFT 积累的推理知识（Table 29），仅用 3.4M tokens 的指令数据来调整输出风格（Table 30；Table 28），这也是 Instruct 模型数学能力远超 OLMo 2 Instruct 的关键原因（Table 25：AIME 2024 从 4.6% 提升到 67.8%；§5.1；§5.5）。

**易混淆点三：OlmoRL 和标准 GRPO 的区别只是工程优化**

❌ 错误理解：OlmoRL 相比 GRPO 的改进主要是吞吐量（连续批处理），算法本身与 GRPO 相同。

✅ 正确理解：OlmoRL 在算法层面做了四项独立改变，每项都有对应文献支撑（§4.4；§4.4.1）：（1）**非对称裁剪**（$\varepsilon_\text{low}=0.2, \varepsilon_\text{high}=0.272$，Table 49）：来自 DAPO，允许高奖励 token 获得更大梯度更新，而非标准 PPO 的对称裁剪；（2）**去除 KL 损失**：减少对 SFT checkpoint 的过度约束；（3）**去除优势方差归一化**：来自 Dr GRPO，消除难度偏差；（4）**截断重要性采样（TIS cap $\rho$=2.0，Table 49）**：处理异步更新导致的 actor/learner 策略分布偏移。工程层面的连续批处理和飞行更新则带来 3.4× 吞吐量提升（Table 23：881→2949 tokens/s；§4.4.3），这是使得 21 天 RL 扩展训练可行的基础设施前提，而非可选优化。两个维度（算法 + 基础设施）共同构成了 OlmoRL 相对于标准 GRPO 的改进（§4.4）。

**易混淆点四：中训练阶段的思维链数据使模型"变成"推理模型**

❌ 错误理解：OLMo 3 Base 在中训练阶段混入了大量推理链数据（QWQ、Gemini reasoning traces 等），因此 Base 模型本身已经具备了 Think 系列的推理能力，后训练只是微调风格。

✅ 正确理解：中训练中的推理链数据（约 7.73B tokens，占 Dolmino Mix 的约 8%，Table 5）的目的是为 Base 模型注入"如何写推理过程"的语言模式，使后续 SFT 阶段的学习效率更高（论文称为"warm-start"；§3.5；§3.5.2）。Table 10 显示加入推理链后 Base 模型在 Math 上只提升 +5.6 点（43.1→48.7），距离 Think 系列的 MATH 96.2% 还有巨大差距（Table 1；Table 14；§4.1）。真正的推理能力提升来自于 Think SFT（45B tokens 高质量推理数据，Table 17；Table 18；§4.2）+ DPO（Delta Learning 偏好对，Table 21；Table 22；§4.3）+ OlmoRL（750步 RLVR，Table 49；§4.4）的完整后训练流程（§2.2；§4.5）。中训练只是"打地基"，而非"建完大楼"。

#### 实验与归因 (Experiments & Attribution)

##### 对比表格

**表 A：OLMo 3.1 Think 32B 在后训练评测集的完整基准对比（Table 1；§4.1；§3.1）**

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

**关键发现（§4.1；§4.5）：** OLMo 3.1 Think 32B 在 AIME 2025（78.1%）和 OMEGA（53.4%）上超越 DS-R1 32B（56.3% / 38.9%）和 Qwen 3 32B（70.9% / 47.7%，Table 1），证明全开放模型在最难数学竞赛题上已达到开放权重模型的顶尖水准。IFBench 上 OLMo 3.1 Think 32B 以 68.1% 大幅领先所有基线（第二名 Qwen 3 VL 32B Think 为 55.1%，Table 1；Table 24），体现了 OlmoRL Instruct 阶段专门训练指令跟随能力的效果（§5.4；§5.5）。PopQA 是唯一弱于 OLMo 2 的指标（30.9 vs. 37.2），说明推理强化导致部分事实性知识回忆能力下降（Table 16评测配置）。

**表 B：OLMo 3 Base 32B 全面基准对比（Table 2，OlmoBaseEval Main；§3.1；§3.7）**

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

**关键发现（§3.7；§3.1）：** OLMo 3 Base 32B 以 5.5T tokens 的预训练量在 OlmoBaseEval Math（61.9）和 Code（39.7）上超越了 Apertus 70B（训练量 15T tokens，Math 39.7 / Code 23.3，Table 2），证明数据质量和混合策略对计算效率的提升超过了规模扩展（Table 38；Table 39；Table 40）。在 LBPP（21.8）上也大幅超过 OLMo 2 32B（8.2，Table 2），证明中训练阶段代码数据的有效性（Table 42；Table 44）。评测集配置详见 Table 45 和 Table 46。

**表 C：OLMo 3 Think 32B 后训练各阶段进展对比（Table 14；§4.1；§4.5）**

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

**关键发现（§4.5）：** AIME 2025 从 SFT（66.2%）→ DPO（70.7%）→ OLMo 3.0 RL（72.5%）→ OLMo 3.1 扩展 RL（78.1%），每一阶段均有稳定提升，且扩展 RL 阶段（+5.6%）贡献最大（Table 14；Table 22）。IFBench 从 DPO（34.4%）→ OLMo 3.0（47.6%）→ OLMo 3.1（68.1%）的跳跃提升主要来自于 Instruct 路线 RL 阶段专项强化指令跟随能力后的知识共享（Table 24；§5.4；§5.5；Table 52；Table 54）。7B 模型的对应结果见 Table 15 和 §4.1。

**表 D：OLMo 3.1 32B Instruct 后训练各阶段对比（Table 25；§5.1；§5.5）**

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

**关键发现（§5.1；§5.5）：** DPO 阶段是 Instruct 路线数学能力的最大贡献者——AIME 2024 从 SFT（12.7%）跳至 DPO（35.2%），增幅 +22.5%，远超后续 RL 的增量（35.2%→67.8%，Table 25；§5.3；§5.4）。LitQA2（55.6%）大幅超越 Qwen 3 32B（46.7%）和 Qwen 2.5 32B（26.2%，Table 25），体现了 olmOCR 科学 PDF 数据对文献理解能力的持续性贡献（Table 4；Table 31）。7B Instruct 的对应结果见 Table 26（§5.1）。函数调用数据集详见 Table 27（§5.2）。安全评测结果见 Table 53 和 Table 55。

##### 归因排序

按对核心推理能力（AIME 2025 + OMEGA 平均 delta）的贡献排序：

- **OlmoRL 扩展训练（21 天 +224 GPUs）** (+12.5 on AIME 2025, Table 14 OLMo 3.0→3.1；§4.4；§4.5)：从 72.5% 到 78.1%，这是单项最大的后训练提升。更多 RL 步数 + 更大 actor 计算允许模型探索更难的数学推理路径（Table 49；Table 20）。OLMo 3.0 Think 已达到 750 步 RL 的收益极限，扩展到更长 RL 持续改善。

- **DPO Delta Learning**（+11.4 on AIME 2024, Table 25 SFT→DPO；§4.3；§5.3）：AIME 2024 从 12.7%→35.2%（Instruct，Table 25）和 73.5%→76.0%（Think，Table 14），DPO 阶段通过大模型 chosen vs. 小模型 rejected 的高质量对比信号，大幅改善了模型对验证性推理步骤的偏好（Table 21；Table 32；Table 48）。

- **Dolmino Mix 中训练（合成推理链 + 合成数学）**（+5.6 on Math eval, Table 10；§3.5；§3.5.4）：无推理链版 Base Math = 43.1，加入推理链后 = 48.7，+5.6 点（Table 6；Table 7；Table 8；Table 9）。这是基础模型层面的核心改进，为后续 SFT 和 RL 提供了更好的参数初始化。

- **Model Souping（32B）**（+2.9 on Math, Table 13 Soup vs. Ingredient 1；§3.5.4）：66.8→69.7（Math），两次独立训练的参数平均使模型落在更平坦的损失盆地，提升了泛化能力，且无推理时额外开销（Table 35）。

- **Think SFT 热启动 Instruct 训练**（+3.3 avg benchmark, Table 29；§5.2；§4.5）：从 Think SFT checkpoint 出发比从 Base 出发平均提升 3.3 个基准点，体现了推理知识向通用指令跟随任务的迁移能力（Table 47；Table 28；Table 30）。

- **OlmoRL 基础设施改进（连续批处理 + 飞行更新）**（+3.4× 吞吐量, Table 23；§4.4）：881→2949 tokens/s 的吞吐量提升不直接体现在评测数字上，但使得 21 天扩展 RL 训练在预算内可行，是间接贡献最大的工程组件（Table 49）。

- **长上下文扩展（Stage 3）**（+5–15 on RULER 32K-65K, Table 12；§3.6；§3.6.3）：Olmo 3 32B 在 RULER 65K 上达到 79.70，高于 Apertus 70B（60.33）和 Qwen 2.5 32B（80.73，Table 12），长上下文扩展成本仅 100B tokens（约 1 天 1024 GPUs，Table 35）但带来了显著的长文本处理能力（Table 11）。RL-Zero（从 Base 直接做 RL）的额外结果见 §6.1 和 §6.2。

##### 可信度检查

**维度一：去污染（Decontamination；§3.3；§3.3.2）**

OLMo 3 使用了专门开发的 `decon` 工具（github.com/allenai/decon）对训练数据做了 8-gram 匹配去污染，同时在评测集选择上明确标注哪些集合是"held-out"（Table 16 中带 * 的任务如 AIME 2024、AIME 2025、MBPP+、LiveCodeBench v3、ZebraLogic、GPQA、AGI Eval 等是专门的保留集）。Table 2 和 Table 3 区分了 "OlmoBaseEval Main" 和 "HeldOut" 两个分区（Table 45；Table 46），Base 模型在 BBH（77.6）和 MMLU Pro MC（49.7）等 held-out 集上的表现与 Main 集相当，未出现 held-out 集异常低的情况，表明训练数据去污染有效（Table 36；§3.4）。但 AIME 题目数量有限（AIME 2024 仅 30 题，AIME 2025 亦然），32 次采样平均后的方差仍较高，单次评估的置信区间约 ±3-5%。

**维度二：Baseline 公平性（§3.1；§3.7）**

论文在 Base 模型对比（Table 2；Table 3）中将 Olmo 3 32B 与 Apertus 70B（15T tokens）、Marin 32B（12.7T tokens）相比，但 Olmo 3 32B 只训练了 5.5T+100B≈5.6T tokens，计算量约为对手的 40%–44%。论文对此透明地列出了各模型的 token 数（Table 13；§3.4），但主表格中未在标题行注明这一差异，读者需要自行对比 Table 13 才能理解这一不对等性。后训练对比（Table 1；§4.1）中，Qwen 3 32B 是一个强竞争对手但其训练数据完全不公开，无法核实基础训练质量；LLM360 K2-V2 是 70B 模型与 32B 的 Olmo 3 对比，存在规模不匹配（Table 14；Table 25）。这些非对等比较在论文中均有文字说明（§3.3），但集中在主表格时容易被忽视。

**维度三：未报告的负面结果（§4.4.3；§6.2）**

论文在 §4.4.3 提到 RL 训练过程出现了"至少 1 天的不稳定性（instability）"，但未详细分析导致不稳定的原因和解决方案（Table 49）。PopQA 指标在后训练后明显退化（OLMo 3.1 Think 32B 仅 30.9，低于 OLMo 2 32B Instruct 的 37.2，Table 1），这一知识回忆能力的"遗忘"问题在论文中虽然出现在表格中但未作专项分析（Table 14；Table 25）。GPQA（57.5%）显著低于 Qwen 3 32B（67.3%）和 DS-R1 32B（61.8%，Table 1），论文未对此差距给出专项解释。RL-Zero（从 Base 直接做 RL）实验仅在 7B 规模进行（§6.1；§6.2），未扩展到 32B，推测是 32B RL-Zero 成本过高（Table 49），但论文未说明为何不做 32B RL-Zero 对比。
#### 机制迁移分析 (Mechanism Transfer Analysis)

##### 机制解耦表格

以下五个计算原语从 OLMo 3 的核心设计决策（DESIGN_DECISIONS）中提炼，每列剥离领域术语，以通用计算/信息论语言重述。

| 原语名称 | 本文用途 | 抽象描述 | 信息论直觉 |
|---|---|---|---|
| **多阶段课程数据混合（Multi-Stage Curriculum Data Mixing）** | 在预训练（§3.4）→中间训练（§3.5）→长上下文扩展（§3.6）三阶段分别使用不同的领域比例（如中间训练阶段合成数学/代码/思考链数据占 ~34%，通用网页占 ~22%，Table 5），通过迭代质量反馈循环调整配比（5轮积分测试，Table 6；Table 7；Table 8；Table 9） | 在参数固定的优化过程中，对输入分布进行动态非均匀采样；每轮用中间检查点评分来重新权衡各子分布的采样概率，使模型接收到的有效信息密度最大化 | 课程混合等价于在各子任务分布上做重要性采样：在欠学习的子空间（数学、代码）增加采样密度（Table 41；Table 42），等价于向低熵区域注入更多信息；质量感知上采样（top-5% 重复拷贝，Table 38；Table 39；Table 40）进一步压缩输入分布的条件熵 |
| **模型权重平均/权重汤（Model Souping / Checkpoint Averaging）** | 对 32B 独立随机种子的两次中间训练结果做线性权重平均（模型汤，§3.5.4），以及在长上下文阶段对最后3个检查点（step 10K/11K/11921）做时序权重平均（§3.6.4）；前者带来 MCSTEM +1 点、数学 +2.9 点的提升（Table 13） | 在参数空间中对多个局部极小值做凸组合；利用不同训练轨迹在损失曲面上探索到的不同低损失盆地，在不增加推理成本的前提下扩大有效模型集成范围 | 权重平均等价于对多个后验分布做混合（mixture of posteriors）；若两个独立随机种子的轨迹收敛到损失曲面上线性连通的低损失区域（"loss valley"），权重平均能维持低交叉熵同时减少每个单一解的方差 |
| **非对称策略梯度裁剪（Asymmetric Policy Gradient Clipping）** | 在 OlmoRL（改进版 GRPO，§4.4；§4.4.1）中采用 ε_low=0.2，ε_high=0.272 的非对称裁剪区间（Table 49），允许高奖励 token 获得更大幅度的策略更新，同时限制低奖励 token 的负向更新幅度 | 对概率比率 r_{i,t} 施加非对称截断：正向偏移上界（1+ε_high）宽于负向偏移下界（1-ε_low），从而在策略改进步长上实现不对称的信任域约束 | 在 KL 散度约束视角下，非对称裁剪等价于对策略分布偏移的方向相关惩罚：向高奖励区域的移动被允许更大步长，降低了探索高价值动作的信息代价；向低奖励区域的反向移动被更严格限制，防止策略熵的灾难性降低 |
| **难度感知样本过滤（Difficulty-Aware Sample Filtering）** | 在 RL 训练前，移除在 8 次采样中正确率超过 62.5%（即超过 5/8 次）的提示词（"离线难度过滤"，§4.4.2；Table 20；Table 50）；同时在 OlmoRL 中实现"主动采样"机制，跳过全对/全错的批次以避免零梯度（Table 49） | 在线/离线地识别并丢弃优化曲面上梯度信号接近零的样本（过于简单导致奖励方差为零），将有效计算集中在信息增益最大的边界区域（margin region） | 过于简单（reward=1）或过于困难（reward=0）的样本在 GRPO 的组相对优势计算中均产生零方差，贡献的 KL 缩减量趋近于零；移除这类样本等价于提升数据集的有效信息密度（每单位计算量的互信息收益） |
| **连续批处理与飞行中权重更新（Continuous Batching + In-Flight Weight Updates）** | 在 RL 推理-训练流水线中抛弃静态批处理，改用 vLLM 连续批处理（§4.4；§4.4.3）；并实现"飞行中更新"：训练器完成一个小批次的梯度更新后立即将新权重推送到仍在运行的 vLLM Actor，无需等待整个 rollout batch 完成；实测吞吐从 881 tokens/sec 提升至 2949 tokens/sec（3.4x，Table 23） | 将生产者-消费者流水线中的同步屏障（synchronization barrier）替换为异步流式更新：下游消费者（推理引擎）持续处理变长序列，上游生产者（训练器）以微批次粒度异步刷新共享状态 | 静态批处理要求所有序列填充至最大长度，导致高达 54% 的有效计算量被浪费（padding tokens 不携带信息）；连续批处理消除了这一信息稀释，使实际处理的 token 密度趋近于序列长度的真实分布；飞行中更新进一步压缩了策略滞后（policy lag），降低了重要性采样比率的方差（Table 49；§4.4.3） |

##### 迁移处方

###### 原语 1：多阶段课程数据混合 → 推荐系统的多源特征配比动态优化

**目标领域+具体问题：** 工业级推荐系统训练中，用户行为日志（点击流）、商品知识图谱嵌入、社交关系链接、商家结构化描述等多个异构数据源的权重配比通常由人工经验固定，无法随模型训练阶段自适应调整，导致不同能力（精排、召回、时序推理）的训练信号不均衡。

**怎么接：** 将现有数据加载 pipeline 中的静态采样权重层替换为迭代质量反馈模块：每训练 N 个 step 后，在一组代理任务（如点击率预测验证集、序列推荐 NDCG、冷启动命中率）上评分，按照类似 OLMo 3 的"积分测试轮次"机制更新各数据源的采样概率；质量感知上采样则对应"高价值样本"（如转化用户行为）的重复拷贝。输入为各数据源原始 batch，输出为重新加权的混合 batch。

**预期收益：** 参考 OLMo 3 中间训练 5 轮迭代将 Math 子项从 47.4 提升至 57.1（+9.7 点），以及引入思考链/指令数据后数学项 +5.6 点的增益，预期在冷启动或数据稀缺子域（低频类目）上的覆盖率可获得显著提升，而不以牺牲高频域精度为代价。

**风险/不适用条件：** 若代理评估任务和真实业务指标之间存在显著分布偏移（如线上 A/B 与离线验证集不一致），迭代混合可能强化噪声信号；若各数据源的时效性差异极大（实时行为流 vs. 静态知识图谱），动态配比会造成训练不稳定；小规模（数据总量 <10B tokens 等价）场景中迭代收益可能不显著。

###### 原语 2：模型权重平均/权重汤 → 多任务医学影像分割模型集成

**目标领域+具体问题：** 医学影像分割中，针对 CT/MRI/PET 等不同模态分别微调的模型往往各有专长，直接集成（ensemble）推理成本高昂，但单模态微调模型在跨模态泛化上表现不稳定。目标是以零推理开销获得跨模态鲁棒的分割模型。

**怎么接：** 替换现有的多模型投票 ensemble 组件：在相同基础预训练模型（如 SAM-Med3D 或 nnU-Net 骨干）上，用不同随机种子或不同模态数据顺序分别完成微调，得到 2-4 个参数配置不同的检查点；然后直接做线性权重平均（或 SLERP 球面插值）合并为单一权重文件，替换下游 inference 服务中的模型加载节点。

**预期收益：** OLMo 3 的模型汤在 MCSTEM 上带来 +1 点、数学 +2.9/1.6 点的提升（Section §3.5.4），且推理成本与单模型相同。在医学分割场景中，参考 model soup 文献（Wortsman et al. 2022），预期在少见病变类型（低频分布尾部）的 Dice 系数可提升 1-3%，同时不引入额外延迟。

**风险/不适用条件：** 权重平均的有效性依赖于多个检查点收敛到损失曲面上线性连通的低损失区域；若不同模态的微调导致权重在参数空间中发生大幅偏移（如 barrier 区域），平均后会出现性能骤降；对于任务差异极大的多任务场景（如同时分割肿瘤和骨骼），需先验证权重连通性（如通过线性插值损失曲线）再部署。

###### 原语 3：非对称策略梯度裁剪 → 金融风控强化学习中的异步奖励优化

**目标领域+具体问题：** 信用风险评估中，强化学习 agent（如 PPO 训练的贷款审批 agent）面临奖励高度不对称的场景：正确批准优质借款人带来的收益（利差收入）远小于错误批准高风险借款人带来的损失（违约损失）；传统对称裁剪（ε=0.2 双向）导致正向策略更新被抑制，模型保守性过高。

**怎么接：** 在现有 PPO/GRPO 训练框架的 ratio clipping 模块中，将 `clip(r, 1-ε, 1+ε)` 替换为 `clip(r, 1-ε_low, 1+ε_high)`，其中 ε_high 设为 ε_low × 1.36（参照 OLMo 3 的 0.272/0.2 比值）；对高奖励动作（如准确识别优质借款人）允许更大步长更新，对低奖励动作维持保守更新。与现有奖励 shaping 模块串联，无需改动数据 pipeline。

**预期收益：** OLMo 3 中非对称裁剪配合 DPO warm-start 使 AIME 2025 从 57.6（SFT）提升至 78.1（最终），其中 DPO+RLVR 组合比单独 SFT+RLVR 高出 +2.2 平均分（Table 22）。金融场景中预期正向决策准确率（召回率）可提升而不显著增加误批率，尤其在正样本稀缺的冷启动阶段。

**风险/不适用条件：** 若奖励信号存在噪声（如违约标签延迟 6-18 个月才可观测），非对称裁剪可能放大噪声方向的更新；监管合规要求模型决策可审计时，ε_high 过大会导致策略漂移超出可解释范围；需确保 KL 惩罚或其他正则项（OLMo 3 选择移除 KL loss，但金融场景建议保留）防止过度偏离参考策略。

###### 原语 4：难度感知样本过滤 → 代码自动补全模型的 RL 训练效率优化

**目标领域+具体问题：** 基于 RLVR 训练代码补全模型（如 pass@1 奖励驱动）时，训练集中大量简单题目（单行补全、常见 API 调用）在 8 次采样中几乎 100% 正确，提供零梯度信号；而极端困难题目（复杂算法、跨文件依赖）全部失败，同样无梯度。这两类样本消耗约 40-60% 的 GPU rollout 时间。

**怎么接：** 在现有 RL rollout 数据生成阶段（生成 candidate responses 后、计算 loss 前）插入难度过滤节点：对每个提示词生成 K=8 次独立回答，计算 pass rate；移除 pass rate > θ_high（如 0.625，对应 5/8 通过）和 pass rate = 0（全部失败）的提示词；剩余的"边界区"提示词进入实际训练批次。该过滤节点可作为独立预处理步骤，替换现有数据加载器的 sampler 组件。

**预期收益：** OLMo 3 的离线难度过滤（>62.5% 通过率截断）配合 inflight updates 使 RL 总吞吐从 881 提升至 2949 tokens/sec（3.4x，Table 23）。代码补全场景中，按 OLMo 3 的估算，静态批处理下高达 54% 的计算量浪费于无效 padding，难度过滤后有效 token 密度可提升 1.5-2x，等价地在相同 GPU 预算内完成更多有效训练步骤。

**风险/不适用条件：** 难度过滤依赖 pass rate 估计需要 K 次采样（K=8），本身引入 K 倍推理开销；若训练数据集规模小（<50K 题），过滤后的有效数据量可能不足以覆盖全部任务分布；动态难度（模型变强后之前的"难题"变简单）要求定期重新评估过滤阈值，否则样本分布会随训练进展发生漂移。

###### 原语 5：连续批处理与飞行中权重更新 → 搜索排序模型的在线学习流水线加速

**目标领域+具体问题：** 在线搜索排序系统中，RLHF/RLAIF 训练需要推理引擎（生成候选排序列表）和训练器（根据用户反馈更新权重）异步协作；传统实现中训练器每完成一个 epoch 才同步权重到推理引擎，导致推理引擎在训练器执行期间使用陈旧策略（policy lag），且请求长度高度可变（简单查询 vs. 复杂多轮对话）导致静态批处理利用率低至 30-40%。

**怎么接：** 将现有 serving + training 集群的同步屏障替换为异步权重流（async weight stream）：参照 OLMo 3 的 OlmoRL 架构，将 vLLM 连续批处理引入推理侧（替换当前 static-batching serving 组件），训练侧完成每个 micro-batch（64-128 个提示词）的梯度更新后立即通过 RDMA 或 gRPC 将 delta 权重推送到推理集群，推理集群在下一个请求批次边界做权重替换；最大异步度（max asynchrony）参数控制推理引擎可以落后训练器的最大步数（OLMo 3 使用 max asynchrony=8）。

**预期收益：** OLMo 3 连续批处理 + 飞行中更新组合将 RL 吞吐提升 3.4x（881→2949 tokens/sec），并将计算利用率（MBU）从 12.9% 提升至 43.2%（Table 23）。搜索场景中，可变长度请求（平均 500-2000 token 输出）与 OLMo 3 的变长生成（平均 14,628 token，最大 32K）结构相似，预期填充浪费可从 40-54% 降至 10-15%，等价于在相同 GPU 成本下支撑约 2-3x 的请求吞吐量。

**风险/不适用条件：** 飞行中更新引入的异步度（asynchrony）会导致推理引擎和训练器使用不同版本的策略，当 max asynchrony 过大时重要性采样比率（IS ratio）偏差加剧，可能导致训练不稳定；需要 vLLM 或等效框架支持运行时权重热更新（不中断正在处理的请求）；若基础设施不支持高带宽互联（如跨数据中心部署），权重推送延迟会成为新瓶颈。

##### 机制家族图谱

###### 前身（Ancestors）

以下 ≥4 个方法构成 OLMo 3 的主要技术继承链，素材来源于 RELATED_WORK 表：

1. **OLMo 2**（OLMo et al., 2024）
   - 继承关系：OLMo 3 是 OLMo 2 的直接后继，沿用了完全相同的解码器专用 Transformer 架构、词表和分词器，以及完全开放的数据/代码/检查点发布模式。
   - 本文改进：OLMo 3 在 OLMo 2 基础上新增了长上下文扩展阶段（65K token，YaRN+Longmino Mix）、全新的 OlmoRL 强化学习基础设施（从 881 到 2949 tokens/sec 的 3.4x 加速）、以及将 RLVR 扩展到数学以外的代码、IF、通用推理等领域，并引入思考模型（Think）和标准指令模型（Instruct）两条独立后训练路径。

2. **GRPO**（Shao et al., 2024）
   - 继承关系：OlmoRL 的核心 RL 目标函数直接继承自 GRPO（Group Relative Policy Optimization），沿用组相对优势估计（group-relative advantage，公式中 A_{i,t} = r − mean(r)）替代传统价值函数估计。
   - 本文改进：OlmoRL 在 GRPO 基础上叠加了四项改动：（1）移除 KL loss 惩罚项；（2）移除标准差归一化（采用 Dr GRPO 方案）；（3）引入非对称裁剪（ε_high=0.272 > ε_low=0.2，来自 DAPO）；（4）引入连续批处理+飞行中更新的高效基础设施，使实际可用训练 token 量提升 3.4x。

3. **DAPO**（Yu et al., 2025）
   - 继承关系：OlmoRL 直接采纳了 DAPO 的三项核心改进：clip-higher 非对称裁剪、token 级损失归一化、以及零梯度样本过滤（对应 OlmoRL 的"主动采样"机制）。
   - 本文改进：OlmoRL 在 DAPO 基础上进一步引入了截断重要性采样（TIS，ρ cap），用于控制飞行中更新引入的异步度所造成的 IS 比率偏差；同时将 DAPO 的在线过滤扩展为离线预过滤（难度过滤阈值 62.5%）与在线主动采样的组合，兼顾效率和分布覆盖。

4. **Dr GRPO**（Liu et al., 2025b）
   - 继承关系：OlmoRL 采纳了 Dr GRPO 的核心洞察：去除 GRPO 中按组标准差归一化优势估计的步骤，以消除难度偏差（易题的组内方差小，归一化后信号被放大；难题方差大，归一化后信号被压缩）。
   - 本文改进：OLMo 3 将 Dr GRPO 的无标准差归一化与 DAPO 的非对称裁剪、TIS 和 OlmoRL 的高效推理基础设施系统性地组合在一起，在单一 RL 框架中同时解决难度偏差、策略更新不对称、以及大规模训练效率三个正交问题。

5. **Tülu 3 / SPPO**（Lambert et al., 2024）
   - 继承关系：OLMo 3 的后训练 pipeline（SFT→DPO→RL）在结构上沿用了 Tülu 3 的三阶段框架，并直接使用 Tülu 3 SFT 数据作为中间训练数据源之一（Dolmino Mix 中占 1.1%）；去污染流程也继承了 Tülu 3 的 8-gram 匹配方法。
   - 本文改进：OLMo 3 用 Delta Learning（Geng et al., 2025）替换了 Tülu 3 的 UltraFeedback 风格偏好对构建方式，改为从大模型（chosen）与小模型（rejected）之间提取对比信号；同时新增了 Think SFT 作为 Instruct SFT 的热启动（warm-start），带来 +3.3 平均分的提升。

###### 兄弟（Siblings）

以下为与 OLMo 3 同期的主要竞争/参照工作，数字来源于 MAIN_RESULTS 中的对比表格：

1. **DeepSeek R1 32B**（Guo et al., 2025）
   - 数字对比（Table 14，Think 模型对比）：AIME 2025：OLMo 3.1 32B Think 78.1 vs. DS-R1 32B 56.3（+21.8）；MATH：96.2 vs. 92.6（+3.6）；但 GPQA：OLMo 57.5 vs. DS-R1 61.8（-4.3）；LiveCodeBench v3：83.3 vs. 79.5（+3.8）。
   - 核心差异：DeepSeek R1 使用闭源预训练数据；OLMo 3 完全开放数据、代码、检查点；OLMo 3 的 OlmoRL 基础设施在推理侧通过连续批处理实现 3.4x 吞吐提升，而 DS-R1 的具体 RL 基础设施未披露。

2. **Qwen 3 32B**（Yang et al., 2025a）
   - 数字对比（Table 14）：AIME 2025：OLMo 78.1 vs. Qwen 3 70.9（+7.2）；OMEGA：53.4 vs. 47.7（+5.7）；但 ZebraLogic：80.1 vs. 88.3（-8.2）；GPQA：57.5 vs. 67.3（-9.8）；LiveCodeBench v3：83.3 vs. 90.2（-6.9）；BBH：88.6 vs. 90.6（-2.0）。
   - 核心差异：Qwen 3 基于闭源数据训练，训练 token 数约为 OLMo 3 的 6 倍；OLMo 3 在 AIME/OMEGA 等最难数学推理任务上超越 Qwen 3，但在知识密集型推理（GPQA）和代码竞赛（LCB）上仍有差距；Qwen 3 不释放预训练基础模型。

3. **Stanford Marin 32B**（Hall et al., 2025）
   - 数字对比（Table 2，基础模型对比）：OlmoBaseEval Math：OLMo 3 61.9 vs. Marin 49.3（+12.6）；Code：39.7 vs. 30.8（+8.9）；MC STEM：74.5 vs. 75.9（-1.4）；GenQA：79.8 vs. 80.3（-0.5）。
   - 核心差异：两者均为完全开放模型；OLMo 3 在数学、代码上显著领先 Marin（均 +8-12 点），但 Marin 在通识问答上略有优势；OLMo 3 拥有长上下文扩展阶段（RULER 96.10 vs. Marin 未报告），是当时同规模完全开放模型中的最高水平。

4. **SmolLM3**（Bakouch et al., 2025）
   - 数字对比：SmolLM3 停止在 SFT+DPO 阶段，未做 RL；OLMo 3 Think 7B 在 AIME 2024 上获得 71.6（SFT 阶段仅 69.6→DPO 74.6→最终 71.6，Table 15）；SmolLM3 未在同等 benchmark 上公开数字，但 RL 阶段对 OLMo 3 的 ZebraLogic 提升从 60.6（DPO）到 66.5（最终），IFBench 从 28.3 到 41.6。
   - 核心差异：SmolLM3 展示了 SFT+DPO 可获得的性能上界；OLMo 3 进一步通过 RL 突破该上界，证明了 RL 阶段在完全开放模型上的有效性。

###### 后代 (Descendants) — 基于引用分析

> 截至 2026-04-02，本文共被引用 **0** 次（数据来源：OpenAlex）

暂无高影响力引用论文。
#### 背景知识补充 (Background Context)

| 外部技术 | 一句话定义 | 在本文中的角色 | 核心引用 |
|---|---|---|---|
| **GRPO（Group Relative Policy Optimization）** | 一种无需价值函数的策略梯度算法，通过对同一提示词的多个采样输出计算组内相对奖励作为优势估计，替代 PPO 中的 critic 网络 | OlmoRL 的基础 RL 目标函数，OLMo 3 在此基础上叠加非对称裁剪、无 KL loss、无标准差归一化等改动 | Shao et al. (2024) |
| **DAPO（Decoupled Clip and Dynamic Sampling Policy Optimization）** | 对 GRPO 的三项改进：clip-higher 非对称裁剪（ε_high > ε_low）、token 级损失归一化、以及零梯度样本（全对/全错）的动态过滤 | OlmoRL 直接采纳了全部三项改进，并额外引入截断重要性采样（TIS）处理飞行中更新的 policy lag | Yu et al. (2025) |
| **Dr GRPO** | 对 GRPO 的改进，移除按组标准差归一化优势的步骤，消除不同难度题目因方差差异导致的梯度放大/压缩偏差 | OlmoRL 采纳无标准差归一化，公式中优势仅为 r − mean(r) 而非 (r − mean(r)) / std(r) | Liu et al. (2025b) |
| **DPO（Direct Preference Optimization）** | 将 RLHF 的奖励最大化问题化为针对偏好对（chosen/rejected）的监督学习，利用 KL 正则化的闭合解避免显式 reward model 训练 | OLMo 3 后训练 pipeline 的第二阶段（SFT→DPO→RL），使用长度归一化的 DPO（β=5）；DPO 检查点作为 RL 的热启动，比纯 SFT 启动高 +2.2 平均分 | Rafailov et al. (2023)（隐含）；本文 Section §4.3 |
| **YaRN（Yet Another RoPE Extensiooon Method）** | 对 RoPE（旋转位置编码）进行非均匀频率插值，以扩展预训练上下文长度而不大幅损失短上下文性能 | OLMo 3 长上下文扩展阶段（65K token）的位置编码扩展方法，创新性地仅应用于全注意力层（而非滑动窗口层），获得最优 RULER 性能 | Peng et al. (2023) |
| **RoPE（Rotary Position Embedding）** | 通过将位置信息编码为查询-键向量对的旋转变换，实现相对位置的隐式建模且支持序列长度外推 | OLMo 3 基础架构的位置编码方案，RoPE θ=5×10^5，配合 YaRN 实现长上下文扩展 | Su et al. (2021)（隐含）；Table 33 |
| **SwiGLU** | 将 Swish 激活函数与门控线性单元（GLU）结合的 FFN 激活方案，在参数量相同的条件下比 ReLU 提供更高的表达能力 | OLMo 3 模型架构的 FFN 激活函数（Table 33），延续自 OLMo 2 | Shazeer (2020)（隐含）；Table 33 |
| **RMSNorm（Root Mean Square Layer Normalization）** | 去掉均值中心化步骤、仅保留均方根缩放的层归一化变体，计算量更低 | OLMo 3 所有层的归一化方案；配合 QK-Norm（对 Query/Key 分别做 RMSNorm）以增强训练稳定性 | Zhang & Sennrich (2019)（隐含）；Table 33 |
| **vLLM（Variable-Length Large Language Model Inference）** | 基于 PagedAttention 的高效 LLM 推理框架，支持连续批处理（continuous batching）以提升变长序列的 GPU 利用率 | OlmoRL 的推理引擎（rollout actor），实现连续批处理和飞行中权重更新（inflight updates），将 RL 吞吐从 881 提升至 2949 tokens/sec | Kwon et al. (2023)（隐含）；Table 23 |
| **olmOCR** | 专为科学 PDF 设计的 OCR + 文档结构化工具，将 PDF 转换为适合 LLM 训练的线性化纯文本，保留公式、表格等科学内容 | OLMo 3 预训练数据（Dolma 3）中科学 PDF 子集的生成工具，贡献 805B tokens（占预训练总量 13.6%）；替代了 OLMo 2 使用的 peS2o | Poznanski et al. (2025a/b) |
| **MinHash Deduplication** | 基于局部敏感哈希（LSH）的近似集合相似度估计算法，用于大规模文本语料的近似重复数据删除 | Dolma 3 数据处理 pipeline 中的去重步骤（继承自 DCLM pipeline），确保训练数据多样性 | 参见 DCLM：Li et al. (2024a) |
| **FastText 质量分类器** | Facebook 开源的轻量级文本分类器，常用于网页内容质量判断 | DCLM pipeline 中的核心质量过滤组件，OLMo 3 在此基础上引入质量感知上采样曲线（top-5% 重复拷贝），代替 DCLM 的平坦四分位过滤 | Li et al. (2024a)；Section §3.4.4 |
| **Delta Learning** | 一种偏好对构建范式，直接从能力差异大的模型对（大模型 chosen，小模型 rejected）中提取偏好信号，而非依赖 LLM judge 评分 | OLMo 3 DPO 阶段的偏好对来源，替代 UltraFeedback 风格的 judge-pair 方式；发现 SFT on chosen responses 有损于性能，对比信号更有价值 | Geng et al. (2025) |
| **滑动窗口注意力（Sliding Window Attention，SWA）** | 将注意力计算限制在固定窗口（如 4096 token）内的局部注意力机制，显著降低长序列的计算/内存开销 | OLMo 3 架构中 3/4 的注意力层使用 SWA（window=4096），仅最后 1/4 层使用全注意力；配合 YaRN（仅应用于全注意力层）实现长上下文扩展 | Beltagy et al. (2020)（隐含）；Table 33 |
