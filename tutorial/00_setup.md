# 第 0 步：安装并验证环境

> 可逐格运行版本：[打开第 0 步 Notebook](../notebooks/00_setup.ipynb)

本步只解决一件事：让课程代码可以从仓库根目录正常导入并运行。

## 0.1 打开仓库根目录

下载仓库后，在 PowerShell 进入包含 `pyproject.toml` 的目录。用下面命令确认：

```powershell
Get-ChildItem pyproject.toml
```

如果找不到该文件，说明当前目录不对。

## 0.2 创建隔离环境

```powershell
python -m venv .venv
.venv/Scripts/Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

`-e` 表示可编辑安装：之后修改 `src/memcast_uav/`，无需重新安装。

如果 PowerShell 阻止激活脚本，可以先在当前窗口执行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv/Scripts/Activate.ps1
```

它只影响当前 PowerShell 窗口。

## 0.3 验证导入

```powershell
python -c "import memcast_uav; print('memcast_uav import OK')"
```

应看到：

```text
memcast_uav import OK
```

如果出现 `ModuleNotFoundError`，不要继续；确认虚拟环境已激活，并重新执行安装命令。

## 0.4 运行基线测试

```powershell
python -m pytest -q
```

应看到 `10 passed`。这表示起点代码正常，以后每次修改都可以与这个结果比较。

## 本步完成检查

- [ ] 当前目录能看到 `pyproject.toml`
- [ ] 命令行前面出现 `(.venv)`
- [ ] 可以导入 `memcast_uav`
- [ ] 10 项测试全部通过

[← 教程目录](README.md) | [下一课：时间窗口 →](01_windowing.md)
