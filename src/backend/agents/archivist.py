from typing import Annotated

from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict 

from langgraph.graph import StateGraph, START, END 
from langgraph.graph.message import add_messages 
from langchain.prompts import PromptTemplate


class AgentRouterState(TypedDict):
    input: str
    output: str
    decision: str

# Creating the first analysis agent to check the prompt structure
# This print part helps you to trace the graph decisions
def analyze_text(state):
    llm = ChatOpenAI()
    prompt = PromptTemplate.from_template("""
    You are an agent that needs to define if a given text input is a note to be saved, a question for a bot to answer or other.

    Text : {input}

    Analyse the question. Only answer note if it appears like someone is writing information to be saved, question if there is a clear question being asked, or other if they want to do something else.

    Your answer (note/question/other) :
    """)
    chain = prompt | llm
    response = chain.invoke({"input": state["input"]})
    decision = response.content.strip().lower()
    return {"decision": decision, "input": state["input"]}

# Creating the generic agent
def other_task(state):
    llm = ChatOpenAI()
    prompt = PromptTemplate.from_template(
        "Give a general and concise answer to the question: {input}"
    )
    chain = prompt | llm
    response = chain.invoke({"input": state["input"]})
    return {"output": response}

def lookup_info_agent(state):
    # looks up information if needed
    pass

def note_saver_agent(state):
    # tool to save text if it has been deemed as information to be saved
    # have this agent look at text and see if any entities are in it that match entities in the db and
    # relate them to the notes
    pass

def entity_extractor_agent(state):
    # can be called by the note saver agent
    # extracts entities in the text, such as player characters, NPCs, etc.
    # return list of entities and look up to see if they exist in the db already and if so link them somehow
    pass

def process_question(state):
    graph = create_graph()
    result = graph.invoke({"input": state["input"]})
    print("\n--- Final answer ---")
    print(result["output"])
    return state

def create_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("analyze", analyze_text)
    workflow.add_node("note_agent", note_saver)
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
    workflow.add_edge("code_agent", END)
    workflow.add_edge("generic_agent", END)

    return workflow.compile()

# send to openai and determine if waht was typed in the box was a qustion, note, or lookup