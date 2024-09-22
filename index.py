from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.schema import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.utilities import SerpAPIWrapper
from langchain.agents import Tool, initialize_agent, AgentType
import gradio as gr
import sys

CHILDREN_WHYS = None

def initialize_children_why():
    global CHILDREN_WHYS

    # 实例化文档加载器和处理
    loader = TextLoader("./children_whys_data.txt")
    documents = loader.load()
    text_splitter = CharacterTextSplitter(separator="\n\n", chunk_size=100, chunk_overlap=0, length_function=len)
    docs = text_splitter.split_documents(documents)

    # 初始化FAISS向量数据库
    db = FAISS.from_documents(docs, OpenAIEmbeddings())
    
    # 定义检索函数
    def retriever(query):
        similar_docs = db.similarity_search(query, k=3)
        context = "\n".join([doc.page_content for doc in similar_docs])
        print("Vector DB Context:", context)
        return context

    # 初始化搜索工具
    search = SerpAPIWrapper()

    # 初始化工具
    tools = [
        Tool(
            name="Search",
            func=search.run,
            description="用于回答关于当前事件或世界现状的问题"
        ),
        Tool(
            name="VectorDB",
            func=retriever,
            description="用于从本地知识库中检索相关信息"
        )
    ]

    # 初始化LLM
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)

    # 初始化 agent, 使用 zero-shot-react-description 策略，verbose=True 会打印出所有日志
    agent = initialize_agent(
        tools, 
        llm, 
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    # 定义模型系统 message
    system_message = """你是一位充满爱心和耐心的妈妈，正在回答自己孩子的"为什么"问题。你的回答应该：
    1. 使用简单、易懂的语言，适合儿童理解。
    2. 充满温暖和鼓励，激发孩子的好奇心和学习兴趣。
    3. 尽可能用生活中的例子来解释复杂的概念。
    4. 如果遇到不确定的问题，诚实地说："这个问题妈妈现在也不太清楚，不如我们一起去查查看，好吗？"
    5. 在回答结束时，可以适当地鼓励孩子继续提问或思考。
    6. 使用亲切的称呼，如"宝贝"、"亲爱的"等。
    7. 偶尔在回答中加入一些温馨的互动，比如"你觉得呢？"或"妈妈很高兴你问这个问题"。

    你有两个信息来源：网络搜索和本地知识库。请综合这两种信息来源，为孩子提供最合适的回答。
    记住，你的目标是不仅回答问题，还要培养孩子的学习兴趣和批判性思维能力。
    回答问题必须使用中文。"""

    # 定义 CHILDREN_WHYS 函数，接受 query 参数，调用 agent.run 方法，返回响应
    CHILDREN_WHYS = lambda query: agent.run(f"{system_message}\n\n孩子的问题: {query}")
    return CHILDREN_WHYS

# 定义 sales_chat 函数，接受 message 和 history 参数，调用 CHILDREN_WHYS 函数，返回响应
def sales_chat(message, history):
    global CHILDREN_WHYS
    if CHILDREN_WHYS is None:
        return "系统未正确初始化，请联系管理员。"
    
    print(f"[message]{message}")
    print(f"[history]{history}")
    
    try:
        # 调用 CHILDREN_WHYS 函数，接受 message 参数，返回响应
        response = CHILDREN_WHYS(message)
        print(f"[result]{response}")
        return response
    except Exception as e:
        print(f"Error occurred: {e}")
        return f"发生错误：{str(e)}"

# 定义 launch_gradio 函数，用于启动 gradio 界面
def launch_gradio():
    print("启动gradio", CHILDREN_WHYS)
    # 创建 gradio 界面，fn 参数指定为 sales_chat 函数，title 参数指定为 "十万个为什么"，chatbot 参数指定为 gr.Chatbot(height=600)
    demo = gr.ChatInterface(
        fn=sales_chat,
        title="十万个为什么",
        chatbot=gr.Chatbot(height=600),
        description="欢迎来到十万个为什么!我是你的智能妈妈,有什么问题尽管问我哦~",
        examples=["为什么天是蓝色的?", "为什么地球是圆的?"],
        retry_btn="重新生成",
        undo_btn="撤销",
        clear_btn="清除对话",
    )

    # 启动 gradio 界面，share=True 表示共享，server_name="0.0.0.0" 表示在所有网络接口上运行
    demo.launch(share=True, server_name="0.0.0.0")

# 如果当前模块是主模块，则执行以下代码
if __name__ == "__main__":
    # 初始化 CHILDREN_WHYS 函数
    CHILDREN_WHYS = initialize_children_why()
    
    # 如果初始化失败，则退出程序
    if CHILDREN_WHYS is None:
        print("初始化失败，程序退出。")
        sys.exit(1)
    
    # 启动 gradio 界面
    launch_gradio()