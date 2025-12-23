# class Node:
#     def __init__(self, value_node, next_node=None):
#         self.value_node = value_node
#         self.next_node = next_node
#
# class LinkedList:
#     def __init__(self):
#         self._node_bat_dau = None
#         self._node_ket_thuc = None
#         self._tong_node = 0
#
#     def insert(self, value_node):
#         # Mỗi node là 1 đôi tượng riêng có value và next nên mỗi lần thêm sẽ tạo 1 node mới
#         node = Node(value_node)
#
#         if not self._node_bat_dau:
#             self._node_bat_dau = self._node_ket_thuc = node
#         else:
#             self._node_ket_thuc.next_node = node
#             self._node_ket_thuc = node
#
#         self._tong_node = self._tong_node + 1
#
#     def __iter__(self):
#         yield from self._iter(self._node_bat_dau)
#
#     def _iter(self, node_bat_dau):
#         if node_bat_dau:
#             yield node_bat_dau.value_node
#             yield from self._iter(node_bat_dau.next_node)
#
#     def __len__(self):
#         return self._tong_node











class Node:
    def __init__(self, value, next=None):
        self.value = value
        self.next = next

class LinkedList:
    def __init__(self):
        self._nodebatdau = None
        self._nodeketthuc = None
        self._tongnode = 0

    def insert(self, value):
        node = Node(value)
        if not self._nodebatdau:
            self._nodebatdau = self._nodeketthuc = node
        else:
            self._nodeketthuc.next = node
            self._nodeketthuc = node

        self._tongnode = self._tongnode + 1


    def __iter__(self):
        yield from self._iter(self._nodebatdau)

    def _iter(self, node):
        if node:
            yield node.value
            yield from self._iter(node.next)

    def __len__(self):
        return self._tongnode







































# # Đây là class Node đại diện cho 1 Nút : Trong nút có value và next value là giá trị và
# # next: là con trỏ để chuyển sang Node tiếp theo, khi không còn giá trị sẽ là None
# class Node(object):
#     def __init__(self, value, next=None):
#         self.value = value
#         self.next = next
#
# # Danh sách liên kết : danh sách sẽ biết được điểm đầu và điểm cuối và tổng số
# class LinkedList(object):
#     def __init__(self):
#         self._head = None
#         self._tail = None
#         self._len = 0
#
#     # hàm thêm phần tử vào danh sách liên kết : dùng value
#     def insert(self, value):
#         node = Node(value)  # mỗi lần thêm sẽ phải tạo 1 Node mới
#         # Nếu chưa có điểm đầu => điểm đầu sẽ bằng điểm cuối =>> None danh sách hiện tại rỗng
#         if not self._head:
#             self._head = self._tail = node
#         # nếu đã có thì sẽ thêm vào cuối danh sách _tail là điểm cuối next là con trỏ chuyển sang Node tiếp theo
#         # ví tail ở cuối nên khi có next sẽ là ví dụ 4 -> None
#         else:
#             self._tail.next = node
#             self._tail = node
#
#         self._len = self._len + 1
#
#     # hàm xóa phần tử cuối cùng trong danh sách liên kết
#     def remove(self, value):
#         node, prev, found = self._find_value(self._head, None, value)
#         # nếu không có node : Node là None thì raise lỗi
#         if not node:
#             raise ValueError
#         if prev: # Nếu có prev
#             prev.next = node.next # thì bỏ qua cái giữa ví dụ 1 2 3 1.next=
#         else: # nếu không có prev : bị None
#             self._head = node.next
#
#         self._len = self._len - 1
#
#     def __contains__(self, value):
#         """
#             Kiểm tra xem một giá trị có tồn tại trong linked list hay không.
#
#             Hàm này được Python tự động gọi khi dùng toán tử `in`,
#             ví dụ:  value in ll
#
#             Cách hoạt động:
#             - Duyệt linked list từ head
#             - So sánh từng node.value với value cần tìm
#             - Trả về True nếu tìm thấy, ngược lại trả về False
#         """
#         _, _, found = self._find_value(self._head, None, value)
#         return found
#
#
#     def __len__(self):
#         """
#            Trả về số lượng phần tử trong linked list.
#
#            Hàm này được Python tự động gọi khi dùng hàm len(),
#            ví dụ: len(ll)
#         """
#         return self._len
#
#
#     def __iter__(self):
#         """
#             Trả về iterator để có thể duyệt linked list bằng vòng for.
#
#             Hàm này được Python tự động gọi khi dùng:
#                 for x in linked_list
#                 list(linked_list)
#
#             Nó bắt đầu duyệt từ node head.
#         """
#         yield from self._iter(self._head)
#
#
#     def _iter(self, node):
#         """
#            Duyệt linked list bắt đầu từ node cho trước và lần lượt
#            yield ra giá trị của từng node.
#
#            Đây là hàm generator, được dùng nội bộ để hỗ trợ __iter__().
#         """
#         if node:
#             yield node.value
#             yield from self._iter(node.next)
#
#
#     # hàm tìm kiếm trong list, tìm kiếm node hiện tại và node trước đó
#     def _find_value(self, crr, prev, value):
#         # nếu crr không phải là None sẽ vòng lặp while để tìm
#         while crr:
#             if crr.value == value: # nếu value của Node = value
#                 return crr, prev, True # => trả về Node hiện tại, node trước đó, và True
#
#             prev = crr
#             crr = crr.next
#
#         return crr, prev, False
#
#
# def test_linkedlist():
#     ll = LinkedList()
#     print(f"test {len(ll)}")
#     # values = [2, 3, 2, 3, 5, -10]
#     # for value in values:
#     #     ll.insert(value)
#     #     print(f"Danh sách liên kết: {list(ll)}")
#     #     print(f"Số phần tử trong danh sách: {len(ll)}")
#     #
#     # # ll.insert(1)
#     # # print(f"Danh sách liên kết: {list(ll)}")
#     # # print(f"Số phần tử trong danh sách: {len(ll)}")
#     #
#     # for value in values:
#     #     ll.remove(value)
#     #     print(f"Danh sách liên kết đã xóa phần tử: {list(ll)}")
#     #     print(f"Số phần tử trong danh sách: {len(ll)}")
#
#     # values = [-100, 23, 3, 2, 1, -10]
#     # for value in values:
#     #     ll.insert(value)
#     #     print(list(ll))
#     #     print(len(ll))
#
#
# test_linkedlist()
