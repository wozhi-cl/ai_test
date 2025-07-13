# 自动化测试工具

基于Python Playwright和NiceGUI开发的自动化测试工具，支持页面结构解析、测试用例生成、测试执行和报告生成。

## 项目结构

```
ai_test/
├── core/                 # 核心功能模块
├── models/              # 数据模型
├── ui/                  # 用户界面
├── utils/               # 工具类
├── data/                # 数据存储
│   ├── test_cases/      # 测试用例数据
│   ├── page_nodes/      # 页面结构数据
│   ├── executions/      # 执行记录
│   ├── reports/         # 测试报告
│   └── screenshots/     # 截图文件
├── main.py              # 主程序入口
├── requirements.txt     # 依赖包
├── .gitignore          # Git忽略文件
└── README.md           # 项目说明
```

## Git忽略配置说明

### 已忽略的文件类型

#### Python相关
- `__pycache__/` - Python字节码缓存
- `*.pyc`, `*.pyo` - 编译的Python文件
- `*.egg-info/` - 包分发信息
- `venv/`, `.venv/` - 虚拟环境

#### IDE相关
- `.idea/` - PyCharm配置
- `.vscode/` - VS Code配置
- `*.sublime-*` - Sublime Text配置

#### 系统相关
- `.DS_Store` - macOS系统文件
- `Thumbs.db` - Windows缩略图文件
- `*.tmp`, `*.temp` - 临时文件

#### 项目特定
- `data/executions/*.json` - 测试执行记录
- `data/reports/*.html` - 生成的HTML报告
- `data/reports/*.json` - 报告数据
- `data/screenshots/` - 截图文件
- `logs/` - 日志文件
- `*.log` - 日志文件

### 可选忽略的文件

以下文件类型默认**不会**被忽略，但你可以根据需要取消注释来忽略：

```gitignore
# 取消注释下面的行来忽略所有测试数据
# data/test_cases/*.json
# data/page_nodes/*.json
```

### 为什么这样配置？

1. **保留示例数据**: 测试用例和页面结构数据可能包含有用的示例，有助于新用户理解项目
2. **忽略执行数据**: 执行记录和报告是运行时生成的，不需要版本控制
3. **忽略大文件**: 截图文件通常较大，不适合提交到版本控制
4. **保护敏感信息**: 日志文件可能包含敏感信息

## 使用方法

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行应用
```bash
python main.py
```

### 访问界面
打开浏览器访问: http://localhost:8080

## 功能特性

- 🔍 **页面解析**: 自动解析网页结构，提取可交互元素
- 📝 **测试生成**: 基于页面结构自动生成测试用例
- 🎯 **测试执行**: 支持多种测试策略和断言函数
- 📊 **报告生成**: 生成详细的HTML测试报告
- 🎨 **友好界面**: 基于NiceGUI的现代化Web界面

## 开发说明

### 添加新的忽略规则

如果需要忽略新的文件类型，请在`.gitignore`文件的相应部分添加规则：

```gitignore
# 新文件类型
*.new_extension
new_directory/
```

### 检查忽略状态

使用以下命令检查文件是否被正确忽略：

```bash
git status --ignored
```

### 强制添加被忽略的文件

如果某个被忽略的文件需要提交，可以使用：

```bash
git add -f path/to/file
```

## 注意事项

1. **数据备份**: 重要的测试数据建议定期备份
2. **环境配置**: 不同环境的配置文件应该被忽略
3. **敏感信息**: 包含密码、API密钥等敏感信息的文件不要提交
4. **大文件**: 超过100MB的文件建议使用Git LFS或外部存储

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License
