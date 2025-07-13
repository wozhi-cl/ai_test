#!/usr/bin/env python3
"""
测试修复后的页面解析功能
"""

import asyncio
import json
from core.page_parser import PageParser

async def test_page_parsing():
    """测试页面解析功能"""
    print("开始测试页面解析功能...")

    # 创建页面解析器
    parser = PageParser()

    # 测试URL - 使用一个简单的表单页面
    test_url = "https://www.tutorialspoint.com/selenium/practice/selenium_automation_practice.php"

    try:
        print(f"正在解析页面: {test_url}")

        # 解析页面
        page_structure = await parser.parse_page_from_url(test_url, headless=True)

        print(f"解析完成！页面标题: {page_structure.title}")
        print(f"解析到的节点数量: {len(page_structure.nodes)}")

        # 显示前几个节点的信息
        print("\n前5个节点的信息:")
        for i, node in enumerate(page_structure.nodes[:5]):
            print(f"节点 {i+1}:")
            print(f"  ID: {node.id}")
            print(f"  类型: {node.type.value}")
            print(f"  标签: {node.tag_name}")
            print(f"  文本: {node.text_content[:50] if node.text_content else 'N/A'}...")
            print(f"  可交互: {node.is_interactive}")
            print(f"  可见: {node.is_visible}")
            print(f"  XPath: {node.xpath}")
            print()

        # 统计节点类型
        type_counts = {}
        for node in page_structure.nodes:
            node_type = node.type.value
            type_counts[node_type] = type_counts.get(node_type, 0) + 1

        print("节点类型统计:")
        for node_type, count in type_counts.items():
            print(f"  {node_type}: {count}")

        # 检查是否有可交互的节点
        interactive_nodes = [node for node in page_structure.nodes if node.is_interactive]
        print(f"\n可交互节点数量: {len(interactive_nodes)}")

        if interactive_nodes:
            print("可交互节点示例:")
            for i, node in enumerate(interactive_nodes[:3]):
                print(f"  {i+1}. {node.tag_name} - {node.text_content[:30] if node.text_content else 'N/A'}...")

        # 保存到文件并检查文件大小
        filename = f"{page_structure.id}.json"
        filepath = f"data/page_nodes/{filename}"

        # 检查文件大小
        import os
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"\n保存的文件大小: {file_size} 字节")

            if file_size > 1000000:  # 1MB
                print("警告: 文件过大，可能包含过多不必要的数据")
            else:
                print("文件大小正常")

        print("\n测试完成！")

    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_page_parsing())
