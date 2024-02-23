import asyncio
import websockets

async def hello(text):
    print(":::::::WORKING_TILL_NOW:::::::")
    uri = "ws://localhost:8001/ws"
    async with websockets.connect(uri) as websocket:
        await websocket.send(text)  # Assuming you want to send a string, not a set inside curly braces
        response = await websocket.recv()
        print(f"Received: {response}")

# Define a function to start the event loop and run the WebSocket client
async def run_websocket_client(text):
    print(":::::::")
    await hello(text)

def main(text = None):
    asyncio.run(run_websocket_client(text))