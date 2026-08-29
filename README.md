# MemCast-UAV Learning Lab

一个面向初学者的、可逐步运行的教学仓库：从时间窗口、轨迹特征和 DTW 检索开始，逐步实现经验记忆、候选轨迹、约束反思、动态置信度，最后迁移到带意图的低空无人机轨迹预测。

> 本仓库是独立编写的教学实现，并非 MemCast 官方代码，也不宣称复现论文指标。思想来源与引用见下文。

## 从这里开始：可点击式教程

不要先运行全部代码。请点击下面的入口，从环境检查开始；完成一页后，使用页面底部的“下一课”继续：

### [▶ 从第 0 步开始：安装并验证环境](tutorial/00_setup.md)

[教程总目录](tutorial/README.md) → [01 窗口](tutorial/01_windowing.md) → [02 特征](tutorial/02_features.md) → [03 检索](tutorial/03_retrieval.md) → [04 记忆](tutorial/04_memory.md) → [05 反思](tutorial/05_reflection.md) → [06 置信度](tutorial/06_confidence.md) → [07 端到端](tutorial/07_end_to_end.md) → [08 意图](tutorial/08_intent.md) → [接入真实无人机数据](docs/03_uav_dataset_adapter.md)

## 你会学到什么

完成八个练习后，你应该能够解释并亲手实现：

1. 如何在时间序列上构造无泄漏的历史/未来窗口；
2. 如何从无人机轨迹提取速度、加速度、航向、转弯率和爬升率；
3. 如何组合特征余弦相似度与原始轨迹 DTW；
4. 如何把历史预测案例组织为可检索的经验记忆；
5. 如何产生多条候选轨迹，并用飞行规律反思和修正；
6. 如何在真实未来可见后，因果地更新记忆置信度；
7. 如何把这些模块组装为一个端到端离线预测器；
8. 如何加入 `cruise / turn_left / turn_right / climb / descend` 意图。

## 快速开始

需要 Python 3.10 或更高版本。

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python scripts/run_all_lessons.py
python -m pytest -q
```

所有基础课程都使用固定随机种子的合成无人机轨迹，不下载数据、不调用大模型，也不会产生 API 费用。

## 学习路线

| 课程（点击进入） | 运行命令 | 核心问题 |
|---|---|---|
| [01 窗口](tutorial/01_windowing.md) | `python -m lessons.lesson_01_windowing` | 模型到底看到了哪些历史和未来？ |
| [02 特征](tutorial/02_features.md) | `python -m lessons.lesson_02_features` | 轨迹如何变成可检索特征？ |
| [03 检索](tutorial/03_retrieval.md) | `python -m lessons.lesson_03_retrieval` | 相似机动如何被找出来？ |
| [04 记忆](tutorial/04_memory.md) | `python -m lessons.lesson_04_memory` | 一个经验条目应保存什么？ |
| [05 反思](tutorial/05_reflection.md) | `python -m lessons.lesson_05_reflection` | 怎样拒绝或修正不可能的飞行轨迹？ |
| [06 置信度](tutorial/06_confidence.md) | `python -m lessons.lesson_06_confidence` | 如何避免用未来信息提前更新记忆？ |
| [07 端到端](tutorial/07_end_to_end.md) | `python -m lessons.lesson_07_end_to_end` | 各模块怎样构成完整预测流程？ |
| [08 意图](tutorial/08_intent.md) | `python -m lessons.lesson_08_intent` | 意图怎样影响检索与候选生成？ |

建议每学一节，都完成该文件末尾的 `TODO`，再运行对应测试。

## 仓库结构

```text
memcast-uav-learning/
├─ lessons/                 # 八个可独立运行的渐进练习
├─ src/memcast_uav/         # 最小、可测试的核心实现
├─ tests/                   # 与每个核心概念对应的测试
├─ docs/                    # 论文概念、完整源码映射、无人机迁移说明
├─ data/                    # 公开数据适配说明，不提交大数据文件
├─ scripts/                 # 一键运行课程和数据检查脚本
└─ .github/workflows/       # GitHub Actions 自动测试
```

## 组合检索

本教学实现使用：

\[
S_{base}=\alpha S_{feature}+(1-\alpha)\exp(-DTW/\gamma)
\]

\[
S_{final}=S_{base}+w_c C+w_i I
\]

其中：

- `S_feature`：轨迹运动学特征的余弦相似度；
- `DTW`：两段三维历史轨迹的动态时间规整距离；
- `C`：历史经验置信度；
- `I`：当前意图与记忆意图是否一致。

## 安全与费用

- 默认实现完全离线；
- `.env`、密钥、真实数据和运行产物均被 `.gitignore` 排除；
- 可选 Qwen 接口只提供配置示例，不会在课程和测试中自动调用；
- 不要把 DJI、UZH-FPV 或 NeuroBEM 的大文件直接提交到 Git。

## 与 MemCast 的关系

本仓库用于学习论文中的经验条件推理思想：

- Tao et al., *MemCast: Memory-Driven Time Series Forecasting with Experience-Conditioned Reasoning*, arXiv:2602.03164, 2026.
- 官方/公开项目：[ustc-time-series/MemCast](https://github.com/ustc-time-series/MemCast)
- 论文：[arXiv:2602.03164](https://arxiv.org/abs/2602.03164)

如果在论文或项目中使用这些思想，请同时引用原论文。本仓库采用 MIT License；上游代码和数据仍分别服从各自许可证。

## 下一步

先进入 [可点击式教程](tutorial/README.md)。完成离线课程后，再按照 [无人机数据迁移指南](docs/03_uav_dataset_adapter.md) 接入真实数据。优先保证坐标系、采样率、序列划分和单位正确，然后再接入任何大模型。
