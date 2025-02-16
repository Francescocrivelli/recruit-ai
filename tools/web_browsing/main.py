from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import json
from datetime import datetime
import os

# Import our service classes
from linkedin_parallel_connect import LinkedInConnector, ConnectionResult
from x_analyzer import XUserAnalysis, analyze_user
from x import TwitterUserSchema

app = FastAPI(title="Web Browser Automation API")

# LinkedIn Connection Request Model
class LinkedInBatchRequest(BaseModel):
    connections: List[Dict[str, str]]
    batch_size: int = 3

# Twitter Analysis Request Model
class TwitterAnalysisRequest(BaseModel):
    search_query: str = "artificial intelligence"
    num_users: int = 5

# Initialize shared configuration
API_KEY = "scrapy-0a7bbe3d-b23a-4801-b412-d7aa56700f0a"
AUTH_STATE_ID = "246f3e24-f93d-4608-a05d-d188548ec737"

# LinkedIn Routes
@app.post("/linkedin/connect/batch", response_model=List[ConnectionResult])
async def batch_connect_linkedin(request: LinkedInBatchRequest):
    connector = LinkedInConnector(API_KEY, AUTH_STATE_ID, batch_size=request.batch_size)
    results = await connector.process_all_connections(request.connections)
    return results

# X/Twitter Routes
@app.post("/x/analyze-user", response_model=XUserAnalysis)
async def analyze_x_user(username: str):
    result = analyze_user(username)
    return result

@app.post("/x/analyze-ai-posts", response_model=TwitterUserSchema)
async def analyze_ai_posts(request: TwitterAnalysisRequest):
    # Initialize the Twitter analysis service
    from x import client, instance, TWITTER_SYSTEM_PROMPT
    
    try:
        response = client.act(
            model=Anthropic(),
            tools=[
                BashTool(instance),
                ComputerTool(instance),
                EditTool(instance),
                BrowserTool(instance),
            ],
            system=TWITTER_SYSTEM_PROMPT,
            prompt=f"Go to x.com, search for '{request.search_query}' posts from the last 24 hours, and analyze the top {request.num_users} most relevant users posting about AI",
            schema=TwitterUserSchema,
            on_step=lambda step: print(step.text),
        )
        return response.output
    finally:
        instance.browser.stop()
        instance.stop()

# Basic test endpoint to verify deployment
@app.get("/")
async def root():
    return {"message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 