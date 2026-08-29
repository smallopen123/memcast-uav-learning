# Data directory

本仓库不分发第三方无人机数据，也不把大型数据文件提交到Git。

建议本地目录：

```text
data/
├─ raw/          # 原始下载文件，已被.gitignore忽略
├─ processed/    # 统一坐标和频率后的文件，已被.gitignore忽略
└─ README.md
```

使用任何公开数据集前，请单独核对其许可证和引用要求。提交适配器时只提交转换代码、字段说明和小型匿名测试夹具。

