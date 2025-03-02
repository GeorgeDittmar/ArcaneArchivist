from fastapi import FastAPI

VERSION = "v0.1"
app = FastAPI()


@app.get("/")
async def root():
    return {"message": f"ArcaneArchive {VERSION}"}

@app.get("/health")
async def health_check():
    return {"message": f"ArcaneArchive {VERSION} \n Status: UP"}

@app.post("/v1/document/ingest")
async def document_ingestion():
    return {"message": f"ArcaneArchive {VERSION} \n Status: UP"}

@app.post("/v1/document/update")
async def document_update():
    return {"message": f"ArcaneArchive {VERSION} \n Status: UP"}

@app.post("/v1/agents/invoke")
async def agent_call():
    """Handles a call to the Agents which will autonamously decide what to do with the user input."""
    return {"message": f"ArcaneArchive {VERSION} \n Status: UP"}