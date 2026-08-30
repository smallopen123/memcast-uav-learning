# 第 7 课：端到端预测管线

> 可逐格运行版本：[打开第 7 课 Notebook](../notebooks/07_end_to_end.ipynb)

目标：把窗口、特征、记忆、检索、候选、反思、基线比较和置信度反馈串成完整闭环。

## 7.1 按顺序打开代码

1. [课程入口：lesson_07_end_to_end.py](../lessons/lesson_07_end_to_end.py)
2. [完整管线：pipeline.py](../src/memcast_uav/pipeline.py)
3. [对应测试：test_pipeline.py](../tests/test_pipeline.py)

在 `pipeline.py` 中先读 `predict_window()`，再读 `run_demo()`。不要从文件第一行顺序通读。

## 7.2 看懂一次预测

```text
当前历史窗口
  → 提取特征
  → 检索 Top-K 经验
  → 经验未来位移生成候选 + 恒速候选
  → 逐候选物理反思
  → 选择有效候选
  → 真实未来成熟后比较基线并更新置信度
```

## 7.3 运行课程

```powershell
python -m lessons.lesson_07_end_to_end
```

输出字段：

- `samples`：测试样本数；
- `mse`：记忆条件预测误差；
- `baseline_mse`：恒速基线误差；
- `memory_entries`：记忆条目数；
- `accepted/rejected_candidates`：反思层接受与拒绝数量。

不能只报告 `mse`；必须与简单基线放在一起，否则无法证明复杂方法带来增益。

## 7.4 做一次单变量实验

在 [pipeline.py](../src/memcast_uav/pipeline.py) 的 `run_demo()` 中只选择一个变量：

- `build_memory(..., limit=10/30)`
- `RetrievalConfig(..., top_k=1/3)`
- `intent_weight=0.0/0.25`

每次修改后运行同一命令，并填写：

| 参数 | MSE | baseline MSE | 接受候选 | 拒绝候选 |
|---|---:|---:|---:|---:|
| 原始值 |  |  |  |  |
| 修改值 |  |  |  |  |

完成后恢复默认参数，避免影响下一课。

## 7.5 验收测试

```powershell
python -m pytest tests/test_pipeline.py -q
```

随后运行全量回归：

```powershell
python -m pytest -q
```

通过标准：端到端输出为有限数值，候选计数与样本数一致，全部 10 项测试通过。

[← 第 6 课](06_confidence.md) | [教程目录](README.md) | [下一课：意图条件预测 →](08_intent.md)
