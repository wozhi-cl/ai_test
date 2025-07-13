from nicegui import ui
from core.test_runner import TestRunner
from core.test_generator import TestGenerator
from core.report_generator import ReportGenerator
import asyncio


class TestRunnerUI:
    """测试运行界面"""

    def __init__(self):
        self.test_runner = TestRunner()
        self.test_generator = TestGenerator()
        self.report_generator = ReportGenerator()
        self.running_tests = False

    def create_interface(self):
        """创建界面"""
        # 设置页面标题
        ui.page_title('测试运行')

        # 创建导航栏
        with ui.header().classes('bg-primary text-white'):
            ui.button('返回主页', icon='home', on_click=self.go_home).classes('q-mr-md')
            ui.label('▶️ 测试运行').classes('text-h6')

        # 主内容区域
        with ui.column().classes('full-width q-pa-md'):
            # 运行测试区域
            with ui.card().classes('full-width q-mb-md'):
                ui.label('运行测试').classes('text-h6 q-mb-md')

                # 选择测试用例
                test_cases = self.test_generator.list_test_cases()
                if test_cases:
                    test_case_options = [(t['name'], t['id']) for t in test_cases]
                    test_case_select = ui.select('选择测试用例', options=test_case_options).classes('q-mb-md')

                    with ui.row().classes('q-gutter-md'):
                        headless_checkbox = ui.checkbox('无头模式', value=True)
                        ui.button('运行测试', icon='play_arrow', on_click=lambda: self.run_single_test(test_case_select.value, headless_checkbox.value)).classes('bg-primary text-white')
                        ui.button('运行所有', icon='playlist_play', on_click=lambda: self.run_all_tests(headless_checkbox.value)).classes('bg-secondary text-white')
                else:
                    ui.label('请先生成测试用例').classes('text-caption text-grey')

            # 执行记录列表
            self.create_execution_list()

    async def run_single_test(self, test_case_id: str, headless: bool):
        """运行单个测试"""
        if not test_case_id:
            ui.notify('请选择测试用例', type='warning')
            return

        if self.running_tests:
            ui.notify('已有测试正在运行', type='warning')
            return

        self.running_tests = True

        try:
            ui.notify('正在运行测试...', type='info')
            execution = await self.test_runner.run_test_case(test_case_id, headless=headless)

            # 生成报告
            report_path = self.report_generator.generate_html_report(execution.id)

            ui.notify(f'测试运行完成: {execution.test_case_name}', type='positive')

            # 显示结果
            self.show_test_result(execution, report_path)
        except Exception as e:
            ui.notify(f'测试运行失败: {str(e)}', type='negative')
        finally:
            self.running_tests = False
            # 刷新列表
            ui.open('/')
            self.create_interface()

    async def run_all_tests(self, headless: bool):
        """运行所有测试"""
        test_cases = self.test_generator.list_test_cases()

        if not test_cases:
            ui.notify('没有可运行的测试用例', type='warning')
            return

        if self.running_tests:
            ui.notify('已有测试正在运行', type='warning')
            return

        self.running_tests = True

        try:
            ui.notify('正在运行所有测试...', type='info')
            test_case_ids = [t['id'] for t in test_cases]
            executions = await self.test_runner.run_test_suite(test_case_ids, headless=headless)

            # 生成套件报告
            execution_ids = [e.id for e in executions]
            report_path = self.report_generator.generate_suite_report(execution_ids, "完整测试套件")

            ui.notify(f'所有测试运行完成，共 {len(executions)} 个测试用例', type='positive')

            # 显示结果
            self.show_suite_result(executions, report_path)
        except Exception as e:
            ui.notify(f'测试运行失败: {str(e)}', type='negative')
        finally:
            self.running_tests = False
            # 刷新列表
            ui.open('/')
            self.create_interface()

    def show_test_result(self, execution, report_path: str):
        """显示单个测试结果"""
        with ui.dialog() as dialog, ui.card().classes('q-pa-lg'):
            ui.label('测试运行结果').classes('text-h6 q-mb-md')

            # 显示基本信息
            ui.label(f'测试用例: {execution.test_case_name}').classes('text-subtitle1')

            status_color = {
                'passed': 'positive',
                'failed': 'negative',
                'error': 'warning',
                'running': 'info'
            }.get(execution.status.value, 'grey')

            ui.label(f'状态: {execution.status.value.upper()}').classes(f'text-{status_color}')
            ui.label(f'总步骤: {execution.total_steps}, 通过: {execution.passed_steps}, 失败: {execution.failed_steps}').classes('text-caption')
            ui.label(f'执行时长: {execution.duration:.2f} 秒').classes('text-caption')

            if execution.error_message:
                ui.label(f'错误信息: {execution.error_message}').classes('text-caption text-negative')

            with ui.row().classes('q-mt-md'):
                ui.button('查看详细报告', on_click=lambda: self.open_report(report_path))
                ui.button('关闭', on_click=dialog.close)
        dialog.open()

    def show_suite_result(self, executions, report_path: str):
        """显示测试套件结果"""
        with ui.dialog() as dialog, ui.card().classes('q-pa-lg'):
            ui.label('测试套件运行结果').classes('text-h6 q-mb-md')

            # 统计信息
            total_executions = len(executions)
            passed_executions = len([e for e in executions if e.status.value == 'passed'])
            failed_executions = len([e for e in executions if e.status.value == 'failed'])
            error_executions = len([e for e in executions if e.status.value == 'error'])

            ui.label(f'总执行数: {total_executions}').classes('text-subtitle1')
            ui.label(f'通过: {passed_executions}, 失败: {failed_executions}, 错误: {error_executions}').classes('text-caption')

            success_rate = (passed_executions / total_executions * 100) if total_executions > 0 else 0
            ui.label(f'成功率: {success_rate:.1f}%').classes('text-caption')

            # 执行列表
            with ui.scroll_area().classes('q-mt-md'):
                for execution in executions:
                    with ui.card().classes('q-mb-sm'):
                        with ui.row().classes('items-center'):
                            ui.label(execution.test_case_name).classes('text-subtitle2')
                            ui.space()
                            status_color = {
                                'passed': 'positive',
                                'failed': 'negative',
                                'error': 'warning'
                            }.get(execution.status.value, 'grey')
                            ui.label(execution.status.value.upper()).classes(f'text-{status_color} text-caption')

            with ui.row().classes('q-mt-md'):
                ui.button('查看详细报告', on_click=lambda: self.open_report(report_path))
                ui.button('关闭', on_click=dialog.close)
        dialog.open()

    def create_execution_list(self):
        """创建执行记录列表"""
        with ui.card().classes('full-width'):
            ui.label('执行记录').classes('text-h6 q-mb-md')

            # 获取执行记录列表
            executions = self.test_runner.list_executions()

            if executions:
                for execution in executions:
                    with ui.card().classes('full-width q-mb-sm'):
                        with ui.row().classes('items-center'):
                            ui.icon('play_arrow').classes('text-blue q-mr-md')
                            with ui.column().classes('col'):
                                ui.label(execution['test_case_name']).classes('text-subtitle1')
                                ui.label(f"开始时间: {execution['start_time'][:19]}").classes('text-caption text-grey')
                                ui.label(f"执行时长: {execution['duration']:.2f} 秒").classes('text-caption text-grey')
                                ui.label(f"步骤统计: 通过 {execution['passed_steps']}, 失败 {execution['failed_steps']}, 总计 {execution['total_steps']}").classes('text-caption text-grey')

                            with ui.row().classes('q-ml-auto'):
                                status_color = {
                                    'passed': 'positive',
                                    'failed': 'negative',
                                    'error': 'warning',
                                    'running': 'info'
                                }.get(execution['status'], 'grey')
                                ui.label(execution['status'].upper()).classes(f'text-{status_color} text-caption')
                                ui.button('查看', on_click=lambda e=execution: self.view_execution(e['id'])).classes('q-btn--small')
                                ui.button('报告', on_click=lambda e=execution: self.view_report(e['id'])).classes('q-btn--small')
                                ui.button('删除', on_click=lambda e=execution: self.delete_execution(e['id'])).classes('bg-negative text-white q-btn--small')
            else:
                ui.label('暂无执行记录').classes('text-caption text-grey q-mt-xl')

    def view_execution(self, execution_id: str):
        """查看执行记录"""
        execution = self.test_runner.load_execution(execution_id)
        if not execution:
            ui.notify('执行记录不存在', type='negative')
            return

        with ui.dialog() as dialog, ui.card().classes('q-pa-lg'):
            ui.label(f'执行记录详情: {execution.test_case_name}').classes('text-h6 q-mb-md')

            # 基本信息
            with ui.card().classes('q-mb-md'):
                ui.label('基本信息').classes('text-subtitle1 q-mb-sm')
                ui.label(f'测试用例: {execution.test_case_name}')
                ui.label(f'状态: {execution.status.value}')
                ui.label(f'开始时间: {execution.start_time}')
                ui.label(f'结束时间: {execution.end_time}')
                ui.label(f'执行时长: {execution.duration:.2f} 秒')
                ui.label(f'总步骤: {execution.total_steps}')
                ui.label(f'通过步骤: {execution.passed_steps}')
                ui.label(f'失败步骤: {execution.failed_steps}')

                if execution.error_message:
                    ui.label(f'错误信息: {execution.error_message}').classes('text-negative')

            # 步骤详情
            with ui.card():
                ui.label('步骤详情').classes('text-subtitle1 q-mb-sm')

                for step_result in execution.step_results:
                    with ui.card().classes('q-mb-sm'):
                        with ui.row().classes('items-center'):
                            ui.label(f"步骤 {step_result.step_number}").classes('text-caption text-grey')
                            ui.label(step_result.action).classes('text-subtitle2 q-ml-md')

                            status_color = {
                                'passed': 'positive',
                                'failed': 'negative',
                                'error': 'warning'
                            }.get(step_result.status.value, 'grey')
                            ui.label(step_result.status.value.upper()).classes(f'text-{status_color} text-caption q-ml-md')

                            if step_result.duration:
                                ui.label(f"{step_result.duration:.2f}s").classes('text-caption text-grey q-ml-md')

            with ui.row().classes('q-mt-md'):
                ui.button('生成报告', on_click=lambda: self.generate_report(execution_id))
                ui.button('关闭', on_click=dialog.close)
        dialog.open()

    def view_report(self, execution_id: str):
        """查看报告"""
        try:
            report_path = self.report_generator.generate_html_report(execution_id)
            self.open_report(report_path)
        except Exception as e:
            ui.notify(f'生成报告失败: {str(e)}', type='negative')

    def generate_report(self, execution_id: str):
        """生成报告"""
        try:
            report_path = self.report_generator.generate_html_report(execution_id)
            ui.notify('报告生成成功', type='positive')
            self.open_report(report_path)
        except Exception as e:
            ui.notify(f'生成报告失败: {str(e)}', type='negative')

    def open_report(self, filepath: str):
        """打开报告"""
        import webbrowser
        import os

        if os.path.exists(filepath):
            webbrowser.open(f'file://{os.path.abspath(filepath)}')
        else:
            ui.notify('报告文件不存在', type='negative')

    def delete_execution(self, execution_id: str):
        """删除执行记录"""
        try:
            success = self.test_runner.delete_execution(execution_id)
            if success:
                ui.notify('执行记录删除成功', type='positive')
                # 刷新列表
                ui.open('/')
                self.create_interface()
            else:
                ui.notify('执行记录删除失败', type='negative')
        except Exception as e:
            ui.notify(f'删除失败: {str(e)}', type='negative')

    def go_home(self):
        """返回主页"""
        ui.open('/')
        from .main_ui import MainUI
        main_ui = MainUI()
        main_ui.create_main_interface()
