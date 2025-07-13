from nicegui import ui
from core.page_parser import PageParser
from models.page_node import NodeType
import asyncio


class PageParserUI:
    """页面解析界面"""

    def __init__(self):
        self.page_parser = PageParser()
        self.current_structure = None

    def create_interface(self):
        """创建界面"""
        # 设置页面标题
        ui.page_title('页面解析')

        # 创建导航栏
        with ui.header().classes('bg-primary text-white'):
            ui.button('返回主页', icon='home', on_click=self.go_home).classes('q-mr-md')
            ui.label('🔍 页面解析').classes('text-h6')

        # 主内容区域
        with ui.column().classes('full-width q-pa-md'):
            # 解析页面区域
            with ui.card().classes('full-width q-mb-md'):
                ui.label('解析页面').classes('text-h6 q-mb-md')

                with ui.row().classes('q-gutter-md'):
                    url_input = ui.input('页面URL', placeholder='请输入要解析的页面URL').classes('col')
                    headless_checkbox = ui.checkbox('无头模式', value=True)
                    ui.button('解析页面', icon='search', on_click=lambda: self.parse_page(url_input.value, headless_checkbox.value)).classes('bg-primary text-white')

            # 页面结构列表
            self.create_structure_list()

    def create_structure_list(self):
        """创建页面结构列表（表格形式）"""
        with ui.card().classes('full-width'):
            ui.label('页面结构列表').classes('text-h6 q-mb-md')

            # 获取页面结构列表
            structures = self.page_parser.list_page_structures()

            if structures:
                with ui.column().classes('w-full'):
                    # 表头
                    with ui.row().classes('w-full items-center bg-blue-1 text-bold').style('border-bottom:1px solid #ccc;'):
                        ui.label('标题').style('min-width:160px;max-width:300px;flex:2')
                        ui.label('URL').style('min-width:220px;max-width:400px;flex:3')
                        ui.label('节点数').style('min-width:60px;max-width:80px;flex:1')
                        ui.label('创建时间').style('min-width:140px;max-width:200px;flex:2')
                        ui.label('操作').style('min-width:180px;max-width:220px;flex:2')
                    # 表体
                    with ui.scroll_area().style('max-height: 350px;'):
                        for s in structures:
                            with ui.row().classes('w-full items-center').style('border-bottom:1px solid #eee;'):
                                ui.label(s['title']).style('min-width:160px;max-width:300px;flex:2')
                                ui.label(s['url']).style('min-width:220px;max-width:400px;flex:3')
                                ui.label(str(s['node_count'])).style('min-width:60px;max-width:80px;flex:1')
                                ui.label(s['created_at'][:19]).style('min-width:140px;max-width:200px;flex:2')
                                with ui.row().style('min-width:180px;max-width:220px;flex:2'):
                                    ui.button('查看', on_click=lambda s=s: self.view_structure(s['id'])).classes('q-btn--dense q-btn--flat q-mx-xs')
                                    ui.button('删除', on_click=lambda s=s: self.delete_structure(s['id'])).classes('q-btn--dense q-btn--flat q-mx-xs bg-negative text-white')
            else:
                ui.label('暂无页面结构数据').classes('text-caption text-grey q-mt-xl')

    async def parse_page(self, url: str, headless: bool):
        """解析页面"""
        if not url:
            ui.notify('请输入页面URL', type='warning')
            return

        try:
            ui.notify('正在解析页面...', type='info')
            page_structure = await self.page_parser.parse_page_from_url(url, headless=headless)
            ui.notify(f'页面解析成功: {page_structure.title}', type='positive')

            # 刷新列表
            ui.open('/')
            self.create_interface()
        except Exception as e:
            ui.notify(f'页面解析失败: {str(e)}', type='negative')

    def view_structure(self, structure_id: str):
        """查看页面结构"""
        structure = self.page_parser.load_page_structure(structure_id)
        if not structure:
            ui.notify('页面结构不存在', type='negative')
            return

        self.current_structure = structure
        self.show_structure_details()

    def show_structure_details(self):
        """显示页面结构详情"""
        if not self.current_structure:
            return

        with ui.dialog() as dialog, ui.card().classes('q-pa-lg'):
            ui.label(f'页面结构详情: {self.current_structure.title}').classes('text-h6 q-mb-md')

            # 基本信息
            with ui.card().classes('q-mb-md'):
                ui.label('基本信息').classes('text-subtitle1 q-mb-sm')
                ui.label(f'URL: {self.current_structure.url}')
                ui.label(f'标题: {self.current_structure.title}')
                ui.label(f'节点数: {len(self.current_structure.nodes)}')
                ui.label(f'创建时间: {self.current_structure.created_at}')

            # 节点统计
            node_stats = self.get_node_statistics()
            with ui.card().classes('q-mb-md'):
                ui.label('节点统计').classes('text-subtitle1 q-mb-sm')
                with ui.row().classes('q-gutter-md'):
                    for node_type, count in node_stats.items():
                        with ui.card().classes('bg-blue-1'):
                            ui.label(str(count)).classes('text-h6 text-blue')
                            ui.label(node_type).classes('text-caption')

            # 节点列表
            with ui.card():
                ui.label('节点列表').classes('text-subtitle1 q-mb-sm')

                # 搜索框
                search_input = ui.input('搜索节点', placeholder='输入关键词搜索').classes('q-mb-md')
                ui.button('搜索', on_click=lambda: self.search_nodes(search_input.value))

                # 节点类型筛选
                node_types = [t.value for t in NodeType]
                type_select = ui.select('节点类型', options=[(t, t) for t in node_types]).classes('q-mb-md')
                ui.button('筛选', on_click=lambda: self.filter_nodes_by_type(type_select.value))

                # 节点列表
                self.create_node_list()

            with ui.row().classes('q-mt-md'):
                ui.button('导出JSON', on_click=lambda: self.export_structure('json'))
                ui.button('导出CSV', on_click=lambda: self.export_structure('csv'))
                ui.button('关闭', on_click=dialog.close)
        dialog.open()

    def get_node_statistics(self):
        """获取节点统计信息"""
        if not self.current_structure:
            return {}

        stats = {}
        for node in self.current_structure.nodes:
            node_type = node.type.value
            stats[node_type] = stats.get(node_type, 0) + 1

        return stats

    def create_node_list(self):
        """创建节点列表"""
        if not self.current_structure:
            return

        # 这里可以创建一个可滚动的节点列表
        # 由于节点可能很多，建议使用虚拟滚动或分页
        with ui.scroll_area().classes('q-mt-md'):
            for i, node in enumerate(self.current_structure.nodes[:50]):  # 限制显示前50个节点
                with ui.card().classes('q-mb-sm'):
                    with ui.row().classes('items-center'):
                        ui.icon(self.get_node_icon(node.type)).classes('text-blue q-mr-md')
                        with ui.column().classes('col'):
                            ui.label(f"{node.tag_name}: {node.text_content or node.xpath[:50]}").classes('text-subtitle2')
                            ui.label(f"类型: {node.type.value}, 可交互: {node.is_interactive}").classes('text-caption text-grey')

                        if node.is_interactive:
                            ui.button('选择', on_click=lambda n=node: self.select_node(n)).classes('q-btn--small')

    def get_node_icon(self, node_type: NodeType):
        """获取节点图标"""
        icon_map = {
            NodeType.BUTTON: 'smart_button',
            NodeType.INPUT: 'input',
            NodeType.LINK: 'link',
            NodeType.TEXT: 'text_fields',
            NodeType.IMAGE: 'image',
            NodeType.SELECT: 'list',
            NodeType.CHECKBOX: 'check_box',
            NodeType.RADIO: 'radio_button_checked',
            NodeType.TABLE: 'table_chart',
            NodeType.FORM: 'dynamic_form',
            NodeType.DIV: 'view_agenda',
            NodeType.SPAN: 'text_fields',
            NodeType.OTHER: 'code'
        }
        return icon_map.get(node_type, 'code')

    def search_nodes(self, keyword: str):
        """搜索节点"""
        if not self.current_structure or not keyword:
            return

        search_results = self.page_parser.search_nodes(self.current_structure.id, keyword)
        ui.notify(f'找到 {len(search_results)} 个匹配的节点', type='info')

    def filter_nodes_by_type(self, node_type: str):
        """根据类型筛选节点"""
        if not self.current_structure or not node_type:
            return

        filtered_nodes = self.page_parser.get_nodes_by_type(self.current_structure.id, node_type)
        ui.notify(f'找到 {len(filtered_nodes)} 个 {node_type} 类型的节点', type='info')

    def select_node(self, node):
        """选择节点"""
        ui.notify(f'已选择节点: {node.tag_name} - {node.text_content or node.xpath[:30]}', type='positive')

    def export_structure(self, format: str):
        """导出页面结构"""
        if not self.current_structure:
            ui.notify('没有选中的页面结构', type='warning')
            return

        try:
            export_data = self.page_parser.export_page_structure(self.current_structure.id, format)

            # 这里可以实现文件下载功能
            ui.notify(f'页面结构已导出为 {format.upper()} 格式', type='positive')

        except Exception as e:
            ui.notify(f'导出失败: {str(e)}', type='negative')

    def delete_structure(self, structure_id: str):
        """删除页面结构"""
        try:
            success = self.page_parser.delete_page_structure(structure_id)
            if success:
                ui.notify('页面结构删除成功', type='positive')
                # 刷新列表
                ui.open('/')
                self.create_interface()
            else:
                ui.notify('页面结构删除失败', type='negative')
        except Exception as e:
            ui.notify(f'删除失败: {str(e)}', type='negative')

    def go_home(self):
        """返回主页"""
        ui.open('/')
        from .main_ui import MainUI
        main_ui = MainUI()
        main_ui.create_main_interface()
