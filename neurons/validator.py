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

from aiohttp import web
import aiohttp
import asyncio
from template.utils.misc import convert_text_to_vector, insert_vector_into_db, get_vector_from_db, delete_vector_from_db

# Bittensor Validator Template:
import template
from template.validator import forward,send_res_to_group_chat
from template.utils import util
# import base validator class which takes care of most of the boilerplate
from template.base.validator import BaseValidatorNeuron
from template.protocol import PingMiner
import random
from config import config

global_object = {}

class Validator(BaseValidatorNeuron):
    """
    Your validator neuron class. You should use this class to define your validator's behavior. In particular, you should replace the forward function with your own logic.

    This class inherits from the BaseValidatorNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a validator such as keeping a moving average of the scores of the miners and using them to set weights at the end of each epoch. Additionally, the scores are reset for new hotkeys at the end of each epoch.
    """

    def __init__(self, config=None):
        super(Validator, self).__init__(config=config)
        bt.logging.info("Validator neuron initialized")
        self.load_state() 
    
    async def forward(self, response):
        """
        Validator forward pass. Consists of:
        - Generating the query
        - Querying the miners
        - Getting the responses
        - Rewarding the miners
        - Updating the scores
        """

        # craete a synapse query
        # bt.logging.info("Creating synapse query", self.step)
        # synapse = template.protocol.Dummy(dummy_input=self.step)
        # {'query': None, 'agent': {'uid': 6, 'tool': 1002}}
        bt.logging.info("Creating synapse query", response)
        # self.query = response
        # self.query["request_type"] = "QUERY_MINER"
        # self.request_type = "QUERY_MINER"
        # {'query': 'add 2 and 3', 'agent': {'alive': False, 'tool_Id': '1004', 'minerId': 6, 'groupId': 5151}}
        self.query = {"query":{
                "query":  response['query'],
                "summary": False,
                "minerId": response['agent']['minerId'],
                "status": False,
                "tool_Id": response['agent']['tool_Id'],
                "is_tool_list": False,
            }
        }
        # self.agent = response['agent'] 
        bt.logging.info("synapse query: ", self.query)
        # bt.logging.info("synapse agent: ", self.agent)
        query_response = await forward(self)
        return query_response
    

    async def interpreter_response(self, response):
        bt.logging.info("interpreter_response", response)
        self.query_res = response
        bt.logging.info("interpreter_response: ", self.query_res)
        query_response = await send_res_to_group_chat(self)
        return query_response


    def get_miner_info(self, query_uids: list):
        uid_to_axon = dict(zip(self.all_uids, self.metagraph.axons))
        query_axons = [uid_to_axon[int(uid)] for uid in query_uids]
        return query_axons


    def get_valid_miners_info(self):
        self.all_uids = [int(uid) for uid in self.metagraph.uids]
        # valid_miners_info = self.get_miner_info(self.all_uids)
        return self.all_uids
    
    async def is_tool_alive(self, miner_id, tool_id):
        """
        Check if the tool is alive.
        """
        self.query = {"query":{
                "query": "sum of two numbers",
                "summary": False,
                "minerId": miner_id,
                "status": True,
                "tool_Id": tool_id,
                "is_tool_list": False,
            }
        }
        tool_status = await forward(self)
        return tool_status
    
    async def check_tool_alive(self, miner_uids,group_id):
        """
        Check if the tool is alive.
        """
        print(":::::::::miner_uids:::::::::::",miner_uids)
        alive_tools_list = []
        self.request_type = "CHECK_TOOL_ALIVE"
        for miner in miner_uids:
            self.query = {"query":{
                    "query": "QUERY_TO_MINER",
                    "summary": False,
                    "minerId": miner['metadata']['uid'],
                    "status": True,
                    "tool_Id": miner['metadata']['toolId'],
                    "is_tool_list": False,
                }
            }

            tool_status = (await forward(self))[0]
            print(":::::::::tool_status:::::::::::",tool_status)
            if tool_status and 'alive' in tool_status and tool_status['alive'] == True:
                tool_status['groupId'] = group_id
                tool_status['agent_id'] = util.generate_agent_reference_id()
                alive_tools_list.append(tool_status)
            print("::::::::::::::::res_tools_list::::::::::::",alive_tools_list)
        return alive_tools_list
    
async def get_query(request: web.Request):
        """
        Get query request handler. This method handles the incoming requests and returns the response from the forward function.
        """
        response = await request.json()
        global global_object
        fetch_group_data = util.get_object_by_group_and_agent(global_object,response['agent']['groupId'],response['agent']['agent_id'])
        if fetch_group_data is None:
            return web.json_response({"message": "Agent not found"})
        response['agent']['tool_Id'] = fetch_group_data['tool_Id']
        response['agent']['minerId'] = fetch_group_data['minerId']
        response['agent']['alive']  = False
        print("::::::::::::::::::::",global_object)
        bt.logging.info(f"Received query request. {response}")
        return web.json_response(await webapp.validator.forward(response))

async def miner_response(request: web.Request):
        """
        Get query request handler. This method handles the incoming requests and returns the response from the forward function.
        """
        response = await request.json()
        
        bt.logging.info(f"Received query request. {response}")
        return web.json_response(await webapp.validator.interpreter_response(response))

def add_object(group_id, object_data):
    try:
        global global_object
        if group_id in global_object:
            global_object[group_id].append(object_data)
        else:
            global_object[group_id] = object_data
    except Exception as e:
        print("Error in add_object: ", e)
        
def find_group_id(search_id):
    try:
        global global_object
        for group_id, objects in global_object.items():
            for obj in objects:
                if obj["id"] == search_id:
                    return group_id
        return None
    except Exception as e:
        print("Error in find_group_id: ", e)
        return None
            
async def request_for_miner(request: web.Request):
    payload = await request.json() 
    # payload = {'tools': ["open interpreter", "self operating computer", "gpt-4"], 'group_id': 'a0be0a03-1831-4ec2-b2b0-225b81b955e3', 'problem_statement': 'Add 2 and 3'}
    global global_object
    print("::::::::::::::global_object::::::::::::::::::::", global_object)
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
        embedded_text = await convert_text_to_vector(payload_for_text_embedding)
        # bt.logging.info(f"Embedded Text: {embedded_text}")
        miner_tools_info = []
        if len(embedded_text['vectorizedChunks']):
            chunk = embedded_text['vectorizedChunks'][0]
            miner_tools_info = (await get_vector_from_db(chunk['vector']))['matches']['matches']
        bt.logging.info(f"::::::::::::::miner_tools_info::::::::::::::::::::. {miner_tools_info}")
        # check if the tool is alive
        alive_tools = await webapp.validator.check_tool_alive(miner_tools_info, payload["group_id"])
        bt.logging.info(f"Alive Tools: {alive_tools}")
        
        # get the unique miner ids
        if len(alive_tools):
            random_alive_tool = random.choice(alive_tools)
            print(":::::::::::::: random_alive_tool::::::::::::::::::::", random_alive_tool)
            tools_to_use.append(random_alive_tool)
            data_to_send.append({
                "groupId": random_alive_tool['groupId'],
                "agent_id": random_alive_tool['agent_id'],
            })
    
    print("::::::::::::::tools_to_use::::::::::::::::::::", tools_to_use)
    add_object(payload['group_id'], tools_to_use)
    print("::::::::::::::global_object::::::::::::::::::::", global_object)
    return web.json_response(data_to_send)

async def delete_miner_tool_info(tool_ids):
    """
    Delete miner info request handler. This method handles the incoming requests and deletes the miner info.
    """
    res = await delete_vector_from_db(tool_ids)
    if(res):
        print("::::::::::::::Data deleted successfully::::::::::::::::::::", res)

async def save_miner_info(alive_tool_list, miner_id):
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
        embedded_text = await convert_text_to_vector(payload)
        if len(embedded_text['vectorizedChunks']):
            for chunk in embedded_text['vectorizedChunks']:
                bt.logging.info(f"Chunk: {chunk}")
                data_to_save.append({"id": f"{miner_id}-{tool_details['toolId']}", "values": chunk['vector'], "metadata": {"name": tool_details['name'], "uid": miner_id, "toolId": tool_details['toolId']}})
                
    print("::::::::::::::data_to_save::::::::::::::::::::", data_to_save) 
    res = await insert_vector_into_db(data_to_save)
    if(res):
        print("::::::::::::::Data saved successfully::::::::::::::::::::", res)

async def get_miner_tool_list(request: web.Request):
    """
    Get query request handler. This method handles the incoming requests and returns the response from the forward function.
    """
    for miner_id in webapp.validator.get_valid_miners_info():
        webapp.validator.query ={
            "query" : {
                "is_tool_list": True,
                "minerId": miner_id,
            }
        }
        tool_list = await forward(webapp.validator)
        if len(tool_list[0].keys()):
            toolids = [f"{miner_id}-{tool['toolId']}" for tool in tool_list[0]['key']]
            await delete_miner_tool_info(toolids)
            alive_tool_list = []
            for tool in tool_list[0]['key']:
                alive_tools = await webapp.validator.is_tool_alive(miner_id, tool['toolId'])
                if alive_tools[0] and 'alive' in alive_tools[0] and alive_tools[0]['alive'] == True:
                    alive_tool_list.append(tool)
            await save_miner_info(alive_tool_list, miner_id)
    else:
        return "Tool list is saved successfully"  


async def remove_agent_from_global_object(all_agents_detail, group_id, agent_id):
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


async def remove_agent(request: web.Request):
    """
    Get query request handler. This method handles the incoming requests and returns the response from the forward function.
    """
    try:
        global global_object
        response = await request.json()
        bt.logging.info(f"::::response:::::remove_agent:::{response}")

        all_agents_detail = remove_agent_from_global_object(
            global_object, response['group_id'], response['agent_id'])
        global_object = all_agents_detail

        bt.logging.info(f"global_object::::: {global_object}")
        return {"message": "Agent removed!"}
    except Exception as e:
        bt.logging.info(f"error in remove_agent::::: {e}")
        return {"message": "Agent not removing!"}

class WebApp(web.Application):
    """
    Web application for the validator. This class is used to create a web server for the validator.
    """

    def __init__(self, validator: Validator):
        super().__init__()
        self.validator = validator
    
webapp = WebApp(Validator())
webapp.add_routes([
    web.post('/forward', get_query),
    web.post('/webhook', miner_response),
    web.post('/request_for_miner', request_for_miner),
    web.post('/tool_list', get_miner_tool_list),
    web.post('/remove_miner', remove_agent)
])
web.run_app(webapp, port=8080, loop=asyncio.get_event_loop())
