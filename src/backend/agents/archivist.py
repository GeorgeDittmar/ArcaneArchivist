from typing import Annotated

from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict 

from langgraph.graph import StateGraph, START, END , MessagesState
from langgraph.graph.message import add_messages 
from langchain.prompts import PromptTemplate

from langchain_core.messages import trim_messages
from langgraph.checkpoint.memory import MemorySaver
# importing os module for environment variables
import os
# importing necessary functions from dotenv library
from dotenv import load_dotenv, dotenv_values 
# loading variables from .env file
load_dotenv() 

class AgentRouterState(MessagesState):
    input: str
    output: str
    decision: str

# Creating the first analysis agent to check the prompt structure
# This print part helps you to trace the graph decisions
def analyze_text(state:AgentRouterState):
    llm = ChatOpenAI()
    prompt = PromptTemplate.from_template("""
    You are an agent that needs to decide if a given text input is a note to be saved or any another task (other).
    
    Analyse the question and determine what the user intends with the text. 
    Only reply "note" if the input appears to be information about something. Otherwise reply "other" for any other type of input.
    
    user input: {input}
                                          
    Your decision can only be "note" or "other".
                                          
    decision: 
    """)

    chain = prompt | llm
    response = chain.invoke({"input": state["input"]},config={"configurable": {"thread_id": "1"}})
    decision = response.content.strip().lower()
    print(decision)
    return {"decision": decision, "messages": state["input"]}

# Creating the generic agent
def other_task(state):
    llm = ChatOpenAI()
    prompt = PromptTemplate.from_template(
        "Perform the task thats been asked: {input}"
    )
    chain = prompt | llm
    response = chain.invoke({"input": [state["input"]] + state['messages']},config={"configurable": {"thread_id": "1"}})
    return {"output": response, 'messages': state['input']}

def lookup_info_agent(state):
    # looks up information if needed
    return {"output": "looking up info..."}

def note_saver_agent(state):
    # tool to save text if it has been deemed as information to be saved
    # have this agent look at text and see if any entities are in it that match entities in the db and
    # relate them to the notes
    llm = ChatOpenAI()
    prompt = PromptTemplate.from_template(
        "Take the note and extract any entities that are found and return the note string with the entity between xml tags. Be sure to label the entity tag with what it is: {input}"
    )
    chain = prompt | llm
    response = chain.invoke({"input": [state["input"]] + state['messages'], "config":{"configurable": {"thread_id": "1"}}})
    return {"output": response, 'messages': state['input']}

# def entity_extractor_agent(state):
#     # can be called by the note saver agent
#     # extracts entities in the text, such as player characters, NPCs, etc.
#     # return list of entities and look up to see if they exist in the db already and if so link them somehow
#     llm = ChatOpenAI()
#     prompt = PromptTemplate.from_template(
#         "Perform the task thats been asked: {input}"
#     )
#     chain = prompt | llm
#     response = chain.invoke({"messages": state["input"]})
#     return {"output": response, 'messages': state['input']}

def process_question(state):
    graph = create_graph()
    result = graph.invoke({"input": state["input"]})
    print("\n--- Final answer ---")
    print(result["output"].content)
    return state

def create_graph():
    workflow = StateGraph(AgentRouterState)

    workflow.add_node("analyze", analyze_text)
    workflow.add_node("note_agent", note_saver_agent)
    workflow.add_node("generic_agent", other_task)

    workflow.add_conditional_edges(
        "analyze",
        lambda x: x["decision"],
        {
            "note": "note_agent",
            "other": "generic_agent"
        }
    )

    workflow.set_entry_point("analyze")
    workflow.add_edge("note_agent", END)
    workflow.add_edge("generic_agent", END)
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)

# send to openai and determine if waht was typed in the box was a qustion, note, or lookup

class UserInput(TypedDict):
    input: str
    continue_conversation: bool

def get_user_input(state: AgentRouterState) -> UserInput:
    user_input = input("\nEnter your question (ou 'q' to quit) : ")
    return {
        "input": [user_input] + state['messages'] ,
        "continue_conversation": user_input.lower() != 'q',
        "messages" : user_input
    }
def create_conversation_graph():
    workflow = StateGraph(AgentRouterState)

    workflow.add_node("get_input", get_user_input)
    workflow.add_node("process_question", process_question)

    workflow.set_entry_point("get_input")

    workflow.add_conditional_edges(
        "get_input",
        lambda x: "continue" if x["continue_conversation"] else "end",
        {
            "continue": "process_question",
            "end": END
        }
    )

    workflow.add_edge("process_question", "get_input")
    memory = MemorySaver() 
    return workflow.compile(checkpointer=memory)

def main():
    conversation_graph = create_conversation_graph()
    # starts building up the state
    conversation_graph.invoke({"input": "", "continue_conversation": True},config={"configurable": {"thread_id": "1"}})

if __name__ == "__main__":
    print("Start")
    main()
# from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langgraph.checkpoint.memory import MemorySaver
# from langgraph.graph import START, MessagesState, StateGraph

# workflow = StateGraph(state_schema=MessagesState)


# # Define the function that calls the model
# def call_model(state: AgentRouterState):
#     llm = ChatOpenAI()

#     system_prompt = (
#         "You are a helpful assistant. "
#         "Answer all questions to the best of your ability."
#     )
#     print()
#     messages = [SystemMessage(content=system_prompt)] + state["messages"]
#     print(messages)
#     print()
#     response = llm.invoke(messages)
#     return {"messages": response}


# # Define the node and edge
# workflow.add_node("model", call_model)
# workflow.add_edge(START, "model")

# # Add simple in-memory checkpointer
# memory = MemorySaver()
# app = workflow.compile(checkpointer=memory)
# print(app.invoke(
#     {"messages": [HumanMessage(content="Translate to French: I love programming.")]},
#     config={"configurable": {"thread_id": "1"}},
# )['messages'])
# print()
# print(app.invoke(
#     {"messages": [HumanMessage(content="What did I just ask you?")]},
#     config={"configurable": {"thread_id": "1"}},
# )['messages'][-1].content)