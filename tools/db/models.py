# tools/db/models.py

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Skill:
    name: str
    proficiency: str  # e.g., "Beginner", "Intermediate", "Expert"
    years_experience: float
    last_used: Optional[str] = None

@dataclass
class Experience:
    company: str
    title: str
    start_date: str
    end_date: Optional[str]
    description: str
    technologies: List[str]

@dataclass
class Candidate:
    full_name: str
    email: str
    phone: Optional[str]
    location: str
    skills: List[Skill]
    experiences: List[Experience]
    education: List[dict]
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    source: str = "direct"
    created_at: str = str(datetime.now())