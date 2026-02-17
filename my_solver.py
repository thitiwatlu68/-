# my_solver.py
from collections import deque

def find_shortest_path(graph):
    """
    ฟังก์ชันหาเส้นทางที่สั้นที่สุด
    :param graph: Dictionary แสดงกราฟ { node_id: [neighbor_id1, neighbor_id2, ...] }
                  โดย node 0 คือจุดเริ่มต้น และ node 1 คือจุดหมาย
    :return: List ของ node_id เรียงตามลำดับการเดิน เช่น [0, 5, 8, ..., 1]
    """
    
    start_node = 0
    end_node = 1
    
    # --- พื้นที่ให้นักเรียนเขียนโค้ด ---
   # --- 1. เลือกโหมดตรงนี้ (สลับระหว่าง "DFS" หรือ "BFS") ---
    mode = "DFS" 
    print(f"กำลังค้นหาทางออกด้วยวิธี: {mode}")
    
    if mode == "DFS":
        return find_path_dfs(graph, start_node, end_node)
    else:
        return find_path_bfs(graph, start_node, end_node)

# --- 2. ฟังก์ชัน BFS 
def find_path_bfs(graph, start, end):
    queue = deque([(start, [start])])
    visited = set()
    while queue:
        node, path = queue.popleft()
        if node == end:
            return path
        if node not in visited:
            visited.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
    return []

# --- 3. ฟังก์ชัน DFS
def find_path_dfs(graph, start, end):
    stack = [(start, [start])]
    visited = set()
    while stack:
        node, path = stack.pop()
        if node == end:
            return path
        if node not in visited:
            visited.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    stack.append((neighbor, path + [neighbor]))
    return []