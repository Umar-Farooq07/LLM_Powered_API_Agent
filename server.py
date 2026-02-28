from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from io import BytesIO
import os
import re 


from chunking import MarkdownChunker
from StoringRetrieval import VectorStoreRetrival
from LLM import QueryLLM

import docker
import tempfile


from dotenv import load_dotenv


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GLOBAL STATE ---
print("⏳ Loading AI Models... (This may take a moment)")
global_chunker = MarkdownChunker()
global_vdb = VectorStoreRetrival()
global_llm = QueryLLM()
print("✅ Models Loaded! Server is ready.")

# --- HELPER CLASSES ---
class RagEngine:
    def __init__(self, vector_store, llm_agent):
        self.vdb = vector_store
        self.llm = llm_agent
        
    def ask(self, query_text):
        context = self.vdb.retrieve_data(query_text)
        response = self.llm.query_llm(context, query_text)
        if hasattr(response, 'content'):
            return response.content
        return str(response)

class ChatMessage(BaseModel):
    text: str
    api_key: str = ""

class RunCodeRequest(BaseModel):
    code: str
    api_key: str = ""

# --- 🚀 LOGIC: SEPARATE TEXT FROM CODE ---
def process_llm_response(full_response: str):
    """
    Separates the explanation text from the Python code block.
    """
    
    code_pattern = r"```(?:python)?\s*(.*?)(?:```|$)"
    match = re.search(code_pattern, full_response, re.DOTALL | re.IGNORECASE)
    
    if match:
        extracted_code = match.group(1).strip()
        return {"text": full_response, "code": extracted_code}
    else:
        return {"text": full_response, "code": None}

# --- ENDPOINTS ---

@app.post("/upload")
async def upload_pdf(pdf: UploadFile = File(...)):
    if pdf.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    print(f"📥 Receiving {pdf.filename}...")
    pdf_bytes = await pdf.read()
    pdf_stream = BytesIO(pdf_bytes)
    pdf_stream.name = pdf.filename 
    
    try:
        print("🔨 Chunking...")
        chunks = global_chunker.convert_to_chunks(pdf_stream)
        print(f"💾 Storing {len(chunks)} chunks...")
        global_vdb.create_db(chunks)
        return {"status": "success", "message": f"Ready! Processed {len(chunks)} chunks."}
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
def chat(query: ChatMessage):
    try:
        engine = RagEngine(global_vdb, global_llm)
        raw_output = engine.ask(query.text)
        
        structured_data = process_llm_response(raw_output)
        
        return {
            "answer": structured_data["text"],      
            "extracted_code": structured_data["code"] 
        }
        
    except Exception as e:
        print(f"❌ Error in chat: {e}")
        return {"answer": f"Error: {str(e)}", "extracted_code": None}

import tempfile
import subprocess
import sys
import os


@app.post("/run-code")
def run_code(req: RunCodeRequest):
    print("💻 Executing code directly on local machine...")

    clean_code = req.code
    # Inject API Key if user provided one
    if req.api_key and req.api_key.strip():
        clean_code = clean_code.replace("your_api_key_here", req.api_key)
        clean_code = clean_code.replace("YOUR_API_KEY", req.api_key)

    try:
        # 1. Create a temporary file to hold the code
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode='w', encoding='utf-8') as temp_script:
            script_content = f"""import os
import sys

# --- USER CODE BELOW ---
{clean_code}
"""
            temp_script.write(script_content)
            temp_script_path = temp_script.name

        # 2. Run the code natively on your machine
        try:
            print("⏳ Running script...")
            
            # 🚀 We use sys.executable to ensure it runs inside your 'venv'
            result = subprocess.run(
                [sys.executable, temp_script_path],
                capture_output=True,
                text=True,
                timeout=30,  # 30-second kill switch so infinite loops don't freeze your PC
                env={**os.environ, "API_KEY": req.api_key} # Pass API key as an environment variable
            )
            
            # Handle Success
            if result.returncode == 0:
                output = result.stdout.strip()
                return {"output": output if output else "✅ Code ran successfully (No Output)"}
            
            # Handle Error in the Python script
            else:
                return {"output": f"❌ Execution Error:\n{result.stderr.strip()}"}
            
        finally:
            # 3. Cleanup the local temp file
            if os.path.exists(temp_script_path):
                os.remove(temp_script_path)

    except subprocess.TimeoutExpired:
        return {"output": "❌ Execution Error: Code took too long to run (Timeout killed it)."}
    except Exception as e:
        print(f"Server Error: {e}")
        return {"output": f"Local Environment Error: {str(e)}"}