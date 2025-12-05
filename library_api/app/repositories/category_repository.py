from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.category import Category
# from typing import List, Optional
from sqlmodel import select

from typing import Optional, List, Dict, Any
from bson import ObjectId
from celery.bin.result import result
from fastapi.concurrency import run_in_threadpool
from app.core.mongo_database import mongodb_client
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryRepository:
    def __init__(self):
        self.db = mongodb_client.get_database() #lấy database đã đc kết nối
        self.collection = self.db["categories"] # lấy collection

    # hàm chuyển _id thành id(str)
    def _to_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if data and "_id" in data:
            data["id"] = str(data.pop("_id"))
        return data

    # Lấy all category
    async def get_all_category(self) -> List[Dict[str, Any]]:
        def db_call():
            return list(self.collection.find()) # dùng list để duyệt document
        categories = await run_in_threadpool(db_call)
        return [self._to_json(cat) for cat in categories]

    # Lấy category theo id
    async def get_by_category_id(self, category_id: str) -> Optional[Dict[str, Any]]:
        def db_call():
            return self.collection.find_one({"_id": ObjectId(category_id)})
        category = await run_in_threadpool(db_call)
        return self._to_json(category)

    # tìm tên trong document
    async def get_category_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        def db_call():
            return self.collection.find_one({"name": name})
        category = await run_in_threadpool(db_call)
        return self._to_json(category)

    # Tạo category mới
    async def create_category(self, category_create: CategoryCreate) -> Dict[str, Any]:
        category_data = category_create.model_dump() # chuyeernpydantic schema thành dict
        # hàm đồng bộ
        def db_call():
            result = self.collection.insert_one(category_data)
            return self.collection.find_one({"_id": result.inserted_id}) # tìm document dựa trên _id
        # tránh làm block event lopp
        new_category = await run_in_threadpool(db_call)

        return self._to_json(new_category)

    # Update
    async def update_category(self, category_id: str, category_update: CategoryUpdate) -> Optional[Dict[str, Any]]:
        update_data = category_update.model_dump(exclude_unset=True)
        def db_call():
            self.collection.update_one(
                {"_id": ObjectId(category_id)},
                {"$set": update_data}
            )
            return self.collection.find_one({"_id": ObjectId(category_id)})

        updated_category = await run_in_threadpool(db_call)
        return self._to_json(updated_category)

    # xóa
    async def delete(self, category_id: str) -> bool:
        def db_call():
            result = self.collection.delete_one({"_id": ObjectId(category_id)})
            return result.deleted_count > 0

        return await run_in_threadpool(db_call)
