from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct, Filter, PointIdsList
from qdrant_client.http.api.points_api import *
import os
from dotenv import load_dotenv
load_dotenv()

def is_iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False

class QdrantClientWrapper:
    def __init__(self):
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
        print('host',host)
        print('port',port)
        self.client = QdrantClient(host = host, port = port)

    def create_collection(self, name, dimension):
        try:
            self.client.create_collection(
                collection_name = name,
                vectors_config = models.VectorParams(size = dimension, distance = models.Distance.COSINE)
            )
            return True
        except Exception as e:
            print('Exception in createCollection', e)
            return False

    def store_data(self, collection_name, payload_json, vector):
        try:
            point = PointStruct(
                id=payload_json.get('tool_id'),
                payload=payload_json,
                vector=vector
            )
            results = self.client.upsert(collection_name=collection_name, points=[point])
            return results.status == 'completed'
        except Exception as e:
            print("Exception in store_data on database", e)
            return False

    def search_data(self, collection_name, query_vector, top_k, filters):
        try:
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                shard_key_selector=None,
                query_filter=filters,
            )
            result = []
            for scored_point in search_result:
                result.append({'id': scored_point.id, 'version': scored_point.version, 'score': scored_point.score,
                                'payload': scored_point.payload})
            return result
        except Exception as e:
            print("Exception in search_data on database", e)
            return False

    def delete_vectors_by_metadata(self, collection_name, points):
        try:
            results = self.client.delete(
                collection_name = f"{collection_name}",
                points_selector = PointIdsList(
                    points = points,
                ),
            )
            return results.status == 'completed'
        except Exception as e:
            print("Exception in search_data on database", e)
            return False

    def get_vector_details_by_id(self, collection_name, id):
        try:
            results = self.client.retrieve(
                collection_name=f"{collection_name}",
                ids=[id]
            )
            res = {}
            for record in results:
                res["id"] = record.id
                res['payload'] = record.payload
            return res
        except Exception as e:
            print("Exception in search_data on database", e)
            return False

    def get_all_points_data(self, collection_name, limit, offset):
        try:
            print(limit, offset)
            res = self.client.scroll(
                collection_name = f"{collection_name}",
                limit = limit,
                offset = offset,
                with_payload = True,
                with_vectors = False
            )
            results = []
            for record in res:
                if is_iterable(record):
                    for i in record :
                        results.append({ "id" : i.id, "payload": i.payload})
            return results
        except Exception as e:
            print("Exception in search_data on database", e)
            return False

    def update_point_metadata(self, collection_name, id, score):
        try:
            results = self.client.retrieve(
                collection_name=f"{collection_name}",
                ids=[id],
                with_vectors=True
            )

            payload = vector = {}
            for Record in results:
                payload = Record.payload
                vector = Record.vector

            payload['score'] = score

            if len(results) != 0:
                self.client.upsert(
                    collection_name=f"{collection_name}",
                    points=[
                        PointStruct(
                            id=id,
                            payload=payload,
                            vector=vector
                        ),
                    ],
                )
            else:
                return False

            return True
        except Exception as e:
            print("Exception in search_data on database", e)
            return False

db_client = QdrantClientWrapper()