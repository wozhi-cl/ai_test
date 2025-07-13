import asyncio
import os
import json
from typing import List, Dict, Any, Optional
from models.page_node import PageStructure, PageNode
from utils.playwright_utils import PlaywrightUtils
import uuid
from datetime import datetime
from models.page_node import NodeType


class PageParser:
    """页面解析器"""

    def __init__(self, data_dir: str = "data/page_nodes"):
        self.data_dir = data_dir
        self.playwright_utils = PlaywrightUtils()
        os.makedirs(data_dir, exist_ok=True)

    async def parse_page_from_url(self, url: str, headless: bool = True) -> PageStructure:
        """从URL解析页面"""
        try:
            await self.playwright_utils.start_browser(headless=headless)
            page_structure = await self.playwright_utils.parse_page_structure(url)

            # 保存页面结构
            self.save_page_structure(page_structure)

            return page_structure
        finally:
            await self.playwright_utils.close_browser()

    async def parse_page_from_playwright_script(self, script_path: str, headless: bool = True) -> PageStructure:
        """从Playwright录制脚本解析页面"""
        try:
            await self.playwright_utils.start_browser(headless=headless)

            # 读取并执行Playwright脚本
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()

            # 这里可以解析Playwright脚本并提取页面信息
            # 简化实现：假设脚本包含URL信息
            url = self._extract_url_from_script(script_content)

            if url:
                page_structure = await self.playwright_utils.parse_page_structure(url)
                self.save_page_structure(page_structure)
                return page_structure
            else:
                raise Exception("无法从脚本中提取URL信息")

        finally:
            await self.playwright_utils.close_browser()

    def _extract_url_from_script(self, script_content: str) -> Optional[str]:
        """从Playwright脚本中提取URL"""
        # 简单的URL提取逻辑，可以根据实际脚本格式调整
        lines = script_content.split('\n')
        for line in lines:
            if 'goto(' in line:
                # 提取goto()中的URL
                start = line.find('goto(') + 5
                end = line.find(')', start)
                if start > 4 and end > start:
                    url = line[start:end].strip().strip("'\"")
                    return url
        return None

    def save_page_structure(self, page_structure: PageStructure):
        """保存页面结构"""
        filename = f"{page_structure.id}.json"
        filepath = os.path.join(self.data_dir, filename)
        page_structure.save_to_file(filepath)

    def load_page_structure(self, structure_id: str) -> Optional[PageStructure]:
        """加载页面结构"""
        filepath = os.path.join(self.data_dir, f"{structure_id}.json")
        if os.path.exists(filepath):
            return PageStructure.load_from_file(filepath)
        return None

    def list_page_structures(self) -> Dict[str, Any]:
        """列出所有页面结构（返回 { headers: [], rows: [] } 格式）"""
        from models import to_table_format_list, get_default_headers

        structures = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.data_dir, filename)
                try:
                    structure = PageStructure.load_from_file(filepath)
                    structures.append(structure)
                except Exception as e:
                    print(f"加载页面结构失败 {filename}: {e}")

        # 按创建时间倒序排列
        structures.sort(key=lambda x: x.created_at, reverse=True)

        # 转换为表格格式
        if structures:
            return to_table_format_list(structures)
        else:
            return {'headers': get_default_headers('page_structure'), 'rows': []}

    def delete_page_structure(self, structure_id: str) -> bool:
        """删除页面结构"""
        filepath = os.path.join(self.data_dir, f"{structure_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

    def get_interactive_nodes(self, structure_id: str) -> List[PageNode]:
        """获取可交互的节点"""
        structure = self.load_page_structure(structure_id)
        if structure:
            return [node for node in structure.nodes if node.is_interactive]
        return []

    def get_nodes_by_type(self, structure_id: str, node_type: str) -> List[PageNode]:
        """根据类型获取节点"""
        structure = self.load_page_structure(structure_id)
        if structure:
            return [node for node in structure.nodes if node.type.value == node_type]
        return []

    def search_nodes(self, structure_id: str, keyword: str) -> List[PageNode]:
        """搜索节点"""
        structure = self.load_page_structure(structure_id)
        if structure:
            keyword_lower = keyword.lower()
            return [
                node for node in structure.nodes
                if (node.text_content and keyword_lower in node.text_content.lower()) or
                   (node.xpath and keyword_lower in node.xpath.lower()) or
                   (node.css_selector and keyword_lower in node.css_selector.lower())
            ]
        return []

    def get_node_hierarchy(self, structure_id: str) -> Dict[str, Any]:
        """获取节点层级结构"""
        structure = self.load_page_structure(structure_id)
        if not structure:
            return {}

        # 构建节点树
        node_dict = {node.id: node for node in structure.nodes}
        root_nodes = []

        for node in structure.nodes:
            if not node.parent_id:
                root_nodes.append(self._build_node_tree(node, node_dict))

        return {
            'structure_id': structure_id,
            'url': structure.url,
            'title': structure.title,
            'root_nodes': root_nodes
        }

    def _build_node_tree(self, node: PageNode, node_dict: Dict[str, PageNode]) -> Dict[str, Any]:
        """构建节点树"""
        tree_node = {
            'id': node.id,
            'type': node.type.value,
            'tag_name': node.tag_name,
            'text_content': node.text_content,
            'xpath': node.xpath,
            'is_interactive': node.is_interactive,
            'children': []
        }

        for child_id in node.children:
            if child_id in node_dict:
                child_node = node_dict[child_id]
                tree_node['children'].append(self._build_node_tree(child_node, node_dict))

        return tree_node

    def export_page_structure(self, structure_id: str, format: str = 'json') -> str:
        """导出页面结构"""
        structure = self.load_page_structure(structure_id)
        if not structure:
            raise Exception("页面结构不存在")

        if format == 'json':
            return json.dumps(structure.to_dict(), ensure_ascii=False, indent=2)
        elif format == 'csv':
            return self._export_to_csv(structure)
        else:
            raise Exception(f"不支持的导出格式: {format}")

    def _export_to_csv(self, structure: PageStructure) -> str:
        """导出为CSV格式"""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # 写入表头
        writer.writerow([
            'ID', 'Type', 'Tag Name', 'Text Content', 'XPath',
            'CSS Selector', 'Is Interactive', 'Is Visible'
        ])

        # 写入数据
        for node in structure.nodes:
            writer.writerow([
                node.id,
                node.type.value,
                node.tag_name,
                node.text_content or '',
                node.xpath,
                node.css_selector or '',
                node.is_interactive,
                node.is_visible
            ])

        return output.getvalue()

    async def parse_forms_from_url(self, url: str, headless: bool = True) -> PageStructure:
        """专门解析页面中的表单元素"""
        try:
            await self.playwright_utils.start_browser(headless=headless)

            # 获取表单结构信息
            form_structure = await self.playwright_utils.extract_form_structure(url)

            # 获取所有可测试节点
            page_structure = await self.playwright_utils.parse_page_structure(url)

            # 过滤出表单相关的节点
            form_nodes = []
            for node in page_structure.nodes:
                # 包含表单元素、按钮、输入框等
                if (node.type in [NodeType.FORM, NodeType.INPUT, NodeType.BUTTON, NodeType.SELECT, NodeType.CHECKBOX, NodeType.RADIO] or
                    node.tag_name in ['form', 'input', 'button', 'select', 'textarea'] or
                    'form' in node.attributes.get('class', '').lower() or
                    node.attributes.get('role') == 'button'):
                    form_nodes.append(node)

            # 创建专门的表单页面结构
            form_page_structure = PageStructure(
                id=f"forms_{page_structure.id}",
                url=url,
                title=f"表单结构 - {page_structure.title}",
                nodes=form_nodes,
                screenshot_path=page_structure.screenshot_path
            )

            # 保存表单结构
            self.save_page_structure(form_page_structure)

            return form_page_structure

        finally:
            await self.playwright_utils.close_browser()

    def get_form_fields(self, structure_id: str) -> List[Dict[str, Any]]:
        """获取表单字段信息"""
        structure = self.load_page_structure(structure_id)
        if not structure:
            return []

        form_fields = []
        for node in structure.nodes:
            if node.type in [NodeType.INPUT, NodeType.SELECT, NodeType.CHECKBOX, NodeType.RADIO]:
                field_info = {
                    'id': node.id,
                    'name': node.attributes.get('name', ''),
                    'type': node.attributes.get('type', node.type.value),
                    'placeholder': node.attributes.get('placeholder', ''),
                    'required': node.attributes.get('required', False),
                    'value': node.attributes.get('value', ''),
                    'selector': node.css_selector or node.xpath,
                    'is_interactive': node.is_interactive
                }
                form_fields.append(field_info)

        return form_fields

    def get_form_buttons(self, structure_id: str) -> List[Dict[str, Any]]:
        """获取表单按钮信息"""
        structure = self.load_page_structure(structure_id)
        if not structure:
            return []

        buttons = []
        for node in structure.nodes:
            if node.type == NodeType.BUTTON or node.tag_name == 'button':
                button_info = {
                    'id': node.id,
                    'name': node.attributes.get('name', ''),
                    'type': node.attributes.get('type', 'button'),
                    'text': node.text_content or node.attributes.get('value', ''),
                    'selector': node.css_selector or node.xpath,
                    'is_interactive': node.is_interactive
                }
                buttons.append(button_info)

        return buttons
