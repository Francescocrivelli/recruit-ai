from fastapi import FastAPI, BackgroundTasks
from scrapybara import Scrapybara
from scrapybara.anthropic import Anthropic
from scrapybara.tools import BashTool, ComputerTool, EditTool, BrowserTool
from scrapybara.prompts import UBUNTU_SYSTEM_PROMPT
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI()

# Schema definitions
class XUserAnalysis(BaseModel):
    username: str
    areas_of_interest: List[str]
    technical_skills: List[str]
    social_fit: str
    sample_posts: List[str]
    overall_analysis: str

class AnalysisRequest(BaseModel):
    username: str

class AnalysisResponse(BaseModel):
    request_id: str
    message: str
    status: str

class AnalysisStatus(BaseModel):
    success: bool
    completed: bool
    current_step: str
    status_updates: List[str]
    result: Optional[XUserAnalysis] = None
    error: str = ""

# Store for task results
task_results = {}

# Initialize Scrapybara client
client = Scrapybara(api_key="scrapy-0a7bbe3d-b23a-4801-b412-d7aa56700f0a")

# Custom system prompt
X_ANALYSIS_PROMPT = f"""{UBUNTU_SYSTEM_PROMPT}

<TASK>
You are tasked with analyzing a user's X/Twitter profile. You will:
1. Navigate to their profile page
2. Analyze their recent posts, bio, and interactions
3. Identify:
   - Key areas of interest and expertise
   - Technical skills and knowledge
   - Communication style and social fit
   - Representative posts that showcase their expertise
4. Provide a comprehensive analysis of their professional profile
</TASK>
"""

def analyze_user(username: str, request_id: str) -> XUserAnalysis:
    instance = client.start_ubuntu(timeout_hours=1)
    
    try:
        instance.browser.start()
        instance.browser.authenticate(auth_state_id="246f3e24-f93d-4608-a05d-d188548ec737")
        
        def log_step(step):
            timestamp = datetime.now().strftime("%H:%M:%S")
            status_message = f"[{timestamp}] {step.text}"
            print(status_message)
            
            if request_id in task_results:
                current_status = task_results[request_id]
                current_status.status_updates.append(status_message)
                current_status.current_step = step.text
                task_results[request_id] = current_status

        response = client.act(
            model=Anthropic(),
            tools=[
                BashTool(instance),
                ComputerTool(instance),
                EditTool(instance),
                BrowserTool(instance),
            ],
            system=X_ANALYSIS_PROMPT,
            prompt=f"Go to x.com/{username} and analyze their profile comprehensively",
            schema=XUserAnalysis,
            on_step=log_step,
        )
        
        return response.output
        
    finally:
        try:
            instance.browser.stop()
            instance.stop()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

async def process_analysis(request_id: str, username: str):
    try:
        # Initialize status
        task_results[request_id] = AnalysisStatus(
            success=False,
            completed=False,
            current_step="Starting analysis...",
            status_updates=[f"[{datetime.now().strftime('%H:%M:%S')}] Starting analysis for @{username}"]
        )
        
        # Perform analysis
        result = analyze_user(username, request_id)
        
        # Update with final result
        task_results[request_id] = AnalysisStatus(
            success=True,
            completed=True,
            current_step="Analysis completed",
            status_updates=task_results[request_id].status_updates + 
                         [f"[{datetime.now().strftime('%H:%M:%S')}] Analysis completed"],
            result=result
        )
        
    except Exception as e:
        error_msg = str(e)
        task_results[request_id] = AnalysisStatus(
            success=False,
            completed=True,
            current_step="Error occurred",
            status_updates=task_results[request_id].status_updates + 
                         [f"[{datetime.now().strftime('%H:%M:%S')}] Error: {error_msg}"],
            error=error_msg
        )

@app.post("/analyze", response_model=AnalysisResponse)
async def create_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    request_id = f"analysis-{request.username}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    background_tasks.add_task(
        process_analysis,
        request_id,
        request.username
    )
    
    return AnalysisResponse(
        request_id=request_id,
        message="Analysis started",
        status="pending"
    )

@app.get("/status/{request_id}", response_model=AnalysisStatus)
async def get_status(request_id: str):
    return task_results.get(request_id, AnalysisStatus(
        success=False,
        completed=False,
        current_step="Request ID not found",
        status_updates=[],
        error="Request ID not found"
    ))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 