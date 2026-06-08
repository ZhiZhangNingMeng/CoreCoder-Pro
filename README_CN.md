# CoreCoder-Pro: 你的专属 AI Agent 助手

本项目是对 Agent 架构 CoreCoder 的二次开发与产品化实践。该架构由作者何宇峰从 Claude Code 约 51 万行源码中提炼出 1400 行核心代码构建而成，原生聚焦于代码编辑场景。本项目在此基础上进行客户端优化与业务逻辑扩充，将其升级为一款具备更强数据分析能力与知识检索能力的可视化 AI 助手。

---
## 核心设计模式与架构
在完整继承 CoreCoder 核心模块的基础上，针对复杂数据流与知识流进行了定制化扩充，同时对原有功能进行了调优。
### 1. 系统逻辑分层

| 架构层级 (Layer) | 核心模块 / 设计模式 | 功能实现与优化点 | 对应核心文件 |
| :--- | :--- | :--- | :--- |
| **交互表现层** | **可视化 Web UI** | 基于 Streamlit 的Web端展示、流式打字机渲染与工具调用动态折叠。 | `app.py` |
| **中枢控制层** | **Agent 调度循环** | 主从架构，支持多工具并行调用与子代理隔离。 | `agent.py`<br>`tools/agent.py` |
| | **三层上下文压缩** | 阶梯式内存监控，支持冗余截断与 LLM 摘要降级。 | `context.py` |
| | **会话持久化** | 会话记录本地保存与记忆摘要。 | `session.py` |
| **安全执行层** | **动态 Python 沙盒** | 进程隔离执行，按需动态拉起 Pandas/NumPy 进行安全数据计算。 | `tools/data_analysis.py` |
| | **安全风控拦截** | 危险命令人工确认与跨端字符编码校验。 | `tools/bash.py` |
| **数据引擎层** | **本地 RAG 引擎** | ChromaDB 向量化存储与文档切片，支持私有文件检索。 | `rag_storage.py` |

### 2. 项目文件目录

```text
pro_corecoder/
├── app.py                      Web 端可视化交互启动口
└── corecoder/
    ├── cli.py                  REPL + 命令行交互入口 (优化)                  
    ├── agent.py                Agent 循环 + 并行调度      
    ├── llm.py                  流式客户端 + 重试机制          
    ├── context.py              上下文三层压缩机制                    
    ├── session.py              会话保存/恢复                
    ├── prompt.py               系统提示词
    ├── rag_storage.py          本地 ChromaDB 向量知识引擎 (新增)              
    ├── config.py               环境变量配置                 
    └── tools/
        ├── bash.py             Shell执行 + 安全防护 + cd 追踪 (优化)    
        ├── edit.py             搜索替换 + 文件diff             
        ├── read.py             文件读取                  
        ├── write.py            文件写入                    
        ├── glob_tool.py        文件搜索                   
        ├── grep.py             文件内容正则搜索
        ├── data_analysis.py    独立 Python 隔离沙盒 (新增)
        ├── knowledge_search.py 本地私有知识库检索 (新增)                      
        └── agent.py            子代理生成                  
```
---
## ✨ 产品核心升级

### 1. 交互产品化：现代 Web 可视化界面
原生架构采用命令行形式，对话记录与上下文的浏览较为不便，且 Agent 的思考过程与工具调用记录会占据大量对话框空间，翻阅查找困难。本项目基于 Streamlit 构建 Web 交互前端，实现了流式输出效果，增加了工具调用的动态显示与可视化折叠面板，并支持一键清空历史记录，显著提升用户体验。
<img width="8812" height="4044" alt="主页面" src="https://github.com/user-attachments/assets/bf83f96d-2f36-4e90-8513-af982c0d4478" />

### 2. 数据处理降本增效：封装动态 Python 沙盒
原模型在处理数据时，会反复调用终端 bash 脚本进行计算操作，导致终端与云端 API 频繁通信，Token 消耗量较大。本项目通过封装动态 Python 沙盒，新增 “data_analysis” 工具，允许 Agent 自主生成并在隔离环境中调用 Python 内置函数（如 Pandas、NumPy 等）执行脚本，大幅降低数据清洗与统计过程中的通信链路开销，实现更高效便捷的数据处理。
<img width="8802" height="4026" alt="数据分析" src="https://github.com/user-attachments/assets/cacef5e7-f221-49a8-b447-a8b782eb4fdf" />


### 3. 信息检索能力增强：轻量化本地 RAG 检索
原生 Agent 在特定垂直领域的专业知识储备无法及时更新，信息检索能力存在不足。本项目新增 “rag_storage” 工具，本地集成 ChromaDB 向量数据库引擎，构建起轻量级 RAG 功能，支持对长文本及专业研报进行切片检索，有效提升垂直场景下的回答精度与可信度。同时，文件的向量化处理完全在本地执行，避免原始文件向云端发送带来的泄密风险，充分保护用户隐私。

在使用时，先使用 “/ingest” 将本地私有文档喂给Agent，进行本地切片与向量化，随后便可以根据内容进行切片搜索与分析。
```text
#测试用例
#  CyberCoder绝密档案

## 1. 核心吉祥物设定
CyberCoder 框架的官方吉祥物是一只名叫“量子橘猫”的赛博宠物。它诞生于 2024 年的某个深夜，由一位熬夜写 Bug 的程序员意外触发的内存泄漏所创造。
- **最喜欢的食物**：赛博小鱼干（Cyber Dried Fish）
- **口头禅**：“喵喵喵，你的代码又 Panic 了！”

## 2. 隐藏指令
在 CyberCoder 的终极版本中，如果用户在终端输入“芝麻开门”，系统将会自动播放一首 8-bit 风格的《摇篮曲》，帮助程序员入睡。
```
<img width="8802" height="4014" alt="rag" src="https://github.com/user-attachments/assets/16efa876-0c38-44fb-9be7-f9b2e2a4f0db" />


### 4. 系统安全加固：底线风控与编码容错
原生框架在执行文件删除命令时会直接执行，存在误删核心文件的风险。本项目引入人工审查机制：当 Agent 希望执行删除操作时，Web 端会弹出询问窗口，减少误删事件发生。同时，修复了原生系统在不同操作系统下交互的缺陷，引入 UTF-8 强制覆写与错误替换机制，解决了 GBK 编码导致的崩溃漏洞。
<img width="8802" height="4036" alt="删除" src="https://github.com/user-attachments/assets/aaa7efa5-82c7-45a9-bb94-2632f682b8e4" />

---

## 🚀 快速启动 (Quick Start)

### 1. 安装环境依赖
在根目录下新建一个 `requirements.txt` 文件，并写入以下核心依赖：
```text
# 核心大模型通信与基础依赖 (Base Engine)
openai>=1.14.0
rich>=13.7.0
prompt_toolkit>=3.0.40
python-dotenv>=1.0.0

# 现代 Web UI 产品化交互 (Frontend)
streamlit>=1.32.0

# 动态数据分析沙盒支持包 (Data Sandbox)
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0

# RAG 轻量级本地知识库 (Vector Database)
chromadb>=0.4.20
```

### 2. 配置环境凭证
在项目根目录下创建一个 `.env` 文件，配置你的大模型 API 密钥（支持任意 OpenAI 兼容接口，如 Kimi、DeepSeek、Qwen 等）：
```bash
#以deepseek为例
CORECODER_BASE_URL=https://api.deepseek.com

CORECODER_API_KEY= your_API_Key

CORECODER_MODEL=deepseek-v4-flash
```

### 3. 启动网页端产品
在终端中运行以下命令，系统会自动在浏览器中弹出现代化的 Web 可视化交互界面：
```bash
streamlit run app.py
```

## 鸣谢与开源声明
本项目是由开源项目 CoreCoder 二次开发而来。
特别感谢原作者何宇峰开源的 Agent 核心引擎。

本分支（CoreCoder-Pro）站在巨人的肩膀上，保留了其强大的核心 Agent 路由与工具调用调度循环，本项目主要核心文件继承自CoreCoder，在其框架上进行了补充升级，新增代码遵循了原有架构规则，并按照其规定路径保存上传。想要了解更多关于CoreCoder的信息，请移步至原作者开源项目[CoreCoder](https://github.com/he-yufeng/CoreCoder)。
