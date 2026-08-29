# 第 1 课：时间窗口与无泄漏划分

目标：把一条连续三维航迹切成“历史输入”和“未来标签”，并保证训练标签不会跨入测试区间。

## 1.1 按顺序打开代码

1. [课程入口：lesson_01_windowing.py](../lessons/lesson_01_windowing.py)
2. [核心实现：data.py](../src/memcast_uav/data.py)
3. [对应测试：test_data.py](../tests/test_data.py)

在 `data.py` 中依次寻找：

- `FlightSequence`：一条完整飞行；
- `TrajectoryWindow`：一条训练或测试样本；
- `make_windows()`：切出历史和未来；
- `make_train_test_windows()`：按时间划分训练集和测试集。

## 1.2 运行课程

```powershell
python -m lessons.lesson_01_windowing
```

重点观察：

```text
history=[228:252)
future=[252:264)
历史形状: (24, 3), 未来形状: (12, 3)
```

`[228:252)` 右端不包含 252，所以共有 24 个历史点；未来从划分点 252 才开始。

## 1.3 手算一个窗口

已知 `split_index=252`、`history=24`、`horizon=12`：

- 历史开始：`252 - 24 = 228`
- 历史结束/预测开始：`252`
- 预测结束：`252 + 12 = 264`

测试历史可以使用 252 之前已经观测到的数据，但测试未来不能进入训练标签。

## 1.4 亲手修改

打开 [lesson_01_windowing.py](../lessons/lesson_01_windowing.py)，把 `stride=12` 改为 `stride=6`，重新运行并回答：

1. 窗口数量为什么增加？
2. 相邻样本是否共享部分历史或未来？
3. 共享未来区间会不会影响统计独立性？

完成观察后，可以把参数改回 12。

## 1.5 验收测试

```powershell
python -m pytest tests/test_data.py -q
```

通过标准：2 项测试通过，并且你能解释下面两个断言：

```python
window.forecast_end <= split_index
window.forecast_start >= split_index
```

[← 第 0 步](00_setup.md) | [教程目录](README.md) | [下一课：运动学特征 →](02_features.md)
