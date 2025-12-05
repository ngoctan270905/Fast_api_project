from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

MONGO_CONNECTION_STRING = "mongodb://root:1@localhost:27017"
MONGO_DB_NAME = "fastapi_mongodb"

client = MongoClient(MONGO_CONNECTION_STRING)
db = client[MONGO_DB_NAME]  # Database
users_collection = db["users"]  # Collection

print('Kết nối thành công vs MongoDB')

# Thêm 1 document vào collection
# user1 = {
#     "name": "Tấn",
#     "email": "nguyentandev05@gmail.com",
#     "age": 18,
#     "created_at": datetime.now(),
# }
#
# user_id = users_collection.insert_one(user1).inserted_id
# print(f"user đã được thêm vào collection: {db} , {user_id}")

# Insert nhiều user cùng lúc
# users = [
#     {"name": "Bob", "age": 30, "created_at": datetime.now()},
#     {"name": "Charlie", "age": 20, "created_at": datetime.now()},
# ]
# inserted_ids = users_collection.insert_many(users).inserted_ids
# print("đã thêm nhiều users",db, inserted_ids)

# tìm user

find_user = users_collection.find_one({"name":"Tấn"})
print(f"Tìm thấy người dùng: {find_user}")

filter_user = list(users_collection.find({"age":{"$gte": 20}}))
print(f"users > 20 tuổi laf: {filter_user}")

# # cập nhật user
# update_user = users_collection.update_one(
#     {"name":"Tấn"},
#     {"$set": {"age":20}}
# ).modified_count
# print(f"update_user {update_user}")

# cập nhật nhiều user
# update_users =  users_collection.update_many(
#     {"age":{"$lt": 20}},
#     {"$set": {"status":"youngg"}}
# )
# print(f"Số users đã đc update {update_users}")

# delete dữ liệu
# delete_user = users_collection.delete_one({"name":"Tấn"}).deleted_count
# print(f"số user đã xóa: {delete_user}")

# xóa nhiều
delete_users = users_collection.delete_many({"age":{"$gte": 20}}).deleted_count
print(f"đã xóa số user: {delete_users}")

