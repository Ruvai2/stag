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

# Bittensor Miner Template:
import template

# import base miner class which takes care of most of the boilerplate
from template.base.miner import BaseMinerNeuron


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
        self, synapse: template.protocol.Dummy
    ) -> template.protocol.Dummy:
        try:
            async def call_openai(input_data,persona):
                try:
                    print("::::::::::::call_openai::::::::::::::",input_data)
                    query = input_data["query"]
                    agent = input_data["agent"]
                    open_api_key = "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"
                    api_url = "https://openai.ru9.workers.dev/v1/chat/completions"
                    headers = { "Content-Type": "application/json"}
                    payload = {
                        "model" : "gpt-3.5-turbo",
                        "messages": [
                            {"role": "system",
                            "content": persona},
                            {"role": "user", "content": query},
                        ],
                    }
                    bt.logging.info('Payload for GPT: ', payload)
                    # bt.logging.info(f"Synapse: {synapse}")
                    async with aiohttp.ClientSession() as session:
                        async with session.post(api_url, headers=headers, json=payload) as response:
                            if response.status == 200:
                                # return (await response.json())["choices"][0]["message"]["content"]
                                result_json = await response.json()
                                content = result_json["choices"][0]["message"]["content"]
                                return content
                            else:
                                # Handle errors, you might want to log or raise an exception
                                print(f"Error: {response.status}, {await response.text()}")
                                return None
                except Exception as e:
                    print(f"Error: {e}")
                    return None
            async def miner_1():
                print(":::::::::::::::miner_1::::::::::::::::::")
                persona = """You are a python project planner who when given a Input you will
                            - First Read and understand the request to see if its relevant to python execution
                            - Understand the request data and create a plan for the developer
                            - If its not related to plan anything just say "Null" or give a reply "Null" 
                            - Once you think the task as completed, Give response 'End_Conversation' and nothing else.
                            - If you fully satisfied with the previous response, then just say "End_Conversation" """
                return await call_openai(synapse.dummy_input,persona)

            async def miner_2():
                print(":::::::::::::::miner_2::::::::::::::::::")
                persona = """You are a python developer who when given a Input you will.
                            - First Read and understand the request to see if its relevant to python execution.
                            - You'll not execute anything if there is no plan or clear instruction to write and provide a code.
                            - If its not related to python or code execution just say "Null" or give a reply "Null" 
                            - Once you think the task as completed, Give response 'End_Conversation' and nothing else.
                            - If you fully satisfied with the previous response, then just say "End_Conversation" """
                return await call_openai(synapse.dummy_input,persona)

            async def miner_3():
                print(":::::::::::::::miner_3::::::::::::::::::")
                persona = """You are a python tester who when given a Input you will
                            - First Read and understand the request to see if its relevant to python execution
                            - Understand the python code and plan to test the code
                            - You try to compile the code by understanding and provide any errors in the code
                            - If its not related to test the python code just say "Null" or give a reply "Null" 
                            - Once you think the task as completed, Give response 'End_Conversation' and nothing else.
                            - If you fully satisfied with the previous response, then just say "End_Conversation" """
                return await call_openai(synapse.dummy_input,persona)

            async def default():
                print(":::::::::::::::default::::::::::::::::::")
                persona = """You are a powerfull tool, just say "End_Conversation" """
                return None
            print(":::::synapse.dummy_input:::::",synapse.dummy_input)
            switch_dict = {1001: miner_1, 1002: miner_2, 1003: miner_3, }
            case_function = switch_dict.get(synapse.dummy_input["agent"]["tool"], default)
            result = await case_function()
            # result = await call_openai(synapse.dummy_input)
            print("::::result:::::",result)
            synapse.dummy_output = result
            return synapse
        except Exception as e:
            print(f"Error: {e}")

    async def blacklist(
        self, synapse: template.protocol.Dummy
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

    async def priority(self, synapse: template.protocol.Dummy) -> float:
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
