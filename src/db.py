import asyncio
import logging
from typing import List

import motor
import motor.motor_asyncio
from pymongo.errors import PyMongoError
from pymongo.results import InsertOneResult

import config_reader
from exceptions import UpdateError, GetOneError, InsertError, GetManyError, DeleteError, MongoConnectionError
from abc import ABC, abstractmethod


class Database(ABC):
    @abstractmethod
    async def insert(self, col_name: str, data: dict, max_retries: int = 3, retry_delay: int = 1) -> str:
        pass

    @abstractmethod
    async def insert_many(self, col_name: str, data: list[dict], max_retries: int = 3, retry_delay: int = 1) -> List[
        str]:
        pass

    @abstractmethod
    async def get_one(self, col_name: str, fltr: dict, max_retries: int = 3, retry_delay: int = 1) -> dict | None:
        pass

    @abstractmethod
    async def get_many(self, col_name: str, fltr: dict = None, max_retries: int = 3, retry_delay: int = 1) -> List[
                                                                                                                  dict] | None:
        pass

    @abstractmethod
    async def update_one(self, col_name: str, fltr: dict, update: dict, max_retries: int = 3,
                         retry_delay: int = 1) -> bool | None:
        pass

    @abstractmethod
    async def update_many(self, col_name: str, fltr: dict, update: dict, max_retries: int = 3,
                          retry_delay: int = 1) -> int:
        pass

    @abstractmethod
    async def replace_one(self, col_name: str, fltr: dict, replacement: dict, max_retries: int = 3,
                          retry_delay: int = 1) -> bool | None:
        pass

    @abstractmethod
    async def delete_one(self, col_name: str, fltr: dict, max_retries: int = 3, retry_delay: int = 1) -> bool | None:
        pass


class Mongo(Database):
    def __init__(self, url: str, database: str):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(url)
        self.db = self.client[database]

    async def insert(self, col_name: str, data: dict, max_retries: int = 3,
                     retry_delay: int = 1) -> str:
        retries = 0
        while retries < max_retries:
            try:
                result: InsertOneResult = await self.db[col_name].insert_one(data)
                return str(result.inserted_id)
            except PyMongoError as err:
                logging.error(f"Error during insert: {err}. Retrying...")
                retries += 1
                await asyncio.sleep(retry_delay)
                if retries == max_retries:
                    error_message = f"Failed to insert data after {max_retries} retries"
                    logging.error(error_message)
                    raise InsertError(error_message) from err

    async def insert_many(self, col_name: str, data: list[dict], max_retries: int = 3,
                          retry_delay: int = 1) -> List[str]:
        retries = 0
        while retries < max_retries:
            try:
                result = await self.db[col_name].insert_many(data)
                return [str(insert_id) for insert_id in result.inserted_ids]
            except PyMongoError as err:
                logging.error(f"Error during insert_many: {err}. Retrying...")
                retries += 1
                await asyncio.sleep(retry_delay)
                if retries == max_retries:
                    error_message = f"Failed to insert data after {max_retries} retries"
                    logging.error(error_message)
                    raise InsertError(error_message) from err

    async def get_one(self, col_name: str, fltr: dict, sort=None, max_retries: int = 3,
                      retry_delay: int = 1) -> dict | None:
        retries = 0
        while retries < max_retries:
            try:
                result = await self.db[col_name].find_one(filter=fltr,
                                                          sort=sort)
                return result
            except PyMongoError as err:
                logging.error(f"Error during find_one: {err}. Retrying...")
                retries += 1
                await asyncio.sleep(retry_delay)
                if retries == max_retries:
                    error_message = f"Failed to find document after {max_retries} retries"
                    logging.error(error_message)
                    raise GetOneError(error_message) from err

    async def get_many(self, col_name: str, fltr: dict = None, max_retries: int = 3, retry_delay: int = 1) -> list:
        retries = 0
        while retries < max_retries:
            try:
                if fltr is None:
                    result = await self.db[col_name].find().to_list(None)
                else:
                    result = await self.db[col_name].find(fltr).to_list(None)
                return result  # WARNING: Maybe this is not the best way to return the data
            except PyMongoError as err:
                logging.error(f"Error during find: {err}. Retrying...")
                retries += 1
                await asyncio.sleep(retry_delay)
                if retries == max_retries:
                    error_message = f"Failed to find documents after {max_retries} retries"
                    logging.error(error_message)
                    raise GetManyError(error_message) from err

    async def update_one(self, col_name: str, fltr: dict, update: dict,
                         max_retries: int = 3, retry_delay: int = 1) -> bool | None:
        retries = 0
        while retries < max_retries:
            try:
                result = await self.db[col_name].update_one(filter=fltr,
                                                            update=update,
                                                            upsert=True)
                return result.modified_count > 0
            except PyMongoError as err:
                error_message = f"Error during update: {err}. Retrying..."
                logging.error(error_message)
                retries += 1
                await asyncio.sleep(retry_delay)
                if retries == max_retries:
                    logging.error(f"Failed to update document after {max_retries} retries")
                    raise UpdateError(error_message) from err

    async def replace_one(self, col_name: str, fltr: dict, replacement: dict,
                          max_retries: int = 3, retry_delay: int = 1) -> bool | None:
        retries = 0
        while retries < max_retries:
            try:
                result = await self.db[col_name].replace_one(filter=fltr,
                                                             replacement=replacement,
                                                             upsert=True)
                return result.modified_count > 0
            except PyMongoError as err:
                error_message = f"Error during replace: {err}. Retrying..."
                logging.error(error_message)
                retries += 1
                await asyncio.sleep(retry_delay)
                if retries == max_retries:
                    logging.error(f"Failed to replace document after {max_retries} retries")
                    raise UpdateError(error_message) from err

    async def update_many(self, col_name: str, fltr: dict, update: dict,
                          max_retries: int = 3, retry_delay: int = 1) -> int:
        retries = 0
        while retries < max_retries:
            try:
                result = await self.db[col_name].update_many(filter=fltr, update=update)
                return result.modified_count
            except PyMongoError as err:
                logging.error(f"Error during update_many: {err}. Retrying...")
                retries += 1
                await asyncio.sleep(retry_delay)
                if retries == max_retries:
                    error_message = f"Failed to update documents after {max_retries} retries"
                    logging.error(error_message)
                    raise UpdateError(error_message) from err

    async def delete_one(self, col_name: str, fltr: dict, max_retries: int = 3, retry_delay: int = 1) -> bool | None:
        retries = 0
        while retries < max_retries:
            try:
                result = await self.db[col_name].delete_one(filter=fltr)
                return result.deleted_count > 0
            except PyMongoError as err:
                error_message = f"Error during delete: {err}. Retrying..."
                logging.error(error_message)
                retries += 1
                await asyncio.sleep(retry_delay)
                if retries == max_retries:
                    logging.error(f"Failed to delete document after {max_retries} retries")
                    raise DeleteError(error_message) from err


try:
    db = Mongo(url=config_reader.config.database.get_secret_value(),
               database=config_reader.config.db_cluster_name.get_secret_value())
except PyMongoError as e:
    logging.error(f"Error in connecting to the database: {e}")
    raise MongoConnectionError("Error in connecting to the database") from e
