# 可点击式逐步教程

> 推荐使用新的 [Jupyter Notebook 分块课程](../notebooks/README.md)；本目录保留为纯文字讲解版。

这里是仓库的学习入口。每一课都包含“读代码 → 运行 → 修改 → 测试 → 提交”五个动作，并在页面底部提供上一课和下一课。

## 使用方法

1. 只打开当前一课，不要一次读完整个仓库；
2. 点击本课列出的源码链接，在 GitHub 中查看真实实现；
3. 复制本课命令到仓库根目录运行；
4. 完成“亲手修改”后执行指定测试；
5. 测试通过再进入下一课。

## 学习路线

| 顺序 | 页面 | 完成标志 |
|---:|---|---|
| 0 | [Notebook](../notebooks/00_setup.ipynb) · [文字版](00_setup.md) | 能导入 `memcast_uav`，10 项测试通过 |
| 1 | [Notebook](../notebooks/01_windowing.ipynb) · [文字版](01_windowing.md) | 能手算首个测试窗口索引 |
| 2 | [Notebook](../notebooks/02_features.ipynb) · [文字版](02_features.md) | 能写出每个特征的单位 |
| 3 | [Notebook](../notebooks/03_retrieval.ipynb) · [文字版](03_retrieval.md) | 能解释 `alpha=0/1` 的排名差异 |
| 4 | [Notebook](../notebooks/04_memory.ipynb) · [文字版](04_memory.md) | 能解释记忆条目的每个字段 |
| 5 | [Notebook](../notebooks/05_reflection.ipynb) · [文字版](05_reflection.md) | 能修复或拒绝非法候选轨迹 |
| 6 | [Notebook](../notebooks/06_confidence.ipynb) · [文字版](06_confidence.md) | 不会提前使用未来真值 |
| 7 | [Notebook](../notebooks/07_end_to_end.ipynb) · [文字版](07_end_to_end.md) | 能与恒速基线比较 |
| 8 | [Notebook](../notebooks/08_intent.ipynb) · [文字版](08_intent.md) | 能说明意图来源和防止泄漏 |
| 9 | [接入真实无人机数据](../docs/03_uav_dataset_adapter.md) | 将真实飞行转换为统一窗口 |

## 遇到问题时

- `ModuleNotFoundError: memcast_uav`：返回 [第 0 步](00_setup.md)，重新执行可编辑安装；
- 不知道从哪个函数读起：严格按照本课“实现顺序”点击；
- 修改后结果异常：只运行本课指定测试，先缩小问题范围；
- 想一次运行全部课程：完成前八课后再执行 `python scripts/run_all_lessons.py`。

[返回仓库首页](../README.md) | [开始第 0 步 →](00_setup.md)
