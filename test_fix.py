#!/usr/bin/env python3
"""
测试页面解析修复
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.playwright_utils import PlaywrightUtils


async def test_page_parsing():
    """测试页面解析"""
    print("🧪 测试页面解析修复...")

    playwright_utils = PlaywrightUtils()

    try:
        # 启动浏览器
        print("启动浏览器...")
        await playwright_utils.start_browser(headless=True)

        # 测试解析一个简单的页面
        print("解析测试页面...")
        page_structure = await playwright_utils.parse_page_structure("https://www.baidu.com")

        print(f"✅ 页面解析成功!")
        print(f"   标题: {page_structure.title}")
        print(f"   节点数量: {len(page_structure.nodes)}")

        # 显示节点类型统计
        node_stats = {}
        for node in page_structure.nodes:
            node_type = node.type.value
            node_stats[node_type] = node_stats.get(node_type, 0) + 1

        print("   节点类型统计:")
        for node_type, count in sorted(node_stats.items()):
            print(f"     - {node_type}: {count}")

        return True

    except Exception as e:
        print(f"❌ 页面解析失败: {str(e)}")
        return False

    finally:
        # 关闭浏览器
        await playwright_utils.close_browser()


async def main():
    """主函数"""
    print("🔧 页面解析修复测试")
    print("=" * 50)

    success = await test_page_parsing()

    if success:
        print("\n🎉 修复测试通过！页面解析功能已正常工作。")
    else:
        print("\n❌ 修复测试失败，需要进一步调试。")


if __name__ == "__main__":
    asyncio.run(main())
