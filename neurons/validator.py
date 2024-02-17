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
from template.utils.misc import convert_text_to_vector, insert_vector_into_db, get_vector_from_db

# Bittensor Validator Template:
import template
from template.validator import forward,send_res_to_group_chat

# import base validator class which takes care of most of the boilerplate
from template.base.validator import BaseValidatorNeuron
from template.protocol import PingMiner
import random

global_object = {}

class Validator(BaseValidatorNeuron):
    """
    Your validator neuron class. You should use this class to define your validator's behavior. In particular, you should replace the forward function with your own logic.

    This class inherits from the BaseValidatorNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a validator such as keeping a moving average of the scores of the miners and using them to set weights at the end of each epoch. Additionally, the scores are reset for new hotkeys at the end of each epoch.
    """

    def __init__(self, config=None):
        super(Validator, self).__init__(config=config)

        bt.logging.info("=====================================> load_state()")
        bt.logging.info(f":::::::self.axon::::::", self.axon)
        self.load_state()
        self.group_miners_association = {}

        # TODO(developer): Anything specific to your use case you can do here   
    
    async def forward(self, response):
        """
        Validator forward pass. Consists of:
        - Generating the query
        - Querying the miners
        - Getting the responses
        - Rewarding the miners
        - Updating the scores
        """
        # TODO(developer): Rewrite this function based on your protocol definition.

        # craete a synapse query
        # bt.logging.info("Creating synapse query", self.step)
        # synapse = template.protocol.Dummy(dummy_input=self.step)
        # {'query': None, 'agent': {'uid': 6, 'tool': 1002}}
        bt.logging.info("Creating synapse query", response)
        self.query = response
        self.query["request_type"] = "QUERY_MINER"
        self.request_type = "QUERY_MINER"
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

    async def ping_miner(self, isToolList):
        """
        Send a query to a miner and get the response.
        """
        print(":::::::::::::: Inside ping_miner_and_get_response :::::::::::::::::::", self.get_valid_miners_info())
        miner_response_list = []
        self.request_type = "PING_MINER"
        for miner in self.get_valid_miners_info():
            self.query ={
                "minerId": miner,
                "isToolList": isToolList,
                "request_type": "PING_MINER",
            }
            miner_list = await forward(self)
            miner_response_list.append(miner_list)
        print("::::::::::::::forward_responses::::::::::::::::::::", miner_response_list)
    
    async def check_tool_alive(self, miner_uids,group_id):
        """
        Check if the tool is alive.
        """
        alive_tools = []
        self.request_type = "CHECK_TOOL_ALIVE"
        for miner in miner_uids:
            self.query = {
                "minerId": miner['metadata']['uid'],
                "toolId": miner['id'],
                "status": "True",
                "request_type": "CHECK_TOOL_ALIVE",
                "groupId": group_id
            }
            tool_status = (await forward(self))[0]
            if len(tool_status.keys()) > 0 and tool_status['alive'] == True:
                tool_status['groupId'] = self.query['groupId']
                alive_tools.append(tool_status)
        return alive_tools
        
async def get_query(request: web.Request):
        """
        Get query request handler. This method handles the incoming requests and returns the response from the forward function.
        """
        response = await request.json()
        bt.logging.info(f"Received query request. {response}")
        # print(":::web.json_response(await webapp.validator.forward(response)):::",web.json_response(await webapp.validator.forward(response)))
        return web.json_response(await webapp.validator.forward(response))

async def miner_response(request: web.Request):
        """
        Get query request handler. This method handles the incoming requests and returns the response from the forward function.
        """
        response = await request.json()
        
        bt.logging.info(f"Received query request. {response}")
        return web.json_response(await webapp.validator.interpreter_response(response))
    
async def save_miner_info(request: web.Request):
    """
    Save miner info request handler. This method handles the incoming requests and saves the miner info.
    """
    response = await request.json()
    print(":::::::::::::: In save miner info :::::::::::::::::::", response)
    payload = {
        "account_id": "112233",
        "chunks": [   
            {
                "id": "1",
                "metadata": {
                    "context": response['metadata']['tool_summary'],
                }
            },
        ]
    }
    
    bt.logging.info(f"Received save_miner_info request. {payload}")
    embedded_text = await convert_text_to_vector(payload)
    if len(embedded_text['vectorizedChunks']):
        for chunk in embedded_text['vectorizedChunks']:
            bt.logging.info(f"Chunk: {chunk['vector']}")
            await insert_vector_into_db(chunk)

def get_unique_miner_ids(data):
    unique_miner_ids = set()
    result = []
    
    for item in data:
        if 'minerId' in item:
            miner_id = item['minerId']
            if miner_id not in unique_miner_ids:
                unique_miner_ids.add(miner_id)
                result.append(item)
    return result

def add_object(group_id, object_data):
    try:
        global global_object
        if group_id in global_object:
            global_object[group_id].append(object_data)
        else:
            global_object[group_id] = [object_data]
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
    response = await request.json()
    bt.logging.info(f"Received save_miner_info request. {response}")
    payload = {
        "account_id": "112233",
        "chunks": [   
            {
                "id": "1",
                "metadata": {
                    "context": response['query']
                }
            },
        ]
    }
    bt.logging.info(f"Received save_miner_info request. {payload}")
    embedded_text = await convert_text_to_vector(payload)
    # bt.logging.info(f"Embedded Text: {embedded_text}")
    miner_tools_info = []
    if len(embedded_text['vectorizedChunks']):
        chunk = embedded_text['vectorizedChunks'][0]
        miner_tools_info = (await get_vector_from_db(chunk['vector']))['matches']['matches']
    bt.logging.info(f"::::::::::::::miner_tools_info::::::::::::::::::::. {miner_tools_info}")
    # check if the tool is alive
    alive_tools = await webapp.validator.check_tool_alive(miner_tools_info,response["group_id"])
    bt.logging.info(f"Alive Tools: {alive_tools}")
    
    
    # get the unique miner ids
    if len(alive_tools):
        unique_miners_details = get_unique_miner_ids(alive_tools)[0]
        print("::::::::::::::unique_miners_details::::::::::::::::::::", unique_miners_details)
        add_object(unique_miners_details['groupId'], unique_miners_details)
        print("::::::::::::::unique_miners_details::::::::::::::::::::", global_object)
        return web.json_response(unique_miners_details)
        
async def ping_miners(request: web.Request):
    # hit the miner with the query every 1 hour
    await webapp.validator.ping_miner(True)
    bt.logging.debug(":::::::::::::: Inside main :::::::::::::::::::")
                
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
    web.post('/save_miner_info', save_miner_info),
    web.post('/request_for_miner', request_for_miner),
    web.post('/ping_miner', ping_miners),
    web.post('/tool_list', get_miner_tool_list)
])
web.run_app(webapp, port=8080, loop=asyncio.get_event_loop())
    
async def miner_response(request: web.Request):
        """
        Get query request handler. This method handles the incoming requests and returns the response from the forward function.
        """
        response = await request.json()
        
        bt.logging.info(f"Received query request. {response}")
        return web.json_response(await webapp.validator.forward(response))

async def get_miner_tool_list(request: web.Request):
        """
        Get query request handler. This method handles the incoming requests and returns the response from the forward function.
        """
        response = await request.json()
        
        bt.logging.info(f"Received query request. {response}")
        return web.json_response(await webapp.validator.forward(response))

webapp = WebApp(Validator())
# webapp.add_routes([web.post('/forward', get_query), web.post('/webhook', miner_response), web.post('/tool_list', get_miner_tool_list)])
web.run_app(webapp, port=9080, loop=asyncio.get_event_loop())
