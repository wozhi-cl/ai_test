from nicegui import ui, app
from typing import Dict, Any, List
import asyncio
import uuid
import json
from core.page_parser import PageParser
from core.test_generator import TestGenerator
from core.test_runner import TestRunner
from core.report_generator import ReportGenerator
from models.test_case import TestType, TestPriority
from models.page_node import NodeType
from utils.assertion_utils import AssertionUtils
from datetime import datetime


class MainUI:
    """主界面类"""

    def __init__(self):
        self.page_parser = PageParser()
        self.test_generator = TestGenerator()
        self.test_runner = TestRunner()
        self.report_generator = ReportGenerator()

        # 状态变量
        self.current_structure_id = None
        self.current_test_case_id = None
        self.selected_nodes = []
        self.running_tests = False
        self.tab_index = '页面结构'
        self.tab_labels = ['页面结构', '测试用例', '执行记录']
        self.tab_table_container = None

    def create_main_interface(self):
        """创建主界面"""
        # 设置页面标题
        ui.page_title('自动化测试工具')

        # 创建导航栏
        with ui.header().classes('bg-primary text-white'):
            ui.label('🤖 自动化测试工具').classes('text-h6 q-ml-md')
            with ui.row().classes('q-ml-auto q-mr-md'):
                ui.button('页面解析', on_click=self.show_page_parser).classes('q-mr-sm')
                ui.button('测试生成', on_click=self.show_test_generator).classes('q-mr-sm')
                ui.button('测试运行', on_click=self.show_test_runner).classes('q-mr-sm')
                ui.button('报告查看', on_click=self.show_reports).classes('q-mr-sm')

        # 创建主内容区域
        with ui.column().classes('full-width q-pa-md'):

            # 快速操作区域
            with ui.card().classes('full-width q-mb-md'):
                ui.label('快速操作').classes('text-h6 q-mb-md')
                with ui.row().classes('q-gutter-md'):
                    ui.button('解析页面', icon='web', on_click=self.quick_parse_page).classes('bg-primary text-white')
                    ui.button('解析表单', icon='dynamic_form', on_click=self.quick_parse_forms).classes('bg-secondary text-white')
                    ui.button('生成测试', icon='playlist_add', on_click=self.quick_generate_test).classes('bg-positive text-white')
                    ui.button('运行测试', icon='play_arrow', on_click=self.quick_run_test).classes('bg-info text-white')
                    ui.button('查看报告', icon='assessment', on_click=self.quick_view_report).classes('bg-warning text-white')

            # 统计信息
            self.create_statistics_section()

            # 最近活动
            self.create_recent_activities_section()


    def create_statistics_section(self):
        """创建统计信息区域"""
        with ui.card().classes('full-width q-mb-md'):
            ui.label('统计信息').classes('text-h6 q-mb-md')

            # 获取统计数据
            page_structures = self.page_parser.list_page_structures()
            test_cases = self.test_generator.list_test_cases()
            executions = self.test_runner.list_executions()
            stats = self.test_runner.get_execution_statistics()

            with ui.row().classes('q-gutter-md'):
                # 页面结构统计
                with ui.card().classes('bg-blue-1'):
                    ui.label(f'{len(page_structures["rows"])}').classes('text-h4 text-blue')
                    ui.label('页面结构').classes('text-caption')

                # 测试用例统计
                with ui.card().classes('bg-green-1'):
                    ui.label(f'{len(test_cases["rows"])}').classes('text-h4 text-green')
                    ui.label('测试用例').classes('text-caption')

                # 执行记录统计
                with ui.card().classes('bg-orange-1'):
                    ui.label(f'{len(executions["rows"])}').classes('text-h4 text-orange')
                    ui.label('执行记录').classes('text-caption')

                # 成功率统计
                with ui.card().classes('bg-purple-1'):
                    ui.label(f'{stats.get("execution_success_rate", 0):.1f}%').classes('text-h4 text-purple')
                    ui.label('执行成功率').classes('text-caption')

    def create_recent_activities_section(self):
        """创建最近活动区域（index驱动表格联动，彻底兼容）"""
        with ui.card().classes('full-width'):
            ui.label('最近活动').classes('text-h6 q-mb-md')
            with ui.tabs(value=self.tab_index).classes('full-width') as tabs:
                ui.tab('页面结构', icon='web')
                ui.tab('测试用例', icon='playlist_add')
                ui.tab('执行记录', icon='play_arrow')

            def on_tab_change(e):
                self.tab_index = e.args  # e.args 就是 tab 的 label
                self.render_tab_table()

            tabs.on('update:model-value', on_tab_change)

            self.tab_table_container = ui.column().classes('full-width q-mt-md')
            self.render_tab_table()

    def render_tab_table(self):
        if self.tab_table_container:
            self.tab_table_container.clear()
        with self.tab_table_container:
            label = self.tab_index
            if label == '页面结构':
                self.create_page_structure_table()
            elif label == '测试用例':
                self.create_test_case_table()
            elif label == '执行记录':
                self.create_execution_table()

    def create_page_structure_table(self):
        """单独卡片展示页面结构表格"""
        with ui.card().classes('full-width q-mt-xl'):
            ui.label('页面结构列表').classes('text-h6 q-mb-md')
            structures_data = self.page_parser.list_page_structures()
            if structures_data['rows']:
                with ui.column().classes('w-full'):
                    # 表头
                    with ui.row().classes('w-full items-center bg-blue-1 text-bold').style('border-bottom:1px solid #ccc;'):
                        for header in structures_data['headers']:
                            ui.label(header).style('min-width:120px;max-width:200px;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;')
                        ui.label('操作').style('min-width:220px;max-width:280px;flex:2')
                    # 表体
                    with ui.scroll_area().style('max-height: 350px;'):
                        for row in structures_data['rows']:
                            with ui.row().classes('w-full items-center').style('border-bottom:1px solid #eee;'):
                                for cell in row:
                                    ui.label(str(cell)).style('min-width:120px;max-width:200px;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;')
                                with ui.row().style('min-width:220px;max-width:280px;flex:2'):
                                    ui.button('查看', on_click=lambda s=row: self.view_page_structure(s[0])).classes('q-btn--dense q-btn--flat q-mx-xs')
                                    ui.button('生成测试', on_click=lambda s=row: self.generate_test_from_structure(s[0])).classes('q-btn--dense q-btn--flat q-mx-xs bg-positive text-white')
                                    ui.button('删除', on_click=lambda s=row: self.delete_page_structure(s[0])).classes('q-btn--dense q-btn--flat q-mx-xs bg-negative text-white')
            else:
                ui.label('暂无页面结构数据').classes('text-caption text-grey q-mt-xl')

    def create_test_case_table(self):
        """测试用例表格（适配新数据格式）"""
        with ui.card().classes('full-width'):
            ui.label('测试用例列表').classes('text-h6 q-mb-md')
            test_cases_data = self.test_generator.list_test_cases()
            if test_cases_data['rows']:
                with ui.column().classes('w-full'):
                    with ui.row().classes('w-full items-center bg-blue-1 text-bold').style('border-bottom:1px solid #ccc;'):
                        for header in test_cases_data['headers']:
                            ui.label(header).style('min-width:100px;max-width:150px;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;')
                        ui.label('操作').style('min-width:280px;max-width:350px;flex:2')
                    with ui.scroll_area().style('max-height: 350px;'):
                        for row in test_cases_data['rows']:
                            with ui.row().classes('w-full items-center').style('border-bottom:1px solid #eee;'):
                                for cell in row:
                                    ui.label(str(cell)).style('min-width:100px;max-width:150px;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;')
                                with ui.row().style('min-width:280px;max-width:350px;flex:2'):
                                    ui.button('查看', on_click=lambda t=row: self.view_test_case(t[0])).classes('q-btn--dense q-btn--flat q-mx-xs')
                                    ui.button('执行', on_click=lambda t=row: self.execute_test_case(t[0])).classes('q-btn--dense q-btn--flat q-mx-xs bg-positive text-white')
                                    ui.button('编辑', on_click=lambda t=row: self.edit_test_case(t[0])).classes('q-btn--dense q-btn--flat q-mx-xs bg-warning text-white')
                                    ui.button('删除', on_click=lambda t=row: self.delete_test_case(t[0])).classes('q-btn--dense q-btn--flat q-mx-xs bg-negative text-white')
            else:
                ui.label('暂无测试用例数据').classes('text-caption text-grey q-mt-xl')

    def create_execution_table(self):
        """执行记录表格（适配新数据格式）"""
        with ui.card().classes('full-width'):
            ui.label('执行记录列表').classes('text-h6 q-mb-md')
            executions_data = self.test_runner.list_executions()
            if executions_data['rows']:
                with ui.column().classes('w-full'):
                    with ui.row().classes('w-full items-center bg-blue-1 text-bold').style('border-bottom:1px solid #ccc;'):
                        for header in executions_data['headers']:
                            ui.label(header).style('min-width:100px;max-width:150px;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;')
                        ui.label('操作').style('min-width:180px;max-width:220px;flex:2')
                    with ui.scroll_area().style('max-height: 350px;'):
                        for row in executions_data['rows']:
                            with ui.row().classes('w-full items-center').style('border-bottom:1px solid #eee;'):
                                for cell in row:
                                    ui.label(str(cell)).style('min-width:100px;max-width:150px;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;')
                                with ui.row().style('min-width:180px;max-width:220px;flex:2'):
                                    ui.button('查看', on_click=lambda e=row: self.view_execution(e[0])).classes('q-btn--dense q-btn--flat q-mx-xs')
            else:
                ui.label('暂无执行记录数据').classes('text-caption text-grey q-mt-xl')

    def show_page_parser(self):
        """显示页面解析界面"""
        ui.open('/')
        from .page_parser_ui import PageParserUI
        page_parser_ui = PageParserUI()
        page_parser_ui.create_interface()

    def show_test_generator(self):
        """显示测试生成界面"""
        ui.open('/')
        from .test_generator_ui import TestGeneratorUI
        test_generator_ui = TestGeneratorUI()
        test_generator_ui.create_interface()

    def show_test_runner(self):
        """显示测试运行界面"""
        ui.open('/')
        from .test_runner_ui import TestRunnerUI
        test_runner_ui = TestRunnerUI()
        test_runner_ui.create_interface()

    def show_reports(self):
        """显示报告界面"""
        ui.open('/')
        self.create_reports_interface()

    def create_reports_interface(self):
        """创建报告界面"""
        # 设置页面标题
        ui.page_title('测试报告')

        # 创建导航栏
        with ui.header().classes('bg-primary text-white'):
            ui.button('返回主页', icon='home', on_click=self.create_main_interface).classes('q-mr-md')
            ui.label('📊 测试报告').classes('text-h6')

        # 主内容区域
        with ui.column().classes('full-width q-pa-md'):
            # 报告列表
            reports_data = self.report_generator.get_report_list()

            if reports_data['rows']:
                ui.label('测试报告列表').classes('text-h5 q-mb-md')

                for row in reports_data['rows']:
                    with ui.card().classes('full-width q-mb-md'):
                        with ui.row().classes('items-center'):
                            ui.icon('description').classes('text-blue q-mr-md')
                            ui.label(row[0]).classes('text-subtitle1')  # filename
                            ui.space()
                            ui.label(f"大小: {row[2]} bytes").classes('text-caption text-grey')  # size
                            ui.button('查看', on_click=lambda r=row: self.open_report(r[1])).classes('q-btn--small')  # filepath
                            ui.button('下载', on_click=lambda r=row: self.download_report(r[1])).classes('q-btn--small')  # filepath
            else:
                ui.label('暂无测试报告').classes('text-h6 text-grey q-mt-xl')

    def quick_parse_page(self):
        """快速解析页面"""
        with ui.dialog() as dialog, ui.card():
            ui.label('快速解析页面').classes('text-h6 q-mb-md')

            url_input = ui.input('页面URL', placeholder='请输入要解析的页面URL')

            with ui.row().classes('q-mt-md'):
                ui.button('取消', on_click=dialog.close)
                ui.button('解析', on_click=lambda: self.parse_page_async(url_input.value, dialog))
        dialog.open()

    async def parse_page_async(self, url: str, dialog):
        """异步解析页面"""
        if not url:
            ui.notify('请输入页面URL', type='warning')
            return

        try:
            ui.notify('正在解析页面...', type='info')
            page_structure = await self.page_parser.parse_page_from_url(url, headless=True)
            ui.notify(f'页面解析成功: {page_structure.title}', type='positive')
            dialog.close()
        except Exception as e:
            ui.notify(f'页面解析失败: {str(e)}', type='negative')

    def quick_generate_test(self):
        """快速生成测试"""
        # 获取页面结构列表
        structures_data = self.page_parser.list_page_structures()

        if not structures_data['rows']:
            ui.notify('请先解析页面结构', type='warning')
            return

        with ui.dialog() as dialog, ui.card():
            ui.label('快速生成测试').classes('text-h6 q-mb-md')

            structure_select = ui.select(
                label='选择页面结构',
                options=[(row[1], row[0]) for row in structures_data['rows']]  # (title, id)
            )

            test_name_input = ui.input('测试用例名称', placeholder='请输入测试用例名称')

            with ui.row().classes('q-mt-md'):
                ui.button('取消', on_click=dialog.close)
                ui.button('生成', on_click=lambda: self.generate_test_quick(
                    structure_select.value, test_name_input.value, dialog
                ))
        dialog.open()

    def generate_test_quick(self, structure_id: str, test_name: str, dialog):
        """快速生成测试用例"""
        if not structure_id or not test_name:
            ui.notify('请选择页面结构并输入测试用例名称', type='warning')
            return

        try:
            # 获取可交互的节点
            interactive_nodes = self.page_parser.get_interactive_nodes(structure_id)

            if not interactive_nodes:
                ui.notify('未找到可交互的节点', type='warning')
                return

            # 生成测试用例（一次性生成所有测试观点）
            test_case = self.test_generator.generate_test_case_from_nodes(
                structure_id=structure_id,
                node_ids=[node.id for node in interactive_nodes[:3]],  # 限制节点数量
                test_name=test_name,
                test_type=TestType.FUNCTIONAL,
                priority=TestPriority.MEDIUM,
                description="快速生成的综合测试用例"
            )

            # 保存测试用例
            self.test_generator.save_test_case(test_case)

            ui.notify(f'测试用例生成成功: {test_case.name} (包含{len(test_case.viewpoints)}个测试观点, {test_case.get_test_data_count()}个测试数据)', type='positive')
            dialog.close()

        except Exception as e:
            ui.notify(f'测试用例生成失败: {str(e)}', type='negative')

    def quick_run_test(self):
        """快速运行测试"""
        # 获取测试用例列表
        test_cases_data = self.test_generator.list_test_cases()

        if not test_cases_data['rows']:
            ui.notify('请先生成测试用例', type='warning')
            return

        with ui.dialog() as dialog, ui.card():
            ui.label('快速运行测试').classes('text-h6 q-mb-md')

            test_case_select = ui.select(
                label='选择测试用例',
                options=[(row[1], row[0]) for row in test_cases_data['rows']]  # (name, id)
            )

            headless_checkbox = ui.checkbox('无头模式')

            with ui.row().classes('q-mt-md'):
                ui.button('取消', on_click=dialog.close)
                ui.button('运行', on_click=lambda: self.run_test_quick(
                    test_case_select.value, headless_checkbox.value, dialog
                ))
        dialog.open()

    async def run_test_quick(self, test_case_id: str, headless: bool, dialog):
        """快速运行测试"""
        if not test_case_id:
            ui.notify('请选择测试用例', type='warning')
            return

        try:
            ui.notify('正在运行测试...', type='info')
            execution = await self.test_runner.run_test_case(test_case_id, headless=headless)

            # 生成报告
            report_path = self.report_generator.generate_html_report(execution.id)

            ui.notify(f'测试运行完成: {execution.test_case_name}', type='positive')
            dialog.close()

            # 显示结果
            self.show_test_result(execution, report_path)
        except Exception as e:
            ui.notify(f'测试运行失败: {str(e)}', type='negative')

    def show_test_result(self, execution, report_path: str):
        """显示测试结果"""
        with ui.dialog() as dialog, ui.card().classes('q-pa-lg'):
            ui.label('测试运行结果').classes('text-h6 q-mb-md')

            # 显示基本信息
            ui.label(f'测试用例: {execution.test_case_name}').classes('text-subtitle1')
            ui.label(f'状态: {execution.status.value}').classes('text-subtitle2')
            ui.label(f'总步骤: {execution.total_steps}, 通过: {execution.passed_steps}, 失败: {execution.failed_steps}').classes('text-caption')

            with ui.row().classes('q-mt-md'):
                ui.button('查看详细报告', on_click=lambda: self.open_report(report_path))
                ui.button('关闭', on_click=dialog.close)
        dialog.open()

    def quick_view_report(self):
        """快速查看报告"""
        reports_data = self.report_generator.get_report_list()

        if not reports_data['rows']:
            ui.notify('暂无测试报告', type='warning')
            return

        # 打开最新的报告
        latest_report = reports_data['rows'][0]
        self.open_report(latest_report[1])  # filepath

    def open_report(self, filepath: str):
        """打开报告"""
        import webbrowser
        import os

        if os.path.exists(filepath):
            webbrowser.open(f'file://{os.path.abspath(filepath)}')
        else:
            ui.notify('报告文件不存在', type='negative')

    def download_report(self, filepath: str):
        """下载报告"""
        import os

        if os.path.exists(filepath):
            # 这里可以实现文件下载功能
            ui.notify('下载功能开发中...', type='info')
        else:
            ui.notify('报告文件不存在', type='negative')

    def view_page_structure(self, structure_id: str):
        """查看页面结构详情并支持节点操作（美化表格+严格对齐）"""
        structure = self.page_parser.load_page_structure(structure_id)
        if not structure:
            ui.notify('页面结构不存在', type='negative')
            return

        # 节点类型统计
        node_stats = {}
        for node in structure.nodes:
            node_type = node.type.value
            node_stats[node_type] = node_stats.get(node_type, 0) + 1

        with ui.dialog() as dialog, ui.card().classes('q-pa-lg').style('min-width: 1100px; max-width: 1500px;'):
            ui.label(f'页面结构详情: {structure.title}').classes('text-h6 q-mb-md')
            ui.label(f'URL: {structure.url}').classes('text-caption')
            ui.label(f'节点数: {len(structure.nodes)}').classes('text-caption')
            ui.label(f'创建时间: {structure.created_at}').classes('text-caption')

            # 节点类型统计
            with ui.row().classes('q-gutter-md q-mb-md'):
                for node_type, count in node_stats.items():
                    with ui.card().classes('bg-blue-1'):
                        ui.label(str(count)).classes('text-h6 text-blue')
                        ui.label(node_type).classes('text-caption')

            ui.label('节点列表（前50个）').classes('text-subtitle1 q-mb-sm')
            with ui.column().classes('w-full'):
                # 添加节点按钮
                with ui.row().classes('q-mb-md'):
                    ui.button('新增节点', icon='add', on_click=lambda: self.add_new_node(structure, dialog)).classes('bg-primary text-white')
                    ui.button('批量操作', icon='settings', on_click=lambda: self.batch_operations(structure, dialog)).classes('bg-secondary text-white')

                # 表头
                with ui.row().classes('w-full items-center bg-blue-1 text-bold').style('border-bottom:1px solid #ccc;'):
                    ui.label('Tag').style('min-width:100px;max-width:120px;flex:1')
                    ui.label('类型').style('min-width:60px;max-width:80px;flex:1')
                    ui.label('选择器').style('min-width:220px;max-width:350px;flex:2')
                    ui.label('文本').style('min-width:120px;max-width:200px;flex:2')
                    ui.label('可交互').style('min-width:60px;max-width:80px;flex:1')
                    ui.label('操作').style('min-width:280px;max-width:350px;flex:2')
                # 表体
                with ui.scroll_area().style('max-height: 400px;'):
                    for node in structure.nodes[:50]:
                        with ui.row().classes('w-full items-center').style('border-bottom:1px solid #eee;'):
                            ui.label(node.tag_name).style('min-width:100px;max-width:120px;flex:1')
                            ui.label(node.type.value).style('min-width:60px;max-width:80px;flex:1')
                            ui.label(node.css_selector or node.xpath).classes('text-mono').style('min-width:220px;max-width:350px;flex:2')
                            ui.label(node.text_content or '').style('min-width:120px;max-width:200px;flex:2')
                            ui.label(str(node.is_interactive)).style('min-width:60px;max-width:80px;flex:1')
                            with ui.row().style('min-width:280px;max-width:350px;flex:2'):
                                ui.button('查看', on_click=lambda n=node: self.view_node_details(structure, n, dialog)).classes('q-btn--dense q-btn--flat q-mx-xs')
                                ui.button('编辑', on_click=lambda n=node: self.edit_node(structure, n, dialog)).classes('q-btn--dense q-btn--flat q-mx-xs')
                                ui.button('验证', on_click=lambda n=node: self.verify_selector(structure.url, n)).classes('q-btn--dense q-btn--flat q-mx-xs')
                                ui.button('删除', on_click=lambda n=node: self.delete_node(structure, n, dialog)).classes('q-btn--dense q-btn--flat q-mx-xs bg-negative text-white')

            with ui.row().classes('q-mt-md'):
                ui.button('关闭', on_click=dialog.close)
        dialog.open()

    def verify_selector(self, url, node):
        """验证选择器是否可用，并高亮节点"""
        async def do_verify():
            from utils.playwright_utils import PlaywrightUtils
            utils = PlaywrightUtils()
            try:
                await utils.start_browser(headless=False)
                await utils.navigate_to_page(url)
                selector = node.css_selector or node.xpath

                # 高亮节点
                found = await utils.highlight_element(selector)
                await utils.close_browser()

                # 直接调用ui.notify，不使用run_in_thread
                if found:
                    ui.notify(f'选择器可用并已高亮: {selector}', type='positive')
                else:
                    ui.notify(f'选择器未定位到元素: {selector}', type='warning')
            except Exception as e:
                ui.notify(f'验证失败: {str(e)}', type='negative')

        asyncio.create_task(do_verify())

    def complete_selector(self, node):
        """补全/推荐选择器"""
        # 简单示例：用tag+id+class组合
        tag = node.tag_name
        id_attr = node.attributes.get('id', '')
        class_attr = node.attributes.get('class', '')
        selector = tag
        if id_attr:
            selector += f'#{id_attr}'
        if class_attr:
            selector += '.' + '.'.join(class_attr.split())
        ui.notify(f'推荐选择器: {selector}', type='info')

    def edit_node_attributes(self, structure, node, parent_dialog):
        """编辑节点属性"""
        with ui.dialog() as dialog, ui.card().classes('q-pa-lg').style('min-width: 650px; max-width: 900px; min-height: 300px;'):
            ui.label(f'编辑节点属性: {node.tag_name}').classes('text-h6 q-mb-md')
            attr_inputs = {}
            for k, v in node.attributes.items():
                attr_inputs[k] = ui.input(k, value=v)
            new_attr_key = ui.input('新属性名')
            new_attr_val = ui.input('新属性值')
            def save():
                # 更新原有属性
                for k in attr_inputs:
                    node.attributes[k] = attr_inputs[k].value
                # 新增属性
                if new_attr_key.value:
                    node.attributes[new_attr_key.value] = new_attr_val.value
                # 保存到文件
                self.page_parser.save_page_structure(structure)
                ui.notify('属性已保存', type='positive')
                dialog.close()
                parent_dialog.close()
                self.view_page_structure(structure.id)
            ui.button('保存', on_click=save).classes('q-btn--small bg-primary text-white')
            ui.button('取消', on_click=dialog.close).classes('q-btn--small')
        dialog.open()

    def add_form_script(self, structure, node, parent_dialog):
        """为表单节点添加操作脚本"""
        with ui.dialog() as dialog, ui.card().classes('q-pa-lg').style('min-width: 650px; max-width: 900px; min-height: 300px;'):
            ui.label(f'添加表单操作脚本: {node.tag_name}').classes('text-h6 q-mb-md')
            script_input = ui.textarea('脚本内容', placeholder='如: await page.fill(...)')
            def save():
                node.attributes['custom_script'] = script_input.value
                self.page_parser.save_page_structure(structure)
                ui.notify('脚本已保存', type='positive')
                dialog.close()
                parent_dialog.close()
                self.view_page_structure(structure.id)
            ui.button('保存', on_click=save).classes('q-btn--small bg-primary text-white')
            ui.button('取消', on_click=dialog.close).classes('q-btn--small')
        dialog.open()

    def delete_node(self, structure, node, parent_dialog):
        """删除节点"""
        # 确认删除
        with ui.dialog() as confirm_dialog, ui.card():
            ui.label(f'确定要删除节点 "{node.tag_name}: {node.text_content or node.xpath[:30]}" 吗？').classes('text-h6 q-mb-md')
            with ui.row().classes('q-mt-md'):
                ui.button('取消', on_click=confirm_dialog.close).classes('q-btn--small')
                ui.button('删除', on_click=lambda: self._confirm_delete_node(structure, node, parent_dialog, confirm_dialog)).classes('q-btn--small bg-negative text-white')
        confirm_dialog.open()

    def _confirm_delete_node(self, structure, node, parent_dialog, confirm_dialog):
        """确认删除节点"""
        try:
            # 从节点列表中移除
            structure.nodes = [n for n in structure.nodes if n.id != node.id]

            # 更新父节点的children列表
            for parent_node in structure.nodes:
                if node.id in parent_node.children:
                    parent_node.children.remove(node.id)

            # 保存到文件
            self.page_parser.save_page_structure(structure)
            ui.notify(f'节点删除成功: {node.tag_name}', type='positive')

            # 关闭确认弹窗和当前弹窗，并重新打开页面结构详情
            confirm_dialog.close()
            parent_dialog.close()
            self.view_page_structure(structure.id)
        except Exception as e:
            ui.notify(f'节点删除失败: {str(e)}', type='negative')

    def view_test_case(self, test_case_id: str):
        """查看测试用例"""
        test_case = self.test_generator.load_test_case(test_case_id)
        if not test_case:
            ui.notify('测试用例不存在', type='negative')
            return

        with ui.dialog() as dialog, ui.card().classes('q-pa-lg').style('min-width: 1600px; max-width: 2000px; max-height: 95vh;'):
            ui.label(f'测试用例详情: {test_case.name}').classes('text-h6 q-mb-md')

            # 基本信息
            with ui.card().classes('q-mb-md'):
                ui.label('基本信息').classes('text-subtitle1 q-mb-sm')
                with ui.row().classes('q-gutter-md'):
                    ui.label(f'ID: {test_case.id}').classes('text-caption')
                    ui.label(f'类型: {test_case.test_type.value}').classes('text-caption')
                    ui.label(f'优先级: {test_case.priority.value}').classes('text-caption')
                    ui.label(f'页面URL: {test_case.page_url}').classes('text-caption')
                ui.label(f'描述: {test_case.description}').classes('text-caption')
                ui.label(f'创建时间: {test_case.created_at.strftime("%Y-%m-%d %H:%M:%S")}').classes('text-caption')
                ui.label(f'更新时间: {test_case.updated_at.strftime("%Y-%m-%d %H:%M:%S")}').classes('text-caption')

            # 测试观点列表 - 使用更大的滚动区域
            with ui.card().classes('q-mb-md').style('height: 70vh;width: 100%;'):
                with ui.row().classes('items-center w-full q-mb-md'):
                    ui.label(f'测试观点 ({len(test_case.viewpoints)})').classes('text-subtitle1')
                    ui.space()
                    ui.button('新增测试观点', icon='add', on_click=lambda: self.add_test_viewpoint(test_case, dialog)).classes('bg-primary text-white q-mr-sm')

                if test_case.viewpoints:
                    with ui.scroll_area().style('height: calc(70vh - 60px);'):
                        for i, viewpoint in enumerate(test_case.viewpoints):
                            with ui.card().classes('q-mb-md').style('border: 2px solid #e0e0e0; border-radius: 8px;'):
                                # 测试观点标题
                                with ui.row().classes('items-center w-full q-mb-md').style('background-color: #f5f5f5; padding: 8px; border-radius: 4px;'):
                                    ui.label(f'{i+1}. {viewpoint.name}').classes('text-h6 font-weight-bold')
                                    ui.space()
                                    ui.badge(viewpoint.strategy.value, color='primary').classes('text-caption')
                                    ui.label(f'({len(viewpoint.test_data_list)}个测试数据)').classes('text-caption text-grey q-ml-sm')
                                    ui.button('删除', icon='delete', on_click=lambda v=viewpoint, tc=test_case: self.delete_test_viewpoint(tc, v, dialog)).classes('q-btn--dense q-btn--flat q-mx-xs bg-negative text-white')

                                # 测试观点描述
                                ui.label(f'描述: {viewpoint.description}').classes('text-body2 q-mb-sm')

                                if viewpoint.target_node:
                                    ui.label(f'目标节点: {viewpoint.target_node.tag_name} ({viewpoint.target_node.type.value})').classes('text-body2 q-mb-md')

                                # 测试数据列表 - 可编辑的表格
                                with ui.row().classes('items-center w-full q-mb-sm'):
                                    ui.label('测试数据:').classes('text-subtitle2 font-weight-bold')
                                    ui.space()
                                    ui.button('新增测试数据', icon='add', on_click=lambda v=viewpoint, tc=test_case: self.add_test_data(tc, v, dialog)).classes('q-btn--dense q-btn--flat q-mx-xs bg-positive text-white')

                                # 使用可编辑的表格显示测试数据
                                with ui.card().classes('q-mb-md').style('height: 400px; overflow-y: auto; border: 1px solid #ddd;'):
                                    # 表头
                                    with ui.row().classes('w-full items-center bg-blue-1 text-bold').style('border-bottom:2px solid #ccc; padding: 10px; position: sticky; top: 0; z-index: 10; background-color: #e3f2fd;'):
                                        ui.label('序号').style('width: 80px; flex-shrink: 0; font-weight: bold;')
                                        ui.label('描述').style('width: 300px; flex-shrink: 0; font-weight: bold;')
                                        ui.label('输入值').style('width: 250px; flex-shrink: 0; font-weight: bold;')
                                        ui.label('预期值').style('width: 250px; flex-shrink: 0; font-weight: bold;')
                                        ui.label('断言函数').style('width: 400px; flex-shrink: 0; font-weight: bold;')
                                        ui.label('操作').style('width: 100px; flex-shrink: 0; font-weight: bold;')

                                    # 表体 - 可编辑的行
                                    for j, test_data in enumerate(viewpoint.test_data_list):
                                        with ui.row().classes('w-full items-center').style('border-bottom:1px solid #eee; padding: 8px; min-height: 60px;'):
                                            # 序号
                                            ui.label(str(j+1)).style('width: 80px; flex-shrink: 0; font-weight: bold;')

                                            # 描述
                                            ui.label(test_data.description).style('width: 300px; flex-shrink: 0; overflow:hidden;text-overflow:ellipsis;white-space:nowrap;')

                                            # 输入值 - 可编辑
                                            input_value_input = ui.input('', value=str(test_data.input_value)).style('width: 250px; flex-shrink: 0;')

                                            # 预期值 - 可编辑
                                            expected_value_input = ui.input('', value=str(test_data.expected_value)).style('width: 250px; flex-shrink: 0;')

                                            # 断言函数 - 下拉多选框
                                            assertion_functions = self._get_available_assertion_functions(viewpoint.target_node)
                                            assertion_select = ui.select(
                                                label='选择断言函数',
                                                options=assertion_functions,
                                                multiple=True,
                                                value=[func[0] for func in test_data.assertion_functions if isinstance(func, tuple)] + [func for func in test_data.assertion_functions if isinstance(func, str)]
                                            ).style('width: 400px; flex-shrink: 0;')

                                            # 断言函数参数容器
                                            assertion_params_container = ui.column().style('width: 400px; flex-shrink: 0;')

                                            # 操作按钮
                                            with ui.row().style('width: 100px; flex-shrink: 0;'):
                                                ui.button('删除', on_click=lambda td=test_data, v=viewpoint, tc=test_case: self.delete_test_data(tc, v, td, dialog)).classes('q-btn--dense q-btn--flat q-mx-xs bg-negative text-white')

                                            # 动态更新断言函数参数表单
                                            def update_assertion_params(selected_functions, container):
                                                container.clear()
                                                for func_name in selected_functions:
                                                    params = self._get_assertion_function_params(func_name)
                                                    if params:
                                                        with container:
                                                            ui.label(f'{func_name} 参数:').classes('text-caption font-weight-bold')
                                                            for param_name, param_info in params.items():
                                                                if param_info['type'] == 'int':
                                                                    ui.input(f'{param_name} ({param_info["description"]})', value=param_info.get('default', '')).style('width: 100%;')
                                                                elif param_info['type'] == 'str':
                                                                    ui.input(f'{param_name} ({param_info["description"]})', value=param_info.get('default', '')).style('width: 100%;')
                                                                elif param_info['type'] == 'bool':
                                                                    ui.checkbox(f'{param_name} ({param_info["description"]})', value=param_info.get('default', False))

                                            assertion_select.on('update:model-value', lambda e: update_assertion_params(e.args, assertion_params_container))
                else:
                    ui.label('暂无测试观点').classes('text-caption text-grey')

            # 统计信息
            with ui.card().classes('q-mb-md'):
                ui.label('统计信息').classes('text-subtitle1 q-mb-sm')
                total_test_data = test_case.get_test_data_count()
                ui.label(f'总测试数据: {total_test_data}').classes('text-caption')
                ui.label(f'测试观点数: {len(test_case.viewpoints)}').classes('text-caption')

            with ui.row().classes('q-mt-md'):
                ui.button('保存', on_click=lambda: self.save_test_case_changes(test_case, dialog)).classes('q-btn--small bg-primary text-white')
                ui.button('关闭', on_click=dialog.close).classes('q-btn--small')
        dialog.open()

    def add_test_viewpoint(self, test_case, parent_dialog):
        """新增测试观点"""
        with ui.dialog() as dialog, ui.card().classes('q-pa-lg').style('min-width: 650px; max-width: 900px; min-height: 300px;'):
            ui.label('新增测试观点').classes('text-h6 q-mb-md')

            name_input = ui.input('观点名称', placeholder='如: 基本功能测试')
            description_input = ui.textarea('观点描述', placeholder='描述这个测试观点的目的和范围')
            strategy_select = ui.select(
                label='测试策略',
                options=[('basic', '基本测试'), ('boundary', '边界值测试'), ('equivalence', '等价类测试'), ('exception', '异常测试'), ('comprehensive', '综合测试')],
                value='basic'
            )

            def save():
                from models.test_case import TestViewpoint
                from models.test_case import TestStrategy

                new_viewpoint = TestViewpoint(
                    id=str(uuid.uuid4()),
                    name=name_input.value,
                    description=description_input.value,
                    strategy=TestStrategy(strategy_select.value),
                    target_node=None,  # 可以后续设置
                    test_data_list=[],
                    created_at=datetime.now()
                )

                test_case.viewpoints.append(new_viewpoint)
                ui.notify('测试观点已添加', type='positive')
                dialog.close()
                parent_dialog.close()
                self.view_test_case(test_case.id)

            with ui.row().classes('q-mt-md'):
                ui.button('保存', on_click=save).classes('q-btn--small bg-primary text-white')
                ui.button('取消', on_click=dialog.close).classes('q-btn--small')
        dialog.open()

    def delete_test_viewpoint(self, test_case, viewpoint, parent_dialog):
        """删除测试观点"""
        with ui.dialog() as confirm_dialog, ui.card():
            ui.label(f'确定要删除测试观点 "{viewpoint.name}" 吗？').classes('text-h6 q-mb-md')
            with ui.row().classes('q-mt-md'):
                ui.button('取消', on_click=confirm_dialog.close).classes('q-btn--small')
                ui.button('删除', on_click=lambda: self._confirm_delete_viewpoint(test_case, viewpoint, parent_dialog, confirm_dialog)).classes('q-btn--small bg-negative text-white')
        confirm_dialog.open()

    def _confirm_delete_viewpoint(self, test_case, viewpoint, parent_dialog, confirm_dialog):
        """确认删除测试观点"""
        try:
            test_case.viewpoints = [v for v in test_case.viewpoints if v.id != viewpoint.id]
            ui.notify(f'测试观点删除成功: {viewpoint.name}', type='positive')
            confirm_dialog.close()
            parent_dialog.close()
            self.view_test_case(test_case.id)
        except Exception as e:
            ui.notify(f'测试观点删除失败: {str(e)}', type='negative')

    def add_test_data(self, test_case, viewpoint, parent_dialog):
        """新增测试数据"""
        with ui.dialog() as dialog, ui.card().classes('q-pa-lg').style('min-width: 650px; max-width: 900px; min-height: 300px;'):
            ui.label(f'新增测试数据 - {viewpoint.name}').classes('text-h6 q-mb-md')

            description_input = ui.input('数据描述', placeholder='如: 正常输入测试')
            input_value_input = ui.input('输入值', placeholder='如: test@example.com')
            expected_value_input = ui.input('预期值', placeholder='如: 验证成功')

            # 断言函数选择
            assertion_functions = self._get_available_assertion_functions(viewpoint.target_node)
            assertion_select = ui.select(
                label='断言函数',
                options=assertion_functions,
                multiple=True
            )

            def save():
                from models.test_case import TestData

                new_test_data = TestData(
                    id=str(uuid.uuid4()),
                    description=description_input.value,
                    input_value=input_value_input.value,
                    expected_value=expected_value_input.value,
                    assertion_functions=assertion_select.value,
                    created_at=datetime.now()
                )

                viewpoint.test_data_list.append(new_test_data)
                ui.notify('测试数据已添加', type='positive')
                dialog.close()
                parent_dialog.close()
                self.view_test_case(test_case.id)

            with ui.row().classes('q-mt-md'):
                ui.button('保存', on_click=save).classes('q-btn--small bg-primary text-white')
                ui.button('取消', on_click=dialog.close).classes('q-btn--small')
        dialog.open()

    def delete_test_data(self, test_case, viewpoint, test_data, parent_dialog):
        """删除测试数据"""
        with ui.dialog() as confirm_dialog, ui.card():
            ui.label(f'确定要删除测试数据 "{test_data.description}" 吗？').classes('text-h6 q-mb-md')
            with ui.row().classes('q-mt-md'):
                ui.button('取消', on_click=confirm_dialog.close).classes('q-btn--small')
                ui.button('删除', on_click=lambda: self._confirm_delete_test_data(test_case, viewpoint, test_data, parent_dialog, confirm_dialog)).classes('q-btn--small bg-negative text-white')
        confirm_dialog.open()

    def _confirm_delete_test_data(self, test_case, viewpoint, test_data, parent_dialog, confirm_dialog):
        """确认删除测试数据"""
        try:
            viewpoint.test_data_list = [td for td in viewpoint.test_data_list if td.id != test_data.id]
            ui.notify(f'测试数据删除成功: {test_data.description}', type='positive')
            confirm_dialog.close()
            parent_dialog.close()
            self.view_test_case(test_case.id)
        except Exception as e:
            ui.notify(f'测试数据删除失败: {str(e)}', type='negative')

    def save_test_case_changes(self, test_case, dialog):
        """保存测试用例的所有更改"""
        try:
            # 更新测试用例的更新时间
            test_case.updated_at = datetime.now()

            # 保存到文件
            self.test_generator.save_test_case(test_case)

            ui.notify('测试用例已保存', type='positive')
            dialog.close()
            self.create_test_case_table()  # 刷新表格
        except Exception as e:
            ui.notify(f'保存失败: {str(e)}', type='negative')

    def execute_test_case(self, test_case_id: str):
        """执行测试用例"""
        test_case = self.test_generator.load_test_case(test_case_id)
        if not test_case:
            ui.notify('测试用例不存在', type='negative')
            return

        with ui.dialog() as dialog, ui.card().classes('q-pa-lg').style('min-width: 650px; max-width: 900px; min-height: 300px;'):
            ui.label(f'执行测试用例: {test_case.name}').classes('text-h6 q-mb-md')

            headless_checkbox = ui.checkbox('无头模式', value=True)

            with ui.row().classes('q-mt-md'):
                ui.button('取消', on_click=dialog.close).classes('q-btn--small')
                ui.button('执行', on_click=lambda: self.run_test_case_async(test_case_id, headless_checkbox.value, dialog)).classes('q-btn--small bg-positive text-white')
        dialog.open()

    async def run_test_case_async(self, test_case_id: str, headless: bool, dialog):
        """异步执行测试用例"""
        try:
            ui.notify('正在执行测试...', type='info')
            execution = await self.test_runner.run_test_case(test_case_id, headless=headless)

            # 生成报告
            report_path = self.report_generator.generate_html_report(execution.id)

            ui.notify(f'测试执行完成: {execution.test_case_name}', type='positive')
            dialog.close()

            # 显示结果
            self.show_test_result(execution, report_path)
        except Exception as e:
            ui.notify(f'测试执行失败: {str(e)}', type='negative')

    def edit_test_case(self, test_case_id: str):
        """编辑测试用例"""
        test_case = self.test_generator.load_test_case(test_case_id)
        if not test_case:
            ui.notify('测试用例不存在', type='negative')
            return

        with ui.dialog() as dialog, ui.card().classes('q-pa-lg').style('min-width: 650px; max-width: 900px; min-height: 300px;'):
            ui.label(f'编辑测试用例: {test_case.name}').classes('text-h6 q-mb-md')
            test_name_input = ui.input('测试用例名称', value=test_case.name)
            test_type_select = ui.select(label='测试类型', options=[t.value for t in TestType], value=test_case.test_type.value)
            test_priority_select = ui.select(label='优先级', options=[p.value for p in TestPriority], value=test_case.priority.value)
            description_input = ui.input('描述', value=test_case.description)

            def save():
                test_case.name = test_name_input.value
                test_case.test_type = TestType(test_type_select.value)
                test_case.priority = TestPriority(test_priority_select.value)
                test_case.description = description_input.value
                self.test_generator.save_test_case(test_case)
                ui.notify('测试用例已更新', type='positive')
                dialog.close()
                self.create_test_case_table() # 刷新表格
            ui.button('保存', on_click=save).classes('q-btn--small bg-primary text-white')
            ui.button('取消', on_click=dialog.close).classes('q-btn--small')
        dialog.open()

    def delete_test_case(self, test_case_id: str):
        """删除测试用例"""
        # 确认删除
        with ui.dialog() as confirm_dialog, ui.card():
            test_case = self.test_generator.load_test_case(test_case_id)
            if not test_case:
                ui.notify('测试用例不存在', type='negative')
                return
            ui.label(f'确定要删除测试用例 "{test_case.name}" 吗？').classes('text-h6 q-mb-md')
            with ui.row().classes('q-mt-md'):
                ui.button('取消', on_click=confirm_dialog.close).classes('q-btn--small')
                ui.button('删除', on_click=lambda: self._confirm_delete_test_case(test_case_id, confirm_dialog)).classes('q-btn--small bg-negative text-white')
        confirm_dialog.open()

    def _confirm_delete_test_case(self, test_case_id: str, confirm_dialog):
        """确认删除测试用例"""
        try:
            self.test_generator.delete_test_case(test_case_id)
            ui.notify('测试用例删除成功', type='positive')
            confirm_dialog.close()
            self.create_test_case_table() # 刷新表格
        except Exception as e:
            ui.notify(f'测试用例删除失败: {str(e)}', type='negative')

    def _get_available_assertion_functions(self, target_node):
        """获取可用的断言函数列表"""
        from utils.assertion_utils import AssertionUtils

        # 使用新的断言系统获取断言函数
        node_type = target_node.type.value if target_node else "input"
        assertions = AssertionUtils.get_assertions_by_node_type(node_type)

        # 转换为UI需要的格式
        return [(assertion["name"], assertion["description"]) for assertion in assertions]

    def _get_assertion_function_params(self, func_name):
        """获取断言函数的参数信息"""
        from utils.assertion_utils import AssertionUtils

        # 使用新的断言系统获取参数信息
        return AssertionUtils.get_assertion_parameters(func_name)

    def view_execution(self, execution_id: str):
        """查看执行记录"""
        ui.notify('执行记录查看功能开发中...', type='info')

    def delete_page_structure(self, structure_id: str):
        """删除页面结构"""
        structure = self.page_parser.load_page_structure(structure_id)
        if not structure:
            ui.notify('页面结构不存在', type='negative')
            return

        # 使用自定义确认弹窗
        with ui.dialog() as confirm_dialog, ui.card():
            ui.label(f'确定要删除页面结构 "{structure.title}" 吗？').classes('text-h6 q-mb-md')
            with ui.row().classes('q-mt-md'):
                ui.button('取消', on_click=confirm_dialog.close).classes('q-btn--small')
                ui.button('删除', on_click=lambda: self._confirm_delete_structure(structure_id, confirm_dialog)).classes('q-btn--small bg-negative text-white')
        confirm_dialog.open()

    def _confirm_delete_structure(self, structure_id: str, confirm_dialog):
        """确认删除页面结构"""
        try:
            self.page_parser.delete_page_structure(structure_id)
            ui.notify('页面结构删除成功', type='positive')
            confirm_dialog.close()
            self.create_page_structure_table() # 刷新表格
        except Exception as e:
            ui.notify(f'页面结构删除失败: {str(e)}', type='negative')

    def add_new_node(self, structure, parent_dialog):
        """新增节点"""
        with ui.dialog() as dialog, ui.card().classes('q-pa-lg').style('min-width: 650px; max-width: 900px; min-height: 300px;'):
            ui.label('新增节点').classes('text-h6 q-mb-md')
            tag_input = ui.input('标签名', placeholder='如: div, button, input')
            type_select = ui.select(label='类型', options=[t.value for t in NodeType])
            selector_input = ui.input('选择器', placeholder='如: .class-name, #id, /xpath')
            text_input = ui.input('文本内容', placeholder='如: 登录, 搜索, 提交')
            interactive_checkbox = ui.checkbox('可交互')

            def save():
                from models.page_node import PageNode
                new_node = PageNode(
                    id=str(uuid.uuid4()),
                    type=NodeType(type_select.value),
                    tag_name=tag_input.value,
                    text_content=text_input.value,
                    attributes={},
                    xpath=selector_input.value if selector_input.value.startswith('/') else '',
                    css_selector=selector_input.value if not selector_input.value.startswith('/') else '',
                    position={"x": 0, "y": 0},
                    size={"width": 0, "height": 0},
                    is_visible=True,
                    is_interactive=interactive_checkbox.value,
                    parent_id=None,
                    children=[],
                    page_url=structure.url,
                    created_at=datetime.now()
                )
                structure.nodes.append(new_node)
                self.page_parser.save_page_structure(structure)
                ui.notify('节点已添加', type='positive')
                dialog.close()
                parent_dialog.close()
                self.view_page_structure(structure.id)
            ui.button('保存', on_click=save).classes('q-btn--small bg-primary text-white')
            ui.button('取消', on_click=dialog.close).classes('q-btn--small')
        dialog.open()

    def batch_operations(self, structure, parent_dialog):
        """批量操作"""
        with ui.dialog() as dialog, ui.card().classes('q-pa-lg').style('min-width: 650px; max-width: 900px; min-height: 300px;'):
            ui.label('批量操作').classes('text-h6 q-mb-md')
            operation_select = ui.select(label='操作', options=['删除', '验证所有', '补全所有选择器'])
            def perform_operation():
                if operation_select.value == '删除':
                    with ui.dialog() as confirm_dialog, ui.card():
                        ui.label('确定要删除所有节点吗？').classes('text-h6 q-mb-md')
                        with ui.row().classes('q-mt-md'):
                            ui.button('取消', on_click=confirm_dialog.close).classes('q-btn--small')
                            ui.button('删除', on_click=lambda: self._confirm_batch_delete(structure, dialog, confirm_dialog)).classes('q-btn--small bg-negative text-white')
                    confirm_dialog.open()
                elif operation_select.value == '验证所有':
                    for node in structure.nodes:
                        self.verify_selector(structure.url, node)
                    ui.notify('所有选择器已验证', type='positive')
                elif operation_select.value == '补全所有选择器':
                    for node in structure.nodes:
                        self.complete_selector(node)
                    ui.notify('所有选择器已补全', type='positive')
                dialog.close()
            ui.button('执行', on_click=perform_operation).classes('q-btn--small bg-primary text-white')
            ui.button('取消', on_click=dialog.close).classes('q-btn--small')
        dialog.open()

    def _confirm_batch_delete(self, structure, parent_dialog, confirm_dialog):
        """确认批量删除"""
        try:
            structure.nodes = []
            self.page_parser.save_page_structure(structure)
            ui.notify('所有节点已删除', type='positive')
            confirm_dialog.close()
            parent_dialog.close()
            self.view_page_structure(structure.id)
        except Exception as e:
            ui.notify(f'批量删除失败: {str(e)}', type='negative')

    def view_node_details(self, structure, node, parent_dialog):
        """查看节点详情"""
        with ui.dialog() as dialog, ui.card().classes('q-pa-lg').style('min-width: 650px; max-width: 900px; min-height: 300px;'):
            ui.label(f'节点详情: {node.tag_name}').classes('text-h6 q-mb-md')
            ui.label(f'ID: {node.id}').classes('text-caption')
            ui.label(f'类型: {node.type.value}').classes('text-caption')
            ui.label(f'选择器: {node.css_selector or node.xpath}').classes('text-mono text-caption')
            ui.label(f'文本内容: {node.text_content}').classes('text-caption')
            ui.label(f'可交互: {node.is_interactive}').classes('text-caption')
            ui.label(f'属性: {json.dumps(node.attributes, indent=2)}').classes('text-caption text-grey')
            ui.label(f'子节点: {len(node.children)}').classes('text-caption')

            with ui.row().classes('q-mt-md'):
                ui.button('关闭', on_click=dialog.close)
        dialog.open()

    def edit_node(self, structure, node, parent_dialog):
        """编辑节点"""
        with ui.dialog() as dialog, ui.card().classes('q-pa-lg').style('min-width: 650px; max-width: 900px; min-height: 300px;'):
            ui.label(f'编辑节点: {node.tag_name}').classes('text-h6 q-mb-md')
            tag_input = ui.input('标签名', value=node.tag_name)
            type_select = ui.select(label='类型', options=[t.value for t in NodeType], value=node.type.value)
            selector_input = ui.input('选择器', value=node.css_selector or node.xpath)
            text_input = ui.input('文本内容', value=node.text_content)
            interactive_checkbox = ui.checkbox('可交互', value=node.is_interactive)

            def save():
                node.tag_name = tag_input.value
                node.type = NodeType(type_select.value)
                if selector_input.value.startswith('/'):
                    node.xpath = selector_input.value
                    node.css_selector = ''
                else:
                    node.css_selector = selector_input.value
                    node.xpath = ''
                node.text_content = text_input.value
                node.is_interactive = interactive_checkbox.value
                self.page_parser.save_page_structure(structure)
                ui.notify('节点已更新', type='positive')
                dialog.close()
                parent_dialog.close()
                self.view_page_structure(structure.id)
            ui.button('保存', on_click=save).classes('q-btn--small bg-primary text-white')
            ui.button('取消', on_click=dialog.close).classes('q-btn--small')
        dialog.open()

    def quick_parse_forms(self):
        """快速解析表单"""
        with ui.dialog() as dialog, ui.card():
            ui.label('快速解析表单').classes('text-h6 q-mb-md')

            url_input = ui.input('页面URL', placeholder='请输入包含表单的页面URL')

            with ui.row().classes('q-mt-md'):
                ui.button('取消', on_click=dialog.close)
                ui.button('解析表单', on_click=lambda: self.parse_forms_async(url_input.value, dialog))
        dialog.open()

    async def parse_forms_async(self, url: str, dialog):
        """异步解析表单"""
        if not url:
            ui.notify('请输入页面URL', type='warning')
            return

        try:
            ui.notify('正在解析表单...', type='info')
            form_structure = await self.page_parser.parse_forms_from_url(url, headless=True)

            # 获取表单字段和按钮信息
            form_fields = self.page_parser.get_form_fields(form_structure.id)
            form_buttons = self.page_parser.get_form_buttons(form_structure.id)

            ui.notify(f'表单解析成功: 找到 {len(form_fields)} 个字段, {len(form_buttons)} 个按钮', type='positive')
            dialog.close()

            # 显示表单详情
            self.show_form_details(form_structure, form_fields, form_buttons)

        except Exception as e:
            ui.notify(f'表单解析失败: {str(e)}', type='negative')

    def show_form_details(self, structure, form_fields, form_buttons):
        """显示表单详情"""
        with ui.dialog() as dialog, ui.card().classes('q-pa-lg').style('min-width: 1000px; max-width: 1400px;'):
            ui.label(f'表单详情: {structure.title}').classes('text-h6 q-mb-md')
            ui.label(f'URL: {structure.url}').classes('text-caption')
            ui.label(f'字段数: {len(form_fields)}, 按钮数: {len(form_buttons)}').classes('text-caption')

            # 表单字段表格
            ui.label('表单字段').classes('text-subtitle1 q-mb-sm')
            with ui.column().classes('w-full'):
                # 表头
                with ui.row().classes('w-full items-center bg-blue-1 text-bold').style('border-bottom:1px solid #ccc;'):
                    ui.label('字段名').style('min-width:120px;max-width:150px;flex:1')
                    ui.label('类型').style('min-width:80px;max-width:100px;flex:1')
                    ui.label('占位符').style('min-width:120px;max-width:200px;flex:2')
                    ui.label('必填').style('min-width:60px;max-width:80px;flex:1')
                    ui.label('选择器').style('min-width:200px;max-width:300px;flex:2')
                # 表体
                with ui.scroll_area().style('max-height: 200px;'):
                    for field in form_fields:
                        with ui.row().classes('w-full items-center').style('border-bottom:1px solid #eee;'):
                            ui.label(field['name'] or field['id']).style('min-width:120px;max-width:150px;flex:1')
                            ui.label(field['type']).style('min-width:80px;max-width:100px;flex:1')
                            ui.label(field['placeholder']).style('min-width:120px;max-width:200px;flex:2')
                            ui.label(str(field['required'])).style('min-width:60px;max-width:80px;flex:1')
                            ui.label(field['selector']).classes('text-mono').style('min-width:200px;max-width:300px;flex:2')

            # 表单按钮表格
            ui.label('表单按钮').classes('text-subtitle1 q-mb-sm q-mt-md')
            with ui.column().classes('w-full'):
                # 表头
                with ui.row().classes('w-full items-center bg-green-1 text-bold').style('border-bottom:1px solid #ccc;'):
                    ui.label('按钮名').style('min-width:120px;max-width:150px;flex:1')
                    ui.label('类型').style('min-width:80px;max-width:100px;flex:1')
                    ui.label('文本').style('min-width:120px;max-width:200px;flex:2')
                    ui.label('选择器').style('min-width:200px;max-width:300px;flex:2')
                # 表体
                with ui.scroll_area().style('max-height: 150px;'):
                    for button in form_buttons:
                        with ui.row().classes('w-full items-center').style('border-bottom:1px solid #eee;'):
                            ui.label(button['name'] or button['id']).style('min-width:120px;max-width:150px;flex:1')
                            ui.label(button['type']).style('min-width:80px;max-width:100px;flex:1')
                            ui.label(button['text']).style('min-width:120px;max-width:200px;flex:2')
                            ui.label(button['selector']).classes('text-mono').style('min-width:200px;max-width:300px;flex:2')

            with ui.row().classes('q-mt-md'):
                ui.button('生成表单测试', on_click=lambda: self.generate_form_test(structure.id, dialog)).classes('bg-primary text-white')
                ui.button('关闭', on_click=dialog.close)
        dialog.open()

    def generate_form_test(self, structure_id: str, dialog):
        """生成表单测试用例"""
        try:
            form_fields = self.page_parser.get_form_fields(structure_id)
            form_buttons = self.page_parser.get_form_buttons(structure_id)

            # 生成测试用例
            test_case = self.test_generator.generate_test_case_from_nodes(
                structure_id=structure_id,
                node_ids=[field['id'] for field in form_fields] + [button['id'] for button in form_buttons],
                test_name="表单自动化测试",
                test_type=TestType.FUNCTIONAL,
                priority=TestPriority.HIGH,
                description="自动生成的表单测试用例"
            )

            # 保存测试用例
            self.test_generator.save_test_case(test_case)

            ui.notify(f'表单测试用例生成成功: {test_case.name}', type='positive')
            dialog.close()

        except Exception as e:
            ui.notify(f'表单测试用例生成失败: {str(e)}', type='negative')

    def generate_test_from_structure(self, structure_id: str):
        """从页面结构生成测试用例"""
        structure = self.page_parser.load_page_structure(structure_id)
        if not structure:
            ui.notify('页面结构不存在', type='negative')
            return

        with ui.dialog() as dialog, ui.card():
            ui.label('从页面结构生成测试用例').classes('text-h6 q-mb-md')

            test_name_input = ui.input('测试用例名称', placeholder='请输入测试用例名称')

            with ui.row().classes('q-mt-md'):
                ui.button('取消', on_click=dialog.close)
                ui.button('生成', on_click=lambda: self.generate_test_from_structure_quick(structure_id, test_name_input.value, dialog))
        dialog.open()

    def generate_test_from_structure_quick(self, structure_id: str, test_name: str, dialog):
        """快速从页面结构生成测试用例"""
        if not test_name:
            ui.notify('请输入测试用例名称', type='warning')
            return

        try:
            # 获取可交互的节点
            interactive_nodes = self.page_parser.get_interactive_nodes(structure_id)

            if not interactive_nodes:
                ui.notify('未找到可交互的节点', type='warning')
                return

            # 生成测试用例
            test_case = self.test_generator.generate_test_case_from_nodes(
                structure_id=structure_id,
                node_ids=[node.id for node in interactive_nodes[:3]],  # 限制节点数量
                test_name=test_name,
                test_type=TestType.FUNCTIONAL,
                priority=TestPriority.MEDIUM,
                description=f"从页面结构生成的综合测试用例"
            )

            # 保存测试用例
            self.test_generator.save_test_case(test_case)

            ui.notify(f'测试用例生成成功: {test_case.name} (包含{len(test_case.viewpoints)}个测试观点, {test_case.get_test_data_count()}个测试数据)', type='positive')
            dialog.close()

        except Exception as e:
            ui.notify(f'测试用例生成失败: {str(e)}', type='negative')


def create_app():
    """创建应用"""
    main_ui = MainUI()
    main_ui.create_main_interface()
    return app
