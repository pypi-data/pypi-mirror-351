import logging
logger = logging.getLogger("InputstreamClient")

from acelerai_inputstream.cache_manager import CacheManager
from acelerai_inputstream.http_aceler import AcelerAIHttpClient
from acelerai_inputstream.utils import CustomJSONEncoder, load_full_object
import asyncio
from datetime import datetime
import hashlib
import os
import json
from acelerai_inputstream.models.inputstream import INSERTION_MODE, Inputstream, InputstreamStatus, InputstreamType

class InputstreamClient:
    """
    Client to interact with ACELER.AI inputstreams
    """

    def __init__(self, token:str, cache_options:dict = None):
        """
        Constructor for LocalInputstream
        :param token: Token to authenticate with ACELER.AI
        :param cache_options: { duration_data: int, duration_inputstream: int } | None
        """        
        self.acelerai_client = AcelerAIHttpClient(token) 
        self.cache_manager = CacheManager(cache_options)
        self.__mode = os.environ.get("EXEC_LOCATION", "LOCAL")


    def __get_inputstream(self, ikey:str) -> Inputstream:
        inputstream = self.acelerai_client.get_inputstream_by_ikey(ikey)
        return inputstream

    async def __allData(self, ikey, query):
        inputstream = self.acelerai_client.get_inputstream_by_ikey(ikey)
        logger.info(f"Getting inputstream with ikey: {ikey}, Name {inputstream.Name}  from ACELER.AI...")
        
        if not os.path.exists(f".acelerai_cache/")               : os.mkdir(f".acelerai_cache/")
        if not os.path.exists(f".acelerai_cache/data/")          : os.mkdir(f".acelerai_cache/data/")
        if not os.path.exists(f".acelerai_cache/data/{ikey}/")   : os.mkdir(f".acelerai_cache/data/{ikey}/")

        logger.info('Downloading data, please wait...')
        start_time = datetime.utcnow()

        await self.acelerai_client.fetch_bigpage(ikey, query)          

        query_str = json.dumps(query, cls=CustomJSONEncoder)
        query_hash = hashlib.sha256(query_str.encode()).hexdigest()
        file_name = f".acelerai_cache/data/{ikey}/{query_hash}.msgpack"
        if not os.path.exists(file_name)   : return False

        end_time = datetime.utcnow()
        logger.info(f"Total time for downloading all data: {round((end_time - start_time).total_seconds()/60, 2)} minutes")
    
        return True


    async def __get_data(self, ikey:str, query:str | dict, mode:str, cache:bool, delete_id:bool=True) -> list[dict]:
        try:
            logger.info(f"Cache: {cache}")
            logger.info(f"Mode: {self.__mode}")
            # TODO: si el find y el find_one pueden compartir el mismo query_hash, dando error
            query_str = json.dumps(query, cls=CustomJSONEncoder)
            query_hash = hashlib.sha256(query_str.encode()).hexdigest()

            logger.info(f"Getting data...")

            if not cache:
                if os.path.exists(f".acelerai_cache/data/{ikey}/{query_hash}.msgpack"):
                    os.remove(f".acelerai_cache/data/{ikey}/{query_hash}.msgpack")

            data = self.cache_manager.get_data(ikey, query_hash) if cache and self.__mode=='LOCAL' else None
            if data is None:
                has_data = False
                if mode == "find_one" :         has_data = await self.acelerai_client.find_one(ikey, query)
                elif mode == "aggregate":         has_data = await self.acelerai_client.aggregate(ikey, query)
                if   mode == "find_singlethread": has_data = await self.__allData(ikey, query)
                
                # if the query or result is empty, return empty list
                if has_data:
                    self.cache_manager.set_data(ikey, query_hash)
                    output_file = f".acelerai_cache/data/{ikey}/{query_hash}.msgpack"
                    data = load_full_object(output_file)
                else:
                    return []

            return data
        except Exception as e:
            raise e


    def get_inputstream_schema(self, ikey:str) -> dict:
        """
        return Inputstream schema
        params:
            ikey: str
            cache: bool = True -> if True, use cache if exists and is not expired
        """
        inputstream = self.__get_inputstream(ikey)
        return json.loads(inputstream.Schema)


    async def find_internal(self, ikey:str, query:dict, cache:bool=True, delete_id:bool=True):
        """
        return data from inputstream
        params:
            ikey: str -> key connection
            query: dict
            cache: bool = True -> if True, use cache if exists and is not expired
        """
        mode = "find_singlethread"
        return await self.__get_data(ikey, query, mode, cache, delete_id)
    
    
    async def find_external(self, ikey:str, dynamic_values:str | dict = {}, cache:bool=True):
        """
        return data from inputstream
        params:
            ikey: str -> key connection to external inputstream
            query: dict
            cache: bool = True -> if True, use cache if exists and is not expired
        """
        mode = "find_singlethread"
        return await self.__get_data(ikey, dynamic_values, mode, cache, False)


    async def find_one(self, ikey:str, query:dict, cache:bool=True):
        """
        return one data from inputstream
        params:
            collection: str
            query: dict
        """
        mode = "find_one"
        data = await self.__get_data(ikey, query, mode, cache)
        if len(data) == 0: return None
        return data[0]


    async def execute_query_external(self, conn_key:str, query:str | dict, cache:bool=True):
        """
        return data from external inputstream
        Please note: if your connection is to MongoDB, the query must be as follows: {"collection_name":"your_collection", "query":'{your_query}'}
        params:
            conn_key: str
            query: dict | str
            cache: bool = True -> if True, use cache if exists and is not expired
        """
        try:   
            if isinstance(query, dict):
                query = json.dumps(query, cls=CustomJSONEncoder)
            if not isinstance(query, str): raise Exception("Query must be a string or a dictionary")
        
            query_str = json.dumps(query, cls=CustomJSONEncoder)
            query_hash = hashlib.sha256(query_str.encode()).hexdigest()
            
            logger.info('Downloading data, please wait...')
            start_time = datetime.utcnow()

            if not cache:
                if os.path.exists(f".acelerai_cache/data/{conn_key}/{query_hash}.msgpack"):
                    os.remove(f".acelerai_cache/data/{conn_key}/{query_hash}.msgpack")
                    
            data = self.cache_manager.get_data(conn_key, query_hash) if cache and self.__mode=='LOCAL' else None
            has_data = False
            if data is None:
                tasks = []
                tasks.append(self.acelerai_client.execute_external_query(conn_key, query))
                await asyncio.gather(*tasks)
                has_data = True

                if has_data: 
                    self.cache_manager.set_data(conn_key, query_hash)
                    output_file = f".acelerai_cache/data/{conn_key}/{query_hash}.msgpack"
                    data = load_full_object(output_file)
                            
            end_time = datetime.utcnow()
            logger.info(f"Total time for downloading all data: {round((end_time - start_time).total_seconds()/60, 2)} minutes")
            
            return data

        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return None
    

    async def execute_command_external(self, conn_key:str, query:str | dict):
        """
        return if command was executed successfully or not
        params: 
            conn_key: str
            query: dict | str
            cache: bool = True -> if True, use cache if exists and is not expired 
        """
        try:     
            if isinstance(query, dict):
                query = json.dumps(query, cls=CustomJSONEncoder)
            if not isinstance(query, str): raise Exception("Query must be a string or a dictionary")
            
            result = await self.acelerai_client.execute_external_command(conn_key, query)
            if result: return True
            return False
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return False
        
        
    async def get_data_aggregate(self, ikey:str, pipeline: list[dict], cache:bool=True):
        """
        return data from inputstream
        params:
            ikey: str
            query: list[dict]
        """
        if not all(isinstance(x, dict) for x in pipeline):      raise Exception("Invalid pipeline, the steps must be dictionaries")
        if len(pipeline) == 0:                                  raise Exception("Invalid pipeline, length must be greater than 0" )
        if any("$out" in x or "$merge" in x for x in pipeline): raise Exception("Invalid pipeline, write operations not allowed"  )

        mode = "aggregate"
        return await self.__get_data(ikey, pipeline, mode, cache)  


    async def __validate_data_async(self, d, schema, schema_validator):
        try:
            schema_validator(d)
            return None  # Si no hay errores, retornamos None
        except Exception as e:
            return f"Error validating data: {e}"  # Devolvemos el error


    async def insert_data_external(self, conn_key:str, data:list[dict], table: str):
        """
        insert data into external connection
        params:
            ikey: str -> key connection
            data: list[dict] -> data to insert
            table: str -> table name
        """
        # validate
        if not isinstance(data, list): raise Exception("Data must be a list of dictionaries")
        if table == '': raise Exception("Table name is required when inserting to a native inputstream")

        logger.info('Inserting data, please wait...')
        
        start_time = datetime.utcnow()
        result = await self.acelerai_client.insert_data_big_external(conn_key, table, data)
        endt = datetime.utcnow()
        if result:
            logger.info(f'SUCCESS: {len(data)} registries inserted successfully in {(endt - start_time).total_seconds() / 60} minutes')
        else:
            logger.info(f'FAIL: inserting {len(data)} records, total time:  {(endt - start_time).total_seconds() / 60} minutes, please see messages for more info.')

    async def insert_data(self, 
        ikey:str, 
        data:list[dict], 
        mode:INSERTION_MODE = INSERTION_MODE.REPLACE, 
        wait_response = True, 
        batch_size:int = 10000,
        validate_schema = True
    ):
        """
        validate data against inputstream JsonSchema and insert into inputstream collection
        params:
            ikey: str
            data: list[dict]
            mode: INSERTION_MODE = INSERTION_MODE.REPLACE -> insertion mode
            wait_response: bool = True -> if True, wait for response from server
            batch_size: int = 1000 -> batch size for insert data
            cache: bool = True -> if True, use cache if exists and is not expired
            validate_schema: bool = True -> if True, validate data against inputstream schema
        """
        
        start = datetime.utcnow()
        inputstream:Inputstream = self.__get_inputstream(ikey)
        logger.debug(f'Demoró {(datetime.utcnow() - start).total_seconds()} segs en obtener el inputstream')

        if inputstream.InputstreamType == InputstreamType.Native:  raise Exception("Inputstream must be type InSystem, please use the insert_data_external method")
        if not isinstance(data, list):  raise Exception("Data must be a list of dictionaries")
        if inputstream.Status != InputstreamStatus.Exposed:
            logger.warning(f"Inputstream is not exposed, status: {inputstream.Status}")
            self.acelerai_client.send_example(ikey, data[0])
            logger.info(f"Example data sent to ACELER.AI for schema validation, please expose the inputstream to insert data.")
            return

        # if validate_schema:
        #     start = datetime.utcnow()
        #     schema = json.loads(inputstream.Schema)
        #     schema_validator = fastjsonschema.compile(schema)
        #     resultados = await asyncio.gather(*(self.__validate_data_async(d, schema, schema_validator) for d in data))

        #     # Manejo de errores
        #     errores = [error for error in resultados if error is not None]
        #     if errores:
        #         for error in errores:
        #             logger.error(error)
        #         raise Exception("Hubo errores durante la validación de datos.")
            
        #     logger.debug(f'Demoró {(datetime.utcnow() - start).total_seconds()} segs en validar los datos')

        logger.info('Inserting data, please wait...')
        start = datetime.utcnow()
        tasks, batch_idx = [], 1
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            tasks.append(self.acelerai_client.insert_data(ikey, batch, mode, wait_response, batch_idx, len(batch)))
            batch_idx += 1
        await asyncio.gather(*tasks)
        
        logger.info(f'{len(data)} registries sent successfully in {(datetime.utcnow() - start).total_seconds() / 60} minutes')
        

    async def remove_documents(self, ikey:str, query:dict) -> int:
        """
        delete data from inputstream
        params:
            ikey: str
            query: dict
        """
        docs = await self.acelerai_client.remove_documents(ikey, query)
        return docs
 

    async def clear_inputstream(self, ikey:str) -> int:
        """
        delete all data from inputstream
        params:
            ikey: str
        """
        docs = await self.acelerai_client.clear_inputstream(ikey)
        return docs

    def upload_asset(self, pkey, file_path, storage_path=''):
        """
        Upload file to the asset storage
        params:
            path: str -> path to the file
        """
        try:
           self.acelerai_client.upload_asset(file_path, pkey, storage_path)

        except Exception as e:
            logger.error(f"{e}")
    
    def get_asset(self, pkey, asset_name, path="", id=None):
        """
        Download file from the asset storage
        params:
            asset_name: str -> asset name"
        """
        try:
            asset = self.acelerai_client.get_asset(asset_name, pkey, id)

             # Crear la carpeta si no existe
            folder = os.path.dirname(path)
            if folder and not os.path.exists(folder):
                os.makedirs(folder)

            if path == "": path = f"{asset_name}"
            with open(path, 'wb') as f:
                f.write(asset)

        except Exception as e:
            logger.error(f"{e}")

    def delete_asset(self, pkey, asset_name, id=None, complete=False):
        """
        Delete file from the asset storage. If an Id is not provided, the last one will be deleted.
        params:
            asset_name: str -> asset name
            id: str -> asset id, optional
            complete: boolean -> if True, delete also the file from the storage
        """
        try:
            self.acelerai_client.delete_asset(pkey, asset_name, id, complete)

        except Exception as e:
            logger.error(f"{e}")

    def list_assets(self, pkey):
        """
        List assets in the asset storage of the project
        """
        try:
            assets = self.acelerai_client.list_assets(pkey)
            assets_list = json.loads(assets.decode('utf-8'))['data']['data']

            list = []
            for asset in assets_list:
                formatted_asset = {}
                formatted_asset['id'] = asset['id']
                formatted_asset['name'] = asset['name']
                formatted_asset['createdOn'] = asset['createdOn']
                list.append(formatted_asset)

            return list

        except Exception as e:
            logger.error(f"{e}")
