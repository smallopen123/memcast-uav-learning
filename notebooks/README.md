# Jupyter Notebook 分块课程

每个 Notebook 都可以按单元格使用 `Shift + Enter` 逐步运行，并在末尾链接到上一课和下一课。

## 第一次使用

```powershell
python -m venv .venv
.venv/Scripts/Activate.ps1
python -m pip install -e ".[dev,notebook]"
jupyter lab
```

然后在 Jupyter 左侧文件栏打开 `notebooks/00_setup.ipynb`。

## 课程入口

| 顺序 | Notebook | 主要内容 |
|---:|---|---|
| 0 | [环境准备与验证](00_setup.ipynb) | 自动定位仓库、导入检查、10 项测试 |
| 1 | [时间窗口](01_windowing.ipynb) | 历史/未来窗口与无泄漏划分 |
| 2 | [运动学特征](02_features.ipynb) | 速度、加速度、转弯率与位移 |
| 3 | [组合检索](03_retrieval.ipynb) | 余弦相似度、DTW、意图和置信度 |
| 4 | [经验记忆](04_memory.ipynb) | 记忆字段、相对未来位移、上下文设计 |
| 5 | [物理反思](05_reflection.ipynb) | 约束检查、修正、复查与拒绝 |
| 6 | [动态置信度](06_confidence.ipynb) | 延迟反馈、因果更新、避免未来泄漏 |
| 7 | [端到端管线](07_end_to_end.ipynb) | 完整预测闭环与恒速基线 |
| 8 | [意图条件预测](08_intent.ipynb) | 意图权重消融与层级意图 |

Notebook 是分块学习入口；原始 `lessons/*.py` 和 `src/memcast_uav/*.py` 保留为可测试的参考实现。

[返回仓库首页](../README.md) · [从第 0 步开始 →](00_setup.ipynb)
