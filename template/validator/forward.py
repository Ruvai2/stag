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
from template.protocol import Dummy
from template.validator.reward import get_rewards
# from template.utils.uids import get_random_uids


async def forward(self):
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
    print("_______self.query: ", self.query, self.agent)
    self.problem_statement = "Create a program of Addition in python."
    print("____________________FORWARD_METHOD____________")
    print("::::self.agent:::::",self.agent)
    responses = self.dendrite.query(
        # Send the query to selected miner axons in the network.
        # axons=[self.metagraph.axons[uid] for uid in miner_uids],
        axons=[self.metagraph.axons[self.agent["uid"]]],
        # Construct a dummy query. This simply contains a single integer.
        synapse=Dummy(dummy_input={"query":self.query, "agent":self.agent}),
        # All responses have the deserialize function called on them before returning.
        # You are encouraged to define your own deserialization function.
        deserialize=True,
    )
    print(":::::::::::RESPONSE::::FORWARD::::::::::::",responses[0])
    print(" :::::::::::RESPONSE::::FORWARD::::::::::::",type(responses))
    res_string  = responses[0]
    if res_string == None:  res_string = "NULL"
    async with aiohttp.ClientSession() as session:
                        async with session.post("http://localhost:8000/api/send_update_after_processing",headers = { "Content-Type": "application/json"}, json={"key" : res_string}) as response:
                            if response.status == 200:
                                print("Successfully called the group chat:::::")
                            else:
                                # Handle errors, you might want to log or raise an exception
                                print(f"Error: {response.status}, {await response.text()}")
                                print("Failed to called the group chat:::::")
    # Log the results for monitoring purposes.
    bt.logging.info(f"Received responses: {responses}")

    # TODO(developer): Define how the validator scores responses.
    # Adjust the scores based on responses from miners.
    rewards = get_rewards(self, query=self.step, responses=responses)

    bt.logging.info(f"Scored responses: {rewards}")
    # Update the scores based on the rewards. You may want to define your own update_scores function for custom behavior.
    self.update_scores(rewards, self.agent["uid"])
