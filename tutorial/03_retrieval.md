# 第 3 课：余弦相似度 + DTW 组合检索

目标：从经验记忆中找出与当前无人机机动最相似的历史案例。

## 3.1 按顺序打开代码

1. [课程入口：lesson_03_retrieval.py](../lessons/lesson_03_retrieval.py)
2. [检索实现：retrieval.py](../src/memcast_uav/retrieval.py)
3. [特征实现：features.py](../src/memcast_uav/features.py)
4. [对应测试：test_retrieval.py](../tests/test_retrieval.py)

在 `retrieval.py` 中按此顺序读：

`cosine_similarity()` → `dtw_distance()` → `retrieve()`。

## 3.2 理解组合分数

```text
feature_similarity = cosine(query_features, memory_features)
structural_similarity = exp(-dtw_distance / gamma)
base_score = alpha * feature_similarity + (1-alpha) * structural_similarity
final_score = base_score + confidence_weight * confidence + intent_weight * intent_match
```

- 余弦相似度比较“整体运动特征方向”；
- DTW 比较“轨迹形状随时间的变化”；
- 置信度体现该经验过去是否可靠；
- 意图奖励让任务语义一致的经验更靠前。

## 3.3 运行课程

```powershell
python -m lessons.lesson_03_retrieval
```

你会看到 Top-3 的记忆编号、意图、余弦相似度、DTW 距离和最终分数。

## 3.4 亲手完成消融

在 [lesson_03_retrieval.py](../lessons/lesson_03_retrieval.py) 中分别运行：

```python
RetrievalConfig(alpha=0.0, gamma=120.0, top_k=3, intent_weight=0.25)
RetrievalConfig(alpha=1.0, gamma=120.0, top_k=3, intent_weight=0.25)
```

记录两个 Top-3：

| 设置 | 只使用什么 | Top-3 是否变化 |
|---|---|---|
| `alpha=0` | DTW 结构相似度 | 自己填写 |
| `alpha=1` | 特征余弦相似度 | 自己填写 |

不要同时修改 `gamma` 和 `intent_weight`，否则无法判断是哪一个变量造成变化。

## 3.5 验收测试

```powershell
python -m pytest tests/test_retrieval.py -q
```

通过标准：2 项测试通过；Top-K 分数降序排列，足够大的意图权重能提升同意图记忆。

[← 第 2 课](02_features.md) | [教程目录](README.md) | [下一课：经验记忆 →](04_memory.md)
