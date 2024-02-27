import bittensor as bt
import random
from base_validator import BaseValidator
from app_config import config
from utils import vectorize_apis,utils
from utils.tool_details import details
from template.protocol import IsToolAlive, StreamPrompting, Dummy, GetToolList, InterpreterRequests,MinerInfo, RunToolRequest
from template.utils import call_openai
import asyncio
import torch
import random
import template
import aiohttp
import asyncio
from utils import utils

miner_group_association = {}
global_miner_details = [{   
    "agentId": "2dfa2ec9-eeb9-4d10-9fc6-9a948b8915b1",
    "minerId": 16,
    "ram_details": {
        "total_ram_mb": 16384.0,
        "available_ram_mb": 2780.812,
        "utilized_ram_percent": 83.0
    },
    "cpu_info": {
        "num_logical_cores": 8,
        "num_physical_cores": 8,
        "cpu_percent_each_core": [
            41.5,
            40.4,
            35.8,
            37.5,
            52.0,
            42.4,
            38.4,
            32.3
        ]
    },
    "gpu_info": []
},{   
    "agentId": "2dfa2ec9-eeb9-4d10-9fc6-9a948b8915b6",
    "minerId": 17,
    "ram_details": {
        "total_ram_mb": 16384.0,
        "available_ram_mb": 2780.812,
        "utilized_ram_percent": 83.0
    },
    "cpu_info": {
        "num_logical_cores": 8,
        "num_physical_cores": 8,
        "cpu_percent_each_core": [
            41.5,
            40.4,
            35.8,
            37.5,
            52.0,
            42.4,
            38.4,
            32.3
        ]
    },
    "gpu_info": []
},
]

user_group_conversation_thread = [] # [{user, group}, {user, group}]

global_agent_tool_association = [{
    "agent_id": "2dfa2ec9-eeb9-4d10-9fc6-9a948b8915b1",
    "tool_id": 1001,
    "miner_id": 16
}]

class GroupChatValidator(BaseValidator):
    def __init__(self, dendrite, config, subtensor, wallet: bt.wallet):
        super().__init__(dendrite, config, subtensor, wallet, timeout=60)
        bt.logging.info("GroupChat Validator initialized.")
        
    async def query_miner(self, metagraph, miner_uid, syn):
        bt.logging.info(f"Querying miner {miner_uid} with {syn}")
        return await self.dendrite([metagraph.axons[miner_uid]], syn, deserialize=False, timeout=self.timeout)
    
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

    async def get_res_from_open_ai(miner_tools_info, query):
        prompt = """  """
        openai_res = await call_openai([{'role': "user", 'content': prompt}], 0.65, "gpt-3.5-turbo")
        
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
            print("::::::::::::SEND_RESPONSE_TO_OPENAI:::::::::::::::")
            await self.get_res_from_open_ai(miner_tools_info)
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

    async def request_for_tools_listing(self, payload: dict):
        global miner_group_association
        print("::::::::::::::miner_group_association::::::::::::::::::::", miner_group_association)

        #  TODO: will have to hit shivang api.......

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
            print("::::::::::::SEND_RESPONSE_TO_OPENAI:::::::::::::::")
            await self.get_res_from_open_ai(miner_tools_info)
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
    
    def find_tool_id_by_agent_id(self, agent_id):
        try:
            for obj in global_agent_tool_association:
                if obj['agent_id'] == agent_id:
                    return obj['tool_id'], obj['miner_id']
            return None
        except Exception as e:
            print("Error in find_tool_id_by_agent_id: ", e)
            return None
       
    # Define a function to find the miner and check for available resources
    def find_miner_and_check_resources(self, miner_details, miner_id, tool_benchmark):
        # Search for the miner
        miner_data = next((miner for miner in miner_details if miner["minerId"] == miner_id), None)
        
        if miner_data:
            # Check if the miner has enough available RAM to run the tool
            if miner_data["ram_details"]["available_ram_mb"] >= tool_benchmark["ram"]:
                # Check if a GPU is required and if the miner has it
                if tool_benchmark["gpu"] is None or (tool_benchmark["gpu"] and len(miner_data["gpu_info"]) > 0):
                    return True, "Miner has enough resources to run the tool."
                else:
                    return False, "Miner does not have the required GPU."
            else:
                return False, "Miner does not have enough available RAM."
        else:
            return False, "Miner not found."
        
    def get_tool_details_with_tool_id(self, tool_details, tool_id):
        try:
            for tool in tool_details:
                if tool['toolId'] == tool_id:
                    return tool
            return None
        except Exception as e:
            print("Error in get_tool_details_with_tool_id: ", e)
            return None
        
    async def run_tool(self, data):
        global global_miner_details
        tool_id, miner_id = self.find_tool_id_by_agent_id(data['agent_id'])
        bt.logging.info(f"Tool ID: {tool_id}, Miner ID: {miner_id}")
        status, message = self.find_miner_and_check_resources(global_miner_details, miner_id, { "cup": 1, "gpu": None, "ram": 1024,})
        bt.logging.info(f"Status: {status}, Message: {message}")
        if(status):
            tool_details = await vectorize_apis.get_vector_from_db(tool_id)
            tool = self.get_tool_details_with_tool_id(tool_details, tool_id)
            bt.logging.info(f"Tool Details: {tool}")
            syn = RunToolRequest(tool_id=tool['toolId'], run_commands=tool['runCommands'], docker_file=tool['dockerFile'])
            response = (await self.query_miner(self.metagraph, miner_id, syn))[0]
            if response['success']:
                alive_tool = self.check_tool_alive([tool], data['group_id'])[0]
                status_of_tool = True if alive_tool['alive'] else False
                if status_of_tool:
                    print({"message": "Tool is running!"})
                else:
                    print({"message": "Tool is not running!"})
        else: 
            return None
    
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


        