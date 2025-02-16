from setup_chroma2 import RecruitingDB
import json
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import numpy as np
from numpy.linalg import norm
from sentence_transformers import SentenceTransformer

def retrieve_candidate_embeddings(db: RecruitingDB):
    """
    Retrieves all candidates and their existing embeddings from Chroma.
    Returns a tuple (candidate_ids, embeddings, candidate_metadata).
    """
    all_data = db.candidates.get(include=["embeddings", "documents", "metadatas"])

    candidate_ids = all_data.get("ids", [])
    candidate_embeddings = all_data.get("embeddings", [])
    candidate_metadatas = all_data.get("metadatas", [])

    return candidate_ids, candidate_embeddings, candidate_metadatas


def visualize_candidates_tsne(candidate_ids, candidate_embeddings, candidate_metadatas):

    # Convert candidate_embeddings to a numpy array and print its shape for debugging.
    X = np.array(candidate_embeddings)
    # print(X)
    # print("Candidate embeddings shape:", X.shape)  # Should be (number_of_candidates, embedding_dimension)
    
    n_samples = X.shape[0]
    if n_samples < 3:
        print(f"Not enough data points for t-SNE. Only {n_samples} embeddings found.")
        return

    # Set perplexity very low for a small sample size (must be < n_samples)
    perplexity_val = min(5, n_samples - 1)
    print("Using perplexity:", perplexity_val)
    
    tsne_model = TSNE(n_components=2, perplexity=perplexity_val, random_state=42, init='pca')
    X_2d = tsne_model.fit_transform(X)

    plt.figure(figsize=(10, 7))
    for i, (x, y) in enumerate(X_2d):
        name = candidate_metadatas[i].get("name", candidate_ids[i])
        plt.scatter(x, y, alpha=0.7)
        plt.text(x + 0.2, y, name, fontsize=9)

    plt.title("t-SNE Visualization of Candidate Embeddings")
    plt.xlabel("Dimension 1")
    plt.ylabel("Dimension 2")
    plt.show()



def cosine_similarity(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

def compute_creativity_rigor_scores(candidate_embeddings, creativity_emb, rigor_emb):
    """
    For each candidate embedding, compute similarity to 'creativity' and 'rigor'.
    Returns two lists: creativity_scores, rigor_scores
    """
    creativity_scores = []
    rigor_scores = []
    
    for emb in candidate_embeddings:
        c_score = cosine_similarity(emb, creativity_emb)
        r_score = cosine_similarity(emb, rigor_emb)
        creativity_scores.append(c_score)
        rigor_scores.append(r_score)
    
    return creativity_scores, rigor_scores


def visualize_candidates_creativity_rigor(candidate_ids, candidate_embeddings, candidate_metadatas):
    # 1. Create anchor embeddings
    model = SentenceTransformer('all-MiniLM-L6-v2')
    creativity_prompt = '''{
    "name": "David Kim",
    "currentPosition": "Indie Game Developer & Founder",
    "education": [
      {
        "institution": "Rhode Island School of Design",
        "degree": "BFA in Digital Media",
        "year": "2018"
      }
    ],
    "experience": [
      {
        "company": "Independent",
        "title": "Game Developer",
        "startDate": "2020",
        "endDate": "Present"
      },
      {
        "company": "Riot Games",
        "title": "Game Designer",
        "startDate": "2018",
        "endDate": "2020"
      }
    ],
    "games": [
      {
        "title": "Neon Dreams",
        "platform": "Steam",
        "downloads": 2500000,
        "rating": 4.8
      },
      {
        "title": "Pixel Warriors",
        "platform": "Mobile",
        "downloads": 5000000,
        "rating": 4.6
      }
    ],
    "hackathonProjects": [
      {
        "name": "AR Garden",
        "event": "Reality Hack",
        "placement": "1st Place",
        "year": "2023"
      },
      {
        "name": "Sound Space",
        "event": "Global Game Jam",
        "placement": "Innovation Award",
        "year": "2022"
      }
    ],
    "awards": [
      {
        "name": "Independent Games Festival Award",
        "category": "Excellence in Visual Art",
        "year": "2023"
      }
    ],
    "skills": [
      "Unity",
      "Unreal Engine",
      "3D Modeling",
      "Game Design",
      "AR/VR Development"
    ]
  }'''
    rigor_prompt = '''"name": "Sarah Chen",
    "currentPosition": "Research Scientist at DeepMind",
    "education": [
      {
        "institution": "MIT",
        "degree": "PhD in Computer Science (Machine Learning)",
        "year": "2020"
      },
      {
        "institution": "UC Berkeley",
        "degree": "BS in Electrical Engineering and Computer Science",
        "year": "2015"
      }
    ],
    "experience": [
      {
        "company": "DeepMind",
        "title": "Research Scientist",
        "startDate": "2020",
        "endDate": "Present"
      },
      {
        "company": "OpenAI",
        "title": "Research Intern",
        "startDate": "2019",
        "endDate": "2019"
      },
      {
        "company": "Google Brain",
        "title": "Research Intern",
        "startDate": "2018",
        "endDate": "2018"
      }
    ],
    "publications": [
      {
        "title": "Advances in Neural Network Compression",
        "conference": "NeurIPS",
        "year": "2023",
        "citations": 245
      },
      {
        "title": "Efficient Transformer Architectures",
        "conference": "ICML",
        "year": "2022",
        "citations": 567
      }
    ],
    "projects": [
      "TinyML: Compression framework for edge devices",
      "EfficientTransformer: State-of-the-art model architecture",
      "NeuroEvolution: Genetic algorithms for neural architecture search"
    ],
    "awards": [
      {
        "name": "Outstanding Paper Award",
        "year": "2023",
        "organization": "NeurIPS"
      },
      {
        "name": "Google PhD Fellowship",
        "year": "2018"
      }
    ],
    "githubMetrics": {
      "followers": 2800,
      "stars": 4500,
      "contributions": 1245
    }'''
    
    creativity_emb = model.encode(creativity_prompt)
    rigor_emb = model.encode(rigor_prompt)
    
    # 2. Compute (creativity, rigor) scores for each candidate
    c_scores = []
    r_scores = []
    for emb in candidate_embeddings:
        c_scores.append(cosine_similarity(emb, creativity_emb))
        r_scores.append(cosine_similarity(emb, rigor_emb))
    
    # 3. Plot in 2D
    plt.figure(figsize=(10, 7))
    for i, (c, r) in enumerate(zip(c_scores, r_scores)):
        name = candidate_metadatas[i].get("name", candidate_ids[i])
        plt.scatter(c, r, alpha=0.7)
        plt.text(c + 0.002, r, name, fontsize=9)
    
    plt.title("Creativity vs. Rigor Embedding Plot")
    plt.xlabel("Creativity Score (similarity)")
    plt.ylabel("Rigor Score (similarity)")
    plt.grid(True)
    plt.show()



if __name__ == "__main__":
    # Initialize your DB (creates or loads from ./chroma_db)
    db = RecruitingDB()

    
    # Example JSON data (you can load this from file, API, etc.)
    sundar_data = {
      "name": "Sundar Pichai",
      "currentPosition": "CEO of Alphabet and Google",
      "education": [
        {
          "institution": "Stanford University",
          "degree": "MS in Materials Science and Engineering",
          "year": "1995"
        },
        {
          "institution": "University of Pennsylvania (Wharton)",
          "degree": "MBA",
          "year": "2002"
        }
      ],
      "experience": [
        {
          "company": "Google/Alphabet",
          "title": "CEO",
          "startDate": "2015",
          "endDate": "Present"
        },
        # ... you can fill in the rest ...
      ],
      "projects": [
        "Google Chrome",
        "Android",
        "Google Drive"
      ],
      "awards": [
        {
          "name": "Padma Bhushan",
          "year": "2022",
          "organization": "Government of India"
        }
      ],
      "boardMemberships": [
        "Alphabet Inc."
      ],
      "achievements": [
        "Led development of Google Chrome",
        "Oversaw Android development"
      ]
    }
    sarah_data = {
    "name": "Sarah Chen",
    "currentPosition": "Research Scientist at DeepMind",
    "education": [
      {
        "institution": "MIT",
        "degree": "PhD in Computer Science (Machine Learning)",
        "year": "2020"
      },
      {
        "institution": "UC Berkeley",
        "degree": "BS in Electrical Engineering and Computer Science",
        "year": "2015"
      }
    ],
    "experience": [
      {
        "company": "DeepMind",
        "title": "Research Scientist",
        "startDate": "2020",
        "endDate": "Present"
      },
      {
        "company": "OpenAI",
        "title": "Research Intern",
        "startDate": "2019",
        "endDate": "2019"
      },
      {
        "company": "Google Brain",
        "title": "Research Intern",
        "startDate": "2018",
        "endDate": "2018"
      }
    ],
    "publications": [
      {
        "title": "Advances in Neural Network Compression",
        "conference": "NeurIPS",
        "year": "2023",
        "citations": 245
      },
      {
        "title": "Efficient Transformer Architectures",
        "conference": "ICML",
        "year": "2022",
        "citations": 567
      }
    ],
    "projects": [
      "TinyML: Compression framework for edge devices",
      "EfficientTransformer: State-of-the-art model architecture",
      "NeuroEvolution: Genetic algorithms for neural architecture search"
    ],
    "awards": [
      {
        "name": "Outstanding Paper Award",
        "year": "2023",
        "organization": "NeurIPS"
      },
      {
        "name": "Google PhD Fellowship",
        "year": "2018"
      }
    ],
    "githubMetrics": {
      "followers": 2800,
      "stars": 4500,
      "contributions": 1245
    }
  }
    alex_data = {
    "name": "Alex Rodriguez",
    "currentPosition": "Founder & CTO of SecureAI",
    "education": [
      {
        "institution": "Stanford University",
        "degree": "MS in Computer Science",
        "year": "2018"
      },
      {
        "institution": "Georgia Tech",
        "degree": "BS in Computer Science",
        "year": "2016"
      }
    ],
    "experience": [
      {
        "company": "SecureAI",
        "title": "Founder & CTO",
        "startDate": "2020",
        "endDate": "Present"
      },
      {
        "company": "Palantir",
        "title": "Security Engineer",
        "startDate": "2018",
        "endDate": "2020"
      }
    ],
    "hackathonAchievements": [
      {
        "name": "ETHGlobal",
        "project": "ZeroTrust: Decentralized Identity Verification",
        "placement": "1st Place",
        "year": "2023"
      },
      {
        "name": "HackMIT",
        "project": "SecureVote: Blockchain-based Voting System",
        "placement": "Grand Prize",
        "year": "2022"
      },
      {
        "name": "CalHacks",
        "project": "PrivacyGuard: Zero-knowledge proof implementation",
        "placement": "2nd Place",
        "year": "2021"
      }
    ],
    "projects": [
      "ZeroTrust Framework",
      "PrivacyGuard",
      "SecureVote"
    ],
    "patents": [
      {
        "title": "Method for Secure Distributed Identity Verification",
        "year": "2023",
        "number": "US20230123456"
      }
    ],
    "githubMetrics": {
      "followers": 3500,
      "stars": 8900,
      "contributions": 892
    }
  }
    maya_data = {
    "name": "Maya Patel",
    "currentPosition": "Lead Developer Relations Engineer at MongoDB",
    "education": [
      {
        "institution": "Carnegie Mellon University",
        "degree": "BS in Information Systems",
        "year": "2019"
      }
    ],
    "experience": [
      {
        "company": "MongoDB",
        "title": "Lead Developer Relations Engineer",
        "startDate": "2022",
        "endDate": "Present"
      },
      {
        "company": "Twilio",
        "title": "Developer Evangelist",
        "startDate": "2019",
        "endDate": "2022"
      }
    ],
    "speakingEngagements": [
      {
        "event": "MongoDB World",
        "topic": "Building Scalable Applications",
        "year": "2023"
      },
      {
        "event": "DevRelCon",
        "topic": "Community-Driven Development",
        "year": "2022"
      }
    ],
    "hackathonMentoring": [
      {
        "event": "HackNY",
        "role": "Lead Mentor",
        "year": "2023"
      },
      {
        "event": "PennApps",
        "role": "Technical Mentor",
        "year": "2022"
      }
    ],
    "content": [
      {
        "platform": "YouTube",
        "subscribers": 45000,
        "videos": 120
      },
      {
        "platform": "Technical Blog",
        "monthlyReaders": 75000,
        "articles": 85
      }
    ],
    "projects": [
      "MongoDB University Courses",
      "Open Source Workshop Series",
      "Developer Community Platform"
    ]
  }
    # Choose which embedding "views" you want
    embedding_types = ["all_info", "experience_only", "education_experience"]

    # Upsert them
    inserted_ids = db.upsert_candidate_embeddings(sundar_data, embedding_types=embedding_types)
    inserted_ids = db.upsert_candidate_embeddings(sarah_data, embedding_types=embedding_types)
    inserted_ids = db.upsert_candidate_embeddings(alex_data, embedding_types=embedding_types)
    inserted_ids = db.upsert_candidate_embeddings(maya_data, embedding_types=embedding_types)
    # print("Upserted doc IDs:", inserted_ids)

    candidate_ids, candidate_embeddings, candidate_metadatas = retrieve_candidate_embeddings(db)
    # print(candidate_ids)
    # Visualize
    # visualize_candidates_tsne(candidate_ids, candidate_embeddings, candidate_metadatas)
    # visualize_candidates_creativity_rigor(candidate_ids, candidate_embeddings, candidate_metadatas)

    # Now you can query with a text prompt
    query_text = "Extensive publications in journals like NeurIPS"
    results = db.query_candidates(query_text, n_results=3)
    print("\nQUERY RESULTS:")
    print(json.dumps(results, indent=2))

    # print("hehe")

    # print(retrieve_candidate_embeddings(db))