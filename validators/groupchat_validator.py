import bittensor as bt
import random
from base_validator import BaseValidator
from app_config import config
from utils import vectorize_apis,utils
from template.protocol import IsToolAlive, StreamPrompting, Dummy, GetToolList, InterpreterRequests,MinerInfo
from template.utils import call_openai,get_response_from_openai,fetch_ip
import asyncio
import torch
import random
import template
import aiohttp
import asyncio
from utils import utils
import json

miner_group_association = {}
global_miner_details = []

class GroupChatValidator(BaseValidator):
    def __init__(self, dendrite, config, subtensor, wallet: bt.wallet):
        super().__init__(dendrite, config, subtensor, wallet, timeout=60)
        bt.logging.info("GroupChat Validator initialized.")
        
    async def query_miner(self, metagraph, uid, syn):
        bt.logging.info(f"Querying miner {uid} with {syn}")
        return await self.dendrite([metagraph.axons[uid]], syn, deserialize=False, timeout=self.timeout)
    
    async def check_tool_alive(self, miner_tools_info, group_id):
        try:
            alive_tools_list = []
            for tool in miner_tools_info:
                syn = IsToolAlive(tool_id = tool['metadata']['toolId'])
                bt.logging.info(f"Checking if the tool is alive {tool} {tool['metadata']['uid']}, syn: {syn}, {self.metagraph.axons[tool['metadata']['uid']]}")
                responses = (await self.query_miner(self.metagraph, tool['metadata']['uid'], syn))[0]
                bt.logging.info(f"Alive Tools: {responses}")
                if responses.status is not None and responses.status['alive']:
                    alive_tools_list.append({
                        "groupId": group_id,
                        "agent_id": utils.generate_agent_reference_id(),
                        "tool_id": tool['metadata']['toolId'],
                        "minerId": tool['metadata']['uid'],
                        "status": "alive"
                    })
            bt.logging.info(f"Alive Tools: {alive_tools_list}")
            return alive_tools_list
        except Exception as e:
            print(f"An unexpected error occurred:::::check_tool_alive::::: {e}")

    async def get_res_from_open_ai(self, query, miner_tools_info):
        print(":::::::::::get_res_from_open_ai::::::::::::")
        print(":::::::::::query::::::::::::", query)
        print(":::::::::::miner_tools_info::::::::::::", miner_tools_info)

        prompt_lines = [
            'Query: {} Based on the descriptions below, which tools (by Tool ID) are capable of addressing the query? Provide the response as an array of "tool_id", "description" and "miner_id" in array of object and you have to send me array data nothing else.\n Tools available:'
        ]
        prompt_lines[0] = prompt_lines[0].format(query)
        for tool in miner_tools_info:
            description = tool.get('description', 'No description available.')
            tool_info = f"- Tool ID: {tool['id']}, Description: {description}, miner_id: {tool['metadata']['uid']}"
            prompt_lines.append(tool_info)
        prompt = '\n'.join(prompt_lines)
        openai_res = await get_response_from_openai(prompt, 0.65, "gpt-4")
        print("Recommended Tool IDs:", openai_res)
        return openai_res

        
    async def request_for_miner(self, payload: dict):
        global miner_group_association
        print("::::::::::::::miner_group_association::::::::::::::::::::", miner_group_association)
        tools_to_use = []
        data_to_send = []
        bt.logging.info(f"Received save_miner_info request. {payload}")
        for tool in payload['tools']:
            prompt = f"I have a query: {payload['problem_statement']} and I want to use {tool} to solve it."
            payload_for_text_embedding = {
                "account_id": config.dassi_vectorize_account_id,
                "chunks": [   
                    {
                        "id": "1",
                        "metadata": {
                            "context": prompt
                        }
                    },
                ]
            }
            bt.logging.info(f"Received save_miner_info request. {payload_for_text_embedding}")
            embedded_text = await vectorize_apis.convert_text_to_vector(payload_for_text_embedding)
            # bt.logging.info(f"Embedded Text: {embedded_text}")
            miner_tools_info = []
            if len(embedded_text['vectorizedChunks']):
                chunk = embedded_text['vectorizedChunks'][0]
                miner_tools_info = (await vectorize_apis.get_vector_from_db(chunk['vector']))['matches']['matches']
            bt.logging.info(f"::::::::::::::miner_tools_info::::::::::::::::::::. {miner_tools_info}")
            # check if the tool is alive
            alive_tools = await self.check_tool_alive(miner_tools_info, payload["group_id"])
            bt.logging.info(f"Alive Tools: {alive_tools}")
            
            # get the unique miner ids
            if alive_tools and len(alive_tools):
                random_alive_tool = random.choice(alive_tools)
                print(":::::::::::::: random_alive_tool::::::::::::::::::::", random_alive_tool)
                tools_to_use.append(random_alive_tool)
                data_to_send.append({
                    "groupId": random_alive_tool['groupId'],
                    "agent_id": random_alive_tool['agent_id'],
                })
        
        print("::::::::::::::tools_to_use::::::::::::::::::::", tools_to_use)
        self.add_object(payload['group_id'], tools_to_use)
        print("::::::::::::::miner_group_association::::::::::::::::::::", miner_group_association)
        return data_to_send

    async def create_global_agent_tool_association(self, data, agent_id):
        global global_agent_tool_association
        global_agent_tool_association = []
        generate_res_for_orchestrator = []
        print(":::::::::::::INSIDE_THE_create_global_agent_tool_association:::::::::")
        print(":::::::::::::data:::::::::", data)
        print('____________',type(data))
        payload_data = json.loads(data)
        print(":::::::::payload_data:::::::::",payload_data)
        print(":::::::::type:::::::::",type(payload_data))
        for item in payload_data:
            if not isinstance(item, dict):
                raise TypeError(f"Expected a dict, got {type(item)}")
            print(">>>>>>>>>>>>>>>>",item['tool_id'])
            global_agent_tool_association.append({
                "agent_id": agent_id,
                "tool_id": item['tool_id'],
                "miner_id": item['miner_id'],
            })
            generate_res_for_orchestrator.append(item.get('description'))
        return generate_res_for_orchestrator

    async def request_for_tools_listing(self, payload: dict):
        try:
            global miner_group_association
            print("::::::::::::::miner_group_association::::::::::::::::::::",
                  miner_group_association)
            print(":::::::Payload:::::::", payload)
            tools_to_use = []
            bt.logging.info(f"Received save_miner_info request. {payload}")
            prompt = f"I have a query: {payload['problem_statement']} and I want to use to solve it."
            payload_for_text_embedding = {
                "account_id": config.dassi_vectorize_account_id,
                "chunks": [
                    {
                        "id": "1",
                        "metadata": {
                            "context": prompt
                        }
                    },
                ]
            }
            bt.logging.info(
                f"Received save_miner_info request. {payload_for_text_embedding}")
            embedded_text = await vectorize_apis.convert_text_to_vector(payload_for_text_embedding)
            miner_tools_info = []
            if len(embedded_text['vectorizedChunks']):
                chunk = embedded_text['vectorizedChunks'][0]
                miner_tools_info = (await vectorize_apis.get_vector_from_db(chunk['vector']))['matches']['matches']
            bt.logging.info(
                f"::::::::::::::miner_tools_info::::::::::::::::::::. {miner_tools_info}")
            print("::::::::::::SEND_RESPONSE_TO_OPENAI:::::::::::::::")
            for tool in miner_tools_info:
                tool['description'] = "I'm a python developer and I can easily write a code in python whatever you gave to me"
            res = await self.get_res_from_open_ai(payload['problem_statement'],miner_tools_info)
            orchestrator_res = await self.create_global_agent_tool_association(res, payload['agent_id'])
            print("::::::::::::::::orchestrator_res::::::::::::::::::::", orchestrator_res)
            fetch_validator_ip = fetch_ip()
            bt.logging.info(f"Alive Tools: {res}")
            return {"ip": fetch_validator_ip, "tool_list": orchestrator_res}
        except Exception as e:
            print("::::request_for_tools_listing::::::::", e)
    
    def add_object(self, group_id, object_data):
        try:
            global miner_group_association
            if group_id in miner_group_association:
                miner_group_association[group_id].append(object_data)
            else:
                miner_group_association[group_id] = object_data
        except Exception as e:
            print("Error in add_object: ", e)
            
    def find_group_id(self, search_id):
        try:
            global miner_group_association
            for group_id, objects in miner_group_association.items():
                for obj in objects:
                    if obj["id"] == search_id:
                        return group_id
            return None
        except Exception as e:
            print("Error in find_group_id: ", e)
            return None
    
    def get_valid_miners_info(self):
        self.all_uids = [int(uid) for uid in self.metagraph.uids]
        return self.all_uids
    
    async def fetch_miner_details(self):
        for miner_id in self.get_valid_miners_info():
            syn = MinerInfo(uid=miner_id)
            bt.logging.info(f"Received get_miner_tool_list request. {syn}, miner_id: {miner_id}")
            miner_details = (await self.query_miner(self.metagraph, miner_id, syn))[0]
            miner_details['agent_id'] = utils.generate_agent_reference_id()
            global_miner_details.append(miner_details)
            bt.logging.info(f"Miner List: {miner_details}")
        return 

    async def save_miner_info(self, alive_tool_list, miner_id):
        """
        Save miner info request handler. This method handles the incoming requests and saves the miner info.
        """
        
        data_to_save = []
        for tool_details in alive_tool_list:
            print(":::::::::::::: In save miner info :::::::::::::::::::", tool_details)
            payload = {
                "account_id": config.dassi_vectorize_account_id,
                "chunks": [   
                    {
                        "id": "1",
                        "metadata": {
                            "context": tool_details['summary'],
                        }
                    },
                ]
            }
            bt.logging.info(f"Received save_miner_info request. {payload}")
            embedded_text = await vectorize_apis.convert_text_to_vector(payload)
            if len(embedded_text['vectorizedChunks']):
                for chunk in embedded_text['vectorizedChunks']:
                    bt.logging.info(f"Chunk: {chunk}")
                    data_to_save.append({"id": f"{miner_id}-{tool_details['toolId']}", "values": chunk['vector'], "metadata": {"name": tool_details['name'], "uid": miner_id, "toolId": tool_details['toolId']}})
                    
        print("::::::::::::::data_to_save::::::::::::::::::::", data_to_save) 
        res = await vectorize_apis.insert_vector_into_db(data_to_save)
        if(res):
            print("::::::::::::::Data saved successfully::::::::::::::::::::", res)

        
    async def get_miner_tool_list(self):
        """
        Get query request handler. This method handles the incoming requests and returns the response from the forward function.
        """
        for miner_id in self.get_valid_miners_info():
        # for miner_id in [16]:
            syn = GetToolList(is_tool_list=True, miner_id=miner_id)
            bt.logging.info(f"Received get_miner_tool_list request. {syn}, miner_id: {miner_id}")
            tool_list = (await self.query_miner(self.metagraph, miner_id, syn))[0]
            bt.logging.info(f"Tool List: {tool_list}")
            if len(tool_list.output.keys()):
                toolids = [f"{miner_id}-{tool['toolId']}" for tool in tool_list.output['key']]
                await vectorize_apis.delete_vector_from_db(toolids)
                alive_tool_list = []
                for tool in tool_list.output['key']:
                    # alive_tools = await webapp.validator.is_tool_alive(miner_id, tool['toolId'])
                    alive_status = (await self.query_miner(self.metagraph, miner_id, IsToolAlive(tool_id=tool['toolId'])))[0]
                    bt.logging.info(f"Alive Tools: {alive_status}")
                    if alive_status.status is not None and alive_status.status['alive']:
                        alive_tool_list.append(tool)
                await self.save_miner_info(alive_tool_list, miner_id)
    
    async def interpreter_response(self, response):
        bt.logging.info("interpreter_response", response)
        self.query_res = response
        bt.logging.info("interpreter_response: ", self.query_res)
        query_response = await self.send_res_to_group_chat()
        return query_response
    
    async def get_group_chat_query(self, data):
        """
        Get query request handler. This method handles the incoming requests and returns the response from the forward function.
        """
        global miner_group_association
        fetch_group_data = utils.get_object_by_group_and_agent(miner_group_association,data['agent']['groupId'],data['agent']['agent_id'])
        bt.logging.info(f"Received query request. {miner_group_association}, {fetch_group_data}")
        if fetch_group_data is None:
            return {"message": "Agent not found"}
        bt.logging.info(f"Received query request. {data}")
        syn = InterpreterRequests(query=data['query'], miner_id=int(fetch_group_data['minerId']), tool_id=fetch_group_data['tool_id'])
        response = await self.forward(syn, fetch_group_data['minerId'])
        print("::::::::::::::::::::",miner_group_association, response)
        return response
    
    async def send_res_to_group_chat(self):
        try:
            while self.query_res["key"] == "INTERPRETER_PROCESSING":
                # Wait until the key becomes "INTEPRETR_PROGESS"
                print("::::::::WAITING_FOR_INTERPRETER_RESPONSE::::::::::")
                await asyncio.sleep(10)
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
            
    async def forward(self, syn: InterpreterRequests, miner_id: int):
        """
        The forward function is called by the validator every time step.

        It is responsible for querying the network and scoring the responses.

        Args:
            self (:obj:`bittensor.neuron.Neuron`): The neuron object which contains all the necessary state for the validator.

        """
        print("::::::::::::::SELF.QUERY::::::::::::::::::", syn)
        try:
            responses = await self.query_miner(self.metagraph, miner_id, syn)
            res_string  = responses[0]
            bt.logging.info("::::::::::::::: res_string:::::::::::::::::", res_string)
            if len(res_string.output.keys()) and res_string.output['key'] == 'INTERPRETER_PROCESSING':
                self.query_res = res_string.output
                await self.send_res_to_group_chat()
                return
            else:
                return responses
        except Exception as e:
            print(":::::Error while sending dendrite:::::::",e)
            
    
    async def remove_agent_from_global_object(self, all_agents_detail, group_id, agent_id):
        try:
            removed_objects = []
            if group_id in all_agents_detail:
                group_data = all_agents_detail[group_id]
                new_group_data = []
                for obj in group_data:
                    if obj['agent_id'] == agent_id:
                        removed_objects.append(obj)
                    else:
                        new_group_data.append(obj)
                all_agents_detail[group_id] = new_group_data
            else:
                return {"message": f"{agent_id} not found in this {group_id} group!"}
            return all_agents_detail
        except Exception as e:
            print("Error in remove_agent_from_global_object: ", e)

    async def remove_agent(self, data):
        try:
            global miner_group_association
            all_agents_detail = self.remove_agent_from_global_object(
                miner_group_association, data['group_id'], data['agent_id'])
            miner_group_association = all_agents_detail

            bt.logging.info(f"miner_group_association::::: {miner_group_association}")
            return {"message": "Agent removed!"}
        except Exception as e:
            bt.logging.info(f"error in remove_agent::::: {e}")
            return {"message": "Agent not removing!"}
    
    async def score_responses(
        self,
        query_responses: list[tuple[int, str]],  # [(uid, response)]
        uid_to_question: dict[int, str],  # uid -> prompt
        metagraph: bt.metagraph,
    ) -> tuple[torch.Tensor, dict[int, float], dict]:
        bt.logging.info(f"Scoring text responses", len(metagraph.hotkeys))
        scores = torch.zeros(len(metagraph.hotkeys))
        uid_scores_dict = {}
        response_tasks = []

        # Decide to score all UIDs this round based on a chance
        will_score_all = self.should_i_score()

        for uid, response in query_responses:
            # self.wandb_data["responses"][uid] = response
            if will_score_all and response:
                prompt = uid_to_question[uid]
                response_tasks.append((uid, self.call_api(prompt, self.provider)))

        api_responses = await asyncio.gather(*[task for _, task in response_tasks])

        scoring_tasks = []
        for (uid, _), api_answer in zip(response_tasks, api_responses):
            if api_answer:
                response = next(res for u, res in query_responses if u == uid)  # Find the matching response
                task = template.reward.api_score(api_answer, response, self.weight)
                scoring_tasks.append((uid, task))

        scored_responses = await asyncio.gather(*[task for _, task in scoring_tasks])

        bt.logging.debug(f"scored responses = {scored_responses}")
        for (uid, _), scored_response in zip(scoring_tasks, scored_responses):
            if scored_response is not None:
                scores[uid] = scored_response
                uid_scores_dict[uid] = scored_response
            else:
                scores[uid] = 0
                uid_scores_dict[uid] = 0
            # self.wandb_data["scores"][uid] = score

        if uid_scores_dict != {}:
            bt.logging.info(f"text_scores is {uid_scores_dict}")
        return scores, uid_scores_dict, self.wandb_data
    
    async def start_query(self, available_uids, metagraph) -> tuple[list, dict]:
        query_tasks = []
        uid_to_question = {}
        # Randomly choose the provider based on specified probabilities
        providers = ["OpenAI"] * 95 + ["Anthropic"] * 5
        self.provider = random.choice(providers)

        if self.provider == "Anthropic":
            # bedrock models = ["anthropic.claude-v2:1", "anthropic.claude-instant-v1", "anthropic.claude-v1", "anthropic.claude-v2"]
            # claude models = ["claude-2.1", "claude-2.0", "claude-instant-1.2"]
            self.model = "anthropic.claude-v2:1"
        elif self.provider == "OpenAI":
            self.model = "gpt-4-1106-preview"

        for uid in available_uids:
            prompt = await self.get_question(len(available_uids))
            uid_to_question[uid] = prompt
            messages = [{'role': 'user', 'content': prompt}]
            syn = StreamPrompting(messages=messages, model=self.model, seed=self.seed, max_tokens=self.max_tokens, temperature=self.temperature, provider=self.provider, top_p=self.top_p, top_k=self.top_k)
            bt.logging.info(
                f"Sending {syn.model} {self.query_type} request to uid: {uid}, "
                f"timeout {self.timeout}: {syn.messages[0]['content']}"
            )
            task = self.query_miner(metagraph, uid, syn)
            query_tasks.append(task)
            self.wandb_data["prompts"][uid] = prompt

        query_responses = await asyncio.gather(*query_tasks)
        return query_responses, uid_to_question


        