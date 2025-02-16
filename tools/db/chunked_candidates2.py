import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Tuple, Union
import re

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
import plotly.express as px
from numpy.linalg import norm

###############################################################################
# 1) Basic text utilities / naive parser
###############################################################################

def cosine_similarity(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

def naive_query_parser(user_input: str) -> Tuple[str, Dict[str, str]]:
    """
    A simplistic parser that tries to detect certain keywords or patterns
    to convert them into metadata filters, leaving the rest for semantic search.
    """
    text = user_input.lower()
    filters = {}

    # Example: detect if user mentions "neurips" or "publication year=2022" etc.
    # Modify or remove if not needed
    if "neurips" in text:
        filters["publication"] = "NeurIPS"
        text = text.replace("neurips", "")

    # Remove extra spaces
    semantic_query = " ".join(text.split())

    return semantic_query, filters


###############################################################################
# 2) Chunk-level ingestion (adapted to the new JSON structure)
###############################################################################

class ChunkedCandidateDB:
    """
    Stores each candidate's data in chunks (personal info, education, experience, 
    publications, projects, awards, etc.) in Chroma with relevant metadata.
    We skip 'skills' and 'interests' to reduce noise.
    """
    def __init__(self, persist_directory: str = "./chroma_db"):
        # Initialize Chroma
        self.client = chromadb.Client()
        # Single collection for all chunked data
        self.collection = self.client.get_or_create_collection(name="candidate_chunks")
        
        # We'll use Sentence Transformers for embeddings
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def load_json_file(self, json_path: str) -> List[Dict[str, Any]]:
        """Loads a JSON file containing multiple candidate profiles."""
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Could not find {json_path}")
        with open(json_path, "r") as f:
            data = json.load(f)
        return data  # Should be a list of candidate dicts

    def ingest_candidates(self, candidates_data: List[Dict[str, Any]]):
        """
        For each candidate dictionary in candidates_data:
          - chunk their data
          - embed each chunk
          - upsert into Chroma with relevant metadata
        """
        for candidate_json in candidates_data:
            self._index_candidate(candidate_json)

    def _index_candidate(self, candidate_json: Dict[str, Any]) -> None:
        """
        Breaks a single candidate's data into relevant chunks and
        stores them in Chroma with metadata for advanced querying.
        We skip 'skills' and 'interests'.
        """

        ########################################################################
        # 1) Determine Candidate ID and Name
        ########################################################################

        # Candidate ID
        candidate_id = candidate_json.get("id", str(datetime.now().timestamp()))

        # Candidate Name:
        #   - Prefer top-level "name" if it exists
        #   - Else, look in personal_info
        #   - Else "Unknown"
        top_level_name = candidate_json.get("name", None)
        personal_info = candidate_json.get("personal_info", {})
        pi_name = personal_info.get("name", None)
        candidate_name = top_level_name if top_level_name else (pi_name if pi_name else "Unknown")

        now_ts = str(datetime.now().timestamp())

        ########################################################################
        # 2) Personal Info Chunk
        ########################################################################
        # This chunk can store phone/email if available, or location, etc.
        pi_phone = personal_info.get("phone", "") or personal_info.get("phone_number", "")
        pi_email = personal_info.get("email", "")
        pi_university = personal_info.get("university", "")
        pi_str = (
            f"Candidate Name: {candidate_name}\n"
            f"Email: {pi_email}\n"
            f"Phone: {pi_phone}\n"
            f"Location: {personal_info.get('location','')}\n"
        )

        # Also check if this candidate has top-level "university" or "name" fields
        # that are not in personal_info
        top_univ = candidate_json.get("university", "")
        if top_univ and top_univ != pi_university:
            pi_str += f"University: {top_univ}\n"

        # If there's an array "education" inside personal_info, handle it here as well
        # We do that in a separate step (education). But for small personal info text, let's embed it anyway.
        if pi_str.strip():
            pi_metadata = {
                "candidate_id": candidate_id,
                "candidate_name": candidate_name,
                "section": "personal_info"
            }
            self._upsert_chunk(
                doc_id=f"{candidate_id}-personal_info-{now_ts}",
                doc_text=pi_str,
                metadata=pi_metadata
            )

        ########################################################################
        # 3) Education
        ########################################################################
        # Some candidates store "education" at top level, others inside "personal_info".
        # Let's unify by collecting them into one list:
        edu_entries: List[Dict[str, Any]] = []

        # 3.1) If top-level "education" is a list, add them
        top_edu = candidate_json.get("education", [])
        if isinstance(top_edu, dict):
            # occasionally it might be a dict
            top_edu = [top_edu]
        if isinstance(top_edu, list):
            edu_entries.extend(top_edu)

        # 3.2) If personal_info["education"] is also present, add them
        pi_edu = personal_info.get("education", [])
        if isinstance(pi_edu, dict):
            pi_edu = [pi_edu]
        if isinstance(pi_edu, list):
            edu_entries.extend(pi_edu)

        # Build a chunk for each education entry
        for i, edu in enumerate(edu_entries):
            edu_text = (
                f"Degree: {edu.get('degree','')}\n"
                f"Institution: {edu.get('institution','')}\n"
                f"Field: {edu.get('field','')}\n"
                f"Year: {edu.get('year','')}\n"
            )
            if edu_text.strip():
                edu_metadata = {
                    "candidate_id": candidate_id,
                    "candidate_name": candidate_name,
                    "section": "education",
                    "institution": edu.get("institution",""),
                }
                self._upsert_chunk(
                    doc_id=f"{candidate_id}-education-{i}-{now_ts}",
                    doc_text=edu_text,
                    metadata=edu_metadata
                )

        ########################################################################
        # 4) Experience
        ########################################################################
        experiences = candidate_json.get("experience", [])
        for i, exp in enumerate(experiences):
            exp_text = (
                f"Title/Position: {exp.get('title') or exp.get('position','')}\n"
                f"Company/Organization: {exp.get('company') or exp.get('organization','')}\n"
                f"Location: {exp.get('location','')}\n"
                f"Description: {exp.get('description','')}\n"
            )
            if exp_text.strip():
                exp_metadata = {
                    "candidate_id": candidate_id,
                    "candidate_name": candidate_name,
                    "section": "experience"
                }
                self._upsert_chunk(
                    doc_id=f"{candidate_id}-experience-{i}-{now_ts}",
                    doc_text=exp_text,
                    metadata=exp_metadata
                )

        ########################################################################
        # 5) Projects
        ########################################################################
        projects = candidate_json.get("projects", [])
        for i, proj in enumerate(projects):
            # Could have "description", "summary", "role", "technologies"
            proj_text = (
                f"Project: {proj.get('name','')}\n"
                f"Description: {proj.get('description','')}\n"
                f"Summary: {proj.get('summary','')}\n"
                f"Role: {proj.get('role','')}\n"
                # "technologies": we can store or skip
            )
            if proj_text.strip():
                proj_metadata = {
                    "candidate_id": candidate_id,
                    "candidate_name": candidate_name,
                    "section": "project"
                }
                self._upsert_chunk(
                    doc_id=f"{candidate_id}-project-{i}-{now_ts}",
                    doc_text=proj_text,
                    metadata=proj_metadata
                )

        ########################################################################
        # 6) Publications (or "publications"/"research")
        ########################################################################
        # Some candidates have top-level "publications", others have "research".
        # We'll handle "publications" first:
        publications = candidate_json.get("publications", [])
        for i, pub in enumerate(publications):
            pub_text = (
                f"Title: {pub.get('title','')}\n"
                f"Authors: {pub.get('authors','')}\n"
                f"Journal/Publisher: {pub.get('journal') or pub.get('publisher','')}\n"
                f"Year: {pub.get('year','')}\n"
                f"Summary: {pub.get('summary','')}\n"
                f"Snippet: {pub.get('snippet','')}\n"
            )
            if pub_text.strip():
                pub_metadata = {
                    "candidate_id": candidate_id,
                    "candidate_name": candidate_name,
                    "section": "publication",
                }
                self._upsert_chunk(
                    doc_id=f"{candidate_id}-publication-{i}-{now_ts}",
                    doc_text=pub_text,
                    metadata=pub_metadata
                )

        # 6.2) Additional "research" field (like "Jack Fan" has "research" list)
        research_entries = candidate_json.get("research", [])
        for i, r in enumerate(research_entries):
            r_text = (
                f"Research Title: {r.get('title','')}\n"
                f"Summary: {r.get('summary','')}\n"
                f"Snippet: {r.get('snippet','')}\n"
                f"Description: {r.get('description','')}\n"  # if any
            )
            if r_text.strip():
                r_metadata = {
                    "candidate_id": candidate_id,
                    "candidate_name": candidate_name,
                    "section": "research"
                }
                self._upsert_chunk(
                    doc_id=f"{candidate_id}-research-{i}-{now_ts}",
                    doc_text=r_text,
                    metadata=r_metadata
                )

        ########################################################################
        # 7) Awards
        ########################################################################
        # Some are arrays of dict (with name, year, desc), others are arrays of strings
        awards = candidate_json.get("awards", [])
        if isinstance(awards, list) and len(awards) > 0:
            # If each item is a dict, store them individually
            # If item is string, store them too
            for i, award_item in enumerate(awards):
                if isinstance(award_item, dict):
                    a_text = (
                        f"Award Name: {award_item.get('name','')}\n"
                        f"Year: {award_item.get('year','')}\n"
                        f"Description: {award_item.get('description','')}\n"
                    )
                else:
                    # just a string
                    a_text = str(award_item)
                if a_text.strip():
                    a_metadata = {
                        "candidate_id": candidate_id,
                        "candidate_name": candidate_name,
                        "section": "awards"
                    }
                    self._upsert_chunk(
                        doc_id=f"{candidate_id}-award-{i}-{now_ts}",
                        doc_text=a_text,
                        metadata=a_metadata
                    )

        ########################################################################
        # 8) Athletics or "athletic_career" or "high_school" etc. 
        #    If needed, parse further.
        ########################################################################
        if "athletic_career" in candidate_json:
            ath = candidate_json["athletic_career"]
            ath_text = (
                f"Sport: {ath.get('sport','')}\n"
                f"Position: {ath.get('position','')}\n"
                f"Team: {ath.get('team','')}\n"
                "Achievements: " + " | ".join(ath.get('achievements',[]))
            ).strip()
            if ath_text:
                ath_metadata = {
                    "candidate_id": candidate_id,
                    "candidate_name": candidate_name,
                    "section": "athletics"
                }
                self._upsert_chunk(
                    doc_id=f"{candidate_id}-athletics-{now_ts}",
                    doc_text=ath_text,
                    metadata=ath_metadata
                )

        if "high_school" in candidate_json:
            hs = candidate_json["high_school"]
            hs_text = (
                f"High School Name: {hs.get('name','')}\n"
                f"Location: {hs.get('location','')}\n"
                f"Graduation Year: {hs.get('graduation_year','')}\n"
                "Achievements: " + " | ".join(hs.get('achievements',[]))
            ).strip()
            if hs_text:
                hs_metadata = {
                    "candidate_id": candidate_id,
                    "candidate_name": candidate_name,
                    "section": "high_school"
                }
                self._upsert_chunk(
                    doc_id=f"{candidate_id}-highschool-{now_ts}",
                    doc_text=hs_text,
                    metadata=hs_metadata
                )

        # 8.1) leadership, extracurriculars, etc.
        if "leadership" in candidate_json and isinstance(candidate_json["leadership"], dict):
            roles = candidate_json["leadership"].get("roles", [])
            for i, r in enumerate(roles):
                lead_text = (
                    f"Title: {r.get('title','')}\n"
                    f"Organization: {r.get('organization','')}\n"
                    f"Description: {r.get('description','')}\n"
                )
                if lead_text.strip():
                    lead_metadata = {
                        "candidate_id": candidate_id,
                        "candidate_name": candidate_name,
                        "section": "leadership"
                    }
                    self._upsert_chunk(
                        doc_id=f"{candidate_id}-leadership-{i}-{now_ts}",
                        doc_text=lead_text,
                        metadata=lead_metadata
                    )

        extras = candidate_json.get("extracurricular_activities", [])
        if isinstance(extras, list) and extras:
            combined_list = []
            for e in extras:
                if isinstance(e, dict):
                    # for ex. { "organization":"xxx", "role":"xxx" }
                    combined_list.append(
                        f"Organization: {e.get('organization','')} | "
                        f"Role: {e.get('role','')} | "
                        f"Description: {e.get('description','')}"
                    )
                else:
                    combined_list.append(str(e))
            if combined_list:
                extras_text = " || ".join(combined_list)
                extras_metadata = {
                    "candidate_id": candidate_id,
                    "candidate_name": candidate_name,
                    "section": "extracurriculars"
                }
                self._upsert_chunk(
                    doc_id=f"{candidate_id}-extracurriculars-{now_ts}",
                    doc_text=extras_text,
                    metadata=extras_metadata
                )

        if "notable_experiences" in candidate_json:
            nexp = candidate_json["notable_experiences"]
            if isinstance(nexp, list) and nexp:
                text = " | ".join(map(str, nexp))
                if text.strip():
                    nexp_metadata = {
                        "candidate_id": candidate_id,
                        "candidate_name": candidate_name,
                        "section": "notable_experiences"
                    }
                    self._upsert_chunk(
                        doc_id=f"{candidate_id}-notableexp-{now_ts}",
                        doc_text=text,
                        metadata=nexp_metadata
                    )
        ########################################################################
        # SKIPPING "skills" and "interests" on purpose, as requested
        ########################################################################

    def _upsert_chunk(self, doc_id: str, doc_text: str, metadata: Dict[str, Any]) -> None:
        """
        Helper: embed the chunk text and upsert to Chroma collection.
        """
        embedding = self.model.encode(doc_text)
        self.collection.upsert(
            ids=[doc_id],
            documents=[doc_text],
            embeddings=[embedding],
            metadatas=[metadata]
        )

    def get_all_chunks(self):
        """Retrieve all docs (chunks) from the collection, including embeddings."""
        return self.collection.get(include=["documents", "metadatas", "embeddings"])

    def query_chunks(self, user_input: str, n_results: int = 20):
        """
        A single user input is parsed to:
          - Extract relevant filters (metadata)
          - Remaining text is used as the semantic query
        Then we do a chunk-level search, but group results by candidate,
        returning a list of candidates with relevant snippets.
        """
        semantic_query, filters = naive_query_parser(user_input)

        # If a "yearRange" or something else is present, handle or remove:
        if "yearRange" in filters:
            filters.pop("yearRange")

        # Build where clause
        if len(filters) == 0:
            where_clause = None
        elif len(filters) == 1:
            (k, v) = list(filters.items())[0]
            where_clause = {k: v}
        else:
            where_clause = {"$and": [{k: v} for k, v in filters.items()]}

        query_params = {
            "query_texts": [semantic_query],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"]
        }
        if where_clause is not None:
            query_params["where"] = where_clause

        results = self.collection.query(**query_params)
        if not results or not results.get("documents"):
            return []

        chunk_docs = results["documents"][0]
        chunk_metas = results["metadatas"][0]
        chunk_dists = results["distances"][0]

        # Group by candidate_id
        candidate_hits = {}
        for doc, meta, dist in zip(chunk_docs, chunk_metas, chunk_dists):
            candidate_id = meta.get("candidate_id", "Unknown")
            candidate_name = meta.get("candidate_name", "Unknown")
            similarity = 1 - dist

            snippet_len = 300
            snippet_text = doc if len(doc) <= snippet_len else (doc[:snippet_len] + "...")
            chunk_info = {
                "snippet": snippet_text,
                "section": meta.get("section", ""),
                "similarity_score": similarity,
            }
            if candidate_id not in candidate_hits:
                candidate_hits[candidate_id] = {"candidate_name": candidate_name, "chunks": []}
            candidate_hits[candidate_id]["chunks"].append(chunk_info)

        candidate_list = []
        for c_id, data in candidate_hits.items():
            best_score = max(ch["similarity_score"] for ch in data["chunks"])
            candidate_list.append({
                "candidate_id": c_id,
                "candidate_name": data["candidate_name"],
                "score": best_score,
                "chunks": data["chunks"]
            })
        candidate_list.sort(key=lambda x: x["score"], reverse=True)
        return candidate_list


###############################################################################
# 3) Aggregator & Plotting (Optional)
###############################################################################

def aggregate_candidate_scores(db: ChunkedCandidateDB):
    """
    Retrieve all chunk embeddings from Chroma and compute each chunk's
    'research' and 'industry' similarity. Then for each candidate, pick the
    'max chunk' in each metric. Return a DataFrame with:
      candidate_id, candidate_name, research_score, industry_score
    """
    all_data = db.get_all_chunks()
    chunk_embeddings = all_data["embeddings"]
    chunk_metadata = all_data["metadatas"]

    research_prompt = "Candidate with significant academic research or publications."
    industry_prompt = "Candidate with extensive industry experience or practical engineering work."
    model = db.model
    research_emb = model.encode(research_prompt)
    industry_emb = model.encode(industry_prompt)

    scores_by_candidate = {}
    for emb, meta in zip(chunk_embeddings, chunk_metadata):
        c_id = meta.get("candidate_id", "Unknown")
        c_name = meta.get("candidate_name", "Unknown")
        r_score = cosine_similarity(emb, research_emb)
        i_score = cosine_similarity(emb, industry_emb)
        if c_id not in scores_by_candidate:
            scores_by_candidate[c_id] = {
                "candidate_name": c_name,
                "max_research_score": -999,
                "max_industry_score": -999
            }
        if r_score > scores_by_candidate[c_id]["max_research_score"]:
            scores_by_candidate[c_id]["max_research_score"] = r_score
        if i_score > scores_by_candidate[c_id]["max_industry_score"]:
            scores_by_candidate[c_id]["max_industry_score"] = i_score

    rows = []
    for c_id, info in scores_by_candidate.items():
        rows.append({
            "candidate_id": c_id,
            "candidate_name": info["candidate_name"],
            "research_score": info["max_research_score"],
            "industry_score": info["max_industry_score"]
        })
    df = pd.DataFrame(rows)
    return df

def plot_research_vs_industry(df: pd.DataFrame):
    fig = px.scatter(
        df,
        x="research_score",
        y="industry_score",
        hover_data=["candidate_name"],
        text="candidate_name",
        title="Research vs. Industry (Best Chunk Per Candidate)"
    )
    fig.update_traces(textposition='top center')
    fig.show()


###############################################################################
# 4) Main Script Entry Point
###############################################################################

if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     print("Usage: python detailed_chunked_candidates.py <path_to_candidates.json>")
    #     sys.exit(1)

    # json_file_path = sys.argv[1]
    db = ChunkedCandidateDB(persist_directory="./chroma_db")

    # 1) Load and ingest candidate data
    data = db.load_json_file('candidates_db.json')
    db.ingest_candidates(data)

    # 2) Optional aggregator + plot
    df = aggregate_candidate_scores(db)
    plot_research_vs_industry(df)

    # 3) Interactive Query Loop
    print("\n--- Single Input Query Demo ---\n(Type 'q' to quit)\n")
    while True:
        user_input = input("Enter your ideal candidate criteria: ")
        if user_input.lower().strip() in ["q", "quit", "exit"]:
            break

        candidate_matches = db.query_chunks(user_input)
        if not candidate_matches:
            print("No matches found.\n")
            continue

        for i, candidate in enumerate(candidate_matches, start=1):
            print(f"{i}. Candidate: {candidate['candidate_name']} (score={candidate['score']:.3f})")
            sorted_chunks = sorted(candidate["chunks"], key=lambda c: c["similarity_score"], reverse=True)
            for j, chunk_info in enumerate(sorted_chunks[:2], start=1):
                print(f"   Chunk {j}: section={chunk_info['section']}, score={chunk_info['similarity_score']:.3f}")
                print(f"       {chunk_info['snippet']}")
            print()
        print("---------------------------------------------------")
