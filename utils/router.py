from semantic_router import Route
from semantic_router.layer import RouteLayer
import os
from templates.orchestrator import Orchestrator

os.environ["OPENAI_API_KEY"] = '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'

class SemanticRouter:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def create_route(self, name, utterances):
        return Route(name=name, utterances=utterances)
    
    def creator_route(self):
        return self.create_route(    
            name="creator",
            utterances=[
                "Create a new tool.",
                "Add a tool to the system.",
                "I want to make a new tool.",
                "Can you create a tool for me?",
                "Initiate tool creation process.",
                "Begin creating a tool.",
                "Generate a new tool.",
                "Start the tool creation.",
                "Make a tool, please.",
                "I need to instantiate a new tool."
            ]
        )
    
    def destroyer_route(self):
        return self.create_route(
            name="destroyer",
            utterances=[
                "Delete a tool from the system.",
                "Remove a tool.",
                "Eliminate a tool.",
                "I want to get rid of a tool.",
                "Destroy a tool.",
                "Terminate a tool.",
                "Withdraw a tool.",
                "Erase a tool.",
                "Take out a tool.",
                "Annihilate a tool from the system."
            ]
        )
        
    def summarizer_route(self):
        return self.create_route(
            name="summarizer",
            utterances=[
                "Generate a summary for the tool's work.",
                "Create a report for the tool's activity.",
                "Get a summary of the tool's work.",
                "Summarize the actions performed by the tool.",
                "Retrieve a summary for the tool.",
                "Compile a report for the tool's tasks.",
                "Provide an overview of the tool's activities.",
                "Generate a summary report for the tool.",
                "Get insights into the tool's work.",
                "Fetch a summary of the tool's tasks."
            ]
        )

    
    def router(self):
        return RouteLayer(
            routes=[
                self.creator_route(),
                self.destroyer_route(),
                self.summarizer_route(),
            ]
        )
        
    # after deciding the route send to the appropriate function
    async def call_orchestrator_tool(self, **kwargs):
        router = self.router()
        route = router(kwargs["problem_statement"])
        print(":::::::SEMASNTIC ROUTING RESULT: :::::::", route.name)
        if route.name == "creator":
            print(":::::::Orchestrator - CREATOR:::::::")
            return await self.orchestrator.creater(
                problem_statement=kwargs["problem_statement"],
                required_agents=kwargs["required_agents"],
                # group_id=kwargs["group_id"]
            )
        elif route.name == "destroyer":
            print(":::::::Orchestrator -  DESTROYER:::::::")
            return await self.orchestrator.deleter(
                agent_id=kwargs["required_agents"],
            )
        elif route.name == "summarizer":
            print(":::::::Orchestrator -  SUMMARIZER:::::::")
            return await self.orchestrator.summarize(
                query=kwargs["query"]
            )
        else:
            return "No route found."
    
semantic_router = SemanticRouter(Orchestrator())
# semantic_router.call_orchestrator_tool(problem_statement="create a new agent for me", required_agents=["agent1", "agent2"], group_id="group1")

# semantic_router.send_to_orchestrator_tool(semantic_router("create a calculator"))

# print(semantic_router("create a calculator").name)
