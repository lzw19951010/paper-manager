# 论文分类规则

本文件定义了论文自动分类的规则，用于将论文归入 `papers/` 下的对应目录。

---

## llm/ — 通用大语言模型

与大语言模型本身的训练、对齐、推理能力、效率优化或 Agent 能力相关的论文。

- **pretraining/** — 预训练：数据工程、模型架构设计（Transformer 变体等）、scaling law、tokenizer 设计、预训练策略（课程学习、数据配比等）
- **alignment/** — 对齐：RLHF、DPO、RLAIF、PPO for LLM、安全对齐、红队测试、指令微调（SFT）、偏好学习
- **reasoning/** — 推理：Chain-of-Thought（CoT）、Tree-of-Thought（ToT）、thinking models（o1/o3 类）、数学推理、代码推理、逻辑推理、自我反思
- **efficiency/** — 效率：量化（GPTQ、AWQ）、知识蒸馏、剪枝、MoE（混合专家）、推理加速（FlashAttention、vLLM、PagedAttention）、LoRA 等参数高效微调方法（PEFT）
- **agent/** — Agent：tool use、function calling、planning（任务规划）、memory（记忆机制）、multi-agent 协作、ReAct、代码执行 Agent

---

## recsys/ — 推荐系统

与推荐系统的召回、排序、建模范式或工程实现相关的论文。

- **matching/** — 召回：双塔模型、图神经网络（GNN）用于推荐、序列推荐（SASRec、BERT4Rec 等）、向量检索（ANN）、用户/物品表示学习
- **ranking/** — 排序：CTR 预估（DeepFM、DCN 等）、多任务学习（MTL）、特征交互建模、重排序（re-ranking）、listwise/pairwise 排序
- **llm-as-rec/** — LLM 即推荐模型：LLM 端到端完成推荐任务，模型本身同时具备自然语言理解/生成能力和推荐能力。核心贡献在于让 LLM 直接理解用户偏好并输出推荐结果，不是简单地把推荐任务转成 NLP prompt 再调用外部 LLM。
- **generative-rec/** — 生成式推荐：用生成范式做推荐（生成 item ID 序列、token 序列等），以 next-token/next-item 预测的方式建模推荐，不一定需要 LLM 的自然语言能力
- **system/** — 推荐系统工程：embedding serving、特征工程与存储、A/B 测试框架、在线学习（online learning）、工业级推荐系统架构

---

## multimodal/ — 多模态与 CV

涉及图像、视频、音频等多种模态，或纯计算机视觉任务的论文。

- **vlm/** — 视觉语言模型：CLIP、LLaVA、BLIP、Flamingo 等多模态理解模型，图文对齐，视觉问答（VQA），多模态大模型
- **generation/** — 生成：Diffusion 模型（DDPM、Stable Diffusion）、视频生成、图像编辑、文生图（text-to-image）、图像超分
- **understanding/** — 理解：目标检测（YOLO、DETR）、图像分割（SAM）、OCR、视觉推理、图像分类、深度估计

---

## misc/ — 其他

不属于以上任何类别的论文，例如：图神经网络（非推荐场景）、强化学习（非 LLM 对齐场景）、数据库、系统、理论等。

---

## 分类规则

1. **按主要贡献归类**：跨领域论文以核心贡献所属方向为准。例如，一篇用 LLM 做推荐的论文，若核心贡献是推荐方法（如新的 ID 建模方式），归 `recsys/llm-as-rec`；若核心贡献是 LLM 本身的新能力（如 in-context learning），则归 `llm/`。
2. **llm-as-rec 优先**：当 `llm-as-rec` 和 `generative-rec` 难以区分时（例如论文同时涉及 LLM 端到端推荐和生成式 item 建模），优先归入 `recsys/llm-as-rec`。
3. **不确定时归 misc/**：若论文不明确属于上述某个子类别，或跨多个领域且无明显主导方向，归入 `misc/`。
4. **输出格式**：返回 JSON `{"category": "大类/子类"}`，例如 `{"category": "llm/pretraining"}` 或 `{"category": "misc"}`。
