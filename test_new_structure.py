#!/usr/bin/env python3
"""
测试新的测试用例数据结构
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.page_parser import PageParser
from core.test_generator import TestGenerator
from models.test_case import TestType, TestPriority, TestData, TestViewpoint, TestStrategy
from models.page_node import PageNode, NodeType
import uuid

async def test_new_structure():
    """测试新的测试用例数据结构"""
    print("🧪 测试新的测试用例数据结构...")

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

        # 4. 生成测试用例（一次性生成所有测试观点）
        print("\n📋 生成测试用例...")
        test_case = test_generator.generate_test_case_from_nodes(
            structure_id=structure_id,
            node_ids=[node.id for node in interactive_nodes[:2]],  # 选择前2个节点
            test_name="新结构测试用例",
            test_type=TestType.FUNCTIONAL,
            priority=TestPriority.MEDIUM,
            description="测试新的数据结构"
        )

        print(f"   ✅ 测试用例生成成功!")
        print(f"   📝 测试用例名称: {test_case.name}")
        print(f"   🔢 测试观点数量: {len(test_case.viewpoints)}")
        print(f"   📊 测试数据总数: {test_case.get_test_data_count()}")

        # 5. 显示测试观点详情
        print("\n📋 测试观点详情:")
        for i, viewpoint in enumerate(test_case.viewpoints):
            print(f"   观点 {i+1}: {viewpoint.name}")
            print(f"     策略: {viewpoint.strategy.value}")
            print(f"     描述: {viewpoint.description}")
            print(f"     目标节点: {viewpoint.target_node.tag_name}")
            print(f"     测试数据数: {len(viewpoint.test_data_list)}")

            # 显示测试数据详情
            for j, test_data in enumerate(viewpoint.test_data_list[:3]):  # 只显示前3个
                print(f"       数据 {j+1}: {test_data.description}")
                print(f"         输入值: {test_data.input_value}")
                print(f"         预期值: {test_data.expected_value}")
                print(f"         断言函数: {test_data.assertion_functions}")

        # 6. 保存测试用例
        test_generator.save_test_case(test_case)
        print(f"\n   💾 测试用例保存成功!")

        # 7. 验证文件完整性
        import os
        test_case_file = f"data/test_cases/{test_case.id}.json"
        if os.path.exists(test_case_file):
            file_size = os.path.getsize(test_case_file)
            print(f"   📄 文件大小: {file_size} 字节")

            # 验证JSON格式
            with open(test_case_file, 'r', encoding='utf-8') as f:
                import json
                data = json.load(f)
                print(f"   ✅ JSON格式验证通过")

                # 验证数据结构
                assert 'viewpoints' in data, "缺少viewpoints字段"
                assert len(data['viewpoints']) > 0, "viewpoints为空"

                for viewpoint in data['viewpoints']:
                    assert 'test_data_list' in viewpoint, "缺少test_data_list字段"
                    assert len(viewpoint['test_data_list']) > 0, "test_data_list为空"

                    for test_data in viewpoint['test_data_list']:
                        assert 'input_value' in test_data, "缺少input_value字段"
                        assert 'expected_value' in test_data, "缺少expected_value字段"
                        assert 'assertion_functions' in test_data, "缺少assertion_functions字段"

                print(f"   ✅ 数据结构验证通过")

        # 8. 测试重新加载
        loaded_test_case = test_generator.load_test_case(test_case.id)
        if loaded_test_case:
            print(f"   ✅ 测试用例重新加载成功")
            print(f"   📊 重新加载后测试观点数: {len(loaded_test_case.viewpoints)}")
            print(f"   📊 重新加载后测试数据数: {loaded_test_case.get_test_data_count()}")

        # 9. 测试列表功能
        test_cases_data = test_generator.list_test_cases()
        print(f"\n📋 测试用例列表:")
        print(f"   表头: {test_cases_data['headers']}")
        print(f"   行数: {len(test_cases_data['rows'])}")

        if test_cases_data['rows']:
            latest_test_case = test_cases_data['rows'][0]
            print(f"   最新测试用例: {latest_test_case[1]} (观点数: {latest_test_case[6]}, 数据数: {latest_test_case[7]})")

        print("\n🎉 新数据结构测试通过！")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_new_structure())
