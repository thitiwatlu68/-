import tkinter as tk
from tkinter import filedialog, messagebox
import importlib.util
import random
import time
import threading

class MazeGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Solver: Shortest Path Education")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f4f8") # สีพื้นหลังสบายตา

        # ตัวแปรระบบ
        self.cell_size = 40
        self.maze_data = [] # 2D Array: 1=ทาง, 0=กำแพง
        self.rows = 0
        self.cols = 0
        self.node_map = {} # (row, col) -> node_id
        self.reverse_node_map = {} # node_id -> (row, col)
        self.graph = {} # Adjacency List สำหรับส่งให้นักเรียน
        self.student_module = None
        self.path_step = 0
        self.solution_path = []

        # สร้าง UI
        self.create_widgets()
        
        # สร้างเขาวงกตเริ่มต้นเพื่อทดสอบ
        self.generate_random_maze()

    def create_widgets(self):
        # Frame ควบคุมด้านขวา
        control_frame = tk.Frame(self.root, bg="#ffffff", bd=2, relief=tk.GROOVE)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        tk.Label(control_frame, text="Control Panel", font=("Arial", 16, "bold"), bg="#ffffff").pack(pady=10)

        # ปุ่มต่างๆ
        self.btn_load_map = self.create_button(control_frame, "📂 1. Load Maze (.txt)", self.load_map_file, "#3498db")
        self.btn_gen_maze = self.create_button(control_frame, "🎲 2. Random Maze", self.generate_random_maze, "#9b59b6")
        self.btn_load_code = self.create_button(control_frame, "🐍 3. Load Student Code", self.load_student_code, "#e67e22")
        self.btn_solve = self.create_button(control_frame, "🚀 4. Solve Maze", self.solve_maze, "#2ecc71")

        tk.Label(control_frame, text="Status:", bg="#ffffff").pack(pady=(20, 5))
        self.lbl_status = tk.Label(control_frame, text="Ready", fg="gray", bg="#ffffff", wraplength=180)
        self.lbl_status.pack()

        # Canvas แสดงเขาวงกต
        self.canvas_frame = tk.Frame(self.root, bg="#f0f4f8")
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#2c3e50")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def create_button(self, parent, text, command, color):
        btn = tk.Button(parent, text=text, command=command, bg=color, fg="black", 
                        font=("Arial", 12), width=20, pady=5, relief=tk.FLAT)
        btn.pack(pady=5)
        return btn

    def generate_random_maze(self):
        # สร้างเขาวงกตแบบสุ่ม (ใช้ DFS Algorithm เพื่อรับประกันว่ามีทางออก)
        rows, cols = 15, 15
        self.maze_data = [[0 for _ in range(cols)] for _ in range(rows)]
        
        # Helper สำหรับสุ่มสร้างทาง
        def carve(r, c):
            self.maze_data[r][c] = 1
            directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
            random.shuffle(directions)
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and self.maze_data[nr][nc] == 0:
                    self.maze_data[r + dr // 2][c + dc // 2] = 1 # ทุบกำแพงตรงกลาง
                    carve(nr, nc)

        carve(0, 0)
        # บังคับจุดจบให้เป็นทางเดิน
        self.maze_data[rows-1][cols-1] = 1
        
        self.load_maze_data(self.maze_data)
        self.lbl_status.config(text="Random maze generated.")

    def load_map_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not file_path: return
        
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            data = []
            for line in lines:
                row = [int(x) for x in line.strip() if x in '01']
                if row: data.append(row)
            
            self.load_maze_data(data)
            self.lbl_status.config(text=f"Loaded map: {file_path.split('/')[-1]}")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid map file: {e}")

    def load_maze_data(self, data):
        self.maze_data = data
        self.rows = len(data)
        self.cols = len(data[0]) if self.rows > 0 else 0
        self.prepare_graph_data() # แปลงข้อมูลเตรียมส่งให้นักเรียน
        self.draw_maze()

    def prepare_graph_data(self):
        # แปลง Grid เป็น Graph ตามเงื่อนไข: Node 0=Start, Node 1=End
        self.node_map = {}
        self.reverse_node_map = {}
        self.graph = {}
        
        start_pos = (0, 0)
        end_pos = (self.rows - 1, self.cols - 1)

        # 1. กำหนด ID ให้ Start และ End ก่อน
        self.node_map[start_pos] = 0
        self.reverse_node_map[0] = start_pos
        
        self.node_map[end_pos] = 1
        self.reverse_node_map[1] = end_pos

        # 2. กำหนด ID ให้ช่องทางเดินอื่น (เลข 1)
        current_id = 2
        for r in range(self.rows):
            for c in range(self.cols):
                if self.maze_data[r][c] == 1:
                    if (r, c) != start_pos and (r, c) != end_pos:
                        self.node_map[(r, c)] = current_id
                        self.reverse_node_map[current_id] = (r, c)
                        current_id += 1
        
        # 3. สร้าง Adjacency List (Edges)
        # ตรวจสอบเพื่อนบ้าน 4 ทิศ (บน ล่าง ซ้าย ขวา)
        for r in range(self.rows):
            for c in range(self.cols):
                if self.maze_data[r][c] == 1 and (r, c) in self.node_map:
                    u = self.node_map[(r, c)]
                    self.graph[u] = []
                    
                    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                    for dr, dc in directions:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            if self.maze_data[nr][nc] == 1:
                                v = self.node_map[(nr, nc)]
                                self.graph[u].append(v)

    def draw_maze(self):
        self.canvas.delete("all")
        cw = min(800 // self.cols, 600 // self.rows) # ปรับขนาดอัตโนมัติ
        self.cell_size = cw

        for r in range(self.rows):
            for c in range(self.cols):
                x1, y1 = c * cw, r * cw
                x2, y2 = x1 + cw, y1 + cw
                
                # 0=Wall (Dark), 1=Path (Light)
                color = "#34495e" if self.maze_data[r][c] == 0 else "#ecf0f1"
                
                # Highlight Start & End
                if (r, c) == (0, 0): color = "#e74c3c" # Start (Redish but will be overriden by player)
                elif (r, c) == (self.rows-1, self.cols-1): color = "#f1c40f" # End (Yellow)

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#bdc3c7")

        # วาดผู้เล่นที่จุดเริ่มต้น
        self.draw_player(0, 0)

    def draw_player(self, r, c):
        self.canvas.delete("player")
        cw = self.cell_size
        pad = cw * 0.2
        x1, y1 = c * cw + pad, r * cw + pad
        x2, y2 = (c + 1) * cw - pad, (r + 1) * cw - pad
        self.canvas.create_oval(x1, y1, x2, y2, fill="#3498db", outline="white", width=2, tags="player")

    def load_student_code(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if not file_path: return

        try:
            # โหลด module แบบ dynamic
            spec = importlib.util.spec_from_file_location("student_solver", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'find_shortest_path'):
                self.student_module = module
                self.lbl_status.config(text="Code loaded successfully!", fg="green")
            else:
                raise ValueError("Function 'find_shortest_path' not found.")
                
        except Exception as e:
            self.student_module = None
            self.lbl_status.config(text=f"Error: {e}", fg="red")
            messagebox.showerror("Code Error", str(e))

    def solve_maze(self):
        if not self.student_module:
            messagebox.showwarning("Warning", "Please load student code first.")
            return
        
        try:
            # เรียกฟังก์ชั่นของนักเรียน ส่ง Graph ไปให้
            # Input: Dict { node_id: [neighbor_ids] }
            path_nodes = self.student_module.find_shortest_path(self.graph)
            
            if not path_nodes or path_nodes[0] != 0 or path_nodes[-1] != 1:
                messagebox.showerror("Result", "Path invalid or does not start at 0/end at 1.")
                return

            self.solution_path = path_nodes
            self.start_animation()
            
        except Exception as e:
            messagebox.showerror("Execution Error", f"Error in student code: {e}")

    def start_animation(self):
        self.path_step = 0
        self.animate_step()

    def animate_step(self):
        if self.path_step < len(self.solution_path):
            node_id = self.solution_path[self.path_step]
            if node_id in self.reverse_node_map:
                r, c = self.reverse_node_map[node_id]
                self.draw_player(r, c)
                
                # วาดรอยเท้าทิ้งไว้
                cw = self.cell_size
                cx, cy = c * cw + cw/2, r * cw + cw/2
                self.canvas.create_oval(cx-3, cy-3, cx+3, cy+3, fill="#2ecc71", outline="", tags="trail")
                
                self.path_step += 1
                self.root.after(200, self.animate_step) # 200ms delay
        else:
            messagebox.showinfo("Success", "Maze Solved!")

if __name__ == "__main__":
    root = tk.Tk()
    app = MazeGameApp(root)
    root.mainloop()