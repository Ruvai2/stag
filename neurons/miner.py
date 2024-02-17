# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# TODO(developer): Set your name
# Copyright © 2023 <your name>

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import time
import typing
import bittensor as bt
import aiohttp
import requests
# Bittensor Miner Template:
import template

# import base miner class which takes care of most of the boilerplate
from template.base.miner import BaseMinerNeuron
from utils import request_handler
# from tools.open_ai import open_ai_main
from tools.interpreter_agent import interpreter_tool
# from tools.interpreter_agent import self_operating_computer

miner_tools = {
        "1003": 8000,
        "1004" : 8000 
    }

BASE_URL = "http://127.0.0.1:"    

class Miner(BaseMinerNeuron):
    """
    Your miner neuron class. You should use this class to define your miner's behavior. In particular, you should replace the forward function with your own logic. You may also want to override the blacklist and priority functions according to your needs.

    This class inherits from the BaseMinerNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a miner such as blacklisting unrecognized hotkeys, prioritizing requests based on stake, and forwarding requests to the forward function. If you need to define custom
    """

    def __init__(self, config=None):
        super(Miner, self).__init__(config=config)

        # TODO(developer): Anything specific to your use case you can do here

    async def forward(
        self, synapse: template.protocol.InterpreterRequests
    ):
        try:
            print(":::::::inside the miner:::::::::::")
            if synapse.query['request_type'] == "CHECK_TOOL_ALIVE":
                interpreter_tool_response = self.interprter_agent_request({"status": synapse.query['status'], "toolId": synapse.query['toolId'], "minerId": synapse.query['minerId']})
                synapse.agent_output = interpreter_tool_response
            elif synapse.query['request_type'] == "PING_MINER":
                synapse.agent_output = {"message": "PONG"}
            elif synapse.query['request_type'] == "QUERY_MINER":
                print("::::::synapse.query::::::",synapse.query)
                interpreter_tool_response = self.interprter_agent_request({"query": synapse.query['query'], "status": synapse.query['agent']['alive'], "toolId": synapse.query['agent']['toolId']})
                synapse.agent_output = interpreter_tool_response
            return synapse
        except Exception as e:
            print(f"Error:::::::forward::::::::::::::;", e)
        
    def interprter_agent_request(self, synapse):
        try:
            print("::::::::::::::INSIDE_THE_interprter_agent_request_METHOD::::::::::::::::::", synapse)
            print("==========",synapse["status"])
            if synapse['status']:
                return self.isAlive(synapse['toolId'], synapse['minerId'])
            else:    
                return self.main(synapse['toolId'], synapse['query'])
        except Exception as e:
            print(f"Error::::::::interprter_agent_request::::::;", e)

    def isAlive(self,toolId, minerId):
        try:
            print("::::::::::::::INSIDE_THE_isAlivet_METHOD::::::::::::::::::", toolId)
            portId = miner_tools[toolId]
            URL = BASE_URL + str(portId) + '/api/alive'
            print("URL:::::::", URL)
            check_tool_status = request_handler.request_handler_get(URL)
            return {'alive': check_tool_status['alive'], 'toolId': toolId, 'minerId': minerId}
        except Exception as e: 
            print('Something went wrong in isAlive method', e) 
    # print(check_tool_status['alive'])

    def main(self, model, query, summary=False):
        try:
            print("::::::::MODEL::::::::::::", model)
            if model == '1004':
                print("::::::::::::::::MAKING_REQUEST_TO_INTERPRETER_TOOL:::::::::::::::")
                interpreter_tool(query)
                return {'key': 'INTERPRETER_PROCESSING'}
            else :
                return {'key': 'Model does not exist'}
        except Exception as e: 
            print(f"Error::::::::main::::::;", e)
        
    
    async def blacklist(
        self, synapse: template.protocol.InterpreterRequests
    ) -> typing.Tuple[bool, str]:
        """
        Determines whether an incoming request should be blacklisted and thus ignored. Your implementation should
        define the logic for blacklisting requests based on your needs and desired security parameters.

        Blacklist runs before the synapse data has been deserialized (i.e. before synapse.data is available).
        The synapse is instead contructed via the headers of the request. It is important to blacklist
        requests before they are deserialized to avoid wasting resources on requests that will be ignored.

        Args:
            synapse (template.protocol.Dummy): A synapse object constructed from the headers of the incoming request.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating whether the synapse's hotkey is blacklisted,
                            and a string providing the reason for the decision.

        This function is a security measure to prevent resource wastage on undesired requests. It should be enhanced
        to include checks against the metagraph for entity registration, validator status, and sufficient stake
        before deserialization of synapse data to minimize processing overhead.

        Example blacklist logic:
        - Reject if the hotkey is not a registered entity within the metagraph.
        - Consider blacklisting entities that are not validators or have insufficient stake.

        In practice it would be wise to blacklist requests from entities that are not validators, or do not have
        enough stake. This can be checked via metagraph.S and metagraph.validator_permit. You can always attain
        the uid of the sender via a metagraph.hotkeys.index( synapse.dendrite.hotkey ) call.

        Otherwise, allow the request to be processed further.
        """
        # TODO(developer): Define how miners should blacklist requests.
        if synapse.dendrite.hotkey not in self.metagraph.hotkeys:
            # Ignore requests from unrecognized entities.
            bt.logging.trace(
                f"Blacklisting unrecognized hotkey {synapse.dendrite.hotkey}"
            )
            return True, "Unrecognized hotkey"

        bt.logging.trace(
            f"Not Blacklisting recognized hotkey {synapse.dendrite.hotkey}"
        )
        return False, "Hotkey recognized!"

    async def priority(self, synapse: template.protocol.InterpreterRequests) -> float:
        """
        The priority function determines the order in which requests are handled. More valuable or higher-priority
        requests are processed before others. You should design your own priority mechanism with care.

        This implementation assigns priority to incoming requests based on the calling entity's stake in the metagraph.

        Args:
            synapse (template.protocol.Dummy): The synapse object that contains metadata about the incoming request.

        Returns:
            float: A priority score derived from the stake of the calling entity.

        Miners may recieve messages from multiple entities at once. This function determines which request should be
        processed first. Higher values indicate that the request should be processed first. Lower values indicate
        that the request should be processed later.

        Example priority logic:
        - A higher stake results in a higher priority value.
        """
        # TODO(developer): Define how miners should prioritize requests.
        caller_uid = self.metagraph.hotkeys.index(
            synapse.dendrite.hotkey
        )  # Get the caller index.
        prirority = float(
            self.metagraph.S[caller_uid]
        )  # Return the stake as the priority.
        bt.logging.trace(
            f"Prioritizing {synapse.dendrite.hotkey} with value: ", prirority
        )
        return prirority


# This is the main function, which runs the miner.
if __name__ == "__main__":
    with Miner() as miner:
        while True:
            bt.logging.info("Miner running...", time.time())
            time.sleep(5)




# TODO(developer): Replace with actual implementation logic.
            # print(":::::::::::::::::synapse.dummy_input:::::::::::::::: ", synapse.dummy_input)
            # api_url = "https://openai.ru9.workers.dev/v1/chat/completions"
            # headers = {
            #            "Content-Type": "application/json" }
            # payload = {
            #     "model": "gpt-4",
            #     "messages": [
            #         {"role": "system", "content": """You are a python project planner who when given a Input you will
            #         - First Read and understand the request to see if its relevant to python execution
            #         - Understand the request data and create a plan for the developer
            #         - If its not related to plan anything just say "Null" or give a reply "Null" 
            #         - Once you think the task as completed, Give response 'End_Conversation' and nothing else.
            #         - If you fully satisfied with the previous response, then just say "End_Conversation" """},
            #         {"role": "user", "content": synapse.dummy_input},
            #     ],
            # }
            # bt.logging.info('Payload for GPT: ', payload)
            # bt.logging.info(f"Synapse: {synapse}")
            # async with aiohttp.ClientSession() as session:
            #     async with session.post(api_url, headers=headers, json=payload) as response:
            #         if response.status == 200:
            #             data_response  = await response.json()
            #             print("::::::::::::data")
            #             synapse.dummy_output = data_response["choices"][0]["message"]["content"]
            #         else:
            #             # Handle errors, you might want to log or raise an exception
            #             print(f"Error: {response.status}, {await response.text()}")