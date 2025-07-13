from nicegui import ui
from core.test_generator import TestGenerator
from core.page_parser import PageParser
from models.test_case import TestType, TestPriority
import uuid


class TestGeneratorUI:
    """测试生成界面"""

    def __init__(self):
        self.test_generator = TestGenerator()
        self.page_parser = PageParser()
        self.selected_structure_id = None
        self.selected_nodes = []

    def create_interface(self):
        """创建界面"""
        # 设置页面标题
        ui.page_title('测试生成')

        # 创建导航栏
        with ui.header().classes('bg-primary text-white'):
            ui.button('返回主页', icon='home', on_click=self.go_home).classes('q-mr-md')
            ui.label('📝 测试生成').classes('text-h6')

        # 主内容区域
        with ui.column().classes('full-width q-pa-md'):
            # 生成测试用例区域
            with ui.card().classes('full-width q-mb-md'):
                ui.label('生成测试用例').classes('text-h6 q-mb-md')

                # 选择页面结构
                structures = self.page_parser.list_page_structures()
                if structures:
                    structure_options = [(s['title'], s['id']) for s in structures]
                    structure_select = ui.select('选择页面结构', options=structure_options).classes('q-mb-md')
                    ui.button('选择结构', on_click=lambda: self.select_structure(structure_select.value))
                else:
                    ui.label('请先解析页面结构').classes('text-caption text-grey')

            # 测试用例列表
            self.create_test_case_list()

    def select_structure(self, structure_id: str):
        """选择页面结构"""
        if not structure_id:
            ui.notify('请选择页面结构', type='warning')
            return

        self.selected_structure_id = structure_id
        self.show_node_selection()

    def show_node_selection(self):
        """显示节点选择界面"""
        if not self.selected_structure_id:
            return

        structure = self.page_parser.load_page_structure(self.selected_structure_id)
        if not structure:
            ui.notify('页面结构不存在', type='negative')
            return

        with ui.dialog() as dialog, ui.card().classes('q-pa-lg'):
            ui.label(f'选择节点生成测试用例: {structure.title}').classes('text-h6 q-mb-md')

            # 节点类型筛选
            with ui.row().classes('q-mb-md'):
                ui.button('全部', on_click=lambda: self.filter_nodes('all'))
                ui.button('可交互', on_click=lambda: self.filter_nodes('interactive'))
                ui.button('按钮', on_click=lambda: self.filter_nodes('button'))
                ui.button('输入框', on_click=lambda: self.filter_nodes('input'))
                ui.button('链接', on_click=lambda: self.filter_nodes('link'))

            # 节点列表
            with ui.scroll_area().classes('q-mb-md'):
                self.create_node_selection_list(structure.nodes)

            # 生成测试用例表单
            with ui.card().classes('q-mb-md'):
                ui.label('测试用例信息').classes('text-subtitle1 q-mb-sm')

                test_name_input = ui.input('测试用例名称', placeholder='请输入测试用例名称').classes('q-mb-sm')

                test_type_select = ui.select(
                    '测试类型',
                    options=[
                        ('功能测试', TestType.FUNCTIONAL.value),
                        ('UI测试', TestType.UI.value),
                        ('集成测试', TestType.INTEGRATION.value),
                        ('回归测试', TestType.REGRESSION.value)
                    ]
                ).classes('q-mb-sm')

                priority_select = ui.select(
                    '优先级',
                    options=[
                        ('高', TestPriority.HIGH.value),
                        ('中', TestPriority.MEDIUM.value),
                        ('低', TestPriority.LOW.value)
                    ]
                ).classes('q-mb-sm')

                description_input = ui.textarea('描述', placeholder='请输入测试用例描述').classes('q-mb-sm')

            with ui.row().classes('q-mt-md'):
                ui.button('生成测试用例', on_click=lambda: self.generate_test_case(
                    test_name_input.value,
                    test_type_select.value,
                    priority_select.value,
                    description_input.value,
                    dialog
                )).classes('bg-primary text-white')
                ui.button('取消', on_click=dialog.close)

    def create_node_selection_list(self, nodes):
        """创建节点选择列表"""
        for node in nodes:
            with ui.card().classes('q-mb-sm'):
                with ui.row().classes('items-center'):
                    ui.checkbox(
                        value=False,
                        on_change=lambda checked, n=node: self.toggle_node_selection(n, checked)
                    )

                    ui.icon(self.get_node_icon(node.type)).classes('text-blue q-mr-md')

                    with ui.column().classes('col'):
                        ui.label(f"{node.tag_name}: {node.text_content or node.xpath[:50]}").classes('text-subtitle2')
                        ui.label(f"类型: {node.type.value}, 可交互: {node.is_interactive}").classes('text-caption text-grey')

    def get_node_icon(self, node_type):
        """获取节点图标"""
        icon_map = {
            'button': 'smart_button',
            'input': 'input',
            'link': 'link',
            'text': 'text_fields',
            'image': 'image',
            'select': 'list',
            'checkbox': 'check_box',
            'radio': 'radio_button_checked',
            'table': 'table_chart',
            'form': 'dynamic_form',
            'div': 'view_agenda',
            'span': 'text_fields',
            'other': 'code'
        }
        return icon_map.get(node_type.value, 'code')

    def toggle_node_selection(self, node, checked: bool):
        """切换节点选择状态"""
        if checked:
            if node not in self.selected_nodes:
                self.selected_nodes.append(node)
        else:
            if node in self.selected_nodes:
                self.selected_nodes.remove(node)

    def filter_nodes(self, filter_type: str):
        """筛选节点"""
        if not self.selected_structure_id:
            return

        structure = self.page_parser.load_page_structure(self.selected_structure_id)
        if not structure:
            return

        if filter_type == 'all':
            filtered_nodes = structure.nodes
        elif filter_type == 'interactive':
            filtered_nodes = [node for node in structure.nodes if node.is_interactive]
        elif filter_type == 'button':
            filtered_nodes = [node for node in structure.nodes if node.type.value == 'button']
        elif filter_type == 'input':
            filtered_nodes = [node for node in structure.nodes if node.type.value == 'input']
        elif filter_type == 'link':
            filtered_nodes = [node for node in structure.nodes if node.type.value == 'link']
        else:
            filtered_nodes = structure.nodes

        ui.notify(f'找到 {len(filtered_nodes)} 个节点', type='info')

    def generate_test_case(self, test_name: str, test_type: str, priority: str, description: str, dialog):
        """生成测试用例"""
        if not test_name:
            ui.notify('请输入测试用例名称', type='warning')
            return

        if not self.selected_nodes:
            ui.notify('请选择至少一个节点', type='warning')
            return

        try:
            # 生成测试用例
            test_case = self.test_generator.generate_test_case_from_nodes(
                structure_id=self.selected_structure_id,
                node_ids=[node.id for node in self.selected_nodes],
                test_name=test_name,
                test_type=TestType(test_type),
                priority=TestPriority(priority),
                description=description
            )

            # 保存测试用例
            self.test_generator.save_test_case(test_case)

            ui.notify(f'测试用例生成成功: {test_case.name}', type='positive')
            dialog.close()

            # 刷新列表
            ui.open('/')
            self.create_interface()

        except Exception as e:
            ui.notify(f'测试用例生成失败: {str(e)}', type='negative')

    def create_test_case_list(self):
        """创建测试用例列表"""
        with ui.card().classes('full-width'):
            ui.label('测试用例列表').classes('text-h6 q-mb-md')

            # 获取测试用例列表
            test_cases = self.test_generator.list_test_cases()

            if test_cases:
                for test_case in test_cases:
                    with ui.card().classes('full-width q-mb-sm'):
                        with ui.row().classes('items-center'):
                            ui.icon('playlist_add').classes('text-green q-mr-md')
                            with ui.column().classes('col'):
                                ui.label(test_case['name']).classes('text-subtitle1')
                                ui.label(test_case['description'] or '无描述').classes('text-caption text-grey')
                                ui.label(f"类型: {test_case['test_type']}, 优先级: {test_case['priority']}, 步骤数: {test_case['step_count']}").classes('text-caption text-grey')
                                ui.label(f"更新时间: {test_case['updated_at'][:19]}").classes('text-caption text-grey')

                            with ui.row().classes('q-ml-auto'):
                                ui.button('查看', on_click=lambda t=test_case: self.view_test_case(t['id'])).classes('q-btn--small')
                                ui.button('编辑', on_click=lambda t=test_case: self.edit_test_case(t['id'])).classes('q-btn--small')
                                ui.button('删除', on_click=lambda t=test_case: self.delete_test_case(t['id'])).classes('bg-negative text-white q-btn--small')
            else:
                ui.label('暂无测试用例数据').classes('text-caption text-grey q-mt-xl')

    def view_test_case(self, test_case_id: str):
        """查看测试用例"""
        test_case = self.test_generator.load_test_case(test_case_id)
        if not test_case:
            ui.notify('测试用例不存在', type='negative')
            return

        with ui.dialog() as dialog, ui.card().classes('q-pa-lg'):
            ui.label(f'测试用例详情: {test_case.name}').classes('text-h6 q-mb-md')

            # 基本信息
            with ui.card().classes('q-mb-md'):
                ui.label('基本信息').classes('text-subtitle1 q-mb-sm')
                ui.label(f'名称: {test_case.name}')
                ui.label(f'描述: {test_case.description or "无描述"}')
                ui.label(f'类型: {test_case.test_type.value}')
                ui.label(f'优先级: {test_case.priority.value}')
                ui.label(f'页面URL: {test_case.page_url}')
                ui.label(f'步骤数: {len(test_case.steps)}')
                ui.label(f'创建时间: {test_case.created_at}')
                ui.label(f'更新时间: {test_case.updated_at}')

            # 测试步骤
            with ui.card():
                ui.label('测试步骤').classes('text-subtitle1 q-mb-sm')

                for step in test_case.steps:
                    with ui.card().classes('q-mb-sm'):
                        with ui.row().classes('items-center'):
                            ui.label(f"步骤 {step.step_number}").classes('text-caption text-grey')
                            ui.label(step.action).classes('text-subtitle2 q-ml-md')

                            if step.target_node:
                                ui.label(f"目标: {step.target_node.tag_name}").classes('text-caption text-grey q-ml-md')

                            if step.input_data:
                                ui.label(f"输入: {step.input_data}").classes('text-caption text-grey q-ml-md')

            with ui.row().classes('q-mt-md'):
                ui.button('导出JSON', on_click=lambda: self.export_test_case(test_case_id, 'json'))
                ui.button('导出CSV', on_click=lambda: self.export_test_case(test_case_id, 'csv'))
                ui.button('关闭', on_click=dialog.close)

    def edit_test_case(self, test_case_id: str):
        """编辑测试用例"""
        ui.notify('编辑功能开发中...', type='info')

    def delete_test_case(self, test_case_id: str):
        """删除测试用例"""
        try:
            success = self.test_generator.delete_test_case(test_case_id)
            if success:
                ui.notify('测试用例删除成功', type='positive')
                # 刷新列表
                ui.open('/')
                self.create_interface()
            else:
                ui.notify('测试用例删除失败', type='negative')
        except Exception as e:
            ui.notify(f'删除失败: {str(e)}', type='negative')

    def export_test_case(self, test_case_id: str, format: str):
        """导出测试用例"""
        try:
            export_data = self.test_generator.export_test_case(test_case_id, format)
            ui.notify(f'测试用例已导出为 {format.upper()} 格式', type='positive')
        except Exception as e:
            ui.notify(f'导出失败: {str(e)}', type='negative')

    def go_home(self):
        """返回主页"""
        ui.open('/')
        from .main_ui import MainUI
        main_ui = MainUI()
        main_ui.create_main_interface()
