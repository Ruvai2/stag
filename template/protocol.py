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

import typing
import bittensor as bt
import pydantic
from typing import Optional
from pydantic import BaseModel

# TODO(developer): Rewrite with your protocol definition.

# This is the protocol for the dummy miner and validator.
# It is a simple request-response protocol where the validator sends a request
# to the miner, and the miner responds with a dummy response.

# ---- miner ----
# Example usage:
#   def dummy( synapse: Dummy ) -> Dummy:
#       synapse.dummy_output = synapse.dummy_input + 1
#       return synapse
#   axon = bt.axon().attach( dummy ).serve(netuid=...).start()

# ---- validator ---
# Example usage:
#   dendrite = bt.dendrite()
#   dummy_output = dendrite.query( Dummy( dummy_input = 1 ) )
#   assert dummy_output == 2


class InterpreterRequests(bt.Synapse):
    """
    A simple dummy protocol representation which uses bt.Synapse as its base.
    This protocol helps in handling dummy request and response communication between
    the miner and the validator.

    Attributes:
    - dummy_input: An integer value representing the input request sent by the validator.
    - dummy_output: An optional integer value which, when filled, represents the response from the miner.
    """

    # Required request input, filled by sending dendrite caller.
    # dummy_input: str

    # Optional request output, filled by recieving axon.
    agent_output: typing.Optional[object] = {}
    query:dict = pydantic.Field(
        default={},
        title="Pipeline Parameters",
        description="Additional generating params",
    )
    # status:bool
    # minerId:str

    def deserialize(self) -> "InterpreterRequests":
        return self.agent_output

    
    # query: str = pydantic.Field(
    # ..., title="Query", description="The query to pass to the provider"
    # )
    # model: str = pydantic.Field(
    #     ..., title="Model", description="The model to use"
    # )
    # This is only used with self-operating-computer as an optional field
    # summary: Optional[bool]= pydantic.Field(
    #     ..., title="Summary", description="Whether to generate a summary or not", value = False
    # )
    # status:  Optional[bool]= pydantic.Field(
    #     ..., title="status", description="Whether to generate a summary or not", value = False
    # )
    # minerId:  Optional[str]= pydantic.Field(
    #     ..., title="minerId", description="Whether to generate a summary or not", value = False
    # )
    # def deserialize(self) -> str:
    #     """
    #     Deserialize the dummy output. This method retrieves the response from
    #     the miner in the form of agent_output, deserializes it and returns it
    #     as the output of the dendrite.query() call.

    #     Returns:
    #     - int: The deserialized response, which in this case is the value of agent_output.

    #     Example:
    #     Assuming a Dummy instance has a agent_output value of 5:
    #     >>> dummy_instance = Dummy(dummy_input=4)
    #     >>> dummy_instance.agent_output = 5
    #     >>> dummy_instance.deserialize()
    #     5
    #     """
    #     return self.agent_output

# class InterpreterRequests(bt.Synapse):
#     # completion: Optional[str] = pydantic.Field(
#     #     None,
#     #     title="Completion",
#     #     description="The completion data of the chat response."
#     # ),
#     query: str = pydantic.Field(
#     ..., title="Query", description="The query to pass to the provider"
#     )
#     # model: str = pydantic.Field(
#     #     ..., title="Model", description="The model to use"
#     # )
#     # This is only used with self-operating-computer as an optional field
#     # summary: Optional[bool]= pydantic.Field(
#     #     ..., title="Summary", description="Whether to generate a summary or not", value = False
#     # )
#     status:  Optional[bool]= pydantic.Field(
#         ..., title="status", description="Whether to generate a summary or not", value = False
#     )
#     minerId:  Optional[str]= pydantic.Field(
#         ..., title="minerId", description="Whether to generate a summary or not", value = False
#     )
#     # def deserialize(self) -> str:
#     #     # """
#     #     # Deserialize the dummy output. This method retrieves the response from
#     #     # the miner in the form of dummy_output, deserializes it and returns it
#     #     # as the output of the dendrite.query() call.

#     #     # Returns:
#     #     # - int: The deserialized response, which in this case is the value of dummy_output.

#     #     # Example:
#     #     # Assuming a Dummy instance has a dummy_output value of 5:
#     #     # >>> dummy_instance = Dummy(dummy_input=4)
#     #     # >>> dummy_instance.dummy_output = 5
#     #     # >>> dummy_instance.deserialize()
#     #     # 5
#     #     # """
#     #     return self.completion