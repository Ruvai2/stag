import aiohttp
from validators.vector_api.vector import Vector

qdrant_api_base_url = "http://192.168.0.129:3000/vector"

async def api_request_handler(**kwargs):
    """
    Request handler for the get query endpoint. This method handles the incoming requests and returns the response from the forward function.
    """
    try:
        print(f"Request {kwargs}")
        async with aiohttp.ClientSession() as session:
            if kwargs['method'] == "GET":
                async with session.get(kwargs['url']) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Error: {response.status}, {await response.text()}")
            elif kwargs['method'] == "POST":
                async with session.post(kwargs['url'], json=kwargs['data']) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Error: {response.status}, {await response.text()}")
            elif kwargs['method'] == "PUT":
                async with session.put(kwargs['url'], json=kwargs['data']) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Error: {response.status}, {await response.text()}")
            elif kwargs['method'] == "PATCH":
                async with session.patch(kwargs['url'], json=kwargs['data']) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Error: {response.status}, {await response.text()}")
            elif kwargs['method'] == "DELETE":
                async with session.delete(kwargs['url']) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Error: {response.status}, {await response.text()}")
    except Exception as e:
        print(f"Error: {e}")
        
async def convert_text_to_vector(payload):
    try:
        text_embedding_url = "https://daasi-text-embedding.ru9.workers.dev/"
        embedded_text = await api_request_handler(method="POST", url=text_embedding_url, data=payload)
        return embedded_text
    except Exception as e:
        print(f"Error: {e}")
        
async def insert_vector_into_db(payload):
    try:
        vector_insert_url = "https://daasi-vectorize.ru9.workers.dev/insert"
        response = await api_request_handler(method="POST", url=vector_insert_url, data=payload)
        return response
    except Exception as e:
        print(f"Error: {e}")
        
async def get_vector_from_db(query_vector):
    try:
        vector_get_url =  f"https://daasi-vectorize.ru9.workers.dev/query"
        response = await api_request_handler(method="POST", url=vector_get_url, data={"values": query_vector})
        return response
    except Exception as e:
        print(f"Error: {e}")
        
async def get_tool_from_vector_db(collection_name, tool_id):
    try:
        res =  Vector.get_point_details(collection_name, tool_id)
        return res
        # vector_get_url =  f"{qdrant_api_base_url}/{collection_name}/{tool_id}"
        # response = await api_request_handler(method="GET", url=vector_get_url)
        # return response
    except Exception as e:
        print(f"Error: {e}")
        
async def delete_vector_from_db(ids):
    try:
        joined_ids = ",".join(ids)
        vector_delete_url =  f"https://daasi-vectorize.ru9.workers.dev/delete?ids={joined_ids}"
        response = await api_request_handler(method="DELETE", url=vector_delete_url)
        return response
    except Exception as e:
        print(f"Error: {e}")
        
async def update_data_in_vector_db(payload):
    try:
        return Vector.update_vector_point(payload["collection_name"], payload["id"], payload["score"])
        # vector_insert_url = f"{qdrant_api_base_url}"
        # response = await api_request_handler(method="PATCH", url=vector_insert_url, data=payload)
        # return response
    except Exception as e:
        print(f"Error: {e}")

