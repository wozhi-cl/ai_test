# 自动化测试工具使用说明

## 快速开始

### 1. 安装依赖

```bash
# 安装Python依赖包
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install
```

### 2. 启动应用

#### 方式一：使用启动脚本（推荐）
```bash
python start.py
```

#### 方式二：直接启动Web界面
```bash
python main.py
```

#### 方式三：运行示例
```bash
python example.py
```

## 功能模块

### 1. 页面解析模块

**功能**：解析网页结构，提取页面节点信息

**使用方式**：
- 在Web界面中点击"页面解析"
- 输入要解析的页面URL
- 系统会自动解析页面并生成节点数据

**支持的操作**：
- 从URL解析页面
- 从Playwright录制脚本解析页面
- 查看页面结构详情
- 搜索和筛选节点
- 导出页面结构数据

### 2. 测试用例生成模块

**功能**：基于页面节点生成测试用例

**使用方式**：
- 在Web界面中点击"测试生成"
- 选择已解析的页面结构
- 选择要测试的节点
- 配置测试用例信息
- 生成测试用例

**支持的操作**：
- 从节点生成测试用例
- 生成综合测试套件
- 编辑和删除测试用例
- 导出测试用例数据

### 3. 测试运行模块

**功能**：执行自动化测试并记录结果

**使用方式**：
- 在Web界面中点击"测试运行"
- 选择要运行的测试用例
- 配置运行参数（如无头模式）
- 执行测试并查看结果

**支持的操作**：
- 运行单个测试用例
- 运行测试套件
- 查看执行记录
- 查看详细执行结果

### 4. 报告生成模块

**功能**：生成测试报告

**使用方式**：
- 在Web界面中点击"报告查看"
- 查看生成的测试报告
- 下载报告文件

**支持的报告格式**：
- HTML报告（美观的网页格式）
- JSON报告（结构化数据格式）

## 工作流程示例

### 完整测试流程

1. **页面解析**
   ```python
   from core.page_parser import PageParser

   page_parser = PageParser()
   page_structure = await page_parser.parse_page_from_url("https://example.com")
   ```

2. **测试用例生成**
   ```python
   from core.test_generator import TestGenerator

   test_generator = TestGenerator()
   test_case = test_generator.generate_test_case_from_nodes(
       structure_id=page_structure.id,
       node_ids=[node.id for node in interactive_nodes],
       test_name="功能测试",
       test_type=TestType.FUNCTIONAL
   )
   ```

3. **测试执行**
   ```python
   from core.test_runner import TestRunner

   test_runner = TestRunner()
   execution = await test_runner.run_test_case(test_case.id)
   ```

4. **报告生成**
   ```python
   from core.report_generator import ReportGenerator

   report_generator = ReportGenerator()
   report_path = report_generator.generate_html_report(execution.id)
   ```

## 数据存储

项目数据存储在 `data/` 目录下：

- `data/page_nodes/` - 页面结构数据
- `data/test_cases/` - 测试用例数据
- `data/reports/` - 测试报告数据
- `data/screenshots/` - 测试截图

## 配置选项

### 浏览器配置

在 `utils/playwright_utils.py` 中可以配置浏览器选项：

```python
# 启动浏览器时配置
await self.playwright.chromium.launch(
    headless=True,  # 无头模式
    slow_mo=1000,   # 慢动作模式（毫秒）
    devtools=False  # 开发者工具
)
```

### 测试配置

在 `core/test_runner.py` 中可以配置测试选项：

```python
# 测试执行配置
execution = await self.test_runner.run_test_case(
    test_case_id,
    headless=True,  # 无头模式
    timeout=30000   # 超时时间（毫秒）
)
```

## 故障排除

### 常见问题

1. **Playwright浏览器未安装**
   ```bash
   playwright install
   ```

2. **依赖包缺失**
   ```bash
   pip install -r requirements.txt
   ```

3. **端口被占用**
   - 修改 `main.py` 中的端口号
   - 或者关闭占用端口的程序

4. **页面解析失败**
   - 检查网络连接
   - 确认URL是否正确
   - 检查页面是否需要登录

### 日志查看

测试执行过程中会生成详细的日志信息，包括：
- 执行步骤详情
- 错误信息
- 性能统计
- 截图路径

## 扩展开发

### 添加新的断言类型

在 `utils/assertion_utils.py` 中添加新的断言方法：

```python
@staticmethod
def assert_custom(actual: Any, expected: Any, message: str = "") -> Dict[str, Any]:
    """自定义断言"""
    # 实现断言逻辑
    pass
```

### 添加新的测试操作

在 `utils/playwright_utils.py` 中添加新的操作方法：

```python
async def custom_action(self, selector: str, data: str):
    """自定义操作"""
    # 实现操作逻辑
    pass
```

### 自定义报告模板

在 `core/report_generator.py` 中修改HTML模板：

```python
def _generate_html_content(self, report_data: Dict[str, Any]) -> str:
    # 自定义HTML模板
    template = Template('''
    <!-- 自定义HTML内容 -->
    ''')
    return template.render(report_data=report_data)
```

## 性能优化

### 提高测试执行速度

1. 使用无头模式运行浏览器
2. 减少等待时间
3. 并行执行测试用例
4. 优化选择器策略

### 减少资源占用

1. 及时关闭浏览器实例
2. 清理临时文件
3. 限制并发测试数量
4. 使用轻量级浏览器

## 最佳实践

1. **页面解析**
   - 选择稳定的页面进行解析
   - 避免解析动态内容过多的页面
   - 定期更新页面结构数据

2. **测试用例设计**
   - 保持测试用例的独立性
   - 使用有意义的测试名称
   - 添加详细的测试描述

3. **测试执行**
   - 在测试环境中运行
   - 定期清理测试数据
   - 监控测试执行时间

4. **报告管理**
   - 定期归档历史报告
   - 分析测试趋势
   - 及时处理失败的测试

## 技术支持

如果遇到问题，请：

1. 查看控制台错误信息
2. 检查日志文件
3. 确认依赖版本
4. 参考示例代码

更多信息请查看项目文档和代码注释。
