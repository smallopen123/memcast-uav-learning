"""Generate the executable, cell-by-cell tutorial notebooks."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "notebooks"

BOOTSTRAP = """
import sys
from pathlib import Path

# 同时兼容：从仓库根目录启动 Jupyter，或从 notebooks/ 目录启动。
search_starts = [Path.cwd(), *Path.cwd().parents]
repo_root = next((path for path in search_starts if (path / "pyproject.toml").exists()), None)
if repo_root is None:
    raise RuntimeError("没有找到 pyproject.toml；请从仓库目录启动 Jupyter。")

src_dir = repo_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

print(f"仓库根目录: {repo_root}")
print(f"Python: {sys.version.split()[0]}")
"""


def markdown(source: str):
    return nbf.v4.new_markdown_cell(dedent(source).strip())


def code(source: str):
    return nbf.v4.new_code_cell(dedent(source).strip())


def notebook(title: str, cells: list, lesson: int):
    document = nbf.v4.new_notebook(cells=[markdown(title), *cells])
    document.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.10"},
        "memcast_uav": {"lesson": lesson, "generated": True},
    }
    return document


NOTEBOOKS = {
    "00_setup.ipynb": notebook(
        """
        # 第 0 步：环境准备与基线验证

        本 Notebook 先验证仓库位置、Python 版本和项目导入，再运行基线测试。

        **学习方式：**选中一个单元格，按 `Shift + Enter` 执行，然后进入下一格。
        """,
        [
            markdown(
                """
                ## 0.1 首次安装

                在仓库根目录的 PowerShell 中执行一次：

                ```powershell
                python -m venv .venv
                .venv/Scripts/Activate.ps1
                python -m pip install --upgrade pip
                python -m pip install -e ".[dev,notebook]"
                jupyter lab
                ```

                已经能打开本 Notebook 时，可以直接运行下一格。
                """
            ),
            code(BOOTSTRAP),
            markdown("## 0.2 验证核心包导入"),
            code(
                """
                import memcast_uav

                print("memcast_uav import OK")
                print("公开对象:", ", ".join(memcast_uav.__all__))
                """
            ),
            markdown("## 0.3 运行项目基线测试"),
            code(
                """
                import subprocess

                result = subprocess.run(
                    [sys.executable, "-m", "pytest", "-q"],
                    cwd=repo_root,
                    check=True,
                    text=True,
                    capture_output=True,
                )
                print(result.stdout)
                """
            ),
            markdown(
                """
                ## 完成检查

                - [ ] 已找到仓库根目录
                - [ ] `memcast_uav import OK`
                - [ ] 显示 `10 passed`

                [教程目录](README.md) · [下一课：时间窗口 →](01_windowing.ipynb)
                """
            ),
        ],
        lesson=0,
    ),
    "01_windowing.ipynb": notebook(
        """
        # 第 1 课：时间窗口与无泄漏划分

        目标：把连续三维航迹切成历史输入与未来标签，并验证训练标签不跨入测试段。
        """,
        [
            code(BOOTSTRAP),
            markdown(
                """
                ## 1.1 导入并生成一条合成飞行

                核心源码：[data.py](../src/memcast_uav/data.py)  
                文字讲解：[01_windowing.md](../tutorial/01_windowing.md)
                """
            ),
            code(
                """
                from memcast_uav.data import make_synthetic_flight, make_train_test_windows

                flight = make_synthetic_flight(n_points=360, seed=7)
                print("位置数组形状:", flight.positions.shape)
                print("采样间隔 dt:", flight.dt)
                print("前 5 个意图:", flight.intents[:5])
                """
            ),
            markdown("## 1.2 按时间切分训练与测试窗口"),
            code(
                """
                split_index = 252
                history = 24
                horizon = 12
                stride = 12

                train, test = make_train_test_windows(
                    flight,
                    split_index=split_index,
                    history=history,
                    horizon=horizon,
                    stride=stride,
                )
                print(f"训练窗口数: {len(train)}，测试窗口数: {len(test)}")
                """
            ),
            markdown("## 1.3 检查第一个测试样本的索引和形状"),
            code(
                """
                first = test[0]
                print(
                    f"history=[{first.history_start}:{first.forecast_start}), "
                    f"future=[{first.forecast_start}:{first.forecast_end})"
                )
                print("历史/未来形状:", first.history.shape, first.future.shape)
                print("意图:", first.intent)
                """
            ),
            markdown(
                """
                手算：`252 - 24 = 228`，因此历史是 `[228:252)`；未来长度为 12，
                所以未来是 `[252:264)`。右端不包含在切片中。
                """
            ),
            code(
                """
                assert all(window.forecast_end <= split_index for window in train)
                assert all(window.forecast_start >= split_index for window in test)
                print("无目标泄漏检查通过")
                """
            ),
            markdown("## 1.4 分块练习：把步长改成 6"),
            code(
                """
                train_stride_6, test_stride_6 = make_train_test_windows(
                    flight,
                    split_index=split_index,
                    history=history,
                    horizon=horizon,
                    stride=6,
                )
                print("stride=12:", len(train), len(test))
                print("stride=6 :", len(train_stride_6), len(test_stride_6))
                # TODO：用自己的话解释窗口数量为什么增加，以及相邻未来区间是否重叠。
                """
            ),
            markdown("## 1.5 本课验收"),
            code(
                """
                import subprocess

                completed = subprocess.run(
                    [sys.executable, "-m", "pytest", "tests/test_data.py", "-q"],
                    cwd=repo_root,
                    check=True,
                    text=True,
                    capture_output=True,
                )
                print(completed.stdout)
                """
            ),
            markdown(
                "[← 第 0 步](00_setup.ipynb) · [教程目录](README.md) · "
                "[下一课：运动学特征 →](02_features.ipynb)"
            ),
        ],
        lesson=1,
    ),
    "02_features.ipynb": notebook(
        """
        # 第 2 课：三维轨迹运动学特征

        目标：将 `[时间, x/y/z]` 位置序列变成可解释的九维运动学特征。
        """,
        [
            code(BOOTSTRAP),
            markdown(
                """
                ## 2.1 准备一个历史窗口

                核心源码：[features.py](../src/memcast_uav/features.py)  
                文字讲解：[02_features.md](../tutorial/02_features.md)
                """
            ),
            code(
                """
                from memcast_uav.data import make_synthetic_flight, make_train_test_windows
                from memcast_uav.features import (
                    FEATURE_NAMES,
                    extract_motion_features,
                    translation_invariant_path,
                )

                flight = make_synthetic_flight(n_points=360)
                _, test = make_train_test_windows(flight, split_index=252)
                window = test[0]
                print("历史窗口形状:", window.history.shape)
                """
            ),
            markdown("## 2.2 从位置差分得到速度、加速度和转弯率"),
            code(
                """
                import numpy as np

                velocity = np.diff(window.history, axis=0) / window.dt
                acceleration = np.diff(velocity, axis=0) / window.dt
                heading = np.unwrap(np.arctan2(velocity[:, 1], velocity[:, 0]))
                turn_rate = np.diff(heading) / window.dt

                print("速度形状:", velocity.shape, "单位 m/s")
                print("加速度形状:", acceleration.shape, "单位 m/s²")
                print("转弯率形状:", turn_rate.shape, "单位 rad/s")
                """
            ),
            markdown("## 2.3 调用正式特征提取函数"),
            code(
                """
                features = extract_motion_features(window.history, window.dt)
                units = ["m/s", "m/s", "m/s", "m/s²", "m/s²", "m/s", "rad/s", "m", "m"]

                for name, value, unit in zip(FEATURE_NAMES, features, units, strict=True):
                    print(f"{name:>24}: {value:9.4f} {unit}")
                print("特征形状:", features.shape)
                """
            ),
            markdown("## 2.4 验证相对轨迹不受整体平移影响"),
            code(
                """
                shifted = window.history + np.array([100.0, -20.0, 7.0])
                same = np.allclose(
                    translation_invariant_path(window.history),
                    translation_invariant_path(shifted),
                )
                print("整体平移后相对轨迹相同:", same)
                assert same
                """
            ),
            markdown("## 2.5 分块练习：观察量纲放大的影响"),
            code(
                """
                scaled = features.copy()
                scaled[-1] *= 1000
                print("原始 altitude_change:", features[-1])
                print("人为放大后:", scaled[-1])
                print("TODO：思考为什么真实数据必须只用训练集统计量进行标准化。")
                """
            ),
            markdown("## 2.6 本课验收"),
            code(
                """
                import subprocess

                completed = subprocess.run(
                    [sys.executable, "-m", "pytest", "tests/test_features.py", "-q"],
                    cwd=repo_root,
                    check=True,
                    text=True,
                    capture_output=True,
                )
                print(completed.stdout)
                """
            ),
            markdown(
                "[← 第 1 课](01_windowing.ipynb) · [教程目录](README.md) · "
                "[下一课：组合检索 →](03_retrieval.ipynb)"
            ),
        ],
        lesson=2,
    ),
    "03_retrieval.ipynb": notebook(
        """
        # 第 3 课：余弦相似度 + DTW 组合检索

        目标：从经验库找出与当前机动最相似的历史案例，并完成 `alpha` 消融。
        """,
        [
            code(BOOTSTRAP),
            markdown(
                """
                ## 3.1 构建查询和记忆库

                核心源码：[retrieval.py](../src/memcast_uav/retrieval.py)  
                文字讲解：[03_retrieval.md](../tutorial/03_retrieval.md)
                """
            ),
            code(
                """
                from memcast_uav.data import make_synthetic_flight, make_train_test_windows
                from memcast_uav.features import extract_motion_features
                from memcast_uav.memory import build_memory
                from memcast_uav.retrieval import RetrievalConfig, retrieve

                flight = make_synthetic_flight()
                train, test = make_train_test_windows(flight, split_index=504)
                memory = build_memory(train, limit=30)
                query = test[0]
                query_features = extract_motion_features(query.history, query.dt)
                print("记忆条目:", len(memory.entries), "查询意图:", query.intent)
                """
            ),
            markdown("## 3.2 组合检索 Top-3"),
            code(
                """
                config = RetrievalConfig(
                    alpha=0.5,
                    gamma=120.0,
                    top_k=3,
                    intent_weight=0.25,
                )
                ranked = retrieve(
                    query.history,
                    query_features,
                    query.intent,
                    memory,
                    config,
                )

                for rank, item in enumerate(ranked, start=1):
                    print(
                        f"Top {rank}: {item.entry.entry_id}, "
                        f"intent={item.entry.intent}, cos={item.feature_similarity:.4f}, "
                        f"dtw={item.dtw_distance:.2f}, match={item.intent_match:.0f}, "
                        f"score={item.final_score:.4f}"
                    )
                """
            ),
            markdown(
                """
                组合公式：

                `base = alpha × cosine + (1-alpha) × exp(-DTW/gamma)`

                `final = base + confidence_weight × confidence + intent_weight × intent_match`
                """
            ),
            markdown("## 3.3 分块练习：只改 alpha"),
            code(
                """
                def top_ids(alpha: float) -> list[str]:
                    results = retrieve(
                        query.history,
                        query_features,
                        query.intent,
                        memory,
                        RetrievalConfig(
                            alpha=alpha,
                            gamma=120.0,
                            top_k=3,
                            intent_weight=0.25,
                        ),
                    )
                    return [item.entry.entry_id for item in results]

                print("alpha=0（只看 DTW）:", top_ids(0.0))
                print("alpha=1（只看特征）:", top_ids(1.0))
                # TODO：记录排名差异，并解释两种相似度分别捕捉什么。
                """
            ),
            markdown("## 3.4 本课验收"),
            code(
                """
                scores = [item.final_score for item in ranked]
                assert scores == sorted(scores, reverse=True)

                import subprocess

                completed = subprocess.run(
                    [sys.executable, "-m", "pytest", "tests/test_retrieval.py", "-q"],
                    cwd=repo_root,
                    check=True,
                    text=True,
                    capture_output=True,
                )
                print(completed.stdout)
                """
            ),
            markdown(
                "[← 第 2 课](02_features.ipynb) · [教程目录](README.md) · "
                "[下一课：经验记忆 →](04_memory.ipynb)"
            ),
        ],
        lesson=3,
    ),
    "04_memory.ipynb": notebook(
        """
        # 第 4 课：经验记忆的结构与构建

        目标：理解一条经验为什么保存历史、未来、特征、意图、策略和置信度。
        """,
        [
            code(BOOTSTRAP),
            markdown(
                """
                ## 4.1 从训练窗口建立记忆

                核心源码：[memory.py](../src/memcast_uav/memory.py)  
                文字讲解：[04_memory.md](../tutorial/04_memory.md)
                """
            ),
            code(
                """
                from memcast_uav.data import make_synthetic_flight, make_train_test_windows
                from memcast_uav.memory import build_memory

                flight = make_synthetic_flight()
                train, _ = make_train_test_windows(flight, split_index=504)
                memory = build_memory(train, limit=5)
                print("记忆条目数:", len(memory.entries))
                """
            ),
            markdown("## 4.2 分块查看一条经验"),
            code(
                """
                entry = memory.entries[0]
                print("ID:", entry.entry_id)
                print("history:", entry.history.shape)
                print("future:", entry.future.shape)
                print("features:", entry.features.shape)
                print("intent:", entry.intent)
                print("strategy:", entry.strategy)
                print("confidence:", entry.confidence)
                """
            ),
            markdown("## 4.3 用相对未来位移迁移机动模式"),
            code(
                """
                displacement = entry.future_displacement
                hypothetical_current_position = entry.history[-1] + [1000.0, -200.0, 10.0]
                reused_candidate = hypothetical_current_position + displacement

                print("未来相对位移末点:", displacement[-1].round(3).tolist())
                print("迁移后候选末点:", reused_candidate[-1].round(3).tolist())
                """
            ),
            markdown(
                """
                ## 4.4 分块练习：设计环境上下文

                先在下面字典中填写预测时已经可见的上下文。不要读取预测区间之后的信息。
                """
            ),
            code(
                """
                context_design = {
                    "wind_enu_mps": [0.0, 0.0, 0.0],
                    "obstacle_density": 0.0,
                    "weather": "clear",
                }
                context_design
                """
            ),
            markdown(
                """
                TODO：

                1. 连续上下文如何标准化？
                2. 离散天气如何计算相似度？
                3. 哪些字段在预测时不可见，可能导致泄漏？
                """
            ),
            markdown("## 4.5 本课验收"),
            code(
                """
                assert len({item.entry_id for item in memory.entries}) == len(memory.entries)
                assert entry.future_displacement.shape == entry.future.shape

                import subprocess

                completed = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pytest",
                        "tests/test_retrieval.py",
                        "tests/test_pipeline.py",
                        "-q",
                    ],
                    cwd=repo_root,
                    check=True,
                    text=True,
                    capture_output=True,
                )
                print(completed.stdout)
                """
            ),
            markdown(
                "[← 第 3 课](03_retrieval.ipynb) · [教程目录](README.md) · "
                "[下一课：物理约束反思 →](05_reflection.ipynb)"
            ),
        ],
        lesson=4,
    ),
    "05_reflection.ipynb": notebook(
        """
        # 第 5 课：物理约束反思

        目标：对候选轨迹执行“检查—修正—复查”，拒绝明显违反飞行规律的输出。
        """,
        [
            code(BOOTSTRAP),
            markdown(
                """
                ## 5.1 准备历史和非法候选

                核心源码：[reflection.py](../src/memcast_uav/reflection.py)  
                文字讲解：[05_reflection.md](../tutorial/05_reflection.md)
                """
            ),
            code(
                """
                import numpy as np

                from memcast_uav.data import make_synthetic_flight, make_train_test_windows
                from memcast_uav.reflection import (
                    FlightConstraints,
                    check_constraints,
                    reflect_candidate,
                    trajectory_metrics,
                )

                flight = make_synthetic_flight(n_points=360)
                _, test = make_train_test_windows(flight, split_index=252)
                window = test[0]

                candidate = window.future.copy()
                candidate[:, 0] += np.linspace(0.0, 300.0, len(candidate))
                candidate[:, 2] = np.linspace(window.history[-1, 2], 180.0, len(candidate))
                print("非法候选形状:", candidate.shape)
                """
            ),
            markdown("## 5.2 检查违反了哪些约束"),
            code(
                """
                constraints = FlightConstraints(
                    max_speed=8.0,
                    max_acceleration=1.5,
                    max_altitude=120.0,
                )
                before_issues = check_constraints(
                    window.history,
                    candidate,
                    window.dt,
                    constraints,
                )
                print("修正前问题:", before_issues)
                print("修正前指标:", trajectory_metrics(window.history, candidate, window.dt))
                """
            ),
            markdown("## 5.3 运行确定性反思修正"),
            code(
                """
                repaired, trace = reflect_candidate(
                    window.history,
                    candidate,
                    window.dt,
                    constraints,
                )
                after_issues = check_constraints(
                    window.history,
                    repaired,
                    window.dt,
                    constraints,
                )
                print("每轮反思记录:", trace)
                print("修正后问题:", after_issues)
                print("修正后指标:", trajectory_metrics(window.history, repaired, window.dt))
                assert not after_issues
                """
            ),
            markdown("## 5.4 分块练习：一次只改变一个约束"),
            code(
                """
                for max_speed in (8.0, 6.0):
                    trial_constraints = FlightConstraints(
                        max_speed=max_speed,
                        max_acceleration=1.5,
                        max_altitude=120.0,
                    )
                    trial, trial_trace = reflect_candidate(
                        window.history,
                        candidate,
                        window.dt,
                        trial_constraints,
                    )
                    metrics = trajectory_metrics(window.history, trial, window.dt)
                    print(
                        f"max_speed={max_speed}: 反思轮数={len(trial_trace)-1}, "
                        f"最终最大速度={metrics['max_speed']:.3f}"
                    )
                """
            ),
            markdown(
                """
                TODO：设计一个圆形禁飞区 `(center_x, center_y, radius)`。
                先考虑如何检查候选点是否落入圆内，再考虑修正策略。
                """
            ),
            markdown("## 5.5 本课验收"),
            code(
                """
                import subprocess

                completed = subprocess.run(
                    [sys.executable, "-m", "pytest", "tests/test_reflection.py", "-q"],
                    cwd=repo_root,
                    check=True,
                    text=True,
                    capture_output=True,
                )
                print(completed.stdout)
                """
            ),
            markdown(
                "[← 第 4 课](04_memory.ipynb) · [教程目录](README.md) · "
                "[下一课：因果置信度 →](06_confidence.ipynb)"
            ),
        ],
        lesson=5,
    ),
    "06_confidence.ipynb": notebook(
        """
        # 第 6 课：因果动态置信度

        目标：只有预测区间真值已经完整可见时，才根据效果更新记忆置信度。
        """,
        [
            code(BOOTSTRAP),
            markdown(
                """
                ## 6.1 创建一条延迟反馈事件

                核心源码：[confidence.py](../src/memcast_uav/confidence.py)  
                文字讲解：[06_confidence.md](../tutorial/06_confidence.md)
                """
            ),
            code(
                """
                from memcast_uav.confidence import CausalConfidenceQueue, FeedbackEvent
                from memcast_uav.data import make_synthetic_flight, make_train_test_windows
                from memcast_uav.memory import build_memory

                flight = make_synthetic_flight()
                train, test = make_train_test_windows(flight, split_index=504)
                memory = build_memory(train, limit=3)
                target = memory.entries[0]

                event = FeedbackEvent(
                    event_id="notebook-feedback",
                    available_at=test[0].forecast_end,
                    contributing_ids=[target.entry_id],
                    feedback={"success": True},
                )
                queue = CausalConfidenceQueue()
                queue.add(event)
                print("反馈成熟时刻:", event.available_at)
                """
            ),
            markdown("## 6.2 预测刚开始：未来真值还不可见"),
            code(
                """
                before = target.confidence
                early_updates = queue.apply_available(test[0].forecast_start, memory)
                print("更新条目数:", early_updates)
                print("置信度:", before, "→", target.confidence)
                assert early_updates == 0
                assert target.confidence == before
                """
            ),
            markdown("## 6.3 预测区间结束：反馈可以应用"),
            code(
                """
                mature_updates = queue.apply_available(test[0].forecast_end, memory)
                after = target.confidence
                print("更新条目数:", mature_updates)
                print("置信度:", before, "→", after)
                assert mature_updates == 1
                assert after > before
                """
            ),
            markdown("## 6.4 同一事件不能重复应用"),
            code(
                """
                repeated_updates = queue.apply_available(test[0].forecast_end, memory)
                print("重复调用更新条目数:", repeated_updates)
                print("置信度仍为:", target.confidence)
                assert repeated_updates == 0
                """
            ),
            markdown("## 6.5 分块练习：失败事件不加分"),
            code(
                """
                failed_target = memory.entries[1]
                failed_event = FeedbackEvent(
                    event_id="notebook-failed-feedback",
                    available_at=test[0].forecast_end,
                    contributing_ids=[failed_target.entry_id],
                    feedback={"success": False},
                )
                failed_queue = CausalConfidenceQueue()
                failed_queue.add(failed_event)
                failed_queue.apply_available(test[0].forecast_end, memory)
                print("失败经验置信度:", failed_target.confidence)
                assert failed_target.confidence == 0.0
                """
            ),
            markdown("## 6.6 本课验收"),
            code(
                """
                import subprocess

                completed = subprocess.run(
                    [sys.executable, "-m", "pytest", "tests/test_confidence.py", "-q"],
                    cwd=repo_root,
                    check=True,
                    text=True,
                    capture_output=True,
                )
                print(completed.stdout)
                """
            ),
            markdown(
                "[← 第 5 课](05_reflection.ipynb) · [教程目录](README.md) · "
                "[下一课：端到端管线 →](07_end_to_end.ipynb)"
            ),
        ],
        lesson=6,
    ),
    "07_end_to_end.ipynb": notebook(
        """
        # 第 7 课：端到端预测管线

        目标：把窗口、特征、记忆、检索、候选、反思、基线和反馈串成闭环。
        """,
        [
            code(BOOTSTRAP),
            markdown(
                """
                ## 7.1 先看数据流

                ```text
                历史窗口 → 特征 → Top-K 记忆 → 多候选
                         → 物理反思 → 选择结果 → 与恒速基线比较
                         → 真值成熟后更新记忆置信度
                ```

                核心源码：[pipeline.py](../src/memcast_uav/pipeline.py)  
                文字讲解：[07_end_to_end.md](../tutorial/07_end_to_end.md)
                """
            ),
            markdown("## 7.2 运行 10 个离线测试样本"),
            code(
                """
                from memcast_uav.pipeline import run_demo

                result = run_demo(test_limit=10)
                result.to_dict()
                """
            ),
            markdown("## 7.3 分字段解释结果"),
            code(
                """
                print("样本数:", result.samples)
                print("MemCast式预测 MSE:", result.mse)
                print("恒速基线 MSE:", result.baseline_mse)
                print("记忆条目:", result.memory_entries)
                print("接受候选:", result.accepted_candidates)
                print("拒绝候选:", result.rejected_candidates)
                print("相对基线改进:", result.baseline_mse - result.mse)
                """
            ),
            markdown(
                """
                不要只看最终 MSE：如果复杂方法没有优于恒速基线，就不能只凭流程复杂度声称有效。
                本教学结果只验证代码链路，不等于复现论文指标。
                """
            ),
            markdown("## 7.4 分块练习：改变测试样本数"),
            code(
                """
                for test_limit in (1, 4, 10):
                    trial = run_demo(test_limit=test_limit)
                    print(
                        f"samples={trial.samples:2d}, "
                        f"mse={trial.mse:.6f}, baseline={trial.baseline_mse:.6f}"
                    )
                # TODO：解释为什么样本太少时，平均误差不稳定。
                """
            ),
            markdown("## 7.5 本课验收"),
            code(
                """
                import math
                import subprocess

                assert math.isfinite(result.mse)
                assert math.isfinite(result.baseline_mse)
                assert (
                    result.accepted_candidates + result.rejected_candidates
                    == 4 * result.samples
                )

                completed = subprocess.run(
                    [sys.executable, "-m", "pytest", "tests/test_pipeline.py", "-q"],
                    cwd=repo_root,
                    check=True,
                    text=True,
                    capture_output=True,
                )
                print(completed.stdout)
                """
            ),
            markdown(
                "[← 第 6 课](06_confidence.ipynb) · [教程目录](README.md) · "
                "[下一课：意图条件预测 →](08_intent.ipynb)"
            ),
        ],
        lesson=7,
    ),
    "08_intent.ipynb": notebook(
        """
        # 第 8 课：意图条件预测

        目标：让检索同时考虑轨迹相似性与当前任务/机动意图，并识别标签泄漏风险。
        """,
        [
            code(BOOTSTRAP),
            markdown(
                """
                ## 8.1 准备查询与记忆

                核心源码：[retrieval.py](../src/memcast_uav/retrieval.py)  
                文字讲解：[08_intent.md](../tutorial/08_intent.md)
                """
            ),
            code(
                """
                from memcast_uav.data import make_synthetic_flight, make_train_test_windows
                from memcast_uav.features import extract_motion_features
                from memcast_uav.memory import build_memory
                from memcast_uav.retrieval import RetrievalConfig, retrieve

                flight = make_synthetic_flight()
                train, test = make_train_test_windows(flight, split_index=504)
                memory = build_memory(train, limit=30)
                query = test[3]
                query_features = extract_motion_features(query.history, query.dt)
                print("查询意图:", query.intent)
                """
            ),
            markdown("## 8.2 封装意图权重实验"),
            code(
                """
                def retrieve_with_intent_weight(weight: float):
                    return retrieve(
                        query.history,
                        query_features,
                        query.intent,
                        memory,
                        RetrievalConfig(
                            alpha=0.5,
                            gamma=120.0,
                            top_k=3,
                            intent_weight=weight,
                        ),
                    )

                without_intent = retrieve_with_intent_weight(0.0)
                with_intent = retrieve_with_intent_weight(0.6)
                """
            ),
            markdown("## 8.3 比较 Top-3"),
            code(
                """
                def summarize(results):
                    return [
                        {
                            "id": item.entry.entry_id,
                            "intent": item.entry.intent,
                            "match": item.intent_match,
                            "score": round(item.final_score, 4),
                        }
                        for item in results
                    ]

                print("不使用意图:")
                for item in summarize(without_intent):
                    print(item)

                print("\\n提高意图权重:")
                for item in summarize(with_intent):
                    print(item)
                """
            ),
            markdown(
                """
                ## 8.4 意图来源与泄漏

                - 任务规划：巡检、配送、返航，通常在预测时可见；
                - 控制指令：左转、爬升、悬停，通常在预测时可见；
                - 在线识别：只能根据已经观测到的历史估计；
                - **禁止**读取真实未来轨迹后再反推当前意图。
                """
            ),
            markdown("## 8.5 分块练习：设计层级意图"),
            code(
                """
                hierarchical_intent = {
                    "mission": "inspection",
                    "maneuver": "turn_right",
                }
                mission_weight = 0.2
                maneuver_weight = 0.6
                print(hierarchical_intent)
                print("TODO：设计 mission_match 和 maneuver_match 的组合分数。")
                """
            ),
            markdown("## 8.6 本课验收"),
            code(
                """
                assert len(without_intent) == 3
                assert len(with_intent) == 3

                import subprocess

                completed = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pytest",
                        "tests/test_retrieval.py",
                        "tests/test_pipeline.py",
                        "-q",
                    ],
                    cwd=repo_root,
                    check=True,
                    text=True,
                    capture_output=True,
                )
                print(completed.stdout)
                """
            ),
            markdown(
                """
                ## 下一阶段

                先阅读 [真实无人机数据迁移指南](../docs/03_uav_dataset_adapter.md)，把 DJI Matrice 100
                或 NeuroBEM/UZH-FPV 转换为统一窗口，再考虑接入 Qwen。

                [← 第 7 课](07_end_to_end.ipynb) · [教程目录](README.md) ·
                [真实无人机数据迁移 →](../docs/03_uav_dataset_adapter.md)
                """
            ),
        ],
        lesson=8,
    ),
}


def main() -> None:
    OUTPUT.mkdir(exist_ok=True)
    for filename, document in NOTEBOOKS.items():
        path = OUTPUT / filename
        nbf.write(document, path)
        print(f"generated {path.relative_to(ROOT)} ({len(document.cells)} cells)")


if __name__ == "__main__":
    main()
