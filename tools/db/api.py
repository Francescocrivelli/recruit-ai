from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
import json
import os
from sentence_transformers import SentenceTransformer
from chunked_candidates_final import ChunkedCandidateDB
import traceback

app = FastAPI()

# Configure CORS - allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = ChunkedCandidateDB()

# Load candidates on startup
try:
    print("Loading candidates data...")
    with open('candidates.json', 'r') as f:
        data = json.load(f)
        candidates = data if isinstance(data, list) else data.get('profiles', [])
    
    print(f"Found {len(candidates)} candidates")
    for candidate in candidates:
        db._index_candidate(candidate)
    print("Successfully loaded all candidates")
except Exception as e:
    print(f"Error loading candidates: {str(e)}")
    raise

class SearchQuery(BaseModel):
    query: str
    n_results: int = 400

@app.post("/api/semantic-search")
async def semantic_search(search_query: SearchQuery):
    try:
        print(f"\n=== New Search Request ===")
        print(f"Query: '{search_query.query}'")
        
        # Clean and normalize the query
        query = search_query.query.strip()
        
        # Use the same search function as terminal
        results = db.multi_subquery_search(
            query,
            search_query.n_results
        )
        
        formatted_results = []
        for result in results:
            sections = {}
            relevant_chunks = []
            
            # Format chunks exactly like terminal output
            for subq_idx, (score, chunk_info) in enumerate(result['chosen_subchunks']):
                section = chunk_info['section'].lower()
                if section not in sections:
                    sections[section] = []
                sections[section].append(chunk_info['snippet'])
                
                # Format chunk like terminal output
                chunk_text = (
                    f"(score={score:.3f}, section={chunk_info['section']}):\n"
                    f"{chunk_info['snippet']}"
                )
                
                relevant_chunks.append({
                    'score': score,
                    'content': chunk_info['snippet'],
                    'section': section,
                    'formatted_text': chunk_text,
                    'subquery_index': subq_idx + 1
                })

            formatted_result = {
                'candidate_id': result['candidate_id'],
                'candidate_name': result['candidate_name'],
                'score': abs(float(result['score'])),
                'sections': {
                    'education': sections.get('education', []),
                    'experience': sections.get('experience', []),
                    'publications': sections.get('publications', []),
                    'projects': sections.get('projects', []),
                    'awards': sections.get('awards', [])
                },
                'relevantChunks': relevant_chunks
            }
            formatted_results.append(formatted_result)
        
        # Sort by score in descending order
        formatted_results.sort(key=lambda x: x['score'], reverse=True)
        
        # Debug output
        print(f"\nFound {len(formatted_results)} matching candidates")
        for i, result in enumerate(formatted_results, 1):
            print(f"{i}. {result['candidate_name']} (score: {result['score']:.3f})")
            for chunk in result['relevantChunks']:
                print(f"   {chunk['formatted_text']}\n")
        
        return {"results": formatted_results}
    except Exception as e:
        print(f"Search error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 