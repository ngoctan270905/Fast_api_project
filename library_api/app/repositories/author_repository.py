from typing import Optional, List, Dict, Any
from bson import ObjectId
from fastapi.concurrency import run_in_threadpool
from app.core.mongo_database import mongodb_client
from app.schemas.author import AuthorCreate, AuthorUpdate

class AuthorRepository:
    # Hàm khởi tạo
    def __init__(self):
        self.db = mongodb_client.get_database()
        self.collection = self.db.get_collection("authors")

    #
    def _to_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if data and "_id" in data:
            data["id"] = str(data.pop("_id"))
        return data
    # tìm tac gia theo name
    async def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"name": name})

        # def db_call():
        #     return self.collection.find_one({"name": name})
        #
        # author = await run_in_threadpool(db_call)
        # return self._to_json(author)
    # add tác giả
    async def create(self, author_create: AuthorCreate) -> Dict[str, Any]:
        author_data = author_create.model_dump()

        def db_call():
            result = self.collection.insert_one(author_data)
            return self.collection.find_one({"_id": result.inserted_id})

        new_author = await run_in_threadpool(db_call)
        return self._to_json(new_author)
    # tìm theo id
    async def get_by_id(self, author_id: str) -> Optional[Dict[str, Any]]:

        def db_call():
            return self.collection.find_one({"_id": ObjectId(author_id)})

        author = await run_in_threadpool(db_call)
        return self._to_json(author)

    # lấy ds tất cả author
    async def get_all(self) -> List[Dict[str, Any]]:
        def db_call():
            return list(self.collection.find())

        authors = await run_in_threadpool(db_call)

        return [self._to_json(author) for author in authors]

    #update
    async def update(self, author_id: str, author_update: AuthorUpdate) -> Optional[Dict[str, Any]]:
        update_data = author_update.model_dump(exclude_unset=True)

        def db_call():

            self.collection.update_one(
                {"_id": ObjectId(author_id)},
                {"$set": update_data}
            )
            return self.collection.find_one({"_id": ObjectId(author_id)})

        updated_author = await run_in_threadpool(db_call)
        return self._to_json(updated_author)

    #delete
    async def delete(self, author_id: str) -> bool:

        def db_call():

            result = self.collection.delete_one({"_id": ObjectId(author_id)})
            return result.deleted_count > 0

        return await run_in_threadpool(db_call)