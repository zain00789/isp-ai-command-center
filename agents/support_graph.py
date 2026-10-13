import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from langgraph.graph import StateGraph, START
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from tools.ticket_tools import create_support_ticket
from tools.customer_tools import (
    get_customer_status,
    get_customer_package
)
from tools.billing_tools import get_customer_bill
# 1. Load API key from .env
load_dotenv()


# 2. Connect to Gemini
llm = ChatGoogleGenerativeAI(
    model=os.environ["GEMINI_MODEL"],
    google_api_key=os.environ["GEMINI_API_KEY"]
)

# 3. Give Gemini access to our tool
tools = [
    get_customer_status,
    get_customer_package,
    get_customer_bill,
    create_support_ticket
]
llm_with_tools = llm.bind_tools(tools)


# 4. Create our AI node
def ai_agent(state: MessagesState):

    # Ask Gemini to process the conversation
    response = llm_with_tools.invoke(state["messages"])

    # Debugging: check whether the agent is running
    print("Agent node executed")

    # Debugging: check whether Gemini requested a tool
    if response.tool_calls:
        print("Tool requested:", response.tool_calls)
    else:
        print("No tool requested")

    return {"messages": [response]}

# 5. Build the LangGraph workflow
workflow = StateGraph(MessagesState)

workflow.add_node("agent", ai_agent)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "agent")

workflow.add_conditional_edges(
    "agent",
    tools_condition
)

workflow.add_edge("tools", "agent")

# 6. Compile the graph
app = workflow.compile()
def show_workflow_steps():
    print("\nOur LangGraph workflow:")
    print("START -> agent")
    print("agent -> tools (if needed)")
    print("tools -> agent")
    print("agent -> END (when finished)")

# 7. Test our workflow
if __name__ == "__main__":
    print("\nStarting LangGraph workflow...\n")

    result = app.invoke({
        "messages": [
            SystemMessage(content="""
            You are a polite Pakistani ISP support assistant.

            Reply in simple Roman Urdu using English letters.
            Always address customers as 'aap'.

            When asked about internet connection status,
            use the get_customer_status tool.

            Never invent connection details.
            The tool uses fictional test data, not live Falcon data.
            """),

 HumanMessage(
    content="ISP001 ka internet bill kitna hai?"
)
        ]
    })

    # Display only the final text
    final_message = result["messages"][-1]

    print("\nAI Agent:")

    for block in final_message.content_blocks:
        if block["type"] == "text":
            print(block["text"])