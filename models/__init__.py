# 数据模型模块初始化文件

from .page_node import PageStructure, PageNode, NodeType
from .test_case import TestCase, TestViewpoint, TestData, TestType, TestPriority, TestStrategy, TestStatus
from .test_data import TestExecution, TestStepResult, TestStatus as ExecutionTestStatus, AssertionResult, TestSuite

__all__ = [
    'PageStructure', 'PageNode', 'NodeType',
    'TestCase', 'TestViewpoint', 'TestData', 'TestType', 'TestPriority', 'TestStrategy', 'TestStatus',
    'TestExecution', 'TestStepResult', 'ExecutionTestStatus', 'AssertionResult', 'TestSuite'
]


def to_table_format_list(objects: list, object_type: str = None) -> dict:
    """将对象列表转换为表格格式 { headers: [], rows: [] }"""
    if not objects:
        return {'headers': [], 'rows': []}

    # 如果对象有 to_table_format 方法，使用它
    if hasattr(objects[0], 'to_table_format'):
        first_format = objects[0].to_table_format()
        headers = first_format['headers']
        rows = []
        for obj in objects:
            row = obj.to_table_format()['rows'][0]  # 取第一个（也是唯一的）行
            rows.append(row)
        return {'headers': headers, 'rows': rows}

    # 否则返回空格式
    return {'headers': [], 'rows': []}


def get_default_headers(object_type: str) -> list:
    """获取默认表头"""
    headers_map = {
        'page_structure': ['ID', '标题', 'URL', '节点数', '创建时间'],
        'test_case': ['ID', '名称', '描述', '类型', '优先级', '页面URL', '步骤数', '创建时间', '更新时间'],
        'test_execution': ['ID', '测试用例ID', '测试用例名称', '状态', '开始时间', '结束时间', '时长', '总步骤', '通过步骤', '失败步骤'],
        'page_node': ['ID', '类型', '标签名', '文本内容', 'XPath', 'CSS选择器', '是否可见', '是否可交互'],
        'test_step': ['ID', '步骤号', '操作', '目标元素', '输入数据', '预期结果', '断言类型', '等待时间'],
        'test_step_result': ['步骤ID', '步骤号', '操作', '状态', '开始时间', '结束时间', '时长', '输入数据', '输出数据', '错误信息'],
        'assertion_result': ['断言类型', '期望值', '实际值', '是否通过', '消息', '执行时间'],
        'test_suite': ['ID', '名称', '描述', '测试用例数', '执行记录数', '创建时间', '更新时间'],
        'report': ['文件名', '文件路径', '大小(字节)', '创建时间', '类型']
    }
    return headers_map.get(object_type, [])
