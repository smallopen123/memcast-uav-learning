# 第 4 课：经验记忆的结构与构建

> 可逐格运行版本：[打开第 4 课 Notebook](../notebooks/04_memory.ipynb)

目标：理解一条经验为什么同时保存历史、未来、特征、策略、意图和置信度。

## 4.1 按顺序打开代码

1. [课程入口：lesson_04_memory.py](../lessons/lesson_04_memory.py)
2. [核心实现：memory.py](../src/memcast_uav/memory.py)
3. [记忆如何被检索：retrieval.py](../src/memcast_uav/retrieval.py)
4. [检索测试：test_retrieval.py](../tests/test_retrieval.py)

在 `memory.py` 中依次阅读：

`MemoryEntry` → `relative_history` → `future_displacement` → `ExperienceMemory` → `build_memory()`。

## 4.2 运行课程

```powershell
python -m lessons.lesson_04_memory
```

确认输出中包含唯一 ID、历史/未来形状、意图、策略摘要、初始置信度以及未来相对位移。

## 4.3 理解为什么保存相对位移

预测时使用：

```python
candidate = current_history[-1] + memory_entry.future_displacement
```

因此，发生在不同绝对位置的相似机动仍可被复用。记忆保存原始历史用于审计，保存特征用于快速比较，保存未来位移用于生成候选。

## 4.4 亲手设计环境上下文

先不要立刻改代码，在纸上或笔记中设计字段：

```python
environment = {
    "wind_enu_mps": [east, north, up],
    "obstacle_density": 0.0,
    "weather": "clear",
}
```

回答：

1. 哪些字段来自预测时可见的传感器？
2. 哪些字段可能误用未来信息？
3. 连续字段怎样归一化，离散字段怎样比较？

然后尝试给 `MemoryEntry` 增加一个带默认值的 `context` 字段，并在 `build_memory()` 中写入默认上下文。修改后运行全量测试。

## 4.5 验收测试

```powershell
python -m pytest tests/test_retrieval.py tests/test_pipeline.py -q
```

通过标准：现有检索和管线仍通过；你能逐一解释 `MemoryEntry` 的字段用途。

[← 第 3 课](03_retrieval.md) | [教程目录](README.md) | [下一课：物理约束反思 →](05_reflection.md)
