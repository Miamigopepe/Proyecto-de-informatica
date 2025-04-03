from node import Node
from segment import Segment


node1 = Node('A', 0, 0)
node2 = Node('B', 3, 4)
node3 = Node('C', 6, 8)

segment1 = Segment('AB', node1, node2)
segment2 = Segment('BC', node2, node3)


print(segment1)
print(segment2)