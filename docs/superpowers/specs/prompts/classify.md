根据论文摘要和以下分类规则，对论文进行分类。

## 论文摘要和关键词

{SUMMARY}

<!-- 运行时由 `deepaper classify` 从 notes.md 的 META 段提取 -->

## 分类规则

{CATEGORIES}

<!-- 运行时由 `deepaper classify` 从 templates/categories.md 注入完整规则 -->
<!-- 包含 4 大类（llm/recsys/multimodal/misc）、13 子类、3 条分类原则 -->

## 输出

仅返回一个 JSON 对象：

```json
{"category": "llm/pretraining"}
```

其中 value 是相对于 papers/ 的分类路径。有效的顶级分类: llm, recsys, multimodal, misc。不确定时归 misc。
