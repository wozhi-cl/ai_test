#!/usr/bin/env python3
"""
自动化测试工具启动脚本
提供多种启动方式
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """检查依赖"""
    try:
        import playwright
        import nicegui
        import pydantic
        import jinja2
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def install_playwright_browsers():
    """安装Playwright浏览器"""
    try:
        print("🔧 正在安装Playwright浏览器...")
        subprocess.run(["playwright", "install"], check=True)
        print("✅ Playwright浏览器安装完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ Playwright浏览器安装失败")
        return False
    except FileNotFoundError:
        print("❌ 未找到playwright命令，请确保已安装playwright")
        return False

def run_web_interface():
    """运行Web界面"""
    print("🌐 启动Web界面...")
    os.system("python main.py")

def run_example():
    """运行示例"""
    print("📝 运行示例脚本...")
    os.system("python example.py")

def show_menu():
    """显示菜单"""
    print("🤖 自动化测试工具")
    print("=" * 50)
    print("请选择操作:")
    print("1. 启动Web界面")
    print("2. 运行示例")
    print("3. 安装Playwright浏览器")
    print("4. 检查依赖")
    print("5. 退出")
    print("=" * 50)

def main():
    """主函数"""
    while True:
        show_menu()
        choice = input("请输入选择 (1-5): ").strip()

        if choice == "1":
            if check_requirements():
                run_web_interface()
            else:
                print("请先安装依赖包")
        elif choice == "2":
            if check_requirements():
                run_example()
            else:
                print("请先安装依赖包")
        elif choice == "3":
            install_playwright_browsers()
        elif choice == "4":
            if check_requirements():
                print("✅ 所有依赖包已安装")
            else:
                print("❌ 缺少依赖包")
        elif choice == "5":
            print("👋 再见！")
            break
        else:
            print("❌ 无效选择，请重新输入")

        input("\n按回车键继续...")

if __name__ == "__main__":
    main()
