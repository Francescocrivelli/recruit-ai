from fastapi import FastAPI
from scrapybara import Scrapybara
from scrapybara.anthropic import Anthropic
from scrapybara.tools import BashTool, ComputerTool, EditTool, BrowserTool
from scrapybara.prompts import UBUNTU_SYSTEM_PROMPT
from pydantic import BaseModel
from typing import List
from datetime import datetime
from fastapi import HTTPException

app = FastAPI()

# Schema definitions
class XUserAnalysis(BaseModel):
    username: str
    recent_posts: List[str]
    areas_of_interest: List[str]
    technical_skills: List[str]
    social_fit: str
    overall_analysis: str

class AnalysisRequest(BaseModel):
    username: str

# Initialize Scrapybara client
client = Scrapybara(api_key="scrapy-0a7bbe3d-b23a-4801-b412-d7aa56700f0a")

# Custom system prompt
X_ANALYSIS_PROMPT = f"""{UBUNTU_SYSTEM_PROMPT}

<TASK>
You are tasked with analyzing a user's X/Twitter profile. You will:
1. Navigate to their profile page
2. Collect and analyze their 5 most recent posts
3. Identify:
   - Key areas of interest and expertise from their posts and bio
   - Technical skills and knowledge demonstrated
   - Communication style and social fit
4. Provide a concise professional analysis
</TASK>
"""

def analyze_user(username: str) -> XUserAnalysis:
    instance = client.start_ubuntu(timeout_hours=1)
    
    try:
        instance.browser.start()
        instance.browser.authenticate(auth_state_id="246f3e24-f93d-4608-a05d-d188548ec737")
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting analysis for @{username}")

        stream_url = instance.get_stream_url().stream_url
        print(f"\nNew instance stream URL: {stream_url}")
        
        response = client.act(
            model=Anthropic(),
            tools=[
                BashTool(instance),
                ComputerTool(instance),
                EditTool(instance),
                BrowserTool(instance),
            ],
            system=X_ANALYSIS_PROMPT,
            prompt=f"""
            1. Go to x.com/{username}
            2. Collect their 5 most recent posts
            3. Analyze their profile and provide a comprehensive analysis
            """,
            schema=XUserAnalysis,
            on_step=lambda step: print(f"[{datetime.now().strftime('%H:%M:%S')}] {step.text}"),
        )
        
        return response.output
        
    finally:
        try:
            instance.browser.stop()
            instance.stop()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

@app.post("/analyze", response_model=XUserAnalysis)
async def create_analysis(request: AnalysisRequest):
    try:
        result = analyze_user(request.username)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 