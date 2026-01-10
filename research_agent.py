import os
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 注意：在 Manus 环境中，TAVILY_API_KEY 已预配置（如果可用）
# 如果不可用，我们将回退到 DuckDuckGo 但增加重试逻辑

def create_agent():
    # 1. 初始化 LLM
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

    # 2. 定义工具
    # 优先尝试 Tavily，因为它在学术和新闻搜索上更准确
    try:
        search = TavilySearchResults(max_results=3)
    except Exception:
        from langchain_community.tools import DuckDuckGoSearchRun
        search = DuckDuckGoSearchRun()
    
    tools = [search]

    # 3. 定义提示词模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业的 AI 研究助手。你的任务是为用户提供准确、详尽且基于事实的回答。\n"
                  "当你被问及最近发生的事件（如 2024 年的奖项）时，请务必使用搜索工具获取最新信息。\n"
                  "如果第一次搜索没有结果，请尝试更换关键词（例如使用英文关键词）再次搜索。"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # 4. 创建 Agent
    agent = create_openai_tools_agent(llm, tools, prompt)

    # 5. 创建 Agent 执行器
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    return agent_executor

if __name__ == "__main__":
    agent = create_agent()
    # 测试一个明确的 2024 年事实
    query = "2024年诺贝尔物理学奖得主是谁？他们获奖的原因是什么？"
    print(f"正在执行查询: {query}\n")
    try:
        response = agent.invoke({"input": query})
        print("\n--- Agent 最终回答 ---")
        print(response["output"])
    except Exception as e:
        print(f"\n运行过程中出现错误: {e}")
