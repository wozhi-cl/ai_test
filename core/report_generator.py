import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from models.test_data import TestExecution, TestSuite
from core.test_runner import TestRunner
from jinja2 import Template
import base64


class ReportGenerator:
    """报告生成器"""

    def __init__(self, data_dir: str = "data/reports"):
        self.data_dir = data_dir
        self.test_runner = TestRunner(data_dir)
        os.makedirs(data_dir, exist_ok=True)

    def generate_html_report(self, execution_id: str) -> str:
        """生成HTML报告"""
        execution = self.test_runner.load_execution(execution_id)
        if not execution:
            raise Exception("执行记录不存在")

        # 准备报告数据
        report_data = self._prepare_report_data(execution)

        # 生成HTML内容
        html_content = self._generate_html_content(report_data)

        # 保存HTML文件
        filename = f"report_{execution_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.data_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return filepath

    def generate_suite_report(self, execution_ids: List[str], suite_name: str = "测试套件报告") -> str:
        """生成测试套件报告"""
        executions = []
        for execution_id in execution_ids:
            execution = self.test_runner.load_execution(execution_id)
            if execution:
                executions.append(execution)

        if not executions:
            raise Exception("没有找到有效的执行记录")

        # 准备套件报告数据
        suite_data = self._prepare_suite_report_data(executions, suite_name)

        # 生成HTML内容
        html_content = self._generate_suite_html_content(suite_data)

        # 保存HTML文件
        filename = f"suite_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.data_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return filepath

    def _prepare_report_data(self, execution: TestExecution) -> Dict[str, Any]:
        """准备报告数据"""
        # 计算统计信息
        total_steps = len(execution.step_results)
        passed_steps = len([step for step in execution.step_results if step.status.value == 'passed'])
        failed_steps = len([step for step in execution.step_results if step.status.value == 'failed'])
        error_steps = len([step for step in execution.step_results if step.status.value == 'error'])

        success_rate = (passed_steps / total_steps * 100) if total_steps > 0 else 0

        # 准备步骤数据
        steps_data = []
        for step_result in execution.step_results:
            step_data = {
                'step_number': step_result.step_number,
                'action': step_result.action,
                'status': step_result.status.value,
                'status_class': self._get_status_class(step_result.status.value),
                'duration': step_result.duration or 0,
                'input_data': step_result.input_data,
                'output_data': step_result.output_data,
                'error_message': step_result.error_message,
                'screenshot_path': step_result.screenshot_path,
                'assertions': []
            }

            # 添加断言信息
            for assertion in step_result.assertions:
                assertion_data = {
                    'type': assertion.assertion_type,
                    'expected': assertion.expected_value,
                    'actual': assertion.actual_value,
                    'passed': assertion.passed,
                    'message': assertion.message,
                    'execution_time': assertion.execution_time
                }
                step_data['assertions'].append(assertion_data)

            steps_data.append(step_data)

        return {
            'execution_id': execution.id,
            'test_case_name': execution.test_case_name,
            'test_case_id': execution.test_case_id,
            'page_url': execution.page_url,
            'status': execution.status.value,
            'status_class': self._get_status_class(execution.status.value),
            'start_time': execution.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': execution.end_time.strftime('%Y-%m-%d %H:%M:%S') if execution.end_time else 'N/A',
            'duration': execution.duration or 0,
            'total_steps': total_steps,
            'passed_steps': passed_steps,
            'failed_steps': failed_steps,
            'error_steps': error_steps,
            'success_rate': round(success_rate, 2),
            'error_message': execution.error_message,
            'browser_info': execution.browser_info,
            'environment_info': execution.environment_info,
            'steps': steps_data,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def _prepare_suite_report_data(self, executions: List[TestExecution], suite_name: str) -> Dict[str, Any]:
        """准备套件报告数据"""
        # 计算套件统计信息
        total_executions = len(executions)
        passed_executions = len([e for e in executions if e.status.value == 'passed'])
        failed_executions = len([e for e in executions if e.status.value == 'failed'])
        error_executions = len([e for e in executions if e.status.value == 'error'])

        total_steps = sum(len(e.step_results) for e in executions)
        passed_steps = sum(len([s for s in e.step_results if s.status.value == 'passed']) for e in executions)
        failed_steps = sum(len([s for s in e.step_results if s.status.value == 'failed']) for e in executions)

        execution_success_rate = (passed_executions / total_executions * 100) if total_executions > 0 else 0
        step_success_rate = (passed_steps / total_steps * 100) if total_steps > 0 else 0

        # 准备执行记录数据
        executions_data = []
        for execution in executions:
            execution_data = {
                'id': execution.id,
                'test_case_name': execution.test_case_name,
                'status': execution.status.value,
                'status_class': self._get_status_class(execution.status.value),
                'start_time': execution.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'duration': execution.duration or 0,
                'total_steps': len(execution.step_results),
                'passed_steps': len([s for s in execution.step_results if s.status.value == 'passed']),
                'failed_steps': len([s for s in execution.step_results if s.status.value == 'failed']),
                'error_message': execution.error_message
            }
            executions_data.append(execution_data)

        return {
            'suite_name': suite_name,
            'total_executions': total_executions,
            'passed_executions': passed_executions,
            'failed_executions': failed_executions,
            'error_executions': error_executions,
            'execution_success_rate': round(execution_success_rate, 2),
            'total_steps': total_steps,
            'passed_steps': passed_steps,
            'failed_steps': failed_steps,
            'step_success_rate': round(step_success_rate, 2),
            'executions': executions_data,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def _get_status_class(self, status: str) -> str:
        """获取状态CSS类"""
        status_classes = {
            'passed': 'success',
            'failed': 'danger',
            'error': 'warning',
            'running': 'info',
            'pending': 'secondary'
        }
        return status_classes.get(status, 'secondary')

    def _generate_html_content(self, report_data: Dict[str, Any]) -> str:
        """生成HTML内容"""
        template = Template('''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试报告 - {{ report_data.test_case_name }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        .status-badge {
            font-size: 0.8em;
            padding: 0.25em 0.5em;
        }
        .step-details {
            background-color: #f8f9fa;
            border-radius: 0.375rem;
            padding: 1rem;
            margin-top: 0.5rem;
        }
        .assertion-item {
            border-left: 3px solid #dee2e6;
            padding-left: 1rem;
            margin: 0.5rem 0;
        }
        .assertion-passed {
            border-left-color: #198754;
        }
        .assertion-failed {
            border-left-color: #dc3545;
        }
        .screenshot-container {
            max-width: 100%;
            overflow-x: auto;
        }
        .screenshot-container img {
            max-width: 100%;
            height: auto;
        }
    </style>
</head>
<body>
    <div class="container-fluid py-4">
        <!-- 报告头部 -->
        <div class="row mb-4">
            <div class="col-12">
                <h1 class="h3 mb-3">
                    <i class="bi bi-file-earmark-text"></i>
                    测试报告
                </h1>
                <div class="card">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h5 class="card-title">{{ report_data.test_case_name }}</h5>
                                <p class="text-muted mb-2">测试用例ID: {{ report_data.test_case_id }}</p>
                                <p class="text-muted mb-2">页面URL: <a href="{{ report_data.page_url }}" target="_blank">{{ report_data.page_url }}</a></p>
                            </div>
                            <div class="col-md-6 text-end">
                                <span class="badge bg-{{ report_data.status_class }} status-badge fs-6">
                                    {{ report_data.status.upper() }}
                                </span>
                                <p class="text-muted mt-2 mb-0">生成时间: {{ report_data.generated_at }}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 统计信息 -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h3 class="text-primary">{{ report_data.total_steps }}</h3>
                        <p class="card-text">总步骤数</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h3 class="text-success">{{ report_data.passed_steps }}</h3>
                        <p class="card-text">通过步骤</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h3 class="text-danger">{{ report_data.failed_steps }}</h3>
                        <p class="card-text">失败步骤</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h3 class="text-info">{{ report_data.success_rate }}%</h3>
                        <p class="card-text">成功率</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- 执行信息 -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="bi bi-info-circle"></i> 执行信息</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>开始时间:</strong> {{ report_data.start_time }}</p>
                                <p><strong>结束时间:</strong> {{ report_data.end_time }}</p>
                                <p><strong>执行时长:</strong> {{ "%.2f"|format(report_data.duration) }} 秒</p>
                            </div>
                            <div class="col-md-6">
                                <p><strong>浏览器:</strong> {{ report_data.browser_info.browser }}</p>
                                <p><strong>无头模式:</strong> {{ "是" if report_data.browser_info.headless else "否" }}</p>
                                <p><strong>平台:</strong> {{ report_data.environment_info.platform }}</p>
                            </div>
                        </div>
                        {% if report_data.error_message %}
                        <div class="alert alert-danger mt-3">
                            <strong>错误信息:</strong> {{ report_data.error_message }}
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>

        <!-- 步骤详情 -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="bi bi-list-ol"></i> 步骤详情</h5>
                    </div>
                    <div class="card-body">
                        {% for step in report_data.steps %}
                        <div class="step-item border-bottom pb-3 mb-3">
                            <div class="d-flex justify-content-between align-items-start">
                                <div class="flex-grow-1">
                                    <h6 class="mb-1">
                                        步骤 {{ step.step_number }}: {{ step.action }}
                                        <span class="badge bg-{{ step.status_class }} ms-2">{{ step.status.upper() }}</span>
                                    </h6>
                                    <p class="text-muted mb-2">执行时长: {{ "%.2f"|format(step.duration) }} 秒</p>

                                    {% if step.input_data %}
                                    <p class="mb-1"><strong>输入数据:</strong> {{ step.input_data }}</p>
                                    {% endif %}

                                    {% if step.output_data %}
                                    <p class="mb-1"><strong>输出数据:</strong> {{ step.output_data }}</p>
                                    {% endif %}

                                    {% if step.error_message %}
                                    <div class="alert alert-danger mt-2">
                                        <strong>错误:</strong> {{ step.error_message }}
                                    </div>
                                    {% endif %}

                                    {% if step.assertions %}
                                    <div class="mt-2">
                                        <strong>断言结果:</strong>
                                        {% for assertion in step.assertions %}
                                        <div class="assertion-item {{ 'assertion-passed' if assertion.passed else 'assertion-failed' }}">
                                            <p class="mb-1">
                                                <strong>{{ assertion.type }}:</strong>
                                                <span class="badge bg-{{ 'success' if assertion.passed else 'danger' }} ms-2">
                                                    {{ '通过' if assertion.passed else '失败' }}
                                                </span>
                                            </p>
                                            <p class="mb-1"><small>期望值: {{ assertion.expected }}</small></p>
                                            <p class="mb-1"><small>实际值: {{ assertion.actual }}</small></p>
                                            <p class="mb-0"><small>{{ assertion.message }}</small></p>
                                        </div>
                                        {% endfor %}
                                    </div>
                                    {% endif %}

                                    {% if step.screenshot_path %}
                                    <div class="mt-2">
                                        <strong>截图:</strong>
                                        <div class="screenshot-container mt-2">
                                            <img src="{{ step.screenshot_path }}" alt="步骤截图" class="img-fluid">
                                        </div>
                                    </div>
                                    {% endif %}
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        ''')

        return template.render(report_data=report_data)

    def _generate_suite_html_content(self, suite_data: Dict[str, Any]) -> str:
        """生成套件HTML内容"""
        template = Template('''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试套件报告 - {{ suite_data.suite_name }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        .status-badge {
            font-size: 0.8em;
            padding: 0.25em 0.5em;
        }
    </style>
</head>
<body>
    <div class="container-fluid py-4">
        <!-- 报告头部 -->
        <div class="row mb-4">
            <div class="col-12">
                <h1 class="h3 mb-3">
                    <i class="bi bi-collection"></i>
                    测试套件报告
                </h1>
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">{{ suite_data.suite_name }}</h5>
                        <p class="text-muted mb-0">生成时间: {{ suite_data.generated_at }}</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- 统计信息 -->
        <div class="row mb-4">
            <div class="col-md-2">
                <div class="card text-center">
                    <div class="card-body">
                        <h3 class="text-primary">{{ suite_data.total_executions }}</h3>
                        <p class="card-text">总执行数</p>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card text-center">
                    <div class="card-body">
                        <h3 class="text-success">{{ suite_data.passed_executions }}</h3>
                        <p class="card-text">通过执行</p>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card text-center">
                    <div class="card-body">
                        <h3 class="text-danger">{{ suite_data.failed_executions }}</h3>
                        <p class="card-text">失败执行</p>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card text-center">
                    <div class="card-body">
                        <h3 class="text-warning">{{ suite_data.error_executions }}</h3>
                        <p class="card-text">错误执行</p>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card text-center">
                    <div class="card-body">
                        <h3 class="text-info">{{ suite_data.execution_success_rate }}%</h3>
                        <p class="card-text">执行成功率</p>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card text-center">
                    <div class="card-body">
                        <h3 class="text-info">{{ suite_data.step_success_rate }}%</h3>
                        <p class="card-text">步骤成功率</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- 执行列表 -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="bi bi-list-ul"></i> 执行记录</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>测试用例</th>
                                        <th>状态</th>
                                        <th>开始时间</th>
                                        <th>执行时长</th>
                                        <th>步骤统计</th>
                                        <th>操作</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for execution in suite_data.executions %}
                                    <tr>
                                        <td>{{ execution.test_case_name }}</td>
                                        <td>
                                            <span class="badge bg-{{ execution.status_class }} status-badge">
                                                {{ execution.status.upper() }}
                                            </span>
                                        </td>
                                        <td>{{ execution.start_time }}</td>
                                        <td>{{ "%.2f"|format(execution.duration) }} 秒</td>
                                        <td>
                                            <small>
                                                通过: {{ execution.passed_steps }} /
                                                失败: {{ execution.failed_steps }} /
                                                总计: {{ execution.total_steps }}
                                            </small>
                                        </td>
                                        <td>
                                            <a href="report_{{ execution.id }}.html" class="btn btn-sm btn-outline-primary">
                                                查看详情
                                            </a>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        ''')

        return template.render(suite_data=suite_data)

    def generate_json_report(self, execution_id: str) -> str:
        """生成JSON报告"""
        execution = self.test_runner.load_execution(execution_id)
        if not execution:
            raise Exception("执行记录不存在")

        report_data = self._prepare_report_data(execution)

        filename = f"report_{execution_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.data_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        return filepath

    def get_report_list(self) -> Dict[str, Any]:
        """获取报告列表（返回 { headers: [], rows: [] } 格式）"""
        from models import get_default_headers

        reports = []
        for filename in os.listdir(self.data_dir):
            if filename.startswith('report_') and filename.endswith('.html'):
                filepath = os.path.join(self.data_dir, filename)
                file_stat = os.stat(filepath)
                reports.append([
                    filename,
                    filepath,
                    file_stat.st_size,
                    datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                    'html'
                ])

        # 按创建时间倒序排列
        reports.sort(key=lambda x: x[3], reverse=True)

        return {
            'headers': get_default_headers('report'),
            'rows': reports
        }
