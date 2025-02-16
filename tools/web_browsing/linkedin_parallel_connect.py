import asyncio
from typing import List, Dict
import json
from scrapybara import Scrapybara
from scrapybara.anthropic import Anthropic
from scrapybara.tools import BashTool, ComputerTool, EditTool
from scrapybara.prompts import UBUNTU_SYSTEM_PROMPT
from pydantic import BaseModel

class ConnectionResult(BaseModel):
    name: str
    university: str
    success: bool
    message_sent: str
    error: str = ""

class LinkedInConnector:
    def __init__(self, api_key: str, auth_state_id: str, batch_size: int = 5):
        self.api_key = api_key
        self.auth_state_id = auth_state_id
        self.batch_size = batch_size
        self.client = Scrapybara(api_key=api_key)
        
        self.LINKEDIN_CONNECT_PROMPT = f"""{UBUNTU_SYSTEM_PROMPT}
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

    async def setup_instance(self) -> tuple:
        """Setup a new Ubuntu instance with browser"""
        instance = self.client.start_ubuntu(timeout_hours=1)
        
        
        instance.browser.start()
        instance.browser.authenticate(auth_state_id=self.auth_state_id)

        stream_url = instance.get_stream_url().stream_url
        print(f"\nNew instance stream URL: {stream_url}")
        return instance

    async def connect_with_person(self, instance, name: str, university: str) -> ConnectionResult:
        """Connect with a single person using the given instance"""
        try:
            search_url = f"https://www.linkedin.com/search/results/all/?keywords={name} {university}"
            response = self.client.act(
                model=Anthropic(),
                tools=[
                    BashTool(instance),
                    ComputerTool(instance),
                    EditTool(instance),
                ],
                system=self.LINKEDIN_CONNECT_PROMPT,
                prompt=f"""
                1. A browser is open and we need to go to: {search_url}
                2. Find {name}'s profile (they attended {university})
                3. Create and send a personalized connection request 
                """,
                schema=ConnectionResult,
                on_step=lambda step: print(f"[{name}] {step.text}"),
            )
            
            return ConnectionResult(
                name=name,
                university=university,
                success=response.output.success,
                message_sent=response.output.message_sent,
                error=response.output.error
            )
            
        except Exception as e:
            return ConnectionResult(
                name=name,
                university=university,
                success=False,
                message_sent="",
                error=str(e)
            )

    async def process_batch(self, batch: List[Dict[str, str]]) -> List[ConnectionResult]:
        """Process a batch of connections in parallel"""
        # Create instances for the batch
        instances = await asyncio.gather(*[self.setup_instance() for _ in batch])
        
        try:
            # Process connections in parallel
            tasks = [
                self.connect_with_person(instance, person['name'], person['university'])
                for instance, person in zip(instances, batch)
            ]
            results = await asyncio.gather(*tasks)
            
            return results
            
        finally:
            # Cleanup instances
            for instance in instances:
                try:
                    instance.browser.stop()
                    instance.stop()
                except Exception as e:
                    print(f"Error during cleanup: {str(e)}")

    async def process_all_connections(self, connections: List[Dict[str, str]]) -> List[ConnectionResult]:
        """Process all connections in batches"""
        all_results = []
        
        # Process connections in batches
        for i in range(0, len(connections), self.batch_size):
            batch = connections[i:i + self.batch_size]
            print(f"\nProcessing batch {i//self.batch_size + 1}...")
            
            # Create and execute all tasks in the batch simultaneously
            results = await self.process_batch(batch)
            all_results.extend(results)
            
            # Print batch results
            for result in results:
                print(f"\nResult for {result.name}:")
                print(f"Success: {'Yes' if result.success else 'No'}")
                print(f"Message Sent: {result.message_sent}")
                if result.error:
                    print(f"Error: {result.error}")
        
        return all_results

async def main():
    # Configuration
    API_KEY = "scrapy-0a7bbe3d-b23a-4801-b412-d7aa56700f0a"
    AUTH_STATE_ID = "246f3e24-f93d-4608-a05d-d188548ec737"
    
    # Sample connections data (you can load this from a JSON file)
    connections = [
        {"name": "Kelvin Cui", "university": "University of Toronto"},
        {"name": "John Smith", "university": "Harvard University"},
        {"name": "Jane Doe", "university": "MIT"},
        {"name": "Alice Johnson", "university": "Stanford University"},
        {"name": "Bob Wilson", "university": "Yale University"},
        {"name": "Carol Brown", "university": "Princeton University"},
    ]
    
    connector = LinkedInConnector(API_KEY, AUTH_STATE_ID, batch_size=3)
    results = await connector.process_all_connections(connections)
    
    # Save results to JSON file
    with open('connection_results.json', 'w') as f:
        json.dump([result.dict() for result in results], f, indent=2)

if __name__ == "__main__":
    asyncio.run(main()) 