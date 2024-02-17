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

import bittensor as bt
import aiohttp
import asyncio
from template.protocol import InterpreterRequests, CheckToolAlive
from template.validator.reward import get_rewards
# from template.utils.uids import get_random_uids
from template.protocol import PingMiner


async def send_res_to_group_chat(self):
    try:
        print("::::::::send_res_to_group_chat::::::",self.query)

        while self.query_res["key"] == "INTERPRETER_PROCESSING":
            # Wait until the key becomes "INTEPRETR_PROGESS"
            print("::::::::WAITING_FOR_INTERPRETER_RESPONSE::::::::::")
            await asyncio.sleep(1)
        async with aiohttp.ClientSession() as session:
            async with session.post("http://localhost:3000/api/send_update_after_processing", headers={"Content-Type": "application/json"}, json={"key": self.query_res["key"]}) as response:
                if response.status == 200:
                    print("Successfully called the group chat:::::")
                else:
                    print(f"Error: {response.status}, {await response.text()}")
                    print("Failed to call the group chat:::::")
        return "Successfully called the group chat:::::"
    except Exception as e:
        print(":::::Error send_res_to_group_chat:::::::", e)

async def forward(self):
    # print("::::::::::::::SELF.QUERY::::::::::::::::::", self.query)
    
    # {'query': 'give me the sum of two numbers', 'status': False, 'minerId': '1001'}
    """
    The forward function is called by the validator every time step.

    It is responsible for querying the network and scoring the responses.

    Args:
        self (:obj:`bittensor.neuron.Neuron`): The neuron object which contains all the necessary state for the validator.

    """
    # TODO(developer): Define how the validator selects a miner to query, how often, etc.
    # get_random_uids is an example method, but you can replace it with your own.
    # miner_uids = get_random_uids(self, k=self.config.neuron.sample_size)

    # The dendrite client queries the network.
    print("::::::::::::::SELF.QUERY::::::::::::::::::", type(self.query))
    print("::::::::::::::SELF.QUERY::::::::::::::::::", self.query)
    # self.problem_statement = "Create a program of Addition in python."
    try:
        responses = self.dendrite.query(
            axons=[self.metagraph.axons[11]],
            synapse=InterpreterRequests(query=self.query),
            deserialize=True,
        )
        return responses
    except Exception as e:
        print(":::::Error while sending dendrite:::::::",e)
    # print(":::::::::::responses:::::::::",responses)
    # Log the results for monitoring purposes.
    # bt.logging.info(f"Received responses: {responses}")

    # TODO(developer): Define how the validator scores responses.
    # Adjust the scores based on responses from miners.
    # rewards = get_rewards(self, query=self.step, responses=responses)

    # bt.logging.info(f"Scored responses: {rewards}")
    # Update the scores based on the rewards. You may want to define your own update_scores function for custom behavior.
    # self.update_scores(rewards, 11)
