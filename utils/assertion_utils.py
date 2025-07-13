import re
import json
import functools
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime
from enum import Enum


class AssertionType(Enum):
    """断言类型"""
    ELEMENT = "element"
    VALUE = "value"
    TEXT = "text"
    LENGTH = "length"
    FORMAT = "format"
    VALIDATION = "validation"


def assertion_function(func_name: str, description: str, assertion_type: AssertionType,
                      parameters: Optional[Dict[str, Dict]] = None,
                      node_types: Optional[List[str]] = None):
    """断言函数装饰器"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                end_time = datetime.now()

                return {
                    "assertion_type": func_name,
                    "expected_value": kwargs.get('expected', ''),
                    "actual_value": kwargs.get('actual', ''),
                    "passed": result,
                    "message": kwargs.get('message', description),
                    "execution_time": (end_time - start_time).total_seconds(),
                    "parameters": kwargs
                }
            except Exception as e:
                end_time = datetime.now()
                return {
                    "assertion_type": func_name,
                    "expected_value": kwargs.get('expected', ''),
                    "actual_value": kwargs.get('actual', ''),
                    "passed": False,
                    "message": f"断言执行失败: {str(e)}",
                    "execution_time": (end_time - start_time).total_seconds(),
                    "parameters": kwargs
                }

        # 添加元数据到函数
        wrapper.func_name = func_name
        wrapper.description = description
        wrapper.assertion_type = assertion_type
        wrapper.parameters = parameters or {}
        wrapper.node_types = node_types or []

        return wrapper
    return decorator


class InputAssertions:
    """输入框断言类"""

    @assertion_function(
        func_name="element_visible",
        description="元素可见性",
        assertion_type=AssertionType.ELEMENT,
        node_types=["input", "button", "select", "textarea"]
    )
    def assert_element_visible(self, actual: bool, expected: bool = True, message: str = "") -> bool:
        """断言元素可见"""
        return actual == expected

    @assertion_function(
        func_name="element_enabled",
        description="元素可用性",
        assertion_type=AssertionType.ELEMENT,
        node_types=["input", "button", "select", "textarea"]
    )
    def assert_element_enabled(self, actual: bool, expected: bool = True, message: str = "") -> bool:
        """断言元素可用"""
        return actual == expected

    @assertion_function(
        func_name="value_equals",
        description="值相等",
        assertion_type=AssertionType.VALUE,
        node_types=["input", "textarea"]
    )
    def assert_value_equals(self, actual: str, expected: str, message: str = "") -> bool:
        """断言值相等"""
        return actual == expected

    @assertion_function(
        func_name="value_contains",
        description="值包含",
        assertion_type=AssertionType.VALUE,
        node_types=["input", "textarea"]
    )
    def assert_value_contains(self, actual: str, expected: str, message: str = "") -> bool:
        """断言值包含"""
        return expected in actual if actual else False

    @assertion_function(
        func_name="value_length",
        description="值长度",
        assertion_type=AssertionType.LENGTH,
        node_types=["input", "textarea"]
    )
    def assert_value_length(self, actual: str, expected: int, message: str = "") -> bool:
        """断言值长度"""
        return len(actual) == expected if actual else False

    @assertion_function(
        func_name="max_length",
        description="最大长度",
        assertion_type=AssertionType.VALIDATION,
        parameters={
            "max_length": {"type": "int", "description": "最大长度", "default": 255}
        },
        node_types=["input", "textarea"]
    )
    def assert_max_length(self, actual: str, max_length: int = 255, message: str = "") -> bool:
        """断言最大长度"""
        return len(actual) <= max_length if actual else True

    @assertion_function(
        func_name="min_length",
        description="最小长度",
        assertion_type=AssertionType.VALIDATION,
        parameters={
            "min_length": {"type": "int", "description": "最小长度", "default": 0}
        },
        node_types=["input", "textarea"]
    )
    def assert_min_length(self, actual: str, min_length: int = 0, message: str = "") -> bool:
        """断言最小长度"""
        return len(actual) >= min_length if actual else False

    @assertion_function(
        func_name="value_format",
        description="值格式",
        assertion_type=AssertionType.FORMAT,
        parameters={
            "pattern": {"type": "str", "description": "正则表达式", "default": ""},
            "case_sensitive": {"type": "bool", "description": "区分大小写", "default": False}
        },
        node_types=["input", "textarea"]
    )
    def assert_value_format(self, actual: str, pattern: str = "", case_sensitive: bool = False, message: str = "") -> bool:
        """断言值格式"""
        if not pattern:
            return True
        if not case_sensitive:
            actual = actual.lower() if actual else ""
            pattern = pattern.lower()
        return bool(re.search(pattern, actual)) if actual else False

    @assertion_function(
        func_name="required_field",
        description="必填字段",
        assertion_type=AssertionType.VALIDATION,
        parameters={
            "required": {"type": "bool", "description": "是否必填", "default": True}
        },
        node_types=["input", "textarea"]
    )
    def assert_required_field(self, actual: str, required: bool = True, message: str = "") -> bool:
        """断言必填字段"""
        if not required:
            return True
        return actual is not None and actual.strip() != ""

    @assertion_function(
        func_name="placeholder_text",
        description="占位符文本",
        assertion_type=AssertionType.TEXT,
        node_types=["input", "textarea"]
    )
    def assert_placeholder_text(self, actual: str, expected: str, message: str = "") -> bool:
        """断言占位符文本"""
        return actual == expected


class ButtonAssertions:
    """按钮断言类"""

    @assertion_function(
        func_name="text_equals",
        description="文本相等",
        assertion_type=AssertionType.TEXT,
        node_types=["button", "a", "input"]
    )
    def assert_text_equals(self, actual: str, expected: str, message: str = "") -> bool:
        """断言文本相等"""
        return actual == expected

    @assertion_function(
        func_name="text_contains",
        description="文本包含",
        assertion_type=AssertionType.TEXT,
        node_types=["button", "a", "input"]
    )
    def assert_text_contains(self, actual: str, expected: str, message: str = "") -> bool:
        """断言文本包含"""
        return expected in actual if actual else False

    @assertion_function(
        func_name="clickable",
        description="可点击",
        assertion_type=AssertionType.ELEMENT,
        node_types=["button", "a", "input"]
    )
    def assert_clickable(self, actual: bool, expected: bool = True, message: str = "") -> bool:
        """断言可点击"""
        return actual == expected

    @assertion_function(
        func_name="button_type",
        description="按钮类型",
        assertion_type=AssertionType.VALIDATION,
        node_types=["button", "input"]
    )
    def assert_button_type(self, actual: str, expected: str, message: str = "") -> bool:
        """断言按钮类型"""
        return actual == expected


class SelectAssertions:
    """选择框断言类"""

    @assertion_function(
        func_name="option_selected",
        description="选项已选择",
        assertion_type=AssertionType.VALUE,
        node_types=["select"]
    )
    def assert_option_selected(self, actual: str, expected: str, message: str = "") -> bool:
        """断言选项已选择"""
        return actual == expected

    @assertion_function(
        func_name="option_available",
        description="选项可用",
        assertion_type=AssertionType.VALIDATION,
        node_types=["select"]
    )
    def assert_option_available(self, actual: List[str], expected: str, message: str = "") -> bool:
        """断言选项可用"""
        return expected in actual if actual else False


class AssertionUtils:
    """断言工具类 - 兼容旧版本"""

    # 保持原有的静态方法以兼容现有代码
    @staticmethod
    def assert_equals(actual: Any, expected: Any, message: str = "") -> Dict[str, Any]:
        """断言相等"""
        start_time = datetime.now()
        passed = actual == expected
        end_time = datetime.now()

        return {
            "assertion_type": "equals",
            "expected_value": expected,
            "actual_value": actual,
            "passed": passed,
            "message": message or f"期望值: {expected}, 实际值: {actual}",
            "execution_time": (end_time - start_time).total_seconds()
        }

    @staticmethod
    def assert_contains(actual: str, expected: str, message: str = "") -> Dict[str, Any]:
        """断言包含"""
        start_time = datetime.now()
        passed = expected in actual if actual else False
        end_time = datetime.now()

        return {
            "assertion_type": "contains",
            "expected_value": expected,
            "actual_value": actual,
            "passed": passed,
            "message": message or f"期望包含: {expected}, 实际值: {actual}",
            "execution_time": (end_time - start_time).total_seconds()
        }

    @staticmethod
    def assert_element_visible(actual: bool, message: str = "") -> Dict[str, Any]:
        """断言元素可见"""
        start_time = datetime.now()
        passed = actual is True
        end_time = datetime.now()

        return {
            "assertion_type": "element_visible",
            "expected_value": True,
            "actual_value": actual,
            "passed": passed,
            "message": message or f"期望元素可见, 实际值: {actual}",
            "execution_time": (end_time - start_time).total_seconds()
        }

    @staticmethod
    def execute_assertion(assertion_type: str, actual: Any, expected: Any, message: str = "") -> Dict[str, Any]:
        """执行断言 - 兼容旧版本"""
        # 创建断言实例
        input_assertions = InputAssertions()
        button_assertions = ButtonAssertions()
        select_assertions = SelectAssertions()

        # 映射断言类型到方法
        assertion_map = {
            "element_visible": input_assertions.assert_element_visible,
            "element_enabled": input_assertions.assert_element_enabled,
            "value_equals": input_assertions.assert_value_equals,
            "value_contains": input_assertions.assert_value_contains,
            "value_length": input_assertions.assert_value_length,
            "max_length": input_assertions.assert_max_length,
            "min_length": input_assertions.assert_min_length,
            "value_format": input_assertions.assert_value_format,
            "required_field": input_assertions.assert_required_field,
            "placeholder_text": input_assertions.assert_placeholder_text,
            "text_equals": button_assertions.assert_text_equals,
            "text_contains": button_assertions.assert_text_contains,
            "clickable": button_assertions.assert_clickable,
            "button_type": button_assertions.assert_button_type,
            "option_selected": select_assertions.assert_option_selected,
            "option_available": select_assertions.assert_option_available,
        }

        if assertion_type in assertion_map:
            return assertion_map[assertion_type](actual=actual, expected=expected, message=message)
        else:
            # 回退到旧版本方法
            if assertion_type == "equals":
                return AssertionUtils.assert_equals(actual, expected, message)
            elif assertion_type == "contains":
                return AssertionUtils.assert_contains(actual, expected, message)
            elif assertion_type == "element_visible":
                return AssertionUtils.assert_element_visible(actual, message)
            else:
                return {
                    "assertion_type": assertion_type,
                    "expected_value": expected,
                    "actual_value": actual,
                    "passed": False,
                    "message": f"不支持的断言类型: {assertion_type}",
                    "execution_time": 0
                }

    @staticmethod
    def get_available_assertions() -> List[Dict[str, str]]:
        """获取所有可用的断言函数信息"""
        input_assertions = InputAssertions()
        button_assertions = ButtonAssertions()
        select_assertions = SelectAssertions()

        assertions = []

        # 收集所有断言函数的信息
        for obj in [input_assertions, button_assertions, select_assertions]:
            for method_name in dir(obj):
                method = getattr(obj, method_name)
                if hasattr(method, 'func_name'):
                    assertions.append({
                        "name": method.func_name,
                        "description": method.description,
                        "type": method.assertion_type.value,
                        "parameters": method.parameters,
                        "node_types": method.node_types
                    })

        return assertions

    @staticmethod
    def get_assertions_by_node_type(node_type: str) -> List[Dict[str, str]]:
        """根据节点类型获取可用的断言函数"""
        all_assertions = AssertionUtils.get_available_assertions()
        return [a for a in all_assertions if node_type in a.get("node_types", [])]

    @staticmethod
    def get_assertion_parameters(assertion_name: str) -> Dict[str, Dict]:
        """获取断言函数的参数信息"""
        all_assertions = AssertionUtils.get_available_assertions()
        for assertion in all_assertions:
            if assertion["name"] == assertion_name:
                return assertion.get("parameters", {})
        return {}
