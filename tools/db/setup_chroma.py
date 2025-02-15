# tools/db/setup_chroma.py

import chromadb
from datetime import datetime
import json
from models import Candidate, Skill, Experience
from typing import List, Optional

class RecruitingDB:
    def __init__(self):
        self.client = chromadb.Client()
        self.candidates = self.client.get_or_create_collection(name="candidates")
        self.skills = self.client.get_or_create_collection(name="skills")
        self.experiences = self.client.get_or_create_collection(name="experiences")
    
    def add_candidate(self, candidate: Candidate):
        """
        Add a candidate to the database with structured data
        """
        try:
            candidate_id = str(datetime.now().timestamp())
            
            # Convert candidate to dictionary for storage
            candidate_dict = {
                "full_name": candidate.full_name,
                "email": candidate.email,
                "phone": candidate.phone,
                "location": candidate.location,
                "skills": [vars(skill) for skill in candidate.skills],
                "experiences": [vars(exp) for exp in candidate.experiences],
                "education": candidate.education,
                "linkedin_url": candidate.linkedin_url,
                "github_url": candidate.github_url,
                "portfolio_url": candidate.portfolio_url,
                "created_at": candidate.created_at
            }
            
            self.candidates.upsert(
                ids=[candidate_id],
                documents=[json.dumps(candidate_dict)],
                metadatas=[{
                    "last_updated": str(datetime.now()),
                    "source": candidate.source,
                    "name": candidate.full_name,
                    "location": candidate.location
                }]
            )
            return candidate_id
        except Exception as e:
            print(f"Error adding candidate: {e}")
            raise

    def search_candidates_by_skills(self, required_skills: List[str], n_results: int = 10):
        """
        Search for candidates based on required skills
        """
        query = f"Looking for candidates with skills in {', '.join(required_skills)}"
        results = self.candidates.query(
            query_texts=[query],
            n_results=n_results
        )
        return results

    def search_candidates_by_location(self, location: str, n_results: int = 10):
        """
        Search for candidates in a specific location
        """
        return self.candidates.query(
            query_texts=[f"Candidates in {location}"],
            n_results=n_results
        )

if __name__ == "__main__":
    # Test the database with structured data
    db = RecruitingDB()
    
    # Create test candidate with structured data
    test_candidate = Candidate(
        full_name="Jane Doe",
        email="jane@example.com",
        phone="+1234567890",
        location="San Francisco, CA",
        skills=[
            Skill(name="Python", proficiency="Expert", years_experience=5.0),
            Skill(name="Machine Learning", proficiency="Intermediate", years_experience=3.0)
        ],
        experiences=[
            Experience(
                company="Tech Corp",
                title="Senior Developer",
                start_date="2020-01",
                end_date="2023-12",
                description="Led development of ML systems",
                technologies=["Python", "TensorFlow", "AWS"]
            )
        ],
        education=[{
            "institution": "Stanford University",
            "degree": "BS Computer Science",
            "graduation_year": "2019"
        }],
        linkedin_url="https://linkedin.com/in/janedoe",
        github_url="https://github.com/janedoe"
    )
    
    try:
        candidate_id = db.add_candidate(test_candidate)
        print(f"Added test candidate with ID: {candidate_id}")
        
        # Test searching by skills
        results = db.search_candidates_by_skills(["Python", "Machine Learning"])
        print("\nSearch results by skills:", json.dumps(results, indent=2))
        
        # Test searching by location
        results = db.search_candidates_by_location("San Francisco")
        print("\nSearch results by location:", json.dumps(results, indent=2))
        
    except Exception as e:
        print(f"Test failed: {e}")