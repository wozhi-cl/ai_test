from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import json
from datetime import datetime
from .test_case import TestCase


class TestStatus(str, Enum):
    """测试状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class AssertionResult(BaseModel):
    """断言结果模型"""
    assertion_type: str = Field(..., description="断言类型")
    expected_value: Any = Field(..., description="期望值")
    actual_value: Any = Field(..., description="实际值")
    passed: bool = Field(..., description="是否通过")
    message: Optional[str] = Field(None, description="断言消息")
    execution_time: float = Field(..., description="执行时间(秒)")

    def to_table_format(self) -> Dict[str, Any]:
        """转换为表格格式 { headers: [], rows: [] }"""
        return {
            'headers': ['断言类型', '期望值', '实际值', '是否通过', '消息', '执行时间'],
            'rows': [[
                self.assertion_type,
                str(self.expected_value),
                str(self.actual_value),
                self.passed,
                self.message or '',
                f"{self.execution_time:.3f}s"
            ]]
        }


class TestStepResult(BaseModel):
    """测试步骤结果模型"""
    step_id: str = Field(..., description="步骤ID")
    step_number: int = Field(..., description="步骤序号")
    action: str = Field(..., description="操作类型")
    status: TestStatus = Field(..., description="执行状态")
    start_time: datetime = Field(..., description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    duration: Optional[float] = Field(None, description="执行时长(秒)")
    input_data: Optional[str] = Field(None, description="输入数据")
    output_data: Optional[str] = Field(None, description="输出数据")
    assertions: List[AssertionResult] = Field(default_factory=list, description="断言结果")
    error_message: Optional[str] = Field(None, description="错误信息")
    screenshot_path: Optional[str] = Field(None, description="截图路径")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def to_table_format(self) -> Dict[str, Any]:
        """转换为表格格式 { headers: [], rows: [] }"""
        return {
            'headers': ['步骤ID', '步骤号', '操作', '状态', '开始时间', '结束时间', '时长', '输入数据', '输出数据', '错误信息'],
            'rows': [[
                self.step_id,
                self.step_number,
                self.action,
                self.status.value,
                self.start_time.isoformat(),
                self.end_time.isoformat() if self.end_time else '',
                self.duration or 0,
                self.input_data or '',
                self.output_data or '',
                self.error_message or ''
            ]]
        }


class TestExecution(BaseModel):
    """测试执行模型"""
    id: str = Field(..., description="执行唯一标识")
    test_case_id: str = Field(..., description="测试用例ID")
    test_case_name: str = Field(..., description="测试用例名称")
    status: TestStatus = Field(..., description="执行状态")
    start_time: datetime = Field(..., description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    duration: Optional[float] = Field(None, description="执行时长(秒)")
    step_results: List[TestStepResult] = Field(default_factory=list, description="步骤结果")
    total_steps: int = Field(..., description="总步骤数")
    passed_steps: int = Field(default=0, description="通过步骤数")
    failed_steps: int = Field(default=0, description="失败步骤数")
    error_message: Optional[str] = Field(None, description="错误信息")
    browser_info: Dict[str, str] = Field(default_factory=dict, description="浏览器信息")
    environment_info: Dict[str, str] = Field(default_factory=dict, description="环境信息")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def calculate_summary(self):
        """计算执行摘要"""
        self.total_steps = len(self.step_results)
        self.passed_steps = len([step for step in self.step_results if step.status == TestStatus.PASSED])
        self.failed_steps = len([step for step in self.step_results if step.status == TestStatus.FAILED])

        if self.end_time and self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()

    def to_table_format(self) -> Dict[str, Any]:
        """转换为表格格式 { headers: [], rows: [] }"""
        return {
            'headers': ['ID', '测试用例ID', '测试用例名称', '状态', '开始时间', '结束时间', '时长', '总步骤', '通过步骤', '失败步骤'],
            'rows': [[
                self.id,
                self.test_case_id,
                self.test_case_name,
                self.status.value,
                self.start_time.isoformat(),
                self.end_time.isoformat() if self.end_time else '',
                self.duration,
                self.total_steps,
                self.passed_steps,
                self.failed_steps
            ]]
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "test_case_id": self.test_case_id,
            "test_case_name": self.test_case_name,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "step_results": [step.dict() for step in self.step_results],
            "total_steps": self.total_steps,
            "passed_steps": self.passed_steps,
            "failed_steps": self.failed_steps,
            "error_message": self.error_message,
            "browser_info": self.browser_info,
            "environment_info": self.environment_info
        }

    def save_to_file(self, file_path: str):
        """保存到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load_from_file(cls, file_path: str) -> 'TestExecution':
        """从文件加载"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)


class TestSuite(BaseModel):
    """测试套件模型"""
    id: str = Field(..., description="测试套件唯一标识")
    name: str = Field(..., description="测试套件名称")
    description: Optional[str] = Field(None, description="测试套件描述")
    test_case_ids: List[str] = Field(default_factory=list, description="测试用例ID列表")
    executions: List[TestExecution] = Field(default_factory=list, description="执行记录")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "test_case_ids": self.test_case_ids,
            "executions": [execution.to_dict() for execution in self.executions],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def save_to_file(self, file_path: str):
        """保存到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load_from_file(cls, file_path: str) -> 'TestSuite':
        """从文件加载"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)

    def to_table_format(self) -> Dict[str, Any]:
        """转换为表格格式 { headers: [], rows: [] }"""
        return {
            'headers': ['ID', '名称', '描述', '测试用例数', '执行记录数', '创建时间', '更新时间'],
            'rows': [[
                self.id,
                self.name,
                self.description or '',
                len(self.test_case_ids),
                len(self.executions),
                self.created_at.isoformat(),
                self.updated_at.isoformat()
            ]]
        }
