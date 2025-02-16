from scrapybara import Scrapybara
from scrapybara.anthropic import Anthropic
from scrapybara.tools import BashTool, ComputerTool, EditTool, BrowserTool
from scrapybara.prompts import UBUNTU_SYSTEM_PROMPT
from pydantic import BaseModel
from typing import List


# Define our schema for structured output
class TwitterUserSchema(BaseModel):
    class User(BaseModel):
        username: str
        bio: str
        post_content: str
        ai_relevance: str
    
    users: List[User]

# Initialize Scrapybara client
client = Scrapybara(api_key="scrapy-0a7bbe3d-b23a-4801-b412-d7aa56700f0a")



# Start an Ubuntu instance
instance = client.start_ubuntu(
    timeout_hours=1,
)

stream_url = instance.get_stream_url().stream_url
print(stream_url)


# Initialize browser
instance.browser.start()
instance.browser.authenticate(auth_state_id="246f3e24-f93d-4608-a05d-d188548ec737")




# Define our custom system prompt
TWITTER_SYSTEM_PROMPT = f"""{UBUNTU_SYSTEM_PROMPT}

<TASK>
You are tasked with analyzing Twitter/X posts about AI. For each relevant post:
1. Evaluate if the post is genuinely about AI technology or development
2. Capture the username and navigate to their profile
3. Analyze their bio and recent posts to determine their AI expertise
4. Only include users who have meaningful AI-related content
</TASK>
"""

# Execute the search and analysis
response = client.act(
    model=Anthropic(),
    tools=[
        BashTool(instance),
        ComputerTool(instance),
        EditTool(instance),
        BrowserTool(instance),
    ],
    system=TWITTER_SYSTEM_PROMPT,
    prompt="Go to x.com, search for 'artificial intelligence' posts from the last 24 hours, and analyze the top 5 most relevant users posting about AI",
    schema=TwitterUserSchema,
    on_step=lambda step: print(step.text),
)

# Process results
if response.output:
    users = response.output.users
    print("\nAnalysis Results:")
    for user in users:
        print(f"\nUsername: @{user.username}")
        print(f"Bio: {user.bio}")
        print(f"Sample Post: {user.post_content}")
        print(f"AI Relevance: {user.ai_relevance}")

# Cleanup
instance.browser.stop()
instance.stop()
