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

# Bittensor
import bittensor as bt

# Bittensor Validator Template:
import template
from template.validator import forward

# import base validator class which takes care of most of the boilerplate
from template.base.validator import BaseValidatorNeuron
from template.protocol import QueryMiner, CheckMinerStatus


class Validator(BaseValidatorNeuron):
    """
    Your validator neuron class. You should use this class to define your validator's behavior. In particular, you should replace the forward function with your own logic.

    This class inherits from the BaseValidatorNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a validator such as keeping a moving average of the scores of the miners and using them to set weights at the end of each epoch. Additionally, the scores are reset for new hotkeys at the end of each epoch.
    """

    def __init__(self, config=None):
        super(Validator, self).__init__(config=config)

        bt.logging.info("load_state()")
        self.load_state()
        self.model = "gpt-4"
        self.agent_ids = [1000,1001]
        self.miners = [
            {
                "name": "Planner",
                "id": 1000,
                "uuid": "597ccbc9-3126-4a10-8225-bed862f7fc79",
                "status": "ACTIVE",
                "url": "https://api.openai.com/v1/chat/completions",
                "instructions": """You are a python project planner who when given a Input you will
    - First Read and understand the request to see if its relevant to python execution
    - Understand the request data and create a plan for the developer
    - If its not related to plan anything just say "Null" or give a reply "Null" 
    - Once you think the task as completed, Give response 'End_Conversation' and nothing else.
    - If you fully satisfied with the previous response, then just say "End_Conversation" """,
                "model": self.model,
                "type": "AGENT",
                "assistant_id": "asst_QvpejJxdxTXoGlNF9wPeRIs2",
                "thread_id": "thread_g85L4ptn2DmxL1WHVT59vAB3",
                "current_thread_ids": [],
                "graph_details": [],
                "response_score_list": [],
            },
            {
                "name": "Developer",
                "id": 1001,
                "uuid": "ee6f2afc-590f-4f03-bbd5-c86ff52c8cd6",
                "status": "ACTIVE",
                "url": "https://api.openai.com/v1/chat/completions",
                "instructions": """You are a python developer who when given a Input you will.
    - First Read and understand the request to see if its relevant to python execution.
    - You'll not execute anything if there is no plan or clear instruction to write and provide a code.
    - If its not related to python or code execution just say "Null" or give a reply "Null" 
    - Once you think the task as completed, Give response 'End_Conversation' and nothing else.
    - If you fully satisfied with the previous response, then just say "End_Conversation" """,
                "name": "Developer",
                "model": self.model,
                "type": "AGENT",
                "assistant_id": "asst_cCCxeo7wgoy8dqJVa0pgrJx9",
                "thread_id": "thread_ecimSSij0p2UkfnExpTE5lyC",
                "current_thread_ids": [],
                "graph_details": [],
                "response_score_list": [],
            },
            {
                "name": "Tester",
                "id": 1002,
                "uuid": "06e89677-2c5b-4b61-bf54-4cd3a9c432d4",
                "status": "ACTIVE",
                "url": "https://api.openai.com/v1/chat/completions",
                "instructions": """You are a python tester who when given a Input you will
    - First Read and understand the request to see if its relevant to python execution
    - Understand the python code and plan to test the code
    - You try to compile the code by understanding and provide any errors in the code
    - If its not related to test the python code just say "Null" or give a reply "Null" 
    - Once you think the task as completed, Give response 'End_Conversation' and nothing else.
    - If you fully satisfied with the previous response, then just say "End_Conversation" """,
                "model": self.model,
                "type": "AGENT",
                "assistant_id": "asst_iBxCOCkfLUsYSGEgTPMQxQSG",
                "thread_id": "thread_lUep0mQKbOw3ra2LgzCylQtz",
                "current_thread_ids": [],
                "graph_details": [],
                "response_score_list": [],
            },
        ]

        # TODO(developer): Anything specific to your use case you can do here

    def generate_query(self, problem_statement):
        query = {
            "problem_statement": problem_statement
        }  # Replace with actual query generation logic
        return query
    async def fetch_agents_details(self, agent_ids):
        print("fetch_agents_details::::::agent_ids", agent_ids)
        result_agents = []
        for agent_id in agent_ids:
            for agent_detail in self.miners:
                if agent_detail.get("id") == agent_id:
                    result_agents.append(agent_detail)
                    break
        return result_agents

    async def query_miners(self, query, miner_details):
        responses = []
        for miner in miner_details:
            # Check if the miner is active by sending a request to the miner.
            check_response = self.dendrite.query(
                axons=[self.neuron.metagraph.axons[miner["id"]]],
                synapse=CheckMinerStatus(status=True),
                deserialize=True,
            )
            is_active = check_response[0].get("active", False)
            if is_active:
                # Miner is active, send the query.
                response = self.dendrite.query(
                    axons=[self.neuron.metagraph.axons[miner["id"]]],
                    synapse=QueryMiner(query, status=True),
                    deserialize=True,
                )
                responses.extend(response)

        return responses

    def process_responses(self, responses, problem_statement):
        # Incorporate the problem_statement and miner responses to generate a score
        for response in responses:
            score = self.generate_score(problem_statement, response)
            # Handle the score as needed

    def generate_score(self, problem_statement, response):
        # Your logic for generating a score based on problem_statement and miner response goes here
        score = 0  # Replace with actual score generation logic
        return score

    async def forward(self):
        """
        Validator forward pass. Consists of:
        - Generating the query
        - Querying the miners
        - Getting the responses
        - Rewarding the miners
        - Updating the scores
        """
        problem_statement = "Create a calculator program in python."  # Replace with your actual problem statement
        query = self.generate_query(problem_statement)
        miner_details = self.fetch_agents_details(self.agent_ids)
        responses = await self.query_miners(query, miner_details)

        # self.process_responses(responses, problem_statement)
        # self.update_scores(responses)
        # rewards = self.calculate_rewards(responses)
        # self.reward_miners(rewards)
        # TODO(developer): Rewrite this function based on your protocol definition.
        return await forward(self)


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    with Validator() as validator:
        while True:
            bt.logging.info("Validator running...", time.time())
            time.sleep(5)
