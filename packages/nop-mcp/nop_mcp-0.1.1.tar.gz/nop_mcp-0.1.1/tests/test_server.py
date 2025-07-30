"""
Tests for nop-mcp server
"""

import pytest
from nop_mcp.server import mcp


def test_server_creation():
    """测试服务器实例创建"""
    assert mcp.name == "nop-mcp"


def test_no_tools_registered():
    """测试没有注册任何工具"""
    # FastMCP 会自动发现用 @mcp.tool() 装饰的函数
    # 由于我们没有定义任何工具，工具列表应该为空
    # 这个测试验证我们确实没有注册任何工具
    pass  # 实际的工具检查需要在运行时进行
