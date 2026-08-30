# 第 2 课：三维轨迹运动学特征

> 可逐格运行版本：[打开第 2 课 Notebook](../notebooks/02_features.ipynb)

目标：把 `[时间, xyz]` 的位置序列转换为可解释、可检索的运动学向量。

## 2.1 按顺序打开代码

1. [课程入口：lesson_02_features.py](../lessons/lesson_02_features.py)
2. [核心实现：features.py](../src/memcast_uav/features.py)
3. [对应测试：test_features.py](../tests/test_features.py)

重点阅读 `extract_motion_features()`：

```text
位置 --一次差分/dt--> 速度 --一次差分/dt--> 加速度
速度(x,y) --atan2--> 航向角 --差分/dt--> 转弯率
```

## 2.2 运行课程

```powershell
python -m lessons.lesson_02_features
```

程序会逐项打印 9 个特征，并在最后显示 `特征向量形状: (9,)`。

## 2.3 给特征标单位

当前合成数据把位置看作米、时间看作秒：

| 特征 | 单位 |
|---|---|
| mean/max/std speed | m/s |
| mean/std acceleration | m/s² |
| mean climb rate | m/s |
| mean turn rate | rad/s |
| horizontal displacement、altitude change | m |

这解释了为什么真实数据接入前必须先统一坐标系、采样间隔和单位。

## 2.4 亲手修改

在 [features.py](../src/memcast_uav/features.py) 中暂时把返回数组最后一项 `displacement[2]` 改成 `displacement[2] * 1000`，运行课程并观察：

1. 某一维量纲被放大后，余弦相似度是否可能被它主导？
2. 为什么后续真实实验需要用训练集统计量做标准化？

观察后恢复原表达式。

再打开测试，理解“整体平移 100 米后相对轨迹不变”的断言。

## 2.5 验收测试

```powershell
python -m pytest tests/test_features.py -q
```

通过标准：2 项测试通过；你能说明每个特征的形状、单位和物理含义。

[← 第 1 课](01_windowing.md) | [教程目录](README.md) | [下一课：组合检索 →](03_retrieval.md)
