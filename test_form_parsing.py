#!/usr/bin/env python3
"""
测试表单解析功能
"""

import asyncio
from core.page_parser import PageParser
from models.page_node import NodeType

async def test_form_parsing():
    """测试表单解析功能"""

    print("🧪 测试表单解析功能...")

    # 创建页面解析器
    parser = PageParser()

    # 测试URL（包含表单的页面）
    test_url = "https://www.tutorialspoint.com/selenium/practice/selenium_automation_practice.php"

    try:
        print(f"1. 解析表单页面: {test_url}")

        # 解析表单
        form_structure = await parser.parse_forms_from_url(test_url, headless=True)

        print(f"   ✅ 表单解析成功")
        print(f"   📊 页面标题: {form_structure.title}")
        print(f"   🔗 URL: {form_structure.url}")
        print(f"   📝 节点数量: {len(form_structure.nodes)}")

        # 统计节点类型
        node_types = {}
        for node in form_structure.nodes:
            node_type = node.type.value
            node_types[node_type] = node_types.get(node_type, 0) + 1

        print("   📈 节点类型统计:")
        for node_type, count in node_types.items():
            print(f"      {node_type}: {count}")

        # 获取表单字段
        form_fields = parser.get_form_fields(form_structure.id)
        print(f"   📋 表单字段数量: {len(form_fields)}")

        # 获取表单按钮
        form_buttons = parser.get_form_buttons(form_structure.id)
        print(f"   🔘 表单按钮数量: {len(form_buttons)}")

        # 显示一些示例字段
        if form_fields:
            print("   📝 示例字段:")
            for i, field in enumerate(form_fields[:3]):
                print(f"      {i+1}. {field['name']} ({field['type']}) - {field['placeholder']}")

        if form_buttons:
            print("   🔘 示例按钮:")
            for i, button in enumerate(form_buttons[:3]):
                print(f"      {i+1}. {button['text']} ({button['type']})")

        print("\n✅ 表单解析测试通过！")

    except Exception as e:
        print(f"❌ 表单解析测试失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_form_parsing())
