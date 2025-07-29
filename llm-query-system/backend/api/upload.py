# backend/api/upload.py

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import os
import tempfile

from doc_processor.pdf_extractor import extract_text_from_pdf
from doc_processor.docx_extractor import extract_text_from_docx
from doc_processor.email_extractor import extract_text_from_email
from doc_processor.chunker import chunk_text
from services.embedding_search import embed_and_store_chunks

router = APIRouter()

@router.post("/")
async def upload_documents(files: List[UploadFile] = File(...)):
    results = []

    for file in files:
        filename = file.filename.lower()
        suffix = os.path.splitext(filename)[-1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        try:
            if filename.endswith(".pdf"):
                text = extract_text_from_pdf(tmp_path)
            elif filename.endswith(".docx"):
                text = extract_text_from_docx(tmp_path)
            elif filename.endswith(".eml"):
                text = extract_text_from_email(tmp_path)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {filename}")
        except Exception as e:
            os.remove(tmp_path)
            raise HTTPException(status_code=500, detail=f"Failed to extract text from {filename}: {str(e)}")

        os.remove(tmp_path)

        chunks = chunk_text(text)
        embed_and_store_chunks(chunks, metadata={"source": filename})

        results.append({
            "filename": filename,
            "chunks_uploaded": len(chunks)
        })

    return JSONResponse(content={"status": "success", "uploaded_files": results})
