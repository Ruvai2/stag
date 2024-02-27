import logging
import time
from typing import Tuple

import base  # noqa

import os
import argparse
import asyncio
import random
import traceback
from pathlib import Path

import bittensor as bt
import torch
# import wandb
from aiohttp import web
from aiohttp.web_response import Response
from image_validator import ImageValidator
from embeddings_validator import EmbeddingsValidator
from text_validator import TextValidator, TestTextValidator
from base_validator import BaseValidator
from groupchat_validator import GroupChatValidator
from envparse import env

import template
from template import utils
import sys

from weight_setter import WeightSetter, TestWeightSetter

from template import forward
from utils import utils

text_vali = None
image_vali = None
embed_vali = None
group_chat_vali = None
metagraph = None
# wandb_runs = {}
# organic requests are scored, the tasks are stored in this queue
# for later being consumed by `query_synapse` cycle:
organic_scoring_tasks = set()
EXPECTED_ACCESS_KEY = os.environ.get('EXPECTED_ACCESS_KEY', "hello")
bt.logging.info("Starting validator...Expecting access key: " + EXPECTED_ACCESS_KEY)

def get_config() -> bt.config:
    parser = argparse.ArgumentParser()
    parser.add_argument("--netuid", type=int, default=77)
    # parser.add_argument('--wandb_off', action='store_false', dest='wandb_on')
    parser.add_argument('--http_port', type=int, default=8080)
    # parser.set_defaults(wandb_on=True)
    bt.subtensor.add_args(parser)
    bt.logging.add_args(parser)
    bt.wallet.add_args(parser)
    config = bt.config(parser)
    _args = parser.parse_args()
    full_path = Path(
        f"{config.logging.logging_dir}/{config.wallet.name}/{config.wallet.hotkey}/netuid{config.netuid}/validator"
    ).expanduser()
    config.full_path = str(full_path)
    full_path.mkdir(parents=True, exist_ok=True)
    return config


# def init_wandb(config, my_uid, wallet: bt.wallet):
#     if not config.wandb_on:
#         return

    # run_name = f'validator-{my_uid}-{template.__version__}'
    # config.uid = my_uid
    # config.hotkey = wallet.hotkey.ss58_address
    # config.run_name = run_name
    # config.version = template.__version__
    # config.type = 'validator'

    # # Initialize the wandb run for the single project
    # run = wandb.init(
    #     name=run_name,
    #     project=template.PROJECT_NAME,
    #     entity='cortex-t',
    #     config=config,
    #     dir=config.full_path,
    #     reinit=True
    # )

    # # Sign the run to ensure it's from the correct hotkey
    # signature = wallet.hotkey.sign(run.id.encode()).hex()
    # config.signature = signature
    # wandb.config.update(config, allow_val_change=True)

    # bt.logging.success(f"Started wandb run for project '{template.PROJECT_NAME}'")

def initialize_components(config: bt.config):
    global metagraph
    bt.logging(config=config, logging_dir=config.full_path)
    bt.logging.info(f"Running validator for subnet: {config.netuid} on network: {config.subtensor.chain_endpoint}")
    wallet = bt.wallet(config=config)
    subtensor = bt.subtensor(config=config)
    metagraph = subtensor.metagraph(config.netuid)
    dendrite = bt.dendrite(wallet=wallet)
    my_uid = metagraph.hotkeys.index(wallet.hotkey.ss58_address)
    if wallet.hotkey.ss58_address not in metagraph.hotkeys:
        bt.logging.error(
            f"Your validator: {wallet} is not registered to chain connection: "
            f"{subtensor}. Run btcli register --netuid 77 and try again."
        )
        sys.exit()

    return wallet, subtensor, dendrite, my_uid


def initialize_validators(vali_config, test=False):
    global text_vali, image_vali, embed_vali, group_chat_vali

    text_vali = (TextValidator if not test else TestTextValidator)(**vali_config)
    image_vali = ImageValidator(**vali_config)
    embed_vali = EmbeddingsValidator(**vali_config)
    group_chat_vali = GroupChatValidator(**vali_config)
    bt.logging.info("initialized_validators")


async def process_text_validator(request: web.Request):
    # Basic request validation
    bt.logging.info(f"Received request: {await request.json()}")
    if request.method != "POST" or request.path != '/text-validator/':
        return web.Response(status=400, text="Invalid request")

    # Check access key
    access_key = request.headers.get("access-key")
    if access_key != EXPECTED_ACCESS_KEY:
        return web.Response(status=401, text="Invalid access key")

    try:
        messages_dict = {int(k): [{'role': 'user', 'content': v}] for k, v in (await request.json()).items()}
    except ValueError:
        return web.Response(status=400, text="Bad request format")
    
    bt.logging.info(f"Received messages: {messages_dict}")

    response = web.StreamResponse()
    await response.prepare(request)

    uid_to_response = dict.fromkeys(messages_dict, "")
    bt.logging.info(f"I'm here:+++++++++++++++++++ {uid_to_response} {messages_dict} {text_vali} {validator_app.weight_setter.metagraph}")
    try:
        async for uid, content in text_vali.organic(validator_app.weight_setter.metagraph, messages_dict):
            uid_to_response[uid] += content
            await response.write(content.encode())
        validator_app.weight_setter.register_text_validator_organic_query(
            uid_to_response, {k: v[0]['content'] for k, v in messages_dict.items()}
        )
    except Exception as e:
        bt.logging.error(f'Encountered in {process_text_validator.__name__}:\n{traceback.format_exc()}')
        await response.write(b'<<internal error>>')

    return response

    
async def forward_query_request(request: web.Request):
    """
    Forward request handler. This method handles the incoming requests and returns the response from the forward function.
    """
    try:
        data = await request.json()
    except ValueError:
        return web.Response(status=400, text="Bad request format")
    
    try:
        res = await group_chat_vali.send_query_to_miner(data)
        temp_res = {"message":"Success"}
        return web.json_response(temp_res)
    except Exception as e:
        bt.logging.error(f'Encountered in {forward_query_request.__name__}:\n{traceback.format_exc()}')
        return web.Response(status=500, text="Internal error")
    
async def handle_request_for_the_miner_agents(request: web.Request):
    """
    Handle request for the miner agents. This method handles the incoming requests and returns the response from the forward function.
    """
    try:
        data = await request.json()
    except ValueError:
        return web.Response(status=400, text="Bad request format")
    
    try:
       return web.json_response(await group_chat_vali.request_for_miner(data))
    except Exception as e:
        bt.logging.error(f'Encountered in {handle_request_for_the_miner_agents.__name__}:\n{traceback.format_exc()}')
        return web.Response(status=500, text="Internal error")

async def handle_request_for_the_tools_list(request: web.Request):
    """
    Handle request for the miner agents. This method handles the incoming requests and returns the response from the forward function.
    """
    try:
        data = await request.json()
    except ValueError:
        return web.Response(status=400, text="Bad request format")
    
    try:
       return web.json_response(await group_chat_vali.process_tool_selection_request(data))
    except Exception as e:
        bt.logging.error(f'Encountered in {handle_request_for_the_miner_agents.__name__}:\n{traceback.format_exc()}')
        return web.Response(status=500, text="Internal error")

async def handle_miner_response(request: web.Request):
        """
        Get query request handler. This method handles the incoming requests and returns the response from the forward function.
        """
        try:
            data = await request.json()
        except ValueError:
            return web.Response(status=400, text="Bad request format")
        
        bt.logging.info(f"Received query request. {data}")
        
        try:
            return web.json_response(await group_chat_vali.interpreter_response(data))
        except Exception as e:
            bt.logging.error(f'Encountered in {handle_miner_response.__name__}:\n{traceback.format_exc()}')
            return web.Response(status=500, text="Internal error")

async def handle_remove_agent_request(request: web.Request):
    """
    Get query request handler. This method handles the incoming requests and returns the response from the forward function.
    """
    try:
        data = await request.json()
    except ValueError:
        return web.Response(status=400, text="Bad request format")
    
    try:
        return web.json_response(await group_chat_vali.remove_agent(data))
    except Exception as e:
        bt.logging.error(f'Encountered in {handle_miner_response.__name__}:\n{traceback.format_exc()}')
        return web.Response(status=500, text="Internal error")
    
async def handle_request_run_tool(request: web.Request):
    """
    Get query request handler. This method handles the incoming requests and returns the response from the forward function.
    """
    try:
        data = await request.json()
    except ValueError:
        return web.Response(status=400, text="Bad request format")
    
    try:
        return web.json_response(await group_chat_vali.run_tool(data))
    except Exception as e:
        bt.logging.error(f'Encountered in {handle_miner_response.__name__}:\n{traceback.format_exc()}')
        return web.Response(status=500, text="Internal error")

async def handle_request_for_delete_tool(request: web.Request):
    """
    Get query request handler. This method handles the incoming requests and returns the response from the forward function.
    """
    try:
        data = await request.json()
    except ValueError:
        return web.Response(status=400, text="Bad request format")
    
    try:
        return web.json_response(await group_chat_vali.delete_tool(data))
    except Exception as e:
        bt.logging.error(f'Encountered in {handle_miner_response.__name__}:\n{traceback.format_exc()}')
        return web.Response(status=500, text="Internal error")

class ValidatorApplication(web.Application):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.weight_setter: WeightSetter | None = None
        

validator_app = ValidatorApplication()
validator_app.add_routes([
    web.post('/text-validator/', process_text_validator),
    web.post('/forward', forward_query_request),
    web.post('/webhook', handle_miner_response),
    web.post('/request_for_miner', handle_request_for_the_miner_agents),
    web.post('/remove_miner', handle_remove_agent_request),
    web.post('/request_tools_list', handle_request_for_the_tools_list),
    web.post('/request_run_tool', handle_request_run_tool),
    web.post('/request_delete_tool', handle_request_for_delete_tool),
    web.post('/query_to_resolve', forward_query_request),
])

def main(run_aio_app=True, test=False) -> None:
    config = get_config()
    wallet, subtensor, dendrite, my_uid = initialize_components(config)
    validator_config = {
        "dendrite": dendrite,
        "config": config,
        "subtensor": subtensor,
        "wallet": wallet
    }
    initialize_validators(validator_config, test)
    # init_wandb(config, my_uid, wallet)
    loop = asyncio.get_event_loop()

    weight_setter = (WeightSetter if not test else TestWeightSetter)(
        loop, dendrite, subtensor, config, wallet, text_vali, image_vali, embed_vali, group_chat_vali)
    validator_app.weight_setter = weight_setter

    if run_aio_app:
        try:
            web.run_app(validator_app, port=config.http_port, loop=loop)
        except KeyboardInterrupt:
            bt.logging.info("Keyboard interrupt detected. Exiting validator.")
        finally:
            state = utils.get_state()
            utils.save_state_to_file(state)
            # if config.wandb_on:
            #     wandb.finish()

if __name__ == "__main__":
    main()
