
from vector_api.db import db_client

class Vector:
    @staticmethod
    def create_collection(name , dimension):
        """_summary_

        Args:
            name (str): name of collection
            dimension (int): number of dimension

        Returns:
            _type_: _description_
        """
        try:
            res = db_client.create_collection(name , dimension)
            if res == True:
                return True
            else:
                return False
        except Exception as e:
            # Handle the exception
            print(f"An error occurred while creating collection : {e}")
            return None

    @staticmethod
    def create_vector_point(collection_name, payload_json, vector):
        """_summary_

        Args:
            collection_name (str): collection name
            payload_json (json): json
            vector (_type_): list of points

        Returns:
            _type_: _description_
        """
        try:
            res = db_client.store_data(collection_name, payload_json, vector)
            if res:
                return True
            else:
                return False
        except Exception as e:
            # Handle the exception
            print(f"An error occurred while saving vector data: {e}")
            return None

    @staticmethod
    def update_vector_point(collection_name, id, score):
        """_summary_

        Args:
            collection_name (str): string
            id (int): id of vector point
            score (float): float

        Returns:
            _type_: _description_
        """
        try:
            res = db_client.update_point_metadata(collection_name, id, score)
            if res:
                return True
            else:
                return False
        except Exception as e:
            # Handle the exception
            print(f"An error occurred while updating vector score data: {e}")
            return None

    @staticmethod
    def search_vector_point(collection_name, query_vector, top_results, filters):
        """_summary_

        Args:
            collection_name (str): _description_
            query_vector (list ): array of vector
            top_results (int): number of results by default is 3
            filters (dict): filters if any 

        Returns:
            _type_: _description_
        """
        try:
            return db_client.search_data(collection_name, query_vector, top_results = 3, filters = {})
        except Exception as e:
            print(f"An error occurred while searching vector data: {e}")
            return None

    @staticmethod
    def delete_vector_point(collection_name, ids):
        try:
            """_summary_
            Args:
            collection_name (str): collection name
            ids (list ): ids of vector
            Returns:
                _type_: _description_
            """
            return db_client.delete_vectors_by_metadata(collection_name, ids)
        except Exception as e:
            print(f"An error occurred while searching vector data: {e}")
            return None

    @staticmethod
    def get_point_details(collection_name, id):
        try:
            """_summary_
            Args:
            collection_name (str): collection name
            id (int ): id of vector
            Returns:
                _type_: _description_
            """
            return db_client.get_vector_details_by_id(collection_name, id)
        except Exception as e:
            print(f"An error occurred while searching vector data: {e}")
            return None

    @staticmethod
    def get_all_vector_points(collection_name, limit =20, offset = 0):
        """_summary_

        Args:
            collection_name (str): _description_
            limit (int): limit
            offset (int): offset

        Returns:
            _type_: _description_
        """
        try:
            return db_client.get_all_points_data(collection_name, limit, offset)
        except Exception as e:
            # Handle the exception
            print(f"An error occurred while getting list of all points : {e}")
            return None
    