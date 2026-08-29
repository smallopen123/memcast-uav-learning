# 教学代码与完整MemCast流程对照

本表帮助你从小型教学实现过渡到公开MemCast代码。上游文件可能继续变化，因此以概念对应为主。

| 概念 | 教学实现 | MemCast公开项目中的主要位置 |
|---|---|---|
| 数据窗口 | `src/memcast_uav/data.py` | `main/ETTh/visual.py`及各任务入口 |
| 轨迹/序列特征 | `src/memcast_uav/features.py` | `extract_time_series_features`相关函数 |
| 经验条目 | `src/memcast_uav/memory.py` | `Memory/cases`生成与摘要逻辑 |
| 组合检索 | `src/memcast_uav/retrieval.py` | `ETTh_main_few_shot_reasoning.py`检索函数 |
| 多候选生成 | `pipeline.py::predict_window` | Few-shot reasoning中的多trajectory循环 |
| 规律检查 | `src/memcast_uav/reflection.py` | Few-shot reasoning中的reflection/QC |
| 置信度 | `src/memcast_uav/confidence.py` | 动态confidence adaptation逻辑 |
| 评估 | `pipeline.py::run_demo` | `evaluate/ETTh/evaluate_ETT_uqmem.py` |

推荐迁移阅读顺序：

1. 先在教学模块中逐行调试；
2. 在上游项目中搜索同一概念的入口函数；
3. 比较输入形状、文件副作用和失败处理；
4. 将差异写成表格，不要直接假定公开代码等于论文实验代码；
5. 先用缓存结果和离线测试验证，再决定是否发起付费API调用。

上游项目：https://github.com/ustc-time-series/MemCast

