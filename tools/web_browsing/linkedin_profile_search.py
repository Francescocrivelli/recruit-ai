from scrapybara import Scrapybara
from scrapybara.anthropic import Anthropic
from scrapybara.tools import BashTool, ComputerTool, EditTool, BrowserTool
from scrapybara.prompts import UBUNTU_SYSTEM_PROMPT
from pydantic import BaseModel
from typing import List, Optional

# Define our schema for structured output
class LinkedInProfileSchema(BaseModel):
    class Profile(BaseModel):
        name: str
        summary: str  # 100-word summary including experience and query-relevant facts
        relevance_score: Optional[float]  # How relevant the profile is to the search query (0-1)
    
    profiles: List[Profile]
    query: str  # Store the original search query

# Initialize Scrapybara client
client = Scrapybara(api_key="scrapy-0a7bbe3d-b23a-4801-b412-d7aa56700f0a")

# Start an Ubuntu instance
instance = client.start_ubuntu(
    timeout_hours=1,
)

# Initialize browser and navigate to LinkedIn
instance.browser.start()
instance.browser.authenticate(auth_state_id="246f3e24-f93d-4608-a05d-d188548ec737")

stream_url = instance.get_stream_url().stream_url
print(stream_url)

# Use BrowserTool to navigate to LinkedIn
# browser_tool = BrowserTool(instance)
# browser_tool = (command="go_to", url="https://www.linkedin.com")

# Define our custom system prompt
LINKEDIN_SYSTEM_PROMPT = f"""{UBUNTU_SYSTEM_PROMPT}

<TASK>
You are tasked with searching and analyzing LinkedIn profiles. For each profile:
1. Navigate to the profile page
2. Create a concise 100-word summary that includes:
   - Key professional experience
   - Facts relevant to the search query
   - Notable achievements or skills
3. Assign a relevance score (0-1) based on how well the profile matches the search query
4. Return only profiles that are highly relevant to the search
5. Ensure to respect LinkedIn's rate limits and terms of service
</TASK>
"""


# for faster search use the url below and prommpt it
# "https://www.linkedin.com/search/results/all/?keywords={query}".format(query="asdfasdfds")

def search_linkedin_profiles(search_query: str, max_profiles: int = 5):
    try:
        response = client.act(
            model=Anthropic(),
            tools=[
                BashTool(instance),
                ComputerTool(instance),
                EditTool(instance),
                # BrowserTool(instance),
            ],
            system=LINKEDIN_SYSTEM_PROMPT,
            prompt=f"A browser is open and we are logged into LinkedIn (wait a bit if you don't see linkedin loaded.). Search for '{search_query}' on linkedin, and analyze the top {max_profiles} most relevant profiles",
            schema=LinkedInProfileSchema,
            on_step=lambda step: print(step.text),
        )
        
        # Handle case where no profiles are found
        if not response.output:
            return LinkedInProfileSchema(profiles=[], query=search_query)
            
        return response.output
    except Exception as e:
        print(f"Error during search: {str(e)}")
        return LinkedInProfileSchema(profiles=[], query=search_query)

def cleanup():
    try:
        instance.browser.stop()
        instance.stop()
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")

# Example usage:
if __name__ == "__main__":
    try:
        # Example for searching a specific profile
        specific_profile = search_linkedin_profiles("Francesco Crivelli, UC Berkeley")
        
        if specific_profile and specific_profile.profiles:
            print("\nSearch Results:")
            print(f"Query: {specific_profile.query}")
            for profile in specific_profile.profiles:
                print(f"\nName: {profile.name}")
                print(f"Summary: {profile.summary}")
                if profile.relevance_score:
                    print(f"Relevance: {profile.relevance_score:.2f}")
        else:
            print("\nNo profiles found matching the search criteria.")
            
    finally:
        cleanup()
