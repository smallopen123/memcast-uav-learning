# 第 6 课：因果动态置信度

> 可逐格运行版本：[打开第 6 课 Notebook](../notebooks/06_confidence.ipynb)

目标：只有当预测区间的真实轨迹已经观测完成，才能根据预测效果更新记忆置信度。

## 6.1 按顺序打开代码

1. [课程入口：lesson_06_confidence.py](../lessons/lesson_06_confidence.py)
2. [核心实现：confidence.py](../src/memcast_uav/confidence.py)
3. [记忆更新：memory.py](../src/memcast_uav/memory.py)
4. [对应测试：test_confidence.py](../tests/test_confidence.py)

重点理解 `FeedbackEvent.available_at` 和 `FeedbackEvent.applied`：

- `available_at`：真实未来全部可见的最早时间；
- `applied`：保证同一反馈事件只应用一次。

## 6.2 运行课程

```powershell
python -m lessons.lesson_06_confidence
```

预期逻辑：

```text
预测刚开始：真实未来不可见 → 更新数 0
预测区间结束：真实未来已可见 → 成功经验置信度 +0.01
```

如果在 `forecast_start` 就用真实误差更新，就等于把未来答案泄漏给当前预测。

## 6.3 跟踪事件生命周期

在调试器中依次观察：

1. `queue.add(event)`
2. `apply_available(forecast_start, memory)`
3. `apply_available(forecast_end, memory)`
4. 再次调用 `apply_available(forecast_end, memory)`

第 4 次不应再次增加置信度。

## 6.4 亲手修改

把课程中的：

```python
feedback={"success": True}
```

改为：

```python
feedback={"success": False}
```

重新运行，确认失败案例不会增加置信度。然后恢复原值。

思考：真实研究中只用 `success=True/False` 是否过于粗糙？可以设计基于相对 MSE 改善幅度的连续 `delta`，但必须保持时间因果性。

## 6.5 验收测试

```powershell
python -m pytest tests/test_confidence.py -q
```

通过标准：2 项测试通过；失败事件不加分，同一事件不会重复应用。

[← 第 5 课](05_reflection.md) | [教程目录](README.md) | [下一课：端到端管线 →](07_end_to_end.md)
