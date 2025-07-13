import os
import json
import uuid
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
from models.page_node import PageNode


class TestType(Enum):
    """测试类型"""
    FUNCTIONAL = "functional"
    UI = "ui"
    PERFORMANCE = "performance"
    SECURITY = "security"
    INTEGRATION = "integration"


class TestPriority(Enum):
    """测试优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TestStatus(Enum):
    """测试状态"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestStrategy(Enum):
    """测试策略"""
    BASIC = "basic"
    BOUNDARY = "boundary"
    EQUIVALENCE = "equivalence"
    NEGATIVE = "negative"
    COMPREHENSIVE = "comprehensive"


@dataclass
class TestData:
    """测试数据"""
    id: str
    input_value: Any
    expected_value: Any
    assertion_functions: List[Union[str, tuple]]  # 断言函数数组，支持字符串或元组
    description: str
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestData':
        """从字典创建"""
        data['created_at'] = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        return cls(**data)


@dataclass
class TestViewpoint:
    """测试观点"""
    id: str
    name: str
    strategy: TestStrategy
    description: str
    target_node: PageNode
    test_data_list: List[TestData]
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def add_test_data(self, test_data: TestData):
        """添加测试数据"""
        self.test_data_list.append(test_data)

    def remove_test_data(self, test_data_id: str):
        """移除测试数据"""
        self.test_data_list = [td for td in self.test_data_list if td.id != test_data_id]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['strategy'] = self.strategy.value
        data['target_node'] = self.target_node.dict() if self.target_node else None
        data['test_data_list'] = [td.to_dict() for td in self.test_data_list]
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestViewpoint':
        """从字典创建"""
        from models.page_node import PageNode

        data['strategy'] = TestStrategy(data['strategy'])
        data['target_node'] = PageNode.parse_obj(data['target_node']) if data.get('target_node') else None
        data['test_data_list'] = [TestData.from_dict(td) for td in data.get('test_data_list', [])]
        data['created_at'] = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        return cls(**data)


@dataclass
class TestCase:
    """测试用例"""
    id: str
    name: str
    description: str
    test_type: TestType
    priority: TestPriority
    page_url: str
    viewpoints: List[TestViewpoint]  # 测试观点列表
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def add_viewpoint(self, viewpoint: TestViewpoint):
        """添加测试观点"""
        self.viewpoints.append(viewpoint)
        self.updated_at = datetime.now()

    def remove_viewpoint(self, viewpoint_id: str):
        """移除测试观点"""
        self.viewpoints = [vp for vp in self.viewpoints if vp.id != viewpoint_id]
        self.updated_at = datetime.now()

    def get_viewpoint(self, viewpoint_id: str) -> Optional[TestViewpoint]:
        """获取测试观点"""
        for viewpoint in self.viewpoints:
            if viewpoint.id == viewpoint_id:
                return viewpoint
        return None

    def get_all_test_data(self) -> List[TestData]:
        """获取所有测试数据"""
        all_test_data = []
        for viewpoint in self.viewpoints:
            all_test_data.extend(viewpoint.test_data_list)
        return all_test_data

    def get_test_data_count(self) -> int:
        """获取测试数据总数"""
        return len(self.get_all_test_data())

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['test_type'] = self.test_type.value
        data['priority'] = self.priority.value
        data['viewpoints'] = [vp.to_dict() for vp in self.viewpoints]
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestCase':
        """从字典创建"""
        # 兼容旧数据格式：忽略steps字段
        if 'steps' in data:
            data.pop('steps')

        data['test_type'] = TestType(data['test_type'])
        data['priority'] = TestPriority(data['priority'])
        data['viewpoints'] = [TestViewpoint.from_dict(vp) for vp in data.get('viewpoints', [])]
        data['created_at'] = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        data['updated_at'] = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        return cls(**data)

    def save_to_file(self, filepath: str):
        """保存到文件"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str) -> 'TestCase':
        """从文件加载"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)


# 表格格式转换函数
def to_table_format_list(items: List[Any]) -> Dict[str, Any]:
    """将对象列表转换为表格格式"""
    if not items:
        return {'headers': [], 'rows': []}

    # 获取第一个对象的字段
    first_item = items[0]
    if hasattr(first_item, 'to_dict'):
        data_dict = first_item.to_dict()
    else:
        data_dict = first_item.__dict__

    headers = list(data_dict.keys())

    rows = []
    for item in items:
        if hasattr(item, 'to_dict'):
            row_data = item.to_dict()
        else:
            row_data = item.__dict__

        row = []
        for header in headers:
            value = row_data.get(header, '')
            if isinstance(value, datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(value, (list, dict)):
                value = str(value)[:50] + '...' if len(str(value)) > 50 else str(value)
            row.append(value)
        rows.append(row)

    return {'headers': headers, 'rows': rows}


def get_default_headers(item_type: str) -> List[str]:
    """获取默认表头"""
    if item_type == 'test_case':
        return ['ID', '名称', '描述', '类型', '优先级', '页面URL', '测试观点数', '测试数据数', '创建时间', '更新时间']
    elif item_type == 'test_viewpoint':
        return ['ID', '名称', '策略', '描述', '目标节点', '测试数据数', '创建时间']
    elif item_type == 'test_data':
        return ['ID', '输入值', '预期值', '断言函数', '描述', '创建时间']
    else:
        return []
