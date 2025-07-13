import asyncio
import os
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from models.test_case import TestCase, TestViewpoint, TestData, TestType, TestPriority, TestStrategy, TestStatus
from models.test_data import TestExecution, TestStepResult, TestStatus as ExecutionTestStatus, AssertionResult
from core.test_generator import TestGenerator
from utils.playwright_utils import PlaywrightUtils
from utils.assertion_utils import AssertionUtils


class TestRunner:
    """测试运行器"""

    def __init__(self, data_dir: str = "data/reports"):
        self.data_dir = data_dir
        self.test_generator = TestGenerator()
        self.playwright_utils = PlaywrightUtils()
        os.makedirs(data_dir, exist_ok=True)

    async def run_test_case(self, test_case_id: str, headless: bool = True) -> TestExecution:
        """运行单个测试用例"""
        # 加载测试用例
        test_case = self.test_generator.load_test_case(test_case_id)
        if not test_case:
            raise Exception("测试用例不存在")

        # 创建执行记录
        execution = TestExecution(
            id=str(uuid.uuid4()),
            test_case_id=test_case_id,
            test_case_name=test_case.name,
            status=TestStatus.RUNNING,
            start_time=datetime.now(),
            total_steps=0,
            browser_info={"browser": "chromium", "headless": headless},
            environment_info={"platform": "web", "timestamp": datetime.now().isoformat()}
        )

        step_results = []
        try:
            # 启动浏览器
            await self.playwright_utils.start_browser(headless=headless)

            # 导航到测试页面
            await self.playwright_utils.navigate_to_page(test_case.page_url)

            # 遍历所有测试观点和测试数据
            for viewpoint in test_case.viewpoints:
                for test_data in viewpoint.test_data_list:
                    step_result = await self._execute_test_data(viewpoint, test_data)
                    step_results.append(step_result)
                    # 如果步骤失败，停止执行
                    if step_result.status == TestStatus.FAILED:
                        break

            execution.step_results = step_results
            execution.end_time = datetime.now()
            execution.calculate_summary()

            # 确定整体执行状态
            if any(step.status == TestStatus.FAILED for step in step_results):
                execution.status = TestStatus.FAILED
            elif any(step.status == TestStatus.ERROR for step in step_results):
                execution.status = TestStatus.ERROR
            else:
                execution.status = TestStatus.PASSED

        except Exception as e:
            execution.status = TestStatus.ERROR
            execution.error_message = str(e)
            execution.end_time = datetime.now()
            execution.calculate_summary()

        finally:
            # 关闭浏览器
            await self.playwright_utils.close_browser()

        # 保存执行记录
        self.save_execution(execution)

        return execution

    async def _execute_test_data(self, viewpoint: TestViewpoint, test_data: TestData) -> TestStepResult:
        """执行单个测试数据（等价于原来的测试步骤）"""
        # 兼容原TestStepResult结构
        step_result = TestStepResult(
            step_id=test_data.id,
            step_number=0,  # 可根据需要编号
            action=viewpoint.strategy.value,  # 或者 viewpoint.target_node.type.value
            status=TestStatus.RUNNING,
            start_time=datetime.now(),
            input_data=test_data.input_value
        )

        try:
            # 获取目标选择器
            target_selector = None
            node = viewpoint.target_node
            if node:
                if node.attributes.get('id'):
                    target_selector = f"#{node.attributes['id']}"
                elif node.css_selector:
                    target_selector = node.css_selector
                else:
                    target_selector = node.xpath

            # 执行操作（根据节点类型和测试数据）
            action = self._determine_action_for_node(node)
            if action in ['click', 'fill', 'type', 'select_option', 'check', 'uncheck']:
                if not target_selector:
                    raise Exception("未找到目标选择器")

                step_data = {
                    'action': action,
                    'target_selector': target_selector,
                    'input_data': test_data.input_value,
                    'wait_time': 1.0
                }

                result = await self.playwright_utils.execute_test_step(step_data)
                step_result.output_data = result.get('output_data')
                step_result.screenshot_path = result.get('screenshot_path')

                if result['status'] == 'error':
                    step_result.status = TestStatus.FAILED
                    step_result.error_message = result['message']
                else:
                    step_result.status = TestStatus.PASSED

            elif action == 'verify_text':
                if not target_selector:
                    raise Exception("未找到目标选择器")

                actual_text = await self.playwright_utils.get_element_text(target_selector)
                step_result.output_data = actual_text

                # 执行断言
                for assertion in test_data.assertion_functions:
                    assertion_type, params = assertion if isinstance(assertion, tuple) else (assertion, {})
                    expected = test_data.expected_value
                    assertion_result = AssertionUtils.execute_assertion(
                        assertion_type,
                        actual_text,
                        expected,
                        f"验证文本内容: {test_data.description}"
                    )
                    step_result.assertions.append(AssertionResult(**assertion_result))
                    if not assertion_result['passed']:
                        step_result.status = TestStatus.FAILED
                        step_result.error_message = assertion_result['message']
                        break
                else:
                    step_result.status = TestStatus.PASSED

            elif action == 'verify_image':
                if not target_selector:
                    raise Exception("未找到目标选择器")

                is_visible = await self.playwright_utils.is_element_visible(target_selector)
                step_result.output_data = is_visible

                for assertion in test_data.assertion_functions:
                    assertion_type, params = assertion if isinstance(assertion, tuple) else (assertion, {})
                    expected = test_data.expected_value
                    assertion_result = AssertionUtils.execute_assertion(
                        assertion_type,
                        is_visible,
                        expected,
                        f"验证图片可见性: {test_data.description}"
                    )
                    step_result.assertions.append(AssertionResult(**assertion_result))
                    if not assertion_result['passed']:
                        step_result.status = TestStatus.FAILED
                        step_result.error_message = assertion_result['message']
                        break
                else:
                    step_result.status = TestStatus.PASSED

            elif action == 'wait':
                await asyncio.sleep(1.0)
                step_result.status = TestStatus.PASSED

            elif action == 'wait_for_element':
                if not target_selector:
                    raise Exception("未找到目标选择器")
                await self.playwright_utils.wait_for_element(target_selector)
                step_result.status = TestStatus.PASSED

            else:
                raise Exception(f"不支持的操作类型: {action}")

        except Exception as e:
            step_result.status = TestStatus.ERROR
            step_result.error_message = str(e)

        finally:
            step_result.end_time = datetime.now()
            if step_result.start_time and step_result.end_time:
                step_result.duration = (step_result.end_time - step_result.start_time).total_seconds()

        return step_result

    def _determine_action_for_node(self, node):
        if not node:
            return 'click'
        if hasattr(node, 'type'):
            t = str(node.type)
            if t == 'NodeType.BUTTON':
                return 'click'
            elif t == 'NodeType.INPUT':
                return 'fill'
            elif t == 'NodeType.LINK':
                return 'click'
            elif t == 'NodeType.SELECT':
                return 'select_option'
            elif t == 'NodeType.CHECKBOX':
                return 'check'
            elif t == 'NodeType.RADIO':
                return 'click'
            elif t == 'NodeType.TEXT':
                return 'verify_text'
            elif t == 'NodeType.IMAGE':
                return 'verify_image'
        return 'click'

    def save_execution(self, execution: TestExecution):
        filename = f"{execution.id}.json"
        filepath = os.path.join(self.data_dir, filename)
        execution.save_to_file(filepath)

    def load_execution(self, execution_id: str) -> Optional[TestExecution]:
        filepath = os.path.join(self.data_dir, f"{execution_id}.json")
        if os.path.exists(filepath):
            return TestExecution.load_from_file(filepath)
        return None

    def list_executions(self) -> Dict[str, Any]:
        executions = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.data_dir, filename)
                try:
                    execution = TestExecution.load_from_file(filepath)
                    executions.append(execution)
                except Exception as e:
                    print(f"加载执行记录失败 {filename}: {e}")
        executions.sort(key=lambda x: x.start_time, reverse=True)
        # 可根据需要自定义表格格式
        return {'headers': ['ID', '测试用例ID', '测试用例名称', '状态', '开始时间', '结束时间', '时长', '总步骤', '通过步骤', '失败步骤'],
                'rows': [
                    [exe.id, exe.test_case_id, exe.test_case_name, exe.status.value, exe.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                     exe.end_time.strftime('%Y-%m-%d %H:%M:%S') if exe.end_time else '', exe.duration, exe.total_steps, exe.passed_steps, exe.failed_steps]
                    for exe in executions
                ]}

    def get_execution_statistics(self) -> Dict[str, Any]:
        executions = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.data_dir, filename)
                try:
                    execution = TestExecution.load_from_file(filepath)
                    executions.append(execution)
                except Exception as e:
                    print(f"加载执行记录失败 {filename}: {e}")
        total = len(executions)
        passed = len([exe for exe in executions if exe.status == TestStatus.PASSED])
        failed = len([exe for exe in executions if exe.status == TestStatus.FAILED])
        error = len([exe for exe in executions if exe.status == TestStatus.ERROR])
        success_rate = (passed / total * 100) if total > 0 else 0
        return {
            'total_executions': total,
            'passed_executions': passed,
            'failed_executions': failed,
            'error_executions': error,
            'execution_success_rate': success_rate
        }

    def get_step_details(self, execution_id: str, step_id: str) -> Optional[Dict[str, Any]]:
        """获取步骤详情"""
        execution = self.load_execution(execution_id)
        if not execution:
            return None
        for step_result in execution.step_results:
            if step_result.step_id == step_id:
                return {
                    'step_id': step_result.step_id,
                    'step_number': step_result.step_number,
                    'action': step_result.action,
                    'status': step_result.status.value,
                    'start_time': step_result.start_time.isoformat(),
                    'end_time': step_result.end_time.isoformat() if step_result.end_time else None,
                    'duration': step_result.duration,
                    'input_data': step_result.input_data,
                    'output_data': step_result.output_data,
                    'error_message': step_result.error_message,
                    'screenshot_path': step_result.screenshot_path,
                    'assertions': [
                        {
                            'assertion_type': assertion.assertion_type,
                            'expected_value': assertion.expected_value,
                            'actual_value': assertion.actual_value,
                            'passed': assertion.passed,
                            'message': assertion.message,
                            'execution_time': assertion.execution_time
                        }
                        for assertion in step_result.assertions
                    ]
                }
        return None

    def delete_execution(self, execution_id: str) -> bool:
        filepath = os.path.join(self.data_dir, f"{execution_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
