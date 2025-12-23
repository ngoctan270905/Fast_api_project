from data_structures.linked_lists.list_class import LinkedList, Node


# def remove_duplicates(ll: LinkedList) -> None:
#     seen = set()
#     current = ll._head
#     prev = None
#
#     while current:
#
#         # --------------- GIÁ TRỊ CHƯA XUẤT HIỆN -----------------
#         if current.value not in seen:
#             seen.add(current.value) # đánh dấu đã gặp
#             print(f"Đã ghi nhớ node: {current.value} ")
#             prev = current
#             current = current.next
#
#         # ---------------- GÍA TRỊ BỊ TRÙNG -----------
#         else:
#             print(f"Node {current.value} này trùng rồi nhé nhưng nó là head nên sẽ giữ nguyên")
#             xoa = current.value
#             # ----- Nếu Node cần xóa chính là head ---------
#             if current == ll._head:
#
#                 ll._head = current.next # nếu node là head = current thì rời node sang current
#                 current = ll._head
#
#
#             else:
#                 print(f"Sẽ xóa 1 ở đằng sau")
#                 prev.next = current.next # bỏ qua current
#                 current = current.next
#
#             ll._len = ll._len - 1
#             print(f"Đã xóa node trùng {xoa} ")
#
#
#
# ll = LinkedList()
# values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1]
# for value in values:
#     ll.insert(value)
# print(f"Danh sách ban đầu: {list(ll)}")
# remove_duplicates(ll)
# print(f"Danh sách sau khi check: {list(ll)}")

# def remove_duplicates(ll: LinkedList) -> None:
#     luu_tru = set()
#     node_hien_tai = ll._head
#     node_truoc_do = None
#
#     while node_hien_tai:
#         luu_tru_node_hien_tai = node_hien_tai.value
#         if node_hien_tai.value not in luu_tru:
#             print(f"Node này chưa co se được lưu lại {node_hien_tai.value}")
#             luu_tru.add(node_hien_tai.value) # lưu lại
#             node_truoc_do = node_hien_tai
#             node_hien_tai = node_hien_tai.next
#
#         else:
#             print(f"Node này đã được lưu sẽ bị xóa à quên đây là head nên ko bị xóa đâu")
#             if node_hien_tai == ll._head:
#                 ll._head = node_hien_tai.next
#                 node_hien_tai = ll._head
#
#             else:
#                 print(f"Node này sẽ bị xóa {luu_tru_node_hien_tai}")
#                 node_truoc_do.next = node_hien_tai.next
#                 node_hien_tai = node_hien_tai.next
#
#             ll._len = ll._len - 1
#
# ll = LinkedList()
# values = [1, 2, 3, 4, 5, 6, 1, 2, 3]
# print("Bắt đầu vòng lặp để xóa trùng")
# for v in values:
#     ll.insert(v)
# print(f"Đã lặp xong danh sach ban đầu là: {list(ll)}")
# remove_duplicates(ll)
# print(f"Danh sách sau khi xóa node trùng: {list(ll)}")
# print(f"Số phần tử còn lại: {len(ll)}")

# def xoa_node_trung(ll: LinkedList)-> None:
#     luu_tru_node = set()
#     node_hien_tai = ll._node_bat_dau
#     node_truoc_do = None
#
#     while node_hien_tai:
#         print(f"Bắt đầu duyệt node {node_hien_tai.value_node}")
#         if node_hien_tai.value_node not in luu_tru_node:
#             print(f"Node {node_hien_tai.value_node} ko có trong biến lưu trữ")
#             luu_tru_node.add(node_hien_tai.value_node) # lưu trữ vào set
#             # Dừng thực thi chuyển sang node khác
#             node_truoc_do = node_hien_tai
#             node_hien_tai = node_hien_tai.next_node
#
#         else:
#             print(f"Node {node_hien_tai.value_node} đã có trong danh sách")
#             # -- Nếu node hiện tại là head
#             if node_hien_tai == ll._node_bat_dau:
#                 ll._head = node_hien_tai.next_node
#                 node_hien_tai = ll._node_bat_dau
#             else:
#                 node_truoc_do.next_node = node_hien_tai.next_node
#                 node_hien_tai = node_hien_tai.next_node
#
#             ll._tong_node = ll._tong_node - 1
#
#
#
# ll = LinkedList()
# values =  [1,2,3,4,1,2,3]
# for value in values:
#     ll.insert(value)
#
# print(f"Ds ban đầu :{list(ll)}")
# xoa_node_trung(ll)
# print(f"Ds sau khi xóa {list(ll)}")
# print(f"Tổng node còn trong ds là {len(ll)}")



# def remove_duplicates(linked_list: LinkedList) -> None:
#     luu_tru_node = set()
#     node_bat_dau = linked_list._nodebatdau
#     node_truoc_do = None
#
#     while node_bat_dau:
#
#         if node_bat_dau.value not in luu_tru_node:
#             print(f"Ds node chưa có trong lưu trữ : {node_bat_dau.value}")
#             luu_tru_node.add(node_bat_dau.value)
#             node_truoc_do = node_bat_dau
#             node_bat_dau = node_bat_dau.next
#         else:
#             print(f"Ds đã có trong lưu trữ nên sẽ bịxoasa : {node_bat_dau.value}")
#
#             node_truoc_do.next = node_bat_dau.next
#             node_bat_dau = node_bat_dau.next
#
#             linked_list._tongnode = linked_list._tongnode - 1
#
#
# linked_list = LinkedList()
# values = [1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 2, 3, 1]
# for value in values:
#     linked_list.insert(value)
#
# print(f"ds trớc {list(linked_list)}")
# remove_duplicates(linked_list)
# print(f"ds sau {list(linked_list)}")

# def nth_from_end(linked_list: LinkedList, n: int):
#     first = linked_list._nodebatdau
#     second = linked_list._nodebatdau
#
#     # Dịch frist trước
#     for _ in range(n - 1):
#         print(f"Đi vào đây")
#         if not first:
#             return None
#         print(f"First đủ độ dài")
#         first = first.next
#         print(f"First sau khi dịch là: {first.value}")
#
#     if not first:
#         return None
#
#     # Chỉ lặp khi first.next là node hợp lệ khi == None sẽ dừng lại
#     while first.next:
#         first = first.next
#         second = second.next
#
#     return second.value
#
# linked_list = LinkedList()
# values = [1, 2, 3, 4, 5]
#
# for value in values:
#     linked_list.insert(value)
#
# print(f"ds trớc {list(linked_list)}")
# print(nth_from_end(linked_list, 1))

# def nth_from_end(ll: LinkedList, n: int):
#     first = ll._nodebatdau
#     second = ll._nodebatdau
#
#     for _ in range(n-1):
#         if not first:
#             return None
#         first = first.next
#
#     while first.next:
#         first = first.next
#         second = second.next
#
#     return second.value
#
# ll = LinkedList()
# values =   [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# for value in values:
#     ll.insert(value)
#
# print(f"Danh sách ban đầu: {list(ll)}")
# print(f"Vị trí thứ 2 trong ds tính từ cuối là {(nth_from_end(ll, 2))}")



def remove_node(node: Node):
    if not node or not node.next:
        raise Exception("Lỗi")
    # Copy bản sao của next sang node hin tại
    node.value = node.next.value
    node.next = node.next.next

ll = LinkedList()
values = [1,2,3,4,5]
for value in values:
    ll.insert(value)

print(f"Danh sách ban đầu: {list(ll)}")
cur = ll._nodebatdau

while cur and cur.value != 4:
    cur = cur.next

    # xóa node 3
remove_node(cur)
print("Sau khi xóa:", list(ll))










