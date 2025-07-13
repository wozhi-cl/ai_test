#!/usr/bin/env python3
"""
测试生成测试用例功能修复
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.page_parser import PageParser
from core.test_generator import TestGenerator
from models.test_case import TestType, TestPriority

async def test_test_case_generation():
    """测试测试用例生成功能"""
    print("🧪 测试测试用例生成功能...")

    # 创建页面解析器和测试生成器
    page_parser = PageParser()
    test_generator = TestGenerator()

    try:
        # 1. 检查是否有现有的页面结构
        structures_data = page_parser.list_page_structures()
        print(f"现有页面结构数量: {len(structures_data['rows'])}")

        if not structures_data['rows']:
            print("❌ 没有找到页面结构，请先解析页面")
            return False

        # 2. 选择第一个页面结构进行测试
        structure_id = structures_data['rows'][0][0]  # 获取第一个结构的ID
        structure_title = structures_data['rows'][0][1]  # 获取第一个结构的标题
        print(f"使用页面结构: {structure_title} (ID: {structure_id})")

        # 3. 获取可交互的节点
        interactive_nodes = page_parser.get_interactive_nodes(structure_id)
        print(f"可交互节点数量: {len(interactive_nodes)}")

        if not interactive_nodes:
            print("❌ 没有找到可交互的节点")
            return False

        # 4. 生成测试用例
        print("生成测试用例...")
        test_case = test_generator.generate_test_case_from_nodes(
            structure_id=structure_id,
            node_ids=[node.id for node in interactive_nodes[:3]],  # 选择前3个节点
            test_name="功能测试用例",
            test_type=TestType.FUNCTIONAL,
            priority=TestPriority.MEDIUM,
            description="测试生成功能修复后的测试用例"
        )

        print(f"✅ 测试用例生成成功!")
        print(f"   测试用例ID: {test_case.id}")
        print(f"   测试用例名称: {test_case.name}")
        print(f"   步骤数量: {len(test_case.steps)}")

        # 5. 保存测试用例
        print("保存测试用例...")
        test_generator.save_test_case(test_case)
        print("✅ 测试用例保存成功!")

        # 6. 验证保存的测试用例
        print("验证保存的测试用例...")
        loaded_test_case = test_generator.load_test_case(test_case.id)
        if loaded_test_case:
            print(f"✅ 测试用例加载成功: {loaded_test_case.name}")
            print(f"   步骤数量: {len(loaded_test_case.steps)}")

            # 显示步骤详情
            for i, step in enumerate(loaded_test_case.steps):
                print(f"   步骤 {i+1}: {step.action}")
                if step.target_node:
                    print(f"     目标: {step.target_node.tag_name}")
                if step.input_data:
                    print(f"     输入: {step.input_data}")
        else:
            print("❌ 测试用例加载失败")
            return False

        # 7. 检查文件完整性
        import os
        test_case_file = f"data/test_cases/{test_case.id}.json"
        if os.path.exists(test_case_file):
            file_size = os.path.getsize(test_case_file)
            print(f"✅ 测试用例文件存在，大小: {file_size} 字节")

            # 尝试读取文件内容验证JSON格式
            with open(test_case_file, 'r', encoding='utf-8') as f:
                import json
                data = json.load(f)
                print(f"✅ JSON格式验证通过")
                print(f"   文件包含 {len(data.get('steps', []))} 个步骤")
        else:
            print("❌ 测试用例文件不存在")
            return False

        print("\n🎉 测试用例生成功能测试通过！")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_test_case_generation())
