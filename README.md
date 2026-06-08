# CoreCoder-Pro: Your Exclusive AI Agent Assistant

This project is a secondary development and productization practice based on the CoreCoder agent architecture. The original architecture, distilled from approximately 510,000 lines of Claude Code source code down to 1,400 core lines by author He Yufeng, originally focused on code editing scenarios. This project optimizes the client side and expands the business logic, upgrading it into a visual AI assistant with stronger data analysis and knowledge retrieval capabilities.

---

## ✨ Core Product Upgrades

### 1. Interactive Productization: Modern Web Visual Interface
The original architecture used a command-line interface, making it inconvenient to browse chat history and context. Furthermore, the Agent's thought processes and tool-call records took up massive console space, making them hard to review. This project builds a Web interactive frontend based on Streamlit, implementing streaming output, dynamic displays of tool calls with visual collapsible panels, and a one-click history clearing feature, significantly enhancing the user experience.

### 2. Data Processing Cost Reduction & Efficiency Enhancement: Dynamic Python Sandbox
When processing data, the original model repeatedly called terminal bash scripts for computation, leading to frequent communication between the terminal and cloud APIs and high Token consumption. This project encapsulates a dynamic Python sandbox, allowing the Agent to autonomously generate and execute scripts using Python built-in functions (such as Pandas and NumPy) in an isolated environment. This drastically reduces the communication link overhead during data cleaning and statistics, realizing more efficient and convenient data processing.

### 3. Enhanced Information Retrieval: Lightweight Local RAG
The original Agent lacked up-to-date professional knowledge in specific vertical domains, leading to insufficient information retrieval capabilities. This project locally integrates the ChromaDB vector database engine to build a lightweight RAG (Retrieval-Augmented Generation) feature. It supports slicing and retrieving long texts and professional research reports, effectively improving the accuracy and credibility of answers in vertical scenarios. Meanwhile, document vectorization is executed completely locally, avoiding the leakage risks of sending original files to the cloud and fully protecting user privacy.

### 4. System Security Reinforcement: Baseline Risk Control & Encoding Fault Tolerance
The original framework executed file deletion commands directly, posing the risk of accidentally deleting core files. This project introduces a Human-in-the-Loop (HITL) review mechanism: when the Agent attempts a deletion operation, a confirmation dialog pops up on the Web frontend, reducing accidental deletions. Additionally, it fixes cross-OS interaction defects in the original system by introducing mandatory UTF-8 overwriting and error replacement mechanisms (`errors="replace"`), resolving crash vulnerabilities caused by GBK encoding.

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
