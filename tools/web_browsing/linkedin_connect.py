from fastapi import FastAPI, BackgroundTasks
from scrapybara import Scrapybara
from scrapybara.anthropic import Anthropic
from scrapybara.tools import BashTool, ComputerTool, EditTool
from scrapybara.prompts import UBUNTU_SYSTEM_PROMPT
from pydantic import BaseModel
from typing import Optional
import uvicorn
from datetime import datetime

class ConnectionResult(BaseModel):
    success: bool
    message_sent: str  # The actual message that was sent
    error: str = ""    # Any error message if the connection failed
    status_updates: list[str] = []  # Add this field to store updates
    last_update: str = ""

# Initialize Scrapybara client
client = Scrapybara(api_key="scrapy-0a7bbe3d-b23a-4801-b412-d7aa56700f0a")

# Start an Ubuntu instance
instance = client.start_ubuntu(timeout_hours=1)

# Initialize browser and authenticate
instance.browser.start()

#Authenticate
instance.browser.authenticate(auth_state_id="246f3e24-f93d-4608-a05d-d188548ec737")

# Get the stream URL
stream_url = instance.get_stream_url().stream_url
print(stream_url)

# Define custom system prompt
LINKEDIN_CONNECT_PROMPT = f"""{UBUNTU_SYSTEM_PROMPT}
<TASK>
You are tasked with sending a LinkedIn connection request. You will:
1. A Chromium website is already open.
2. Go to the provided search URL with the given name and university: f"https://www.linkedin.com/search/results/all/?keywords={{name}}%20{{university}}"
3. Open the top most result by clicking on the desired name (MAKE SURE YOU ARE ON THE PROFILE YOU WANT TO CONNECT WITH)
4. Create a personalized 170-character connection message that:
   - References their background/experience
   - Explains why you'd like to connect
4. Click "Connect", add a note, and send the connection request
5. Verify the connection request was sent successfully

Remember: The connection message must be under 170 characters
</TASK>
"""

def connect_with_person(name: str, university: str) -> ConnectionResult:
    try:
        search_url = f"https://www.linkedin.com/search/results/all/?keywords={name} {university}"
        
        def log_step(step):
            timestamp = datetime.now().strftime("%H:%M:%S")
            status_message = f"[{timestamp}] {step.text}"
            print(f"Agent action: {step.text}")
            
            if current_request_id in task_results:
                current_result = task_results[current_request_id]
                current_result.status_updates.append(status_message)
                current_result.last_update = step.text
                task_results[current_request_id] = current_result
        
        response = client.act(
            model=Anthropic(),
            tools=[
                BashTool(instance),
                ComputerTool(instance),
                EditTool(instance),
            ],
            system=LINKEDIN_CONNECT_PROMPT,
            prompt=f"""
            1. A browser is open and we need to go to: {search_url}
            2. Find {name}'s profile (they attended {university})
            3. Create and send a personalized connection request 
            """,
            schema=ConnectionResult,
            on_step=log_step,
        )
        
        # Add final status update
        if current_request_id in task_results:
            current_result = task_results[current_request_id]
            current_result.status_updates.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] Connection request completed"
            )
            current_result.last_update = "Completed"
            task_results[current_request_id] = current_result
        
        return response.output
        
    except Exception as e:
        error_msg = str(e)
        return ConnectionResult(
            success=False,
            message_sent="",
            error=error_msg,
            status_updates=[f"[{datetime.now().strftime('%H:%M:%S')}] Error: {error_msg}"]
        )

def cleanup():
    try:
        instance.browser.stop()
        instance.stop()
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")

app = FastAPI()

class LinkedInConnectRequest(BaseModel):
    name: str
    university: str

class LinkedInConnectResponse(BaseModel):
    request_id: str
    message: str
    status: str

# Dictionary to store task results
task_results = {}

async def process_connection(request_id: str, name: str, university: str):
    global current_request_id
    current_request_id = request_id
    
    try:
        # Initialize status
        task_results[request_id] = ConnectionResult(
            success=False,
            message_sent="Starting connection process...",
            error="",
            status_updates=[f"[{datetime.now().strftime('%H:%M:%S')}] Starting connection process..."]
        )
        
        result = connect_with_person(name, university)
        task_results[request_id] = result
        
    except Exception as e:
        error_msg = str(e)
        task_results[request_id] = ConnectionResult(
            success=False,
            message_sent="",
            error=error_msg,
            status_updates=[f"[{datetime.now().strftime('%H:%M:%S')}] Error: {error_msg}"]
        )

@app.post("/connect", response_model=LinkedInConnectResponse)
async def create_connection(request: LinkedInConnectRequest, background_tasks: BackgroundTasks):
    request_id = f"{request.name}-{request.university}".replace(" ", "-").lower()
    
    background_tasks.add_task(
        process_connection,
        request_id,
        request.name,
        request.university
    )
    #this part below is not quite working
    return LinkedInConnectResponse(
        request_id=request_id,
        message="Connection request is being processed",
        status="pending"
    )

@app.get("/status/{request_id}", response_model=Optional[ConnectionResult])
async def get_status(request_id: str):
    return task_results.get(request_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
