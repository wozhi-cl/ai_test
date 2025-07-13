from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import json
from datetime import datetime


class NodeType(str, Enum):
    """节点类型枚举"""
    BUTTON = "button"
    INPUT = "input"
    LINK = "link"
    TEXT = "text"
    IMAGE = "image"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TABLE = "table"
    FORM = "form"
    DIV = "div"
    SPAN = "span"
    OTHER = "other"


class PageNode(BaseModel):
    """页面节点模型"""
    id: str = Field(..., description="节点唯一标识")
    type: NodeType = Field(..., description="节点类型")
    tag_name: str = Field(..., description="HTML标签名")
    text_content: Optional[str] = Field(None, description="文本内容")
    attributes: Dict[str, str] = Field(default_factory=dict, description="HTML属性")
    xpath: str = Field(..., description="XPath路径")
    css_selector: Optional[str] = Field(None, description="CSS选择器")
    position: Dict[str, Union[int, float]] = Field(default_factory=dict, description="位置信息")
    size: Dict[str, Union[int, float]] = Field(default_factory=dict, description="尺寸信息")
    is_visible: bool = Field(True, description="是否可见")
    is_interactive: bool = Field(False, description="是否可交互")
    parent_id: Optional[str] = Field(None, description="父节点ID")
    children: List[str] = Field(default_factory=list, description="子节点ID列表")
    page_url: str = Field(..., description="页面URL")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

    @validator('position', 'size', pre=True)
    def convert_float_to_int(cls, v):
        """将浮点数转换为整数"""
        if isinstance(v, dict):
            return {k: int(float(val)) if isinstance(val, (int, float)) else val for k, val in v.items()}
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def to_table_format(self) -> Dict[str, Any]:
        """转换为表格格式 { headers: [], rows: [] }"""
        return {
            'headers': ['ID', '类型', '标签名', '文本内容', 'XPath', 'CSS选择器', '是否可见', '是否可交互'],
            'rows': [[
                self.id,
                self.type.value,
                self.tag_name,
                self.text_content or '',
                self.xpath,
                self.css_selector or '',
                self.is_visible,
                self.is_interactive
            ]]
        }

    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        if isinstance(d.get("created_at"), datetime):
            d["created_at"] = d["created_at"].isoformat()
        return d


class PageStructure(BaseModel):
    """页面结构模型"""
    id: str = Field(..., description="页面结构唯一标识")
    url: str = Field(..., description="页面URL")
    title: str = Field(..., description="页面标题")
    nodes: List[PageNode] = Field(default_factory=list, description="页面节点列表")
    screenshot_path: Optional[str] = Field(None, description="截图路径")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    def to_table_format(self) -> Dict[str, Any]:
        """转换为表格格式 { headers: [], rows: [] }"""
        return {
            'headers': ['ID', '标题', 'URL', '节点数', '创建时间'],
            'rows': [[
                self.id,
                self.title,
                self.url,
                len(self.nodes),
                self.created_at.isoformat()
            ]]
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "nodes": [node.dict() for node in self.nodes],
            "screenshot_path": self.screenshot_path,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else str(self.created_at),
            "updated_at": self.updated_at.isoformat() if self.updated_at and isinstance(self.updated_at, datetime) else None
        }

    def save_to_file(self, file_path: str):
        """保存到文件"""
        # 更新updated_at字段
        self.updated_at = datetime.now()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load_from_file(cls, file_path: str) -> 'PageStructure':
        """从文件加载"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 处理缺失的updated_at字段
        if 'updated_at' not in data:
            data['updated_at'] = None

        return cls(**data)
