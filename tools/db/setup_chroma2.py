# tools/db/setup_chroma.py

import json
from datetime import datetime
from typing import List
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

class RecruitingDB:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize a Chroma DB client with persistence so data is retained across sessions.
        """
        self.client = chromadb.Client()
        
        # We'll keep one collection named 'candidates'
        self.candidates = self.client.get_or_create_collection(name="candidates")
        
        # You may choose to store different "views" in separate collections,
        # but let's use one single collection for simplicity.

        # Sentence Transformers model (you can swap with any embedding model)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def build_text_for_embedding(self, candidate_json: dict, embedding_type: str) -> str:
        """
        Given the candidate JSON and a chosen embedding_type, build the text
        that will be used to generate embeddings.

        You can define any logic here to pick/merge certain parts of the JSON
        depending on 'embedding_type'. For example:
         - 'all_info' includes everything
         - 'experience_only' includes only job experience
         - 'education_experience' might merge education and experience
         - etc.
        """
        # Extract common fields
        name = candidate_json.get("name", "")
        current_position = candidate_json.get("currentPosition", "")
        education = candidate_json.get("education", [])
        experience = candidate_json.get("experience", [])
        projects = candidate_json.get("projects", [])
        awards = candidate_json.get("awards", [])
        board_memberships = candidate_json.get("boardMemberships", [])
        achievements = candidate_json.get("achievements", [])

        # Build text selectively based on the embedding type
        if embedding_type == "all_info":
            # Combine all possible fields
            text_parts = [
                f"Name: {name}",
                f"Current Position: {current_position}",
                "Education: " + " | ".join(
                    f"{ed.get('degree', '')} at {ed.get('institution', '')} ({ed.get('year', '')})"
                    for ed in education
                ),
                "Experience: " + " | ".join(
                    f"{exp.get('title', '')} at {exp.get('company', '')} from {exp.get('startDate', '')} to {exp.get('endDate', '')}"
                    for exp in experience
                ),
                "Projects: " + ", ".join(projects),
                "Awards: " + " | ".join(
                    f"{awd.get('name', '')} ({awd.get('year', '')})"
                    for awd in awards
                ),
                "Board Memberships: " + ", ".join(board_memberships),
                "Achievements: " + ", ".join(achievements),
            ]
            return "\n".join(text_parts)
        
        elif embedding_type == "experience_only":
            text_parts = [
                f"Name: {name}",
                "Experience: " + " | ".join(
                    f"{exp.get('title', '')} at {exp.get('company', '')} from {exp.get('startDate', '')} to {exp.get('endDate', '')}"
                    for exp in experience
                )
            ]
            return "\n".join(text_parts)

        elif embedding_type == "education_experience":
            text_parts = [
                f"Name: {name}",
                "Education: " + " | ".join(
                    f"{ed.get('degree', '')} at {ed.get('institution', '')} ({ed.get('year', '')})"
                    for ed in education
                ),
                "Experience: " + " | ".join(
                    f"{exp.get('title', '')} at {exp.get('company', '')} from {exp.get('startDate', '')} to {exp.get('endDate', '')}"
                    for exp in experience
                )
            ]
            return "\n".join(text_parts)

        # Fallback if an unknown embedding_type is passed in
        return json.dumps(candidate_json)

    def upsert_candidate_embeddings(
        self,
        candidate_json: dict,
        embedding_types: List[str] = ["all_info"]
    ) -> List[str]:
        """
        Generates multiple embeddings for the candidate, each corresponding to
        a different 'view' of the data (as defined in build_text_for_embedding).
        Then upserts each into the 'candidates' collection with unique IDs.

        Returns a list of doc IDs that were upserted for reference.
        """
        doc_ids = []
        now_ts = str(datetime.now().timestamp())
        candidate_name = candidate_json.get("name", "Unknown")

        for embed_type in embedding_types:
            # Build the text relevant to this embedding type
            text_for_embedding = self.build_text_for_embedding(candidate_json, embed_type)
            # Generate the embedding
            embedding = self.model.encode(text_for_embedding)

            # We'll create a doc ID that includes candidate name and embed_type
            # plus a timestamp, to keep them unique
            doc_id = f"{candidate_name}-{embed_type}-{now_ts}"
            doc_ids.append(doc_id)

            # Upsert into Chroma
            self.candidates.upsert(
                ids=[doc_id],
                documents=[text_for_embedding],  # or store the raw JSON if you prefer
                embeddings=[embedding],
                metadatas=[{
                    "name": candidate_name,
                    "embedding_type": embed_type,
                    "timestamp": now_ts
                }]
            )
        return doc_ids
    
    def query_candidates(self, query_text: str, n_results: int = 5):
        """
        Query the candidates collection using Chroma's built-in text embedding.
        (If you want manual embedding, you can do query_embeddings=... instead.)
        """
        results = self.candidates.query(
            query_texts=[query_text],
            n_results=n_results,
            include=["documents", "metadatas"]  # so we can see the text and metadata
        )
        return results


