# 第 8 课：意图条件预测

> 可逐格运行版本：[打开第 8 课 Notebook](../notebooks/08_intent.ipynb)

目标：让检索不仅回答“历史轨迹像不像”，还回答“当前任务意图是否一致”。

## 8.1 按顺序打开代码

1. [课程入口：lesson_08_intent.py](../lessons/lesson_08_intent.py)
2. [意图写入窗口：data.py](../src/memcast_uav/data.py)
3. [意图写入记忆：memory.py](../src/memcast_uav/memory.py)
4. [意图参与打分：retrieval.py](../src/memcast_uav/retrieval.py)
5. [意图检索测试：test_retrieval.py](../tests/test_retrieval.py)

## 8.2 区分三种意图来源

| 来源 | 示例 | 预测时是否可用 |
|---|---|---|
| 任务规划 | 巡检、配送、返航 | 通常可用 |
| 控制指令 | 左转、爬升、悬停 | 通常可用 |
| 在线识别器 | 根据已观测历史估计下一机动 | 可用，但有识别误差 |

禁止先读取真实未来轨迹，再把未来动作标签作为当前输入；这属于标签泄漏。

## 8.3 运行意图消融

```powershell
python -m lessons.lesson_08_intent
```

课程对比：

```text
intent_weight = 0.0  → 只依赖轨迹与置信度
intent_weight = 0.6  → 同意图记忆得到额外奖励
```

观察两个 Top-3 的意图组成是否发生变化。

## 8.4 亲手设计层级意图

先设计两层标签：

```text
mission: inspection / delivery / return_home
maneuver: cruise / turn_left / turn_right / climb / descend
```

再设计分数：

```text
intent_bonus =
    mission_weight * mission_match
  + maneuver_weight * maneuver_match
```

思考当“任务相同但机动不同”以及“任务不同但机动相同”时，哪一层应占更大权重。真实实验必须分别报告无意图、真值可用意图和在线识别意图，不能混为一种结果。

## 8.5 验收测试

```powershell
python -m pytest tests/test_retrieval.py tests/test_pipeline.py -q
```

通过标准：意图奖励能影响检索，但关闭意图后系统仍可运行。

## 下一阶段

你已经跑通完整的离线最小实现。接下来不要直接接 Qwen，先按照 [无人机数据迁移指南](../docs/03_uav_dataset_adapter.md) 把 DJI Matrice 100 或 NeuroBEM/UZH-FPV 转换为相同的 `TrajectoryWindow` 结构。

[← 第 7 课](07_end_to_end.md) | [教程目录](README.md) | [下一阶段：真实无人机数据 →](../docs/03_uav_dataset_adapter.md)
