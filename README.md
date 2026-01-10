# 🤖 AI Research Agent

这是一个基于 **LangChain** 和 **GPT-4** 搭建的智能研究助手，具备联网搜索和逻辑推理能力。

## 🚀 功能特点
- **自主联网**：自动搜索最新信息（支持 DuckDuckGo 和 Tavily）。
- **智能推理**：基于大模型整合搜索结果，给出详尽回答。
- **Web 界面**：基于 Streamlit 的友好交互界面。

## 🛠️ 部署说明
本项目支持在 **Streamlit Community Cloud** 上一键部署。

### 部署步骤：
1. 将本项目的所有文件上传到您的 GitHub 仓库。
2. 访问 [Streamlit Cloud](https://share.streamlit.io/)。
3. 连接您的 GitHub 仓库并选择 `app.py` 作为主文件。
4. **关键步骤**：在 Streamlit Cloud 的 `Secrets` 设置中添加您的 `OPENAI_API_KEY`。

## 📄 文件清单
- `app.py`: Web 界面入口。
- `research_agent.py`: Agent 核心逻辑。
- `requirements.txt`: 依赖库列表。
