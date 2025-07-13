#!/usr/bin/env python3
"""
自动化测试工具主应用入口
基于Python Playwright和NiceGUI的自动化测试工具
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from nicegui import ui, app
from ui.main_ui import MainUI


def create_app():
    """创建应用"""
    # 设置应用配置
    app.title = "自动化测试工具"
    app.description = "基于Python Playwright和NiceGUI的自动化测试工具"

    # 创建主界面
    main_ui = MainUI()
    main_ui.create_main_interface()

    return app


def main():
    """主函数"""
    print("🤖 启动自动化测试工具...")
    print("📝 功能特性:")
    print("   - 页面解析: 运行Playwright录制的预处理脚本，解析页面生成节点数据")
    print("   - 测试用例生成: 基于节点数据生成测试用例")
    print("   - 测试数据生成: 生成测试数据、预期值和断言函数")
    print("   - 流程管理: 支持拖拽调整测试流程顺序")
    print("   - 测试执行: 运行自动化测试并生成报告")
    print("   - 数据管理: 支持各环节数据的增删改查")
    print()

    # 检查依赖
    check_dependencies()

    # 创建数据目录
    create_data_directories()

    # 启动应用
    app = create_app()

    # 启动NiceGUI服务器
    ui.run(
        title="自动化测试工具",
        port=8080,
        reload=False,
        show=True,
        favicon="🤖"
    )


def check_dependencies():
    """检查依赖"""
    try:
        import playwright
        import nicegui
        import pydantic
        import jinja2
        print("✅ 所有依赖包已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("请运行: pip install -r requirements.txt")
        sys.exit(1)


def create_data_directories():
    """创建数据目录"""
    directories = [
        "data",
        "data/page_nodes",
        "data/test_cases",
        "data/reports",
        "data/screenshots"
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    print("✅ 数据目录已创建")


if __name__ == "__main__":
    main()
