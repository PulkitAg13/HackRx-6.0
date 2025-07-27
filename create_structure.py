import os

structure = {
    "llm-query-system": {
        "frontend": {
            "public": {},
            "src": {
                "components": {
                    "DocumentUpload.js": "",
                    "QueryForm.js": "",
                    "ResultCard.js": ""
                },
                "pages": {
                    "index.js": "",
                    "upload.js": ""
                },
                "services": {
                    "api.js": ""
                },
                "styles": {},
                "utils": {
                    "formatter.js": ""
                }
            },
            "package.json": "",
            ".env": "VITE_BACKEND_URL=http://localhost:8000"
        },
        "backend": {
            "api": {
                "upload.py": "",
                "query.py": "",
                "health.py": ""
            },
            "services": {
                "llm_parser.py": "",
                "embedding_search.py": "",
                "clause_matcher.py": "",
                "logic_engine.py": "",
                "json_formatter.py": ""
            },
            "doc_processor": {
                "pdf_extractor.py": "",
                "docx_extractor.py": "",
                "email_extractor.py": "",
                "chunker.py": ""
            },
            "pinecone": {
                "client.py": "",
                "index_manager.py": ""
            },
            "db": {
                "models.py": "",
                "crud.py": "",
                "database.py": ""
            },
            "core": {
                "config.py": "",
                "logger.py": ""
            },
            "main.py": "",
            "requirements.txt": "",
            ".env": ""
        },
        "tests": {
            "test_llm_parser.py": "",
            "test_embedding_search.py": "",
            "test_clause_matcher.py": "",
            "test_logic_engine.py": "",
            "test_api_endpoints.py": ""
        },
        "data": {
            "uploads": {},
            "processed": {},
            "pinecone_index": {}
        },
        "notebooks": {
            "test_query_parsing.ipynb": "",
            "test_semantic_search.ipynb": ""
        },
        ".env": "",
        "README.md": "",
        "docker-compose.yml": "",
        "setup.sh": ""
    }
}

def create_structure(base_path, tree):
    for name, content in tree.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            os.makedirs(base_path, exist_ok=True)
            with open(path, "w") as f:
                f.write(content)

if __name__ == "__main__":
    create_structure(".", structure)
    print("✅ Project structure created successfully!")
