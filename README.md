# CoreCoder-Pro: Your Exclusive AI Agent Assistant

This project is a secondary development and productization practice based on the CoreCoder agent architecture. The original architecture, distilled from approximately 510,000 lines of Claude Code source code down to 1,400 core lines by author He Yufeng, originally focused on code editing scenarios. This project optimizes the client side and expands the business logic, upgrading it into a visual AI assistant with stronger data analysis and knowledge retrieval capabilities.

---
## 🧰 Core Design Patterns and Architecture
Based on a complete inheritance of the CoreCoder core modules, this project introduces customized extensions for complex data and knowledge flows, while also tuning the original functionality.

### 1. System Logic Layering

| Architecture Layer | Core Module / Design Pattern | Function Implementation & Optimization | Corresponding Core File |
| :--- | :--- | :--- | :--- |
| **Interaction & Presentation Layer** | **Visual Web UI** | Streamlit-based web display, streaming typewriter rendering, and dynamic collapsible tool calls. | `app.py` |
| **Orchestration & Control Layer** | **Agent Scheduling Loop** | Master‑slave architecture supporting parallel tool calls and sub‑agent isolation. | `agent.py`<br>`tools/agent.py` |
| | **Three‑Tier Context Compression** | Staged memory monitoring with redundant truncation and LLM‑based summarization fallback. | `context.py` |
| | **Session Persistence** | Local session saving and memory summarization. | `session.py` |
| **Security & Execution Layer** | **Dynamic Python Sandbox** | Process‑isolated execution, on‑demand dynamic invocation of Pandas/NumPy for safe data computation. | `tools/data_analysis.py` |
| | **Security Risk Control** | Human confirmation for dangerous commands and cross‑platform character encoding validation. | `tools/bash.py` |
| **Data Engine Layer** | **Local RAG Engine** | ChromaDB vector storage and document chunking, supporting private file retrieval. | `rag_storage.py` |

### 2. Project File Directory

```text
pro_corecoder/
├── app.py                      Web‑side visual interaction entry point
└── corecoder/
    ├── cli.py                  REPL + command line interaction entry (optimized)                  
    ├── agent.py                Agent loop + parallel scheduling      
    ├── llm.py                  Streaming client + retry mechanism          
    ├── context.py              Three‑tier context compression mechanism                    
    ├── session.py              Session save/restore                
    ├── prompt.py               System prompt
    ├── rag_storage.py          Local ChromaDB vector knowledge engine (new)              
    ├── config.py               Environment variable configuration                 
    └── tools/
        ├── bash.py             Shell execution + security protection + cd tracking (optimized)    
        ├── edit.py             Search & replace + file diff             
        ├── read.py             File reading                  
        ├── write.py            File writing                    
        ├── glob_tool.py        File search                   
        ├── grep.py             File content regex search
        ├── data_analysis.py    Standalone Python isolation sandbox (new)
        ├── knowledge_search.py Local private knowledge base retrieval (new)                      
        └── agent.py            Sub‑agent generation
```
---

## ✨ Core Product Upgrades

### 1. Interactive Productization: Modern Web Visual Interface
The original architecture used a command-line interface, making it inconvenient to browse chat history and context. Furthermore, the Agent's thought processes and tool-call records took up massive console space, making them hard to review. This project builds a Web interactive frontend based on Streamlit, implementing streaming output, dynamic displays of tool calls with visual collapsible panels, and a one-click history clearing feature, significantly enhancing the user experience.
<img width="8802" height="4046" alt="主页面eng" src="https://github.com/user-attachments/assets/12f79038-3f90-4bf1-b39d-14f47d1a77f6" />

### 2. Data Processing Cost Reduction & Efficiency Enhancement: Dynamic Python Sandbox
When processing data, the original model repeatedly called terminal bash scripts for computation, leading to frequent communication between the terminal and cloud APIs and high Token consumption. This project encapsulates a dynamic Python sandbox and adds a new "data_analysis" tool, allowing the Agent to autonomously generate and execute scripts in an isolated environment using built‑in Python functions (such as Pandas, NumPy, etc.). This significantly reduces communication overhead during data cleaning and statistical processing, achieving more efficient and convenient data handling.
<img width="8802" height="4024" alt="数据分析eng" src="https://github.com/user-attachments/assets/d5b499f1-e98e-4936-bc38-78507986ddd9" />

### 3. Enhanced Information Retrieval: Lightweight Local RAG
The original Agent lacked up-to-date professional knowledge in specific vertical domains, leading to insufficient information retrieval capabilities. This project adds a new "rag_storage" tool, locally integrating the ChromaDB vector database engine to build lightweight RAG functionality. It supports chunk‑based retrieval of long texts and professional reports, effectively improving answer accuracy and credibility in vertical scenarios. At the same time, all file vectorization is performed locally, avoiding the risk of data leakage from sending original files to the cloud and fully protecting user privacy.

When using it, first run “/ingest” to feed local private documents to the Agent for local chunking and vectorization. After that, you can perform chunk‑based searching and analysis on the content.
```text
# Test Case  
# CyberCoder Top‑Secret File  

## 1. Core Mascot Settings  
The official mascot of the CyberCoder framework is a cyborg pet named "Quantum Orange Cat". It was born late one night in 2024, accidentally created by a programmer staying up late to fix bugs, triggered by a memory leak.  
- **Favorite food**: Cyber Dried Fish  
- **Catchphrase**: "Meow meow meow, your code has panicked again!"  

## 2. Hidden Command  
In the ultimate version of CyberCoder, if the user types "Open Sesame" in the terminal, the system will automatically play an 8‑bit style "Lullaby" to help the programmer fall asleep.
```
<img width="8802" height="4054" alt="rageng" src="https://github.com/user-attachments/assets/73f89639-499c-48c2-bfa6-977bf1272e5e" />

### 4. System Security Reinforcement: Baseline Risk Control & Encoding Fault Tolerance
The original framework executed file deletion commands directly, posing the risk of accidentally deleting core files. This project introduces a Human-in-the-Loop (HITL) review mechanism: when the Agent attempts a deletion operation, a confirmation dialog pops up on the Web frontend, reducing accidental deletions. Additionally, it fixes cross-OS interaction defects in the original system by introducing mandatory UTF-8 overwriting and error replacement mechanisms (`errors="replace"`), resolving crash vulnerabilities caused by GBK encoding.
<img width="8802" height="4024" alt="删除eng" src="https://github.com/user-attachments/assets/282d80ef-b503-4a01-83ca-21ea3a021eee" />

---

## 🚀 Quick Start

### 1. Install Dependencies
Create a `requirements.txt` file in the root directory and add the following core dependencies:
```text
# Base Engine & LLM Communication
openai>=1.14.0
rich>=13.7.0
prompt_toolkit>=3.0.40
python-dotenv>=1.0.0

# Frontend Web UI Productization
streamlit>=1.32.0

# Dynamic Data Sandbox Dependencies
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0

# Lightweight Local RAG (Vector Database)
chromadb>=0.4.20
```

### 2. Configure Environment Credentials
Create a `.env` file in the project root directory and configure your LLM API key (supports any OpenAI-compatible API, such as Kimi, DeepSeek, Qwen, etc.):
```bash
# Taking DeepSeek as an example
CORECODER_BASE_URL=[https://api.deepseek.com](https://api.deepseek.com)

CORECODER_API_KEY=your_API_Key

CORECODER_MODEL=deepseek-v4-flash
```

### 3. Launch the Web Product
Run the following command in the terminal, and the system will automatically pop up the modern Web visual interactive interface in your browser:
```bash
streamlit run app.py
```

## Acknowledgments & Open Source Declaration
This project is a secondary development derived from the open-source project CoreCoder.
Special thanks to the original author He Yufeng for open-sourcing the core Agent engine.

This branch (CoreCoder-Pro) stands on the shoulders of giants, retaining its powerful core Agent routing and tool-call scheduling loop. The main core files of this project are inherited from CoreCoder, with supplementary upgrades built upon its framework. Newly added code follows the original architectural rules and is saved and uploaded according to the prescribed paths. To learn more about CoreCoder, please visit the original author's open-source project [CoreCoder](https://github.com/he-yufeng/CoreCoder).
