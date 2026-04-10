---
arxiv_id: '2512.13961'
baselines:
- Stanford Marin 32B（全开源，OlmoBaseEval Math 49.3）
- Qwen 3 32B（开放权重，AIME 2024 86.3，训练 token 约 6× 更多）
- DeepSeek R1 32B（开放权重，闭源数据）
- OLMo 2 32B（前代全开源，RL infra 881 tok/s）
category: llm/pretraining
date: '2025-12-15'
failed_gates: []
key_numbers:
- baseline: Qwen 3 32B
  baseline_value: 86.3%
  metric: AIME 2024 (Think 32B)
  value: 80.6%
- baseline: DeepSeek R1 32B
  baseline_value: ~90%
  metric: MATH 500 (Think 32B)
  value: 96.2%
- baseline: Marin 32B
  baseline_value: '49.3'
  metric: OlmoBaseEval Math (Base 32B)
  value: '61.9'
- baseline: OLMo 2 RL baseline
  baseline_value: 881 tok/s
  metric: RL Throughput (OlmoRL)
  value: 2949 tok/s
key_tradeoffs:
- chosen_over: 全层全注意力
  decision: SWA 覆盖 3/4 层 + 末层全注意力
  reason: 显著节省显存，RULER 分数损失可控
- chosen_over: 所有层统一 YaRN
  decision: YaRN 仅施加于全注意力层
  reason: 获得最优 RULER 长上下文分数（Figure 13a）
- chosen_over: 从 base 启动
  decision: Instruct SFT 从 Think SFT checkpoint 启动
  reason: +3.3pp avg，且不增加输出冗余
- chosen_over: 标准 GRPO
  decision: OlmoRL 去除 KL 项 + 去除方差归一化
  reason: 消除难题偏置，允许更大策略更新步长
mechanisms:
- ancestor: DAPO / GRPO
  name: OlmoRL（异步 RL + 飞行权重更新）
  scope: Think RL 阶段
- ancestor: DPO + Delta Learning (Geng 2025)
  name: Delta Learning DPO
  scope: Think DPO 阶段
- ancestor: Domain-weighted mixing
  name: Conditional Mixing（虚拟域冻结）
  scope: 预训练数据混合
- ancestor: GRPO zero-gradient filtering
  name: Active Sampling（非零优势采样）
  scope: RL-Zero / Think RL
pipeline_version: 1
quality: full
tags:
- fully-open-llm
- pretraining
- midtraining
- long-context
- reinforcement-learning-from-verifiable-rewards
- delta-learning
- model-souping
- staged-post-training
- olmocr
- thinking-model
title: OLMo 3
tldr: OLMo 3 Think 32B 在 AIME 2024 上达到 80.6%、MATH 500 上达到 96.2%，以约 6 倍更少的训练 token
  追平 Qwen 3 32B，同时保持数据与权重全部开源。
url: https://arxiv.org/abs/2512.13961
---

#### 核心速览

**TL;DR:** OLMo 3 通过分阶段中训（100B token 数学/代码/推理合成数据）+ Delta Learning DPO + 异步飞行权重 RL，在全开源框架下使 32B Think 模型 AIME 2024 达到 80.6%、MATH 500 达到 96.2%，RL 训练吞吐相比前代提升 3.3×。

**核心机制一句话:** 用飞行权重异步更新（OlmoRL）重写 RL 训练基础设施，以 Delta Learning DPO 初始化策略，同时将推理 traces 注入中训数据，从而在全开源约束下以 6 倍更少 token 逼近闭源 SOTA。

**关键数字表**

| 指标 | 数值 | 基线 | 基线值 | 增益 |
|------|------|------|--------|------|
| AIME 2024 (Think 32B) | 80.6% | Qwen 3 32B | 86.3% | −5.7pp（6× 更少 token） |
| MATH 500 (Think 32B) | 96.2% | OLMo 3.0 Think | 92.4% | +3.8pp（Extended RL） |
| OlmoBaseEval Math (Base 32B) | 61.9 | Marin 32B | 49.3 | +12.6pp |
| 7B Math（中训后） | 59.8 | 中训前 | 23.5 | +36.3pp（100B token） |
| RL 吞吐 (OlmoRL) | 2949 tok/s | OLMo 2 baseline | 881 tok/s | +235% |
| AIME 2025 Extended RL | 78.1% | 3.0 Think | 72.5% | +5.6pp |
| Instruct AIME 2025 | 57.9 | Qwen 3 32B No-Think | 21.3 | +36.6pp |



#### 第一性原理分析

##### 痛点 (The Gap)

在 OLMo 3 之前，"完全开放"（fully open）的大模型存在三重结构性困境：其一，以 Stanford Marin 32B 为代表的开源模型在数学（49.3）和代码（30.8）上远落后于闭源模型，根本原因是预训练数据质量与混合策略粗糙——平铺过滤而非质量感知上采样；其二，以 DeepSeek R1、Qwen 3 32B 为代表的"开放权重"模型虽能力强，但训练数据、中间检查点、代码均不公开，无法复现；其三，开源社区的 RL 训练基础设施吞吐极低（OLMo 2 基线仅 881 tok/s），致使强化学习实验成本高昂、迭代缓慢。OLMo 3 要在"完全开放"约束下同时突破数据质量天花板与 RL 算法效率瓶颈。

##### 因果链

[C1] Because 平铺过滤会对所有质量分段一视同仁，高质量样本复现频次不足 → Therefore 引入质量感知上采样（最高 7× 上采样、底部 40% 过滤），使有限计算预算优先消化高价值 token，32B 数学分 OlmoBaseEval +12.6pp vs Marin。
— 如同图书馆选书：宁可把经典读七遍，也不把劣质书塞满书架。

[C2] Because 推理模型需要"知道如何思考"才能从 RL 中获益，而从随机初始化直接做 RL 会面临冷启动稀疏奖励 → Therefore 如 Figure 2 所示，管道设计为 Think SFT（温启动）→ Delta Learning DPO（用 Qwen3-32B chosen vs Qwen3-0.6B rejected 最大化质量差）→ RL，DPO+RL 比 SFT+RL 在 7B 上平均再高 +2.2pp。
— Figure 2 的模型流图清晰展示了"先给模型装推理范式，再用 RL 放大优势"的级联逻辑。

[C3] Because 连续批处理（continuous batching）下训练节点必须等待推理节点生成完整 rollout 再更新权重，GPU 利用率受制于 IO 等待 → Therefore OlmoRL 引入 inflight weight updates（训练与推理异步并行，IS 比率 π_old/π_vllm 修正分布漂移），吞吐从 881 tok/s 提升至 2949 tok/s（+235%），使 Figure 1 中从数据到检查点的全流水线在合理成本内闭合。
— Figure 1 展示的正是这条从 Dolma 3 数据、训练代码到中间检查点的完整开放链路，inflight 更新是其中计算效率的关键节点。




#### 技术精要

##### 方法流程

预训练数据(Dolma 3, 5.93T) → 标准预训练(7B/32B, SWA架构) → 中间训练(Dolmino Mix, 100B, 数学/代码/推理合成) → 长上下文扩展(YaRN, 50-100B tokens) → Think SFT(2.27M样本) → Delta Learning DPO(200K, Qwen3-32B chosen/Qwen3-0.6B rejected) → OlmoRL(GRPO变体, inflight权重更新) → Instruct SFT(从Think SFT checkpoint热启动, 2.15M样本) → Olmo 3.1 Think/Instruct 32B

> Figure 2 展示了从Think SFT热启动到最终模型的完整模型流; Figure 1 展示了训练数据、代码与中间checkpoint的全局流程。

##### 核心公式与符号

OlmoRL目标函数（基于DAPO改进，去除KL项与标准差归一化）：

$$J(\theta) = \frac{1}{\sum|y_i|} \sum_i \sum_t \min\!\left(\frac{\pi_\theta}{\pi_\text{vllm}}, \rho\right) \cdot \min\!\left(r_{i,t} A_{i,t},\ \text{clip}(r_{i,t}, 1{-}\varepsilon_\text{low}, 1{+}\varepsilon_\text{high}) A_{i,t}\right)$$

优势估计（无标准差归一化）：

$$A_{i,t} = r(x, y_i) - \text{mean}\!\left(\{r(x, y_i)\}_{i=1}^G\right)$$

| 符号 | 含义 | 关键值 |
|------|------|--------|
| $r_{i,t}$ | token级重要性采样比 $\pi_\theta / \pi_{\theta_\text{old}}$ | 逐token计算 |
| $\rho$ | IS截断上限 | 裁剪大比值以降低方差 |
| $\varepsilon_\text{low}, \varepsilon_\text{high}$ | 非对称clip边界 | $\varepsilon_\text{high} > \varepsilon_\text{low}$，允许更大的向上更新 |
| $A_{i,t}$ | 优势估计（无std归一化） | 去除难度偏差 |
| $G$ | 每prompt采样组大小 | RL rollout group size |

##### 设计决策

| 决策 | 备选方案 | 选择理由 | 证据来源 |
|------|---------|---------|---------|
| SWA覆盖前3/4层(window=4096) + 末层全注意力 | 全层全注意力 | 显著降低KV缓存内存 | Section 3.2, p.7 |
| YaRN仅应用于全注意力层做长上下文扩展 | 全层YaRN | RULER得分最优 | Figure 13a, p.34 |
| LC训练34%长上下文+66%短上下文混合 | ≥50%长上下文比例 | 反转比例导致OlmoBaseEval下降2.5pp vs 0.8pp | Section 3.6.3, p.35 |
| Delta Learning DPO: chosen=Qwen3-32B, rejected=Qwen3-0.6B | 直接SFT Qwen3-32B输出 | 直接SFT平均下降−5.8pp；DPO方案+2.6pp | Table 21, p.48 |
| Instruct SFT从Think SFT checkpoint热启动 | 从base checkpoint开始 | 平均+3.3pp，无冗余verbosity | Table 29, p.59 |

##### 消融排序

| 排名 | 组件 | 增益 | 数据来源 |
|------|------|------|---------|
| 1 | OlmoRL inflight权重更新 | +117% 吞吐量(2949 vs 881 tok/s基线) | Table 23, p.47 |
| 2 | Delta Learning DPO先于RL | DPO+RL全面优于SFT+RL; 7B平均+2.2pp | Table 22, p.53 |
| 3 | 中间训练含指令/思维链数据 | 基础评测平均+1.9pp vs 无此混合 | Table 10, p.22 |
| 4 | 模型Soup（32B合并2个中间训练seed） | Math+2.9pp, MCSTEM+1pp, GenQA+0.4pp | Section 3.5.4, p.30 |
| 5 | Delta Learning+GPT偏好联合 | Instruct平均+8.5pp vs SFT基线 | Table 32, p.61 |
| 6 | 扩展RL(3.0→3.1, 750→2300步) | AIME 2024+3.8pp, AIME 2025+5.6pp, IFBench+20.5pp | Table 14, p.50 |

消融证据充分，7B/32B均有独立实验验证，可信度高。Delta Learning与GPT偏好的互补增益（各+5.7/+5.5，联合+8.5）表明两者覆盖不同错误模式。

##### 易混淆点

- ❌ 错误理解：OlmoRL与GRPO相同，只是套用了DAPO的zero-gradient过滤
- ✅ 正确理解：OlmoRL在DAPO基础上额外去除KL项和std归一化，并引入inflight权重更新（online policy覆盖旧policy）与主动采样（>90%非零优势batch），是系统级工程+算法的联合改进

- ❌ 错误理解：中间训练加入指令/思维链数据会污染base模型，导致评测失真
- ✅ 正确理解：关键是**省略特殊token**（如`<|im_start|>`）；若保留特殊token，base模型推理时会自动emit导致GSM8K→0；去除特殊token后指令数据合法提升base eval +1.9pp

- ❌ 错误理解：长上下文训练比例越高越好，更多长文档等于更强的LC能力
- ✅ 正确理解：LC比例超过50%会损害短上下文质量（OlmoBaseEval −2.5pp），34%LC是经实验确定的帕累托最优点

##### 隐性成本

| 成本项 | 量化数据 | 对决策的影响 |
|-------|---------|-------------|
| 全流程训练墙钟时间 | ~56天 / 1024块H100（含扩展RL+21天/224 GPU） | 决定了迭代速度；单次RL sweep已占总时间16% |
| 估算总费用 | ~$275万（@$2/H100-hr） | 完全开放的代价：无法使用商业闭源数据降本 |
| RL计算分配比 | 推理:训练 ≈ 5:1（20推理节点:8训练节点，32B） | inflight更新需大量推理算力；GPU分配对吞吐影响显著 |
| 预训练占总计算比例 | >90% | 中间训练/后训练边际成本低，但base质量决定上限 |
| 扩展RL(3.0→3.1)额外成本 | +21天/224 GPU | IFBench+20.5pp收益集中于此阶段，但非所有团队可复现 |


#### 机制迁移

##### 机制解耦

| 原语名称 | 本文用途 | 抽象描述 | 信息论/几何直觉 |
|---------|---------|---------|----------------|
| OlmoRL 飞行权重更新 | 解耦 vLLM 推理节点与训练节点，推理节点每 N 步异步接收新权重 | 异步参数广播 + 重要性采样修正旧策略生成的样本 | 旧策略生成数据落在参数空间旧点，IS 权重将 KL 散度拉回当前策略邻域，维持策略梯度方差界 |
| Delta Learning DPO | 用大模型（Qwen3-32B）chosen + 小模型（Qwen3-0.6B）rejected 构建对比对 | 最大化 chosen-rejected 质量差距以增强 DPO 信号 | 在响应质量空间中，增大正负样本的边际距离等价于提升对比学习的 SNR |
| Active Sampling | RL 训练中过滤掉优势值全零的批次，维持 >90% 非零优势批 | 在策略梯度估计中剔除零梯度批次 | 零优势批贡献零信息量（Fisher 矩阵迹为零），剔除它们等价于维持有效样本的 Fisher 信息密度 |
| 条件混合（Conditional Mixing） | 将迟到 PDF 数据注入为独立虚拟域，冻结已有混合权重比例 | 在不重启训练 swarm 的情况下动态追加新数据域 | 新域引入额外自由度，等价于在数据分布凸包中追加一个顶点，不破坏已收敛的域边界 |

##### 机制谱系

**前身 (Ancestors, ≥3):**
- **GRPO（Shao et al. 2024）** — OlmoRL 保留 group 优势估计，去除 KL 惩罚和方差归一化，减少难题偏置
- **DAPO（Yu et al. 2025）** — OlmoRL 继承 token 级 loss 归一化 + 零梯度过滤，新增飞行权重更新实现 4× 吞吐提升
- **Dr.GRPO（Liu et al. 2025b）** — 提出去除 std-dev 归一化以消除难题偏置；OlmoRL 将其集成并扩展到 32B 规模
- **Delta Learning（Geng et al. 2025）** — 提出 chosen-rejected 质量差最大化原则；OLMo 3 将其用于 Think DPO 阶段并验证其与 RL 的互补性
- **Model Souping（Wortsman et al. 2022）** — 在参数空间合并多个中训种子，OLMo 3 32B 获 +2.9pp Math

**兄弟 (Siblings):**
- **DeepSeek R1（Guo et al. 2025）** — 同期闭源数据 RLVR 推理模型，OLMo 3 全开源数据，AIME 2024 持平 80.6% vs 79.8%
- **Qwen 3 32B（Yang et al. 2025）** — 同期开放权重思考模型，约 6× 更多训练 token；OLMo 3 用更少算力逼近

**创新增量:** OLMo 3 的核心增量在于将飞行权重更新（OlmoRL）与 Delta Learning DPO 热启动组合，解决了开源 RL 基础设施吞吐瓶颈（从 881→2949 tok/s）；同时首次在 Figure 1、Figure 2 所示全流程（预训/中训/长上下文/SFT/DPO/RL）中做到数据、代码、权重全部开放，使 AIME 2024 80.6% 的结果完全可复现。
