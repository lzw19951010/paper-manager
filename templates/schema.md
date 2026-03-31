请输出一个 JSON 对象（不要 markdown 代码块，不要多余解释），包含以下字段。
结构化元数据字段为简短值，分析字段为完整的 Markdown 文本（可包含子标题、表格、代码块等富格式）。

{
  "venue": "发表场所 (如 NeurIPS 2023)，未找到则为 null",
  "publication_type": "论文类型: conference/journal/preprint/workshop/thesis 之一",
  "doi": "DOI 标识符（如 10.xxxx/yyyy），从论文中提取，未找到则为 null",
  "keywords": ["关键词1", "关键词2", "...5-10个技术关键词"],
  "tldr": "一句话总结论文核心贡献（≤100字，纯文本）",
  "core_contribution": "核心贡献类型: new-method/new-dataset/new-benchmark/new-framework/survey/empirical-study/theoretical 之一或组合",
  "baselines": ["对比的主要baseline方法名称列表"],
  "datasets": ["使用的数据集名称列表"],
  "metrics": ["使用的评估指标列表，如 BLEU, Recall@20, NDCG@10"],
  "code_url": "官方代码仓库 URL，从论文中提取，未找到则为 null",
  "executive_summary": "核心速览的完整 Markdown 文本（含 TL;DR、一图流、核心机制一句话）",
  "motivation": "动机与第一性原理的完整 Markdown 文本（含痛点、核心洞察、直觉解释）",
  "methodology": "方法详解的完整 Markdown 文本（含直觉版、精确版、设计决策、易混淆点）",
  "experiments": "实验与归因的完整 Markdown 文本（含核心收益、归因分析、可信度检查）",
  "critical_review": "专家批判的完整 Markdown 文本（含隐性成本、工程落地建议、关联思考）",
  "mechanism_transfer": "机制迁移分析的完整 Markdown 文本（含机制解耦、迁移处方、机制家族图谱）",
  "background_context": "背景知识补充的 Markdown 文本，如不需要则为 null"
}
