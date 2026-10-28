# 基于风格迁移的西夏文化衍生品开发系统

面向西夏文化视觉元素再创作与文创衍生品设计的桌面应用。项目将图像风格迁移、素材管理与衍生品设计工作流结合，支持从创意到视觉方案的探索。

## 技术栈

- Python
- PyQt 桌面界面
- SQLite 本地数据存储
- 图像处理与风格迁移

## 快速开始

1. 安装 Python 3.10 或更高版本。
2. 在项目根目录创建并启用虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. 安装依赖并启动应用：

```powershell
pip install -r requirements.txt
python main.py
```

## 项目结构

- `app/`：应用业务逻辑、界面与页面模块
- `assets/`：可随仓库分发的界面与示例资源
- `data/`：本地数据与运行时数据目录
- `main.py`：应用启动入口
- `requirements.txt`：Python 依赖清单

## 团队协作

请先阅读 [团队协作规范](docs/TEAM_WORKFLOW.md) 与 [贡献指南](CONTRIBUTING.md)。

- 不直接向 `main` 分支提交功能代码。
- 每项工作从 `feat/`、`fix/` 或 `docs/` 前缀的新分支开始。
- 通过 Pull Request 合并，并至少请一位组员审阅。
- 使用 Issue 跟踪需求、缺陷和任务分工。

## 安全与素材

- 不提交访问令牌、账户信息、数据库密码或本地隐私数据。
- 将本地配置保存在未跟踪文件中；提交前检查 `.gitignore`。
- 第三方 SDK、图像与文化素材应遵守各自的授权条款。

## 许可

当前仓库未附带开源许可证。未经项目维护者书面许可，请勿将项目代码或素材用于仓库声明范围以外的用途。