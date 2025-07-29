# CSarXiv Context Server

一个专门用于从CSarXiv.org（中国社会科学预印本平台）获取社科基金申报代码的Model Context Protocol (MCP) 服务器。

## 功能特性

### 📋 社科基金申报代码
- 从CSarXiv.org静态主页获取当年社科基金项目申报代码
- 支持DJ、DJA、DJB等新格式代码解析
- 按学科分类查询和展示申报代码
- 提供申报代码建议和分析
- 智能解析多种代码格式（表格、列表、文本等）

### 📚 学科分类
- 完整的社会科学学科分类体系
- 从A到V的学科代码对照表，包含新增的DJ分类
- 支持按分类筛选相关申报代码

## 安装

### 前提条件
- Python 3.13+
- uv 包管理器（推荐）或 pip
- 稳定的网络连接（访问CSarXiv.org）

### 使用 uv 安装
```bash
# 克隆项目
git clone <repository-url>
cd CSarXivContextServer

# 安装依赖
uv sync

# 运行服务器
uv run csarxivcontextserver
```

### 使用 pip 安装
```bash
# 克隆项目
git clone <repository-url>
cd CSarXivContextServer

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -e .

# 运行服务器
csarxivcontextserver
```

## MCP 客户端配置

### Claude Desktop 配置
在 Claude Desktop 的配置文件中添加：

```json
{
  "mcpServers": {
    "csarxiv": {
      "command": "uv",
      "args": ["run", "csarxivcontextserver"],
      "cwd": "/path/to/CSarXivContextServer"
    }
  }
}
```

### 其他 MCP 客户端
对于其他支持 MCP 的客户端，使用以下命令启动服务器：
```bash
csarxivcontextserver
```

## 可用功能

### 资源 (Resources)
- `csarxiv://funding-codes` - 社科基金申报代码

### 工具 (Tools)
1. **get-funding-codes** - 获取社科基金项目申报代码
   - 参数：`category` (可选，如DJ、FX、GL等)

### 提示模板 (Prompts)
1. **analyze-funding-codes** - 分析社科基金申报代码
   - 参数：`research_area` (可选)

## 使用示例

### 获取所有申报代码
```
使用工具 get-funding-codes 获取所有社科基金申报代码
```

### 获取特定分类代码
```
使用工具 get-funding-codes，参数 category 为 "DJ"，获取中共党史党建学相关代码
```

### 分析申报代码
```
使用提示模板 analyze-funding-codes，参数 research_area 为 "党史研究"
```

## 主要学科代码示例

从CSarXiv.org获取的实际学科代码包括：

### DJ - 中共党史党建学
- **DJ**: 中共党史党建学
- **DJA**: 党史
- **DJB**: 党建  
- **DJC**: 中共党史党建学其他学科

### FX - 法学
- **FX**: 法学
- **FXA**: 理论法学
- **FXB**: 法律史学
- **FXC**: 部门法学
- **FXD**: 国际法学
- **FXE**: 法学其他学科

### GL - 管理学
- **GL**: 管理学
- **GLA**: 管理思想史
- **GLB**: 管理学理论与方法
- **GLC**: 战略与决策管理
- 等等...

*注：完整的代码列表通过工具动态获取，包含数百个学科代码*

## 技术架构

### 依赖项
- `mcp>=1.9.1` - Model Context Protocol 核心库
- `aiohttp>=3.9.0` - 异步HTTP客户端
- `beautifulsoup4>=4.12.0` - HTML解析
- `lxml>=4.9.0` - XML/HTML解析器
- `requests>=2.31.0` - HTTP请求库

### 核心组件
- `CSarXivClient` - 网站内容解析客户端
- MCP 服务器实现
- 异步HTTP请求处理
- 基于CSS选择器的精确HTML解析

### 解析策略
服务器基于实际HTML结构进行解析：

1. **学科组解析** - 查找`discipline-group`类的div元素
2. **主分类解析** - 从`discipline-header`中提取主分类代码和名称
3. **子分类解析** - 从`subdiscipline`元素中提取子分类代码和名称
4. **数据整理** - 按代码排序并去重

支持的代码格式：
- `DJ - 中共党史党建学` (主分类)
- `DJA: 党史` (子分类)
- `FX - 法学` (主分类)
- `FXA: 理论法学` (子分类)

## 开发

### 项目结构
```
CSarXivContextServer/
├── src/
│   └── csarxivcontextserver/
│       ├── __init__.py
│       └── server.py
├── examples/
│   └── usage_example.py
├── pyproject.toml
├── README.md
├── claude_desktop_config.json
└── uv.lock
```

### 贡献指南
1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 注意事项

### 网络访问
- **需要稳定的网络连接访问 CSarXiv.org**
- 建议配置合适的超时设置
- 遵守网站的访问频率限制

### 数据准确性
- 解析结果依赖于网站的HTML结构
- 网站结构变化可能影响数据提取
- 基于CSS选择器的解析策略，准确可靠
- 支持主分类和子分类的完整解析

### 使用限制
- 仅用于学术研究和教育目的
- 遵守CSarXiv.org的使用条款
- 不得用于商业用途

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 联系方式

- 作者：bai-z-l
- 邮箱：b@iziliang.com

## 更新日志

### v0.1.0
- 初始版本发布
- 专注于社科基金申报代码获取
- 基于实际HTML结构的精确解析
- 支持DJ、FX、GL等学科代码格式
- 移除错误的分类对照表，使用动态数据
- 增强解析的准确性和可靠性