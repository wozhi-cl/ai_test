import os
import json
import uuid
import random
from typing import List, Dict, Any, Optional, Union
from models.page_node import PageStructure, PageNode, NodeType
from models.test_case import TestCase, TestViewpoint, TestData, TestType, TestPriority, TestStrategy
from core.page_parser import PageParser
from utils.assertion_utils import AssertionUtils
from datetime import datetime
from models import to_table_format_list, get_default_headers


class TestGenerator:
    """测试用例生成器"""

    def __init__(self, data_dir: str = "data/test_cases"):
        self.data_dir = data_dir
        self.page_parser = PageParser()
        os.makedirs(data_dir, exist_ok=True)

    def generate_test_case_from_nodes(self,
                                    structure_id: str,
                                    node_ids: List[str],
                                    test_name: str,
                                    test_type: TestType = TestType.FUNCTIONAL,
                                    priority: TestPriority = TestPriority.MEDIUM,
                                    description: str = "") -> TestCase:
        """从节点生成测试用例，一次性生成所有测试观点"""
        # 加载页面结构
        page_structure = self.page_parser.load_page_structure(structure_id)
        if not page_structure:
            raise Exception("页面结构不存在")

        # 获取选中的节点
        selected_nodes = [node for node in page_structure.nodes if node.id in node_ids]
        if not selected_nodes:
            raise Exception("未找到选中的节点")

        # 为每个节点生成所有测试观点
        viewpoints = []
        for node in selected_nodes:
            node_viewpoints = self._generate_all_viewpoints_for_node(node, page_structure.url)
            viewpoints.extend(node_viewpoints)

        # 创建测试用例
        test_case = TestCase(
            id=str(uuid.uuid4()),
            name=test_name,
            description=description,
            test_type=test_type,
            priority=priority,
            page_url=page_structure.url,
            viewpoints=viewpoints
        )

        return test_case

    def _generate_all_viewpoints_for_node(self, node: PageNode, page_url: str) -> List[TestViewpoint]:
        """为单个节点生成所有测试观点"""
        viewpoints = []

        # 1. 基本测试观点
        basic_viewpoint = self._generate_basic_viewpoint(node, page_url)
        if basic_viewpoint:
            viewpoints.append(basic_viewpoint)

        # 2. 边界值测试观点
        boundary_viewpoint = self._generate_boundary_viewpoint(node, page_url)
        if boundary_viewpoint:
            viewpoints.append(boundary_viewpoint)

        # 3. 等价类测试观点
        equivalence_viewpoint = self._generate_equivalence_viewpoint(node, page_url)
        if equivalence_viewpoint:
            viewpoints.append(equivalence_viewpoint)

        # 4. 异常测试观点
        negative_viewpoint = self._generate_negative_viewpoint(node, page_url)
        if negative_viewpoint:
            viewpoints.append(negative_viewpoint)

        return viewpoints

    def _generate_basic_viewpoint(self, node: PageNode, page_url: str) -> Optional[TestViewpoint]:
        """生成基本测试观点"""
        test_data_list = []
        action = self._determine_action_for_node(node)

        if not action:
            return None

        # 生成基本测试数据
        test_data = TestData(
            id=str(uuid.uuid4()),
            input_value=self._generate_basic_input_value(node, action),
            expected_value=self._generate_expected_value(node, action),
            assertion_functions=self._generate_assertion_functions(node, action),
            description=f"基本{action}操作测试"
        )
        test_data_list.append(test_data)

        return TestViewpoint(
            id=str(uuid.uuid4()),
            name=f"{node.tag_name}基本测试",
            strategy=TestStrategy.BASIC,
            description=f"对{node.tag_name}元素进行基本{action}操作测试",
            target_node=node,
            test_data_list=test_data_list
        )

    def _generate_boundary_viewpoint(self, node: PageNode, page_url: str) -> Optional[TestViewpoint]:
        """生成边界值测试观点"""
        if node.type not in [NodeType.INPUT, NodeType.SELECT]:
            return None

        test_data_list = []
        input_type = node.attributes.get('type', 'text').lower()

        if node.type == NodeType.INPUT:
            boundary_data = self._generate_input_boundary_data(node, input_type)
        else:  # SELECT
            boundary_data = self._generate_select_boundary_data(node)

        for i, (input_val, expected_val, description) in enumerate(boundary_data):
            test_data = TestData(
                id=str(uuid.uuid4()),
                input_value=input_val,
                expected_value=expected_val,
                assertion_functions=self._generate_assertion_functions(node, "fill" if node.type == NodeType.INPUT else "select"),
                description=f"边界值测试: {description}"
            )
            test_data_list.append(test_data)

        return TestViewpoint(
            id=str(uuid.uuid4()),
            name=f"{node.tag_name}边界值测试",
            strategy=TestStrategy.BOUNDARY,
            description=f"对{node.tag_name}元素进行边界值测试",
            target_node=node,
            test_data_list=test_data_list
        )

    def _generate_equivalence_viewpoint(self, node: PageNode, page_url: str) -> Optional[TestViewpoint]:
        """生成等价类测试观点"""
        if node.type not in [NodeType.INPUT, NodeType.SELECT]:
            return None

        test_data_list = []
        input_type = node.attributes.get('type', 'text').lower()

        if node.type == NodeType.INPUT:
            equivalence_data = self._generate_input_equivalence_data(node, input_type)
        else:  # SELECT
            equivalence_data = self._generate_select_equivalence_data(node)

        for i, (input_val, expected_val, description) in enumerate(equivalence_data):
            test_data = TestData(
                id=str(uuid.uuid4()),
                input_value=input_val,
                expected_value=expected_val,
                assertion_functions=self._generate_assertion_functions(node, "fill" if node.type == NodeType.INPUT else "select"),
                description=f"等价类测试: {description}"
            )
            test_data_list.append(test_data)

        return TestViewpoint(
            id=str(uuid.uuid4()),
            name=f"{node.tag_name}等价类测试",
            strategy=TestStrategy.EQUIVALENCE,
            description=f"对{node.tag_name}元素进行等价类测试",
            target_node=node,
            test_data_list=test_data_list
        )

    def _generate_negative_viewpoint(self, node: PageNode, page_url: str) -> Optional[TestViewpoint]:
        """生成异常测试观点"""
        if node.type not in [NodeType.INPUT, NodeType.SELECT]:
            return None

        test_data_list = []
        input_type = node.attributes.get('type', 'text').lower()

        if node.type == NodeType.INPUT:
            negative_data = self._generate_input_negative_data(node, input_type)
        else:  # SELECT
            negative_data = self._generate_select_negative_data(node)

        for i, (input_val, expected_val, description) in enumerate(negative_data):
            test_data = TestData(
                id=str(uuid.uuid4()),
                input_value=input_val,
                expected_value=expected_val,
                assertion_functions=self._generate_assertion_functions(node, "fill" if node.type == NodeType.INPUT else "select"),
                description=f"异常测试: {description}"
            )
            test_data_list.append(test_data)

        return TestViewpoint(
            id=str(uuid.uuid4()),
            name=f"{node.tag_name}异常测试",
            strategy=TestStrategy.NEGATIVE,
            description=f"对{node.tag_name}元素进行异常测试",
            target_node=node,
            test_data_list=test_data_list
        )

    def _generate_input_boundary_data(self, node: PageNode, input_type: str) -> List[tuple]:
        """生成输入框边界值测试数据"""
        boundary_data = []

        if input_type == 'text':
            boundary_data = [
                ("", "", "空字符串测试"),
                ("a", "a", "单字符测试"),
                ("a" * 50, "a" * 50, "50字符测试"),
                ("a" * 100, "a" * 100, "100字符测试"),
                ("a" * 255, "a" * 255, "255字符测试"),
                ("a" * 256, "a" * 256, "256字符测试（超出边界）"),
                ("测试数据", "测试数据", "中文字符测试"),
                ("Test Data 123", "Test Data 123", "混合字符测试"),
                ("   ", "   ", "空格字符测试"),
                ("\t\n\r", "\t\n\r", "特殊字符测试")
            ]
        elif input_type == 'email':
            boundary_data = [
                ("", "", "空邮箱测试"),
                ("a@b.c", "a@b.c", "最短邮箱测试"),
                ("test@example.com", "test@example.com", "标准邮箱测试"),
                ("a" * 50 + "@example.com", "a" * 50 + "@example.com", "长用户名邮箱测试"),
                ("test@" + "a" * 100 + ".com", "test@" + "a" * 100 + ".com", "长域名邮箱测试"),
                ("test@example", "test@example", "无效邮箱格式测试"),
                ("test.example.com", "test.example.com", "缺少@符号测试"),
                ("@example.com", "@example.com", "缺少用户名测试"),
                ("test@", "test@", "缺少域名测试"),
                ("test@.com", "test@.com", "缺少二级域名测试")
            ]
        elif input_type == 'number':
            min_val = node.attributes.get('min')
            max_val = node.attributes.get('max')

            if min_val and max_val:
                min_val = int(min_val)
                max_val = int(max_val)
                boundary_data = [
                    (str(min_val - 1), str(min_val - 1), f"最小值-1测试 ({min_val - 1})"),
                    (str(min_val), str(min_val), f"最小值测试 ({min_val})"),
                    (str(min_val + 1), str(min_val + 1), f"最小值+1测试 ({min_val + 1})"),
                    (str(max_val - 1), str(max_val - 1), f"最大值-1测试 ({max_val - 1})"),
                    (str(max_val), str(max_val), f"最大值测试 ({max_val})"),
                    (str(max_val + 1), str(max_val + 1), f"最大值+1测试 ({max_val + 1})"),
                    ("0", "0", "零值测试"),
                    ("-1", "-1", "负值测试"),
                    ("abc", "abc", "非数字输入测试"),
                    ("", "", "空值测试")
                ]
            else:
                boundary_data = [
                    ("0", "0", "零值测试"),
                    ("-1", "-1", "负值测试"),
                    ("999999", "999999", "大数值测试"),
                    ("-999999", "-999999", "大负值测试"),
                    ("abc", "abc", "非数字输入测试"),
                    ("", "", "空值测试")
                ]
        elif input_type == 'password':
            boundary_data = [
                ("", "", "空密码测试"),
                ("a", "a", "单字符密码测试"),
                ("a" * 8, "a" * 8, "8字符密码测试"),
                ("a" * 16, "a" * 16, "16字符密码测试"),
                ("a" * 32, "a" * 32, "32字符密码测试"),
                ("a" * 33, "a" * 33, "33字符密码测试（超出边界）"),
                ("Test123!", "Test123!", "标准密码测试"),
                ("测试密码123", "测试密码123", "中文密码测试"),
                ("   ", "   ", "空格密码测试"),
                ("\t\n\r", "\t\n\r", "特殊字符密码测试")
            ]
        else:
            boundary_data = [
                ("", "", "空值测试"),
                ("test", "test", "标准输入测试"),
                ("a" * 100, "a" * 100, "长输入测试"),
                ("测试数据", "测试数据", "中文输入测试"),
                ("Test Data 123", "Test Data 123", "混合输入测试")
            ]

        return boundary_data

    def _generate_input_equivalence_data(self, node: PageNode, input_type: str) -> List[tuple]:
        """生成输入框等价类测试数据"""
        equivalence_data = []

        if input_type == 'text':
            equivalence_data = [
                ("正常文本", "正常文本", "正常文本输入测试"),
                ("123", "123", "数字文本测试"),
                ("Test", "Test", "英文文本测试"),
                ("测试", "测试", "中文文本测试"),
                ("Test123", "Test123", "混合文本测试"),
                ("test@example.com", "test@example.com", "包含特殊字符文本测试"),
                ("   test   ", "   test   ", "前后空格文本测试"),
                ("", "", "空文本测试")
            ]
        elif input_type == 'email':
            equivalence_data = [
                ("user@domain.com", "user@domain.com", "标准邮箱格式测试"),
                ("user.name@domain.com", "user.name@domain.com", "包含点号邮箱测试"),
                ("user+tag@domain.com", "user+tag@domain.com", "包含加号邮箱测试"),
                ("user@sub.domain.com", "user@sub.domain.com", "子域名邮箱测试"),
                ("user@domain.co.uk", "user@domain.co.uk", "多级域名邮箱测试"),
                ("", "", "空邮箱测试"),
                ("invalid-email", "invalid-email", "无效邮箱格式测试")
            ]
        elif input_type == 'number':
            equivalence_data = [
                ("123", "123", "正整数测试"),
                ("0", "0", "零值测试"),
                ("-123", "-123", "负整数测试"),
                ("123.45", "123.45", "小数测试"),
                ("", "", "空值测试"),
                ("abc", "abc", "非数字测试")
            ]
        else:
            equivalence_data = [
                ("正常输入", "正常输入", "正常输入测试"),
                ("", "", "空输入测试"),
                ("特殊字符!@#", "特殊字符!@#", "特殊字符测试")
            ]

        return equivalence_data

    def _generate_input_negative_data(self, node: PageNode, input_type: str) -> List[tuple]:
        """生成输入框异常测试数据"""
        negative_data = []

        if input_type == 'text':
            negative_data = [
                ("a" * 1000, "a" * 1000, "超长文本测试"),
                ("<script>alert('xss')</script>", "<script>alert('xss')</script>", "XSS攻击测试"),
                ("' OR '1'='1", "' OR '1'='1", "SQL注入测试"),
                ("../../etc/passwd", "../../etc/passwd", "路径遍历测试"),
                ("\x00\x01\x02", "\x00\x01\x02", "二进制数据测试"),
                ("\u0000\u0001\u0002", "\u0000\u0001\u0002", "Unicode控制字符测试"),
                ("a" * 10000, "a" * 10000, "极长文本测试"),
                ("", "", "空值测试"),
                ("   ", "   ", "纯空格测试")
            ]
        elif input_type == 'email':
            negative_data = [
                ("<script>alert('xss')@example.com", "<script>alert('xss')@example.com", "XSS邮箱测试"),
                ("user@<script>alert('xss')</script>", "user@<script>alert('xss')</script>", "XSS域名测试"),
                ("user@domain.com' OR '1'='1", "user@domain.com' OR '1'='1", "SQL注入邮箱测试"),
                ("user@domain.com; DROP TABLE users;", "user@domain.com; DROP TABLE users;", "SQL注入测试"),
                ("user@domain.com\n<script>alert('xss')</script>", "user@domain.com\n<script>alert('xss')</script>", "换行符注入测试"),
                ("", "", "空邮箱测试"),
                ("invalid", "invalid", "无效格式测试")
            ]
        elif input_type == 'number':
            negative_data = [
                ("999999999999999999999999999999", "999999999999999999999999999999", "超大数字测试"),
                ("-999999999999999999999999999999", "-999999999999999999999999999999", "超大负数测试"),
                ("1.234567890123456789", "1.234567890123456789", "超长小数测试"),
                ("abc", "abc", "非数字输入测试"),
                ("<script>alert('xss')</script>", "<script>alert('xss')</script>", "XSS攻击测试"),
                ("' OR '1'='1", "' OR '1'='1", "SQL注入测试"),
                ("", "", "空值测试")
            ]
        else:
            negative_data = [
                ("<script>alert('xss')</script>", "<script>alert('xss')</script>", "XSS攻击测试"),
                ("' OR '1'='1", "' OR '1'='1", "SQL注入测试"),
                ("../../etc/passwd", "../../etc/passwd", "路径遍历测试"),
                ("a" * 10000, "a" * 10000, "超长输入测试"),
                ("", "", "空值测试")
            ]

        return negative_data

    def _generate_select_boundary_data(self, node: PageNode) -> List[tuple]:
        """生成下拉框边界值测试数据"""
        options = self._get_select_options(node)
        boundary_data = []

        if options:
            # 测试第一个选项
            boundary_data.append((options[0], options[0], "选择第一个选项"))
            # 测试最后一个选项
            boundary_data.append((options[-1], options[-1], "选择最后一个选项"))
            # 测试中间选项
            if len(options) > 2:
                boundary_data.append((options[len(options)//2], options[len(options)//2], "选择中间选项"))

        return boundary_data

    def _generate_select_equivalence_data(self, node: PageNode) -> List[tuple]:
        """生成下拉框等价类测试数据"""
        options = self._get_select_options(node)
        equivalence_data = []

        if options:
            # 为每个选项生成测试
            for option in options:
                equivalence_data.append((option, option, f"选择选项: {option}"))

        return equivalence_data

    def _generate_select_negative_data(self, node: PageNode) -> List[tuple]:
        """生成下拉框异常测试数据"""
        negative_data = [
            ("invalid_option", "invalid_option", "选择无效选项"),
            ("<script>alert('xss')</script>", "<script>alert('xss')</script>", "XSS选项测试"),
            ("' OR '1'='1", "' OR '1'='1", "SQL注入选项测试"),
            ("", "", "空选项测试"),
            ("   ", "   ", "空格选项测试")
        ]

        return negative_data

    def _get_select_options(self, node: PageNode) -> List[str]:
        """获取下拉框的选项值"""
        # 这里应该从页面结构中获取实际的选项
        # 暂时返回模拟数据
        if 'gender' in node.id.lower():
            return ['Male', 'Female', 'Other']
        elif 'country' in node.id.lower():
            return ['USA', 'China', 'Japan', 'UK', 'Germany']
        elif 'state' in node.id.lower():
            return ['California', 'New York', 'Texas', 'Florida']
        else:
            return ['Option 1', 'Option 2', 'Option 3']

    def _determine_action_for_node(self, node: PageNode) -> Optional[str]:
        """确定节点的操作类型"""
        if node.type == NodeType.BUTTON:
            return "click"
        elif node.type == NodeType.INPUT:
            return "fill"
        elif node.type == NodeType.LINK:
            return "click"
        elif node.type == NodeType.SELECT:
            return "select_option"
        elif node.type == NodeType.CHECKBOX:
            return "check"
        elif node.type == NodeType.RADIO:
            return "click"
        elif node.type == NodeType.TEXT:
            return "verify_text"
        elif node.type == NodeType.IMAGE:
            return "verify_image"
        else:
            return "click"  # 默认点击操作

    def _generate_basic_input_value(self, node: PageNode, action: str) -> Any:
        """生成基本输入值"""
        if action == "fill":
            # 根据输入框类型生成测试数据
            input_type = node.attributes.get('type', 'text').lower()
            if input_type == 'email':
                return "test@example.com"
            elif input_type == 'password':
                return "testpassword123"
            elif input_type == 'number':
                return "123"
            elif input_type == 'tel':
                return "13800138000"
            else:
                return "测试数据"
        elif action == "select_option":
            # 获取选项值
            return node.attributes.get('value', '')
        else:
            return None

    def _generate_expected_value(self, node: PageNode, action: str) -> Any:
        """生成预期值"""
        if action == "fill":
            return self._generate_basic_input_value(node, action)
        elif action == "click":
            return "元素被点击"
        elif action == "select_option":
            return self._generate_basic_input_value(node, action)
        elif action == "check":
            return True
        elif action == "verify_text":
            return node.text_content
        elif action == "verify_image":
            return "图片正确显示"
        else:
            return "操作成功执行"

    def _generate_assertion_functions(self, node: PageNode, action: str) -> List[Union[str, tuple]]:
        """生成断言函数数组"""
        assertion_functions = []

        if action == "fill":
            assertion_functions.extend([
                "element_visible",
                "element_enabled",
                ("value_equals", {"expected": self._generate_basic_input_value(node, action)}),
                "no_error_message"
            ])
        elif action == "click":
            assertion_functions.extend([
                "element_clickable",
                "element_visible",
                ("page_navigated", {"timeout": 5000}),
                "no_error_message"
            ])
        elif action == "select_option":
            assertion_functions.extend([
                "element_visible",
                "element_enabled",
                ("option_selected", {"expected": self._generate_basic_input_value(node, action)}),
                "no_error_message"
            ])
        elif action == "check":
            assertion_functions.extend([
                "element_visible",
                "element_enabled",
                "checkbox_checked",
                "no_error_message"
            ])
        elif action == "verify_text":
            assertion_functions.extend([
                "element_visible",
                ("text_contains", {"expected": node.text_content}),
                "no_error_message"
            ])
        elif action == "verify_image":
            assertion_functions.extend([
                "element_visible",
                "image_loaded",
                "no_error_message"
            ])
        else:
            assertion_functions.extend([
                "element_visible",
                "no_error_message"
            ])

        return assertion_functions

    def save_test_case(self, test_case: TestCase):
        """保存测试用例"""
        filename = f"{test_case.id}.json"
        filepath = os.path.join(self.data_dir, filename)
        test_case.save_to_file(filepath)

    def load_test_case(self, test_case_id: str) -> Optional[TestCase]:
        """加载测试用例"""
        filepath = os.path.join(self.data_dir, f"{test_case_id}.json")
        if os.path.exists(filepath):
            return TestCase.load_from_file(filepath)
        return None

    def list_test_cases(self) -> Dict[str, Any]:
        """列出所有测试用例（返回 { headers: [], rows: [] } 格式）"""
        test_cases = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.data_dir, filename)
                try:
                    test_case = TestCase.load_from_file(filepath)
                    test_cases.append(test_case)
                except Exception as e:
                    print(f"加载测试用例失败 {filename}: {e}")

        # 按更新时间倒序排列
        test_cases.sort(key=lambda x: x.updated_at, reverse=True)

        # 转换为表格格式
        if test_cases:
            headers = ['ID', '名称', '描述', '类型', '优先级', '页面URL', '测试观点数', '测试数据数', '创建时间', '更新时间']
            rows = []
            for test_case in test_cases:
                rows.append([
                    test_case.id,
                    test_case.name,
                    test_case.description or '',
                    test_case.test_type.value,
                    test_case.priority.value,
                    test_case.page_url,
                    len(test_case.viewpoints),
                    test_case.get_test_data_count(),
                    test_case.created_at.strftime('%Y-%m-%d %H:%M:%S') if test_case.created_at else '',
                    test_case.updated_at.strftime('%Y-%m-%d %H:%M:%S') if test_case.updated_at else ''
                ])
            return {'headers': headers, 'rows': rows}
        else:
            return {'headers': get_default_headers('test_case'), 'rows': []}

    def delete_test_case(self, test_case_id: str) -> bool:
        """删除测试用例"""
        filepath = os.path.join(self.data_dir, f"{test_case_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

    def update_test_case(self, test_case: TestCase):
        """更新测试用例"""
        test_case.updated_at = datetime.now()
        self.save_test_case(test_case)

    def add_viewpoint_to_test_case(self, test_case_id: str, viewpoint: TestViewpoint):
        """向测试用例添加测试观点"""
        test_case = self.load_test_case(test_case_id)
        if test_case:
            test_case.add_viewpoint(viewpoint)
            self.update_test_case(test_case)

    def remove_viewpoint_from_test_case(self, test_case_id: str, viewpoint_id: str):
        """从测试用例删除测试观点"""
        test_case = self.load_test_case(test_case_id)
        if test_case:
            test_case.remove_viewpoint(viewpoint_id)
            self.update_test_case(test_case)

    def add_test_data_to_viewpoint(self, test_case_id: str, viewpoint_id: str, test_data: TestData):
        """向测试观点添加测试数据"""
        test_case = self.load_test_case(test_case_id)
        if test_case:
            viewpoint = test_case.get_viewpoint(viewpoint_id)
            if viewpoint:
                viewpoint.add_test_data(test_data)
                self.update_test_case(test_case)

    def remove_test_data_from_viewpoint(self, test_case_id: str, viewpoint_id: str, test_data_id: str):
        """从测试观点删除测试数据"""
        test_case = self.load_test_case(test_case_id)
        if test_case:
            viewpoint = test_case.get_viewpoint(viewpoint_id)
            if viewpoint:
                viewpoint.remove_test_data(test_data_id)
                self.update_test_case(test_case)

    def export_test_case(self, test_case_id: str, format: str = 'json') -> str:
        """导出测试用例"""
        test_case = self.load_test_case(test_case_id)
        if not test_case:
            raise Exception("测试用例不存在")

        if format == 'json':
            return json.dumps(test_case.to_dict(), ensure_ascii=False, indent=2)
        elif format == 'csv':
            return self._export_to_csv(test_case)
        else:
            raise Exception(f"不支持的导出格式: {format}")

    def _export_to_csv(self, test_case: TestCase) -> str:
        """导出为CSV格式"""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # 写入测试用例信息
        writer.writerow(['测试用例信息'])
        writer.writerow(['ID', test_case.id])
        writer.writerow(['名称', test_case.name])
        writer.writerow(['描述', test_case.description or ''])
        writer.writerow(['类型', test_case.test_type.value])
        writer.writerow(['优先级', test_case.priority.value])
        writer.writerow(['页面URL', test_case.page_url])
        writer.writerow(['测试观点数', len(test_case.viewpoints)])
        writer.writerow(['测试数据数', test_case.get_test_data_count()])
        writer.writerow([])

        # 写入测试观点信息
        for i, viewpoint in enumerate(test_case.viewpoints):
            writer.writerow([f'测试观点 {i+1}'])
            writer.writerow(['观点ID', viewpoint.id])
            writer.writerow(['观点名称', viewpoint.name])
            writer.writerow(['测试策略', viewpoint.strategy.value])
            writer.writerow(['描述', viewpoint.description])
            writer.writerow(['目标节点', f"{viewpoint.target_node.tag_name}: {viewpoint.target_node.text_content or viewpoint.target_node.xpath}" if viewpoint.target_node else ""])
            writer.writerow(['测试数据数', len(viewpoint.test_data_list)])
            writer.writerow([])

            # 写入测试数据信息
            writer.writerow(['测试数据'])
            writer.writerow(['输入值', '预期值', '断言函数', '描述'])

            for test_data in viewpoint.test_data_list:
                assertion_str = str(test_data.assertion_functions)
                writer.writerow([
                    test_data.input_value,
                    test_data.expected_value,
                    assertion_str,
                    test_data.description
                ])
            writer.writerow([])

        return output.getvalue()
