import random

def initialize_maze(rows, cols):
    maze = [[0 for _ in range(cols)] for _ in range(rows)]
    return maze

def generate_maze(rows, cols):
    if rows%2 == 0:
        rows += 1
    if cols%2 == 0:
        cols += 1
    maze = initialize_maze(rows, cols)

    start_row, start_col = 0, 0
    maze[start_row][start_col] = 1

    walls = []

    def add_walls(now_row, now_col):
        for dr, dc in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
            new_row, new_col = now_row + dr, now_col + dc
            if 0 <= new_row < rows and 0 <= new_col < cols:
                if maze[new_row][new_col] == 0:
                    walls_r = now_row + dr // 2
                    walls_c = now_col + dc // 2
                    walls.append((walls_r, walls_c, new_row, new_col))

    add_walls(start_row, start_col)
    while walls:
        wall = random.choice(walls)
        walls.remove(wall)
        wall_row, wall_col, new_row, new_col = wall
        if maze[new_row][new_col] == 0:
            maze[wall_row][wall_col] = 1
            maze[new_row][new_col] = 1
            add_walls(new_row, new_col)

    return maze

def main():
    try:
        print("=== โปรแกรมสร้างเขาวงกตด้วย Prim's Algorithm ===")
        N = int(input("กรอกจํานวนแถว (Rows): "))
        M = int(input("กรอกจํานวนหลัก (Cols): "))
        filename = input("ตั้งชื่อไฟล์ผลลัพธ์ (เช่น map01.txt): ")
        maze = generate_maze(N, M)
        with open(filename, 'w') as f:
            for row in maze:
                f.write(' '.join(map(str, row)) + '\n')
        print(f"เขาวงกตถูกสร้างและบันทึกในไฟล์ {filename} เรียบร้อยแล้ว!")
    except ValueError:
        print("กรุณากรอกตัวเลขที่ถูกต้องสำหรับแถวและหลัก.")
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    main()