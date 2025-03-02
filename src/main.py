from fastapi import FastAPI

VERSION = "v0.1"
app = FastAPI()


@app.get("/")
async def root():
    return {"message": f"ArcaneArchive {VERSION}"}

@app.get("/health")
async def root():
    return {"message": f"ArcaneArchive {VERSION} \n Status: UP"}