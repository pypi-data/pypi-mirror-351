#!/usr/bin/env python3
"""
nop-mcp server: A no-operation MCP server that provides empty tools list.

This server implements the MCP protocol but provides no actual tools,
making it useful for testing, placeholders, or special purposes.
"""

import asyncio
import logging
from mcp.server.fastmcp import FastMCP


# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nop-mcp")

# 初始化 FastMCP 服务器
mcp = FastMCP("nop-mcp")


async def main():
    """主函数：启动 MCP 服务器"""
    logger.info("Starting nop-mcp server...")
    logger.info("This server provides no tools - it's a no-operation MCP server")

    # 运行服务器（使用 stdio 传输）
    await mcp.run(transport="stdio")


def cli_main():
    """命令行入口点：用于 PyPI 安装后的命令行工具"""
    logger.info("Starting nop-mcp server...")
    logger.info("This server provides no tools - it's a no-operation MCP server")
    
    # 直接运行 FastMCP，它会内部处理事件循环
    mcp.run(transport="stdio")


if __name__ == "__main__":
    # 运行服务器
    asyncio.run(main())
