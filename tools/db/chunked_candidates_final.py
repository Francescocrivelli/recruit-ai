import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Tuple
import re

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
import plotly.express as px
from numpy.linalg import norm
from sklearn.feature_extraction.text import TfidfVectorizer

###############################################################################
# 1) Basic text utilities
###############################################################################

def cosine_similarity(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

def naive_query_parser(user_input: str) -> Tuple[str, Dict[str, str]]:
    """
    Very naive parser: remove certain words for semantic weighting,
    set 'section=publication' if user says 'publication/publications', etc.
    """
    text = user_input.lower()
    filters = {}

    # If user mentions publications
    if "publications" in text or "publication" in text or 'published' in text:
        filters["section"] = "publication"
        text = text.replace("publications", "")
        text = text.replace("publication", "")

    # If user mentions popular conferences
    if "neurips" in text:
        filters["publication"] = "Neurips"
        text = text.replace("neurips", "")
    if "icml" in text:
        filters["publication"] = "ICML"
        text = text.replace("icml", "")
    if "iclr" in text:
        filters["publication"] = "ICLR"
        text = text.replace("iclr", "")

    semantic_query = " ".join(text.split())
    return semantic_query, filters

def parse_subquery_for_filters(sub_text: str) -> Tuple[str, Dict[str, Any]]:
    """
    Further refine each subquery. 
    - If subquery includes 'industry', add filter section='experience'.
    - If subquery includes 'nature', add filter journal='Nature'.
    - If subquery includes 'student', add filter section='education'.
    - etc.
    """
    sub_text = sub_text.lower().strip()
    sub_filters = {}

    # For example, look for 'industry'
    if "experience" in sub_text or 'industry' in sub_text:
        sub_filters["section"] = "experience"
        # remove the word 'industry' so it doesn't overly bias semantic part
        sub_text = sub_text.replace("industry", "")

    # If user specifically says "nature" => might expect 'journal=Nature'
    if "nature" in sub_text:
        sub_filters["journal"] = "Nature"
        sub_text = sub_text.replace("nature", "")

    # If subquery includes 'student', it's often about education
    # We can guess they want 'section=education'
    if "student" in sub_text:
        sub_filters["section"] = "education"
        sub_text = sub_text.replace("student", "")
    
    # If user mentions publications
    if "publications" in sub_text or "publication" in sub_text or 'published' in sub_text:
        sub_filters["section"] = "publication"
        sub_text = sub_text.replace("publications", "")
        sub_text = sub_text.replace("publication", "")

    # If user mentions popular conferences
    if "neurips" in sub_text:
        sub_filters["publication"] = "Neurips"
        sub_text = sub_text.replace("neurips", "")
    if "icml" in sub_text:
        sub_filters["publication"] = "ICML"
        sub_text = sub_text.replace("icml", "")
    if "iclr" in sub_text:
        sub_filters["publication"] = "ICLR"
        sub_text = sub_text.replace("iclr", "")

    # You can add more triggers: e.g., "biomedical" => do something 
    # For now, let's just rely on semantic text if "biomedical" is not structured.

    # Combine with naive query parser for existing logic
    semantic_part, old_filters = naive_query_parser(sub_text)

    # Merge old_filters into sub_filters
    # (old_filters might set section=publication if 'publication' is in sub-text)
    for k, v in old_filters.items():
        sub_filters[k] = v

    return semantic_part.strip(), sub_filters


###############################################################################
# 2) Chunk-level ingestion
###############################################################################

class ChunkedCandidateDB:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(name="candidate_chunks")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def load_json_file(self, json_path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Could not find {json_path}")
        with open(json_path, "r") as f:
            data = json.load(f)
        if isinstance(data, dict) and "profiles" in data:
            return data["profiles"]
        elif isinstance(data, list):
            return data
        else:
            raise ValueError("Unexpected JSON structure.")

    def ingest_candidates(self, candidates_data: List[Any]):
        valid_count = 0
        for candidate in candidates_data:
            if isinstance(candidate, str):
                try:
                    candidate = json.loads(candidate)
                except Exception as e:
                    print(f"Error parsing candidate string: {candidate}\n{e}")
                    continue
            if not isinstance(candidate, dict):
                print(f"Skipping non-dict candidate: {candidate}")
                continue
            self._index_candidate(candidate)
            valid_count += 1
        print(f"Ingested {valid_count} candidate profiles.")

    def _index_candidate(self, candidate_json: Dict[str, Any]) -> None:
        candidate_id = candidate_json.get("id", str(datetime.now().timestamp()))
        top_level_name = candidate_json.get("name")
        personal_info = candidate_json.get("personal_info", {})
        pi_name = personal_info.get("name")
        candidate_name = top_level_name if top_level_name else (pi_name if pi_name else "Unknown")
        now_ts = str(datetime.now().timestamp())

        # 1) Personal Info
        pi_phone = personal_info.get("phone", "") or personal_info.get("phone_number", "")
        pi_email = personal_info.get("email", "")
        pi_location = personal_info.get("location", "")
        pi_university = personal_info.get("university", "")
        pi_str = (
            f"Candidate Name: {candidate_name}\n"
            f"Email: {pi_email}\n"
            f"Phone: {pi_phone}\n"
            f"Location: {pi_location}\n"
            f"University: {pi_university}\n"
        )
        if pi_str.strip():
            pi_metadata = {
                "candidate_id": candidate_id,
                "candidate_name": candidate_name,
                "section": "personal_info"
            }
            self._upsert_chunk(f"{candidate_id}-personal_info-{now_ts}", pi_str, pi_metadata)

        # 2) Education
        edu_entries: List[Dict[str, Any]] = []
        top_edu = candidate_json.get("education", [])
        if isinstance(top_edu, dict):
            top_edu = [top_edu]
        if isinstance(top_edu, list):
            edu_entries.extend(top_edu)
        pi_edu = personal_info.get("education", [])
        if isinstance(pi_edu, dict):
            pi_edu = [pi_edu]
        if isinstance(pi_edu, list):
            edu_entries.extend(pi_edu)
        for i, edu in enumerate(edu_entries):
            edu_text = (
                f"Degree: {edu.get('degree','')}\n"
                f"Institution: {edu.get('institution','')}\n"
                f"Field: {edu.get('field','')}\n"
                f"Year: {edu.get('year','')}\n"
                f"Cross-registration: {edu.get('cross_registration','')}\n"
            )
            if edu_text.strip():
                edu_metadata = {
                    "candidate_id": candidate_id,
                    "candidate_name": candidate_name,
                    "section": "education"
                }
                self._upsert_chunk(f"{candidate_id}-education-{i}-{now_ts}", edu_text, edu_metadata)

        # 3) Experience
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
                self._upsert_chunk(f"{candidate_id}-experience-{i}-{now_ts}", exp_text, exp_metadata)

        # 4) Projects
        projects = candidate_json.get("projects", [])
        for i, proj in enumerate(projects):
            proj_text = (
                f"Project: {proj.get('name','')}\n"
                f"Description: {proj.get('description','')}\n"
                f"Summary: {proj.get('summary','')}\n"
                f"Role: {proj.get('role','')}\n"
            )
            if proj_text.strip():
                proj_metadata = {
                    "candidate_id": candidate_id,
                    "candidate_name": candidate_name,
                    "section": "project"
                }
                self._upsert_chunk(f"{candidate_id}-project-{i}-{now_ts}", proj_text, proj_metadata)

        # 5) Publications
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
            # skip if not meaningful
            if not pub.get('summary') or not pub.get('snippet') or (not pub.get('publisher') and not pub.get('journal')):
                continue
            if pub_text.strip():
                pub_metadata = {
                    "candidate_id": candidate_id,
                    "candidate_name": candidate_name,
                    "section": "publication"
                }
                self._upsert_chunk(f"{candidate_id}-publication-{i}-{now_ts}", pub_text, pub_metadata)

        # 6) Research
        research_entries = candidate_json.get("research", [])
        for i, r in enumerate(research_entries):
            if isinstance(r, dict):
                r_text = (
                    f"Research Title: {r.get('title','')}\n"
                    f"Summary: {r.get('summary','')}\n"
                    f"Snippet: {r.get('snippet','')}\n"
                    f"Description: {r.get('description','')}\n"
                )
            else:
                r_text = str(r)
            if r_text.strip():
                r_metadata = {
                    "candidate_id": candidate_id,
                    "candidate_name": candidate_name,
                    "section": "research"
                }
                self._upsert_chunk(f"{candidate_id}-research-{i}-{now_ts}", r_text, r_metadata)

        # 7) Awards
        awards = candidate_json.get("awards", [])
        if isinstance(awards, list) and awards:
            for i, award_item in enumerate(awards):
                if isinstance(award_item, dict):
                    a_text = (
                        f"Award Name: {award_item.get('name','')}\n"
                        f"Year: {award_item.get('year','')}\n"
                        f"Description: {award_item.get('description','')}\n"
                    )
                else:
                    a_text = str(award_item)
                if a_text.strip():
                    a_metadata = {
                        "candidate_id": candidate_id,
                        "candidate_name": candidate_name,
                        "section": "awards"
                    }
                    self._upsert_chunk(f"{candidate_id}-award-{i}-{now_ts}", a_text, a_metadata)

        # 8) Athletics, High School, etc.
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
                self._upsert_chunk(f"{candidate_id}-athletics-{now_ts}", ath_text, ath_metadata)

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
                self._upsert_chunk(f"{candidate_id}-highschool-{now_ts}", hs_text, hs_metadata)

        # 9) Leadership/Extracurricular
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
                    self._upsert_chunk(f"{candidate_id}-leadership-{i}-{now_ts}", lead_text, lead_metadata)

        extras = candidate_json.get("extracurricular_activities", [])
        if isinstance(extras, list) and extras:
            combined_list = []
            for e in extras:
                if isinstance(e, dict):
                    combined_list.append(
                        f"Organization: {e.get('organization','')} | Role: {e.get('role','')} | Description: {e.get('description','')}"
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
                self._upsert_chunk(f"{candidate_id}-extracurriculars-{now_ts}", extras_text, extras_metadata)

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
                    self._upsert_chunk(f"{candidate_id}-notableexp-{now_ts}", text, nexp_metadata)

    def extract_query_keywords(self, query_text: str, top_n: int = 5) -> List[str]:
        """
        Builds a TF-IDF vectorizer over all candidate chunks and extracts the top_n keywords
        from the query text based on their TF-IDF weights.
        """
        # Get all chunk documents as a list of strings.
        all_chunks = self.get_all_chunks().get("documents", [])
        if not all_chunks or not isinstance(all_chunks, list):
            # Fallback: just split the query text.
            return query_text.lower().split()
        
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(all_chunks)
        feature_names = vectorizer.get_feature_names_out()
        # Transform the query text using the same vectorizer.
        query_tfidf = vectorizer.transform([query_text])
        scores = query_tfidf.toarray()[0]
        # Get indices of top scoring words
        top_indices = scores.argsort()[::-1]
        keywords = []
        for idx in top_indices:
            if scores[idx] > 0:
                keywords.append(feature_names[idx])
            if len(keywords) >= top_n:
                break
        return keywords

    def _upsert_chunk(self, doc_id: str, doc_text: str, metadata: Dict[str, Any]) -> None:
        embedding = self.model.encode(doc_text)
        self.collection.upsert(
            ids=[doc_id],
            documents=[doc_text],
            embeddings=[embedding],
            metadatas=[metadata]
        )

    def get_all_chunks(self):
        return self.collection.get(include=["documents", "metadatas", "embeddings"])

    def query_chunks(self, semantic_query: str, filters: Dict[str, Any] = None, n_results: int = 200):
        """
        Takes a semantic_query (some text) and optional filters (e.g. {"section": "experience"}).
        Returns chunk-level matches grouped by candidate.
        Boosts chunks that contain keywords from the query as determined by TF-IDF.
        """
        if filters is None:
            filters = {}
        
        # Build the 'where' clause from filters.
        if len(filters) == 0:
            where_clause = None
        elif len(filters) == 1:
            (k, v) = list(filters.items())[0]
            where_clause = {k: v}
        else:
            and_clauses = [{k: v} for k, v in filters.items()]
            where_clause = {"$and": and_clauses}

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

        # Extract TF-IDF keywords from the query
        query_keywords = set(self.extract_query_keywords(semantic_query))

        candidate_hits = {}
        for doc, meta, dist in zip(chunk_docs, chunk_metas, chunk_dists):
            # Compute base similarity
            similarity = 1 - dist

            # Compute bonus from keyword matches.
            bonus = 0.0
            doc_lower = doc.lower()
            for kw in query_keywords:
                if kw in doc_lower:
                    bonus += 0.01  # you can tune this bonus value
            new_similarity = min(similarity + bonus, 1.0)

            # Optionally skip very low scoring chunks
            if new_similarity < -0.4:
                continue

            candidate_id = meta.get("candidate_id", "Unknown")
            candidate_name = meta.get("candidate_name", "Unknown")
            snippet_text = doc[:800] + ("..." if len(doc) > 800 else "")
            chunk_info = {
                "snippet": snippet_text,
                "section": meta.get("section", ""),
                "similarity_score": new_similarity,
            }
            if candidate_id not in candidate_hits:
                candidate_hits[candidate_id] = {"candidate_name": candidate_name, "chunks": []}
            candidate_hits[candidate_id]["chunks"].append(chunk_info)

        candidate_list = []
        for cid, data in candidate_hits.items():
            best_score = max(ch["similarity_score"] for ch in data["chunks"])
            candidate_list.append({
                "candidate_id": cid,
                "candidate_name": data["candidate_name"],
                "score": best_score,
                "chunks": data["chunks"]
            })
        candidate_list.sort(key=lambda x: x["score"], reverse=True)
        return candidate_list


    def multi_subquery_search(self, user_input: str, n_results: int = 200):
        """
        Splits the user_input on "and" to create multiple subqueries.
        - Each subquery is further parsed for filters (e.g. 'industry' => section=experience, etc.).
        - We run each subquery separately, then intersect the candidate results.
        - For each candidate, we pick distinct top chunks for each subquery.
        Returns a list of candidate-level results with a "chosen_subchunks" key.
        """
        # Step 1: Split the user query on "and"
        sub_texts = [s.strip() for s in user_input.lower().split(" and ")]

        # If there is only one subquery, fall back to normal query_chunks
        if len(sub_texts) < 2:
            base_semantic, base_filters = naive_query_parser(user_input)
            res = self.query_chunks(base_semantic, base_filters, n_results)
            # For each candidate in the fallback result, choose the best chunk as a single subquery.
            for cand in res:
                if cand["chunks"]:
                    best_chunk = max(cand["chunks"], key=lambda c: c["similarity_score"])
                    cand["chosen_subchunks"] = [(0, best_chunk)]
                else:
                    cand["chosen_subchunks"] = []
            return res

        # Step 2: Run each subquery separately
        merged = {}
        sub_count = len(sub_texts)
        for i, stext in enumerate(sub_texts):
            sub_semantic, sub_filters = parse_subquery_for_filters(stext)
            results_subq = self.query_chunks(sub_semantic, sub_filters, n_results)
            for c in results_subq:
                cid = c["candidate_id"]
                cname = c["candidate_name"]
                cscore = c["score"]
                cchunks = c["chunks"]
                if cid not in merged:
                    merged[cid] = {
                        "candidate_name": cname,
                        "score_subq": [None] * sub_count,
                        "chunks_subq": [[] for _ in range(sub_count)]
                    }
                merged[cid]["score_subq"][i] = cscore
                merged[cid]["chunks_subq"][i] = cchunks

        # Step 3: Keep only candidates that appear in all subqueries
        final_candidates = []
        for cid, info in merged.items():
            if any(s is None for s in info["score_subq"]):
                continue  # Candidate did not appear in all subqueries
            avg_score = sum(info["score_subq"]) / sub_count
            final_candidates.append({
                "candidate_id": cid,
                "candidate_name": info["candidate_name"],
                "score": avg_score,
                "chunks_subq": info["chunks_subq"]
            })
        final_candidates.sort(key=lambda x: x["score"], reverse=True)

        # Step 4: For each candidate, pick the best chunk from each subquery,
        # ensuring we don't repeat the same chunk. If none qualifies, add an empty dict.
        for cand in final_candidates:
            used_chunks = set()
            chosen_chunks = []
            for i, chunk_list in enumerate(cand["chunks_subq"]):
                # Sort chunk_list by similarity descending
                chunk_list.sort(key=lambda c: c["similarity_score"], reverse=True)
                chosen = None
                for ch in chunk_list:
                    snippet_key = ch["snippet"]
                    if snippet_key not in used_chunks:
                        chosen = ch
                        used_chunks.add(snippet_key)
                        break
                if chosen is None:
                    chosen = {}  # Ensure a value exists
                chosen_chunks.append((i, chosen))
            cand["chosen_subchunks"] = chosen_chunks

        return final_candidates




###############################################################################
# 3) Aggregator & Plotting (Optional)
###############################################################################

def aggregate_candidate_scores(db: ChunkedCandidateDB):
    all_data = db.get_all_chunks()
    if len(all_data.get("embeddings", [])) == 0:
        return pd.DataFrame()  # no data
    chunk_embeddings = all_data["embeddings"]
    chunk_metadata = all_data["metadatas"]
    research_prompt = "Candidate with significant academic research or publications."
    industry_prompt = "Candidate with extensive industry experience or practical engineering work."
    research_emb = db.model.encode(research_prompt)
    industry_emb = db.model.encode(industry_prompt)
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
# 4) Main Script Entry
###############################################################################

if __name__ == "__main__":
    db = ChunkedCandidateDB(persist_directory="./chroma_db")
    data = db.load_json_file('candidates.json')
    db.ingest_candidates(data)

    # # Optional aggregator + plot
    # df = aggregate_candidate_scores(db)
    # if not df.empty:
    #     plot_research_vs_industry(df)
    # else:
    #     print("No aggregated candidate data to plot.")

    # Interactive multi-subquery usage
    print("\n--- Single Input Query Demo ---\n(Type 'q' to quit)\n")
    while True:
        user_input = input("Enter your ideal candidate criteria: ")
        if user_input.lower().strip() in ["q", "quit", "exit"]:
            break

        # Use the improved multi-subquery approach
        candidate_matches = db.multi_subquery_search(user_input)
        if not candidate_matches:
            print("No matches found.\n")
            continue

        for i, candidate in enumerate(candidate_matches, start=1):
            print(f"{i}. Candidate: {candidate['candidate_name']} (score={candidate['score']:.3f})")
            # Each candidate has chosen_subchunks: list of (subq_index, chunk_info)
            # showing the best chunk from each sub-query.
            for (sub_idx, chunk_info) in candidate["chosen_subchunks"]:
                print(f"   Subquery {sub_idx+1} best chunk (score={chunk_info['similarity_score']:.3f}, section={chunk_info['section']}):")
                snippet = chunk_info["snippet"]
                # Truncate snippet for display
                max_display = 800
                snippet_display = snippet[:max_display] + ("..." if len(snippet) > max_display else "")
                print(f"       {snippet_display}")
            print()
        print("---------------------------------------------------")
