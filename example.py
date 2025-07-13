#!/usr/bin/env python3
"""
自动化测试工具示例脚本
演示如何使用各个模块的功能
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.page_parser import PageParser
from core.test_generator import TestGenerator
from core.test_runner import TestRunner
from core.report_generator import ReportGenerator
from models.test_case import TestType, TestPriority


async def example_workflow():
    """示例工作流程"""
    print("🚀 开始自动化测试工具示例工作流程...")

    # 1. 页面解析
    print("\n1️⃣ 页面解析阶段")
    page_parser = PageParser()

    # 解析一个示例页面（使用百度首页作为示例）
    try:
        print("正在解析百度首页...")
        page_structure = await page_parser.parse_page_from_url("https://www.baidu.com", headless=True)
        print(f"✅ 页面解析成功: {page_structure.title}")
        print(f"   节点数量: {len(page_structure.nodes)}")

        # 显示节点统计
        node_stats = {}
        for node in page_structure.nodes:
            node_type = node.type.value
            node_stats[node_type] = node_stats.get(node_type, 0) + 1

        print("   节点类型统计:")
        for node_type, count in sorted(node_stats.items()):
            print(f"     - {node_type}: {count}")

    except Exception as e:
        print(f"❌ 页面解析失败: {e}")
        return

    # 2. 测试用例生成
    print("\n2️⃣ 测试用例生成阶段")
    test_generator = TestGenerator()

    try:
        # 获取可交互的节点
        interactive_nodes = page_parser.get_interactive_nodes(page_structure.id)
        print(f"找到 {len(interactive_nodes)} 个可交互节点")

        if interactive_nodes:
            # 生成测试用例
            test_case = test_generator.generate_test_case_from_nodes(
                structure_id=page_structure.id,
                node_ids=[node.id for node in interactive_nodes[:3]],  # 选择前3个节点
                test_name="百度首页功能测试",
                test_type=TestType.FUNCTIONAL,
                priority=TestPriority.HIGH,
                description="测试百度首页的基本功能"
            )

            # 保存测试用例
            test_generator.save_test_case(test_case)
            print(f"✅ 测试用例生成成功: {test_case.name}")
            print(f"   步骤数量: {len(test_case.steps)}")

            # 显示测试步骤
            print("   测试步骤:")
            for step in test_case.steps:
                print(f"     - 步骤 {step.step_number}: {step.action}")
                if step.target_node:
                    print(f"       目标: {step.target_node.tag_name}")
                if step.input_data:
                    print(f"       输入: {step.input_data}")

    except Exception as e:
        print(f"❌ 测试用例生成失败: {e}")
        return

    # 3. 测试执行
    print("\n3️⃣ 测试执行阶段")
    test_runner = TestRunner()

    try:
        print("正在运行测试...")
        execution = await test_runner.run_test_case(test_case.id, headless=True)

        print(f"✅ 测试执行完成: {execution.test_case_name}")
        print(f"   执行状态: {execution.status.value}")
        print(f"   总步骤: {execution.total_steps}")
        print(f"   通过步骤: {execution.passed_steps}")
        print(f"   失败步骤: {execution.failed_steps}")
        print(f"   执行时长: {execution.duration:.2f} 秒")

        if execution.error_message:
            print(f"   错误信息: {execution.error_message}")

    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        return

    # 4. 报告生成
    print("\n4️⃣ 报告生成阶段")
    report_generator = ReportGenerator()

    try:
        # 生成HTML报告
        report_path = report_generator.generate_html_report(execution.id)
        print(f"✅ HTML报告生成成功: {report_path}")

        # 生成JSON报告
        json_report_path = report_generator.generate_json_report(execution.id)
        print(f"✅ JSON报告生成成功: {json_report_path}")

    except Exception as e:
        print(f"❌ 报告生成失败: {e}")
        return

    print("\n🎉 示例工作流程完成！")
    print("📊 生成的文件:")
    print(f"   - 页面结构: data/page_nodes/{page_structure.id}.json")
    print(f"   - 测试用例: data/test_cases/{test_case.id}.json")
    print(f"   - 执行记录: data/reports/{execution.id}.json")
    print(f"   - HTML报告: {report_path}")
    print(f"   - JSON报告: {json_report_path}")


def show_statistics():
    """显示统计信息"""
    print("\n📈 统计信息:")

    # 页面结构统计
    page_parser = PageParser()
    structures = page_parser.list_page_structures()
    print(f"   页面结构数量: {len(structures)}")

    # 测试用例统计
    test_generator = TestGenerator()
    test_cases = test_generator.list_test_cases()
    print(f"   测试用例数量: {len(test_cases)}")

    # 执行记录统计
    test_runner = TestRunner()
    executions = test_runner.list_executions()
    stats = test_runner.get_execution_statistics()
    print(f"   执行记录数量: {len(executions)}")
    print(f"   执行成功率: {stats.get('execution_success_rate', 0):.1f}%")


def main():
    """主函数"""
    print("🤖 自动化测试工具示例")
    print("=" * 50)

    # 检查数据目录
    if not os.path.exists("data"):
        print("❌ 数据目录不存在，请先运行主应用")
        return

    # 运行示例工作流程
    asyncio.run(example_workflow())

    # 显示统计信息
    show_statistics()


if __name__ == "__main__":
    main()


# https://www.tutorialspoint.com/selenium/practice/selenium_automation_practice.php

