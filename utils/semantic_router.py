from semantic_router import Route
from semantic_router.layer import RouteLayer
import os
import bittensor as bt

os.environ["OPENAI_API_KEY"] = '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'
class SemanticRouter:
    def __init__(self):
        pass
    
    @staticmethod
    def create_route(name, utterances):
        return Route(name=name, utterances=utterances)
    
    @staticmethod
    async def find_best_route(problem_statement, dynamic_routes):
        try:
            print(":::::::::::: Finding best route ::::::::::::")
            
            routes = [SemanticRouter.create_route(route['id'], route['payload']['conversationStarters']) for route in dynamic_routes]
            router_layer = RouteLayer(routes=routes)
        
            best_route = await router_layer(problem_statement)  # This line is hypothetical and assumes router_layer supports async
            print(f"best route for problem statement: {best_route}")
            
            return {"id": best_route.name}
        except Exception as e:
            print(f"An error occurred while finding the best route: {e}")
            return {"error": "An error occurred while processing your request."}
