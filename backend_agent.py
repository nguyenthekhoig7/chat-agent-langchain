import os
try:
    import api_key
except:
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import api_key

os.environ['OPENAI_API_KEY'] = api_key.OPENAI_API_KEY
# os.environ['LANGCHAIN_API_KEY'] = api_key.LANGSMITH_KEY

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
import bs4
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import StateGraph, MessagesState
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool

from langgraph.graph import END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

class AgentWithChatGPT():
    def __init__(self):
        self._build_agent_graph()

    def answer_with_session_config(self, input_message_with_config: dict):
        # input_message = "Hello"
        config = input_message_with_config['config']
        input_message = input_message_with_config['message']
        output = self.graph.invoke({"messages": input_message}, config=config)          
        return output['messages'][-1].content

    def answer_static(self, input_message):
        # input_message = "Hello"
        config = {"configurable": {"thread_id": "user1234"}}
        output = self.graph.invoke({"messages": input_message}, config=config)          
        return output['messages'][-1].content
    
    def answer_stream(self, input_message):
        return "The model is in building stage."
    

    @tool(response_format="content_and_artifact")
    def _retrieve(self, query: str):
        """Retrieve information related to query"""
        retrieved_docs = self.vector_store.similarity_search(query, k=2)
        serialized = "\n\n".join( [f"Source: {doc.metadata}\nContent: {doc.page_content}"
                                for doc in retrieved_docs])
        return serialized, retrieved_docs
    

    def _query_or_respond(self, state: MessagesState):
        """Generate tool call for retrieval or respond directly"""
        llm_with_tools = self.llm.bind_tools([self._retrieve])
        response = llm_with_tools.invoke(state['messages'])

        return {"messages": [response]}

    def _generate(self, state: MessagesState):
        """Generate answer."""

        recent_tool_messages = []
        for message in reversed(state['messages']): # why need reversed?
            if message.type == "tool":
                recent_tool_messages.append(message)
            else:
                break
        tool_messages = recent_tool_messages[::-1] # reverse the list, why?

        docs_content = "\n\n".join(doc.content for doc in tool_messages)

        system_message_content = (
                "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise."
            "\n\n"
            f"{docs_content}"
        )
        conversational_messages = [
            message 
            for message in state['messages']
                if message.type in ('human', 'system')
                or (message.type == 'ai' and not message.tool_calls)
        ]
        prompt = [SystemMessage(system_message_content)] + conversational_messages

        response = self.llm.invoke(prompt)
        return {'messages': [response]}


    def _build_agent_graph(self):
        """
        Initialize the LLM model and build the agent graph.        
        """
        self.llm = ChatOpenAI(model='gpt-4o-mini')
        embeddings = OpenAIEmbeddings(model='text-embedding-3-large')
        self.vector_store = InMemoryVectorStore(embeddings)
        # Load and chunk contents of the blog
        loader = WebBaseLoader(
            web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
            bs_kwargs=dict(
                parse_only=bs4.SoupStrainer(
                    class_=("post-content", "post-title", "post-header")
                )
            ),
        )
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        all_splits = text_splitter.split_documents(docs)
        self.vector_store.add_documents(all_splits)
        graph_builder = StateGraph(MessagesState)

        _tools = ToolNode([self._retrieve])

        graph_builder.add_node(self._query_or_respond)
        graph_builder.add_node(_tools)
        graph_builder.add_node(self._generate)

        graph_builder.set_entry_point("_query_or_respond") # ? is this equivalent to? .add_edge(START, "query_or_respond")
        graph_builder.add_conditional_edges(
            "_query_or_respond",
            tools_condition,
            {END: END, "tools": "tools"}
        )
        graph_builder.add_edge("tools", "_generate")
        graph_builder.add_edge("_generate", END)

        memory = MemorySaver()
        self.graph = graph_builder.compile(checkpointer=memory)