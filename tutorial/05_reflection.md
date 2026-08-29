# 第 5 课：物理约束反思

目标：对候选轨迹执行“检查—修正—复查”，避免输出明显违反飞行规律的结果。

## 5.1 按顺序打开代码

1. [课程入口：lesson_05_reflection.py](../lessons/lesson_05_reflection.py)
2. [核心实现：reflection.py](../src/memcast_uav/reflection.py)
3. [对应测试：test_reflection.py](../tests/test_reflection.py)

在 `reflection.py` 中按此顺序读：

`FlightConstraints` → `trajectory_metrics()` → `check_constraints()` → `_project_once()` → `reflect_candidate()`。

## 5.2 理解反思循环

```text
候选轨迹
  ↓
计算高度、速度、加速度、转弯率
  ↓
是否违反约束？ ── 否 ──> 接受
  │
  是
  ↓
投影修正，再次检查 ── 多轮仍失败 ──> 拒绝
```

本仓库使用确定性数值修正，不调用大模型，因此结果可重复且没有 API 费用。

## 5.3 运行课程

```powershell
python -m lessons.lesson_05_reflection
```

课程会故意制造高速爬升且超过高度上限的轨迹。你应看到“修正前违反”非空，而“修正后违反”为空。

## 5.4 亲手修改约束

在 [lesson_05_reflection.py](../lessons/lesson_05_reflection.py) 中依次尝试：

```python
FlightConstraints(max_speed=6.0, max_acceleration=1.5, max_altitude=120.0)
FlightConstraints(max_speed=8.0, max_acceleration=0.5, max_altitude=120.0)
```

每次只修改一个约束，记录修正轮数和最终指标。解释为什么更严格的约束可能需要更多轮修正。

进阶任务：设计圆形禁飞区 `(center_x, center_y, radius)`。先只实现检查，再考虑修正；空间几何约束不能仅靠数值上下界表达。

## 5.5 验收测试

```powershell
python -m pytest tests/test_reflection.py -q
```

通过标准：非法候选修正后不再违反约束；你能解释“检查函数”和“修正函数”为何必须分开。

[← 第 4 课](04_memory.md) | [教程目录](README.md) | [下一课：因果置信度 →](06_confidence.md)
