from typing import Optional, List, Dict, Any
from bson import ObjectId
from sqlalchemy import select
import uuid
from app.core.mongo_database import mongodb_client
from app.schemas.auth import UserRegister


class UserRepository:
    def __init__(self):
        self.db = mongodb_client.get_database()
        self.collection = self.db.get_collection("users")
        self.oauths = self.db.get_collection("oauth_accounts")

    async def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        return user

    # Truy vấn DB tìm name user
    async def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        user_name = await self.collection.find_one({"username": username})
        return user_name


    # Truy vấm DB tìm email user
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        user_email = await self.collection.find_one({"email": email})
        return user_email


    # Truy vấn DB thêm user
    async def create(self, user_dict: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        return user_dict


    # Truy vấn DB update user
    async def update(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.collection.update_one({"_id": user_id}, {"$set": user_data})
        updated_user = await self.collection.find_one({"_id": ObjectId(user_id)})
        return updated_user


    # Login OAUTH
    async def find_or_create_by_oauth(
        self,
        provider: str,
        account_id: str,
        email: str,
        username: str
    ) -> Dict[str, Any]:
        # 1. Tìm OAuthAccount
        oauth = await self.oauths.find_one({
            "provider": provider,
            "account_id": account_id
        })
        if oauth:
            user = await self.collection.find_one({"_id": oauth["user_id"]})
            if user:
                user["_id"] = str(user["_id"])
                return user

        # 2. Tìm user theo email
        user = await self.collection.find_one({"email": email})
        if user:
            oauth_doc = {
                "provider": provider,
                "account_id": account_id,
                "access_token": "dummy",  # cập nhật sau nếu cần
                "user_id": user["_id"]
            }
            await self.oauths.insert_one(oauth_doc)
            user["_id"] = str(user["_sub"] if "_sub" in user else str(user["_id"]))
            return user

        # 3. Tạo user mới
        base_username = username.replace(" ", "_").lower()
        new_username = base_username
        i = 1
        while await self.collection.find_one({"username": new_username}):
            new_username = f"{base_username}{i}"
            i += 1

        new_user = {
            "username": new_username,
            "email": email,
            "hashed_password": None,
            "is_active": True,
            "email_verified": True,
            "role": "user"
        }
        result = await self.collection.insert_one(new_user)
        new_user["_id"] = result.inserted_id

        oauth_doc = {
            "provider": provider,
            "account_id": account_id,
            "access_token": "dummy",
            "user_id": new_user["_id"]
        }
        await self.oauths.insert_one(oauth_doc)

        new_user["_id"] = str(new_user["_id"])
        return new_user
