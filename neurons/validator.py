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
import asyncio

# Bittensor Validator Template:
import template
from template.validator import forward

# import base validator class which takes care of most of the boilerplate
from template.base.validator import BaseValidatorNeuron




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
        
        bt.logging.info("Creating synapse query", response)
        self.query = response
        bt.logging.info("synapse query: ", self.query)
        query_response = await forward(self)
        return query_response
    
async def get_query(request: web.Request):
        """
        Get query request handler. This method handles the incoming requests and returns the response from the forward function.
        """
        response = await request.json()
        
        bt.logging.info(f"Received query request. {response}")
        return web.json_response(await webapp.validator.forward(response))
    
class WebApp(web.Application):
    """
    Web application for the validator. This class is used to create a web server for the validator.
    """

    def __init__(self, validator: Validator):
        super().__init__()
        self.validator = validator
    
webapp = WebApp(Validator())
webapp.add_routes([web.post('/forward', get_query)])
web.run_app(webapp, port=9080, loop=asyncio.get_event_loop())