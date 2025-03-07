from pydantic import BaseModel

class IngestDocument(BaseModel):
    pass

class Document(BaseModel):
    """Object that represents a document being returned"""
    id : str
    text: list[str] # each element is a page
    doc_type: str # if it was pdf or word or user input
    doc_category: str # if it was about recalling last game info, game notes etc.

class Summerize(BaseModel):
    input_text: str
    history: list[str]

class InvokeAgent(BaseModel):
    user_input: str
    message_hist: str

class AgentResponse(BaseModel):
    response: str
    metadata: str

class Character(BaseModel):
    uuid: str
    name: str
    history: list[str] # list of all the things that has happened with this character
    inventory: dict 
