# nop-mcp

一个空操作的 MCP (Model Context Protocol) 服务器，专门设计为不实现任何工具的占位符服务器。

## 功能

- 实现完整的 MCP 服务器协议
- `list_tools` 接口返回空工具列表
- 专用于占位、测试或需要无功能MCP服务器的特殊场景

## 使用场景

- **占位符**：在系统配置中需要MCP服务器但不需要实际功能时
- **测试环境**：测试MCP客户端连接和基础协议功能
- **开发调试**：验证MCP协议实现而不受具体工具干扰
- **兼容性测试**：确保MCP客户端能正确处理无工具的服务器

## 安装

### 从 PyPI 安装（推荐）

```bash
pip install nop-mcp
```

### 本地开发安装

```bash
# 激活虚拟环境
source .venv/bin/activate

# 依赖已预装，直接使用即可
```

## 使用方法

### 直接运行

```bash
# 从PyPI安装后
nop-mcp

# 或使用模块方式
python -m nop_mcp.server

# 本地开发时使用便捷脚本
python run_server.py
```

### 在 Claude Desktop 中配置

在 `~/Library/Application Support/Claude/claude_desktop_config.json` 中添加：

```json
{
    "mcpServers": {
        "nop-mcp": {
            "command": "nop-mcp"
        }
    }
}
```

或者如果是本地开发版本：

```json
{
    "mcpServers": {
        "nop-mcp": {
            "command": "python",
            "args": [
                "-m", 
                "nop_mcp.server"
            ],
            "cwd": "/path/to/your/nop-mcp"
        }
    }
}
```

## 开发

```bash
# 激活环境
source .venv/bin/activate

# 运行测试
python -m pytest tests/ -v

# 代码格式化
python -m black .

# 代码检查
python -m flake8 nop_mcp tests run_server.py --max-line-length=88
```

## 发布到 PyPI

项目包含完整的 PyPI 发布脚本：

```bash
# 快速发布到测试PyPI（推荐首次使用）
./scripts/quick-start.sh

# 或分步操作：
# 1. 构建包
./scripts/build.sh

# 2. 上传到测试PyPI
./scripts/upload-test.sh

# 3. 上传到正式PyPI
./scripts/upload.sh

# 清理构建文件
./scripts/clean.sh
```

详细发布指南请参阅 [PUBLISH.md](PUBLISH.md)。

## 项目结构

```
nop-mcp/
├── nop_mcp/              # 主包
│   ├── __init__.py       # 包初始化
│   └── server.py         # 空操作MCP服务器实现
├── tests/                # 测试代码
│   ├── __init__.py
│   └── test_server.py    # 服务器测试
├── scripts/              # 发布脚本
│   ├── build.sh          # 构建脚本
│   ├── upload.sh         # 上传到PyPI
│   ├── upload-test.sh    # 上传到测试PyPI
│   ├── clean.sh          # 清理脚本
│   └── quick-start.sh    # 快速开始脚本
├── .venv/                # 虚拟环境（Python 3.13）
├── .gitignore            # Git忽略文件
├── LICENSE               # MIT许可证
├── PUBLISH.md            # 发布指南
├── pyproject.toml        # 项目配置
├── README.md             # 项目说明
├── run_server.py         # 便捷启动脚本
└── USAGE.md              # 详细使用说明
```

## 验证

项目已完全配置并验证：

- ✅ 实现完整的MCP协议
- ✅ 返回空工具列表
- ✅ 支持标准stdio传输
- ✅ 所有测试通过
- ✅ 代码质量检查通过
- ✅ PyPI发布就绪 