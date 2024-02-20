from fastapi import FastAPI, HTTPException, UploadFile
from typing import Annotated
import uvicorn
from io import StringIO
from parser import ParserFactory
from summarise_gpt import summarise_doc
from utils import get_file_extension

# Create an instance of the FastAPI class
app = FastAPI()


# Define a route using a decorator
@app.get("/")
async def sanity_check():
    return {"message": "Service is up!"}


@app.post("/generate_summary")
async def generate_summary(file: UploadFile):
    file_extension = get_file_extension(file.filename)
    source_stream = await file.read()
    try:
        parser = ParserFactory(source_stream, file_extension).build()
    except NotImplementedError:
        raise HTTPException(status_code=400, detail="Send a valid docx file")
    read_docs = parser.read()
    return {"summary": summarise_doc(read_docs)}


if __name__ == "__main__":
    uvicorn.run("mainapi:app",reload=True)
