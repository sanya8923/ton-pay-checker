from db import Database, db


class DbManager:
    def __init__(self, db: Database):
        self.db = db

    async def add_one(self, col_name: str, data: dict):
        return await self.db.insert(col_name, data)

    async def add_many(self, col_name: str, data: list[dict]):
        return await self.db.insert_many(col_name, data)

    async def get_one(self, col_name: str, fltr: dict, sort=None) -> dict:
        return await self.db.get_one(col_name, fltr, sort)

    async def get_many_async(self, col_name: str, fltr: dict = None) -> list[dict]:
        return await self.db.get_many(col_name, fltr)

    async def get_many(self, col_name: str, fltr: dict = None) -> list[dict]:
        return await self.db.get_many(col_name, fltr)

    async def update_one(self, col_name: str, fltr: dict, update: dict):
        return await self.db.update_one(col_name, fltr, update)

    async def update_many(self, col_name: str, fltr: dict, update: dict):
        return await self.db.update_many(col_name, fltr, update)

    async def replace_one(self, col_name: str, fltr: dict, replacement: dict):
        return await self.db.replace_one(col_name, fltr, replacement)

    async def delete_one(self, col_name: str, fltr: dict):
        return await self.db.delete_one(col_name, fltr)


db_manager: DbManager = DbManager(db)
