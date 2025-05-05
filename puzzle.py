import tkinter as tk
from tkinter import ttk
import time, heapq
from collections import deque

# Estado inicial e objetivo
initial_state = [[3, 4, 6], [5, 8, 0], [2, 1, 7]]
goal_state = [[1, 2, 3], [8, 4, 0], [7, 6, 5]]

# Utilitários
def state_to_tuple(state): return tuple(num for row in state for num in row)
def is_goal(state): return state == goal_state

def find_zero(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j

def get_neighbors(state):
    i, j = find_zero(state)
    moves = [(-1,0),(1,0),(0,-1),(0,1)]
    neighbors = []
    for dx, dy in moves:
        ni, nj = i + dx, j + dy
        if 0 <= ni < 3 and 0 <= nj < 3:
            new_state = [row[:] for row in state]
            new_state[i][j], new_state[ni][nj] = new_state[ni][nj], new_state[i][j]
            neighbors.append(new_state)
    return neighbors

# Heurísticas
def misplaced_tiles(state):
    return sum(1 for i in range(3) for j in range(3) if state[i][j] and state[i][j] != goal_state[i][j])

def manhattan(state):
    return sum(abs(i - x) + abs(j - y)
        for i in range(3) for j in range(3)
        for x in range(3) for y in range(3)
        if state[i][j] != 0 and state[i][j] == goal_state[x][y])

# Busca em Largura (BFS)
def bfs(start):
    frontier = deque([start])
    came_from = {state_to_tuple(start): None}
    while frontier:
        current = frontier.popleft()
        if is_goal(current):
            path, node = [], state_to_tuple(current)
            while node:
                path.append([[node[i*3+j] for j in range(3)] for i in range(3)])
                node = came_from[node]
            return path[::-1]
        for neighbor in get_neighbors(current):
            t = state_to_tuple(neighbor)
            if t not in came_from:
                frontier.append(neighbor)
                came_from[t] = state_to_tuple(current)

# Busca Gulosa
def greedy(start, heuristic):
    frontier = [(heuristic(start), start)]
    came_from = {state_to_tuple(start): None}
    while frontier:
        _, current = heapq.heappop(frontier)
        if is_goal(current):
            path, node = [], state_to_tuple(current)
            while node:
                path.append([[node[i*3+j] for j in range(3)] for i in range(3)])
                node = came_from[node]
            return path[::-1]
        for neighbor in get_neighbors(current):
            t = state_to_tuple(neighbor)
            if t not in came_from:
                heapq.heappush(frontier, (heuristic(neighbor), neighbor))
                came_from[t] = state_to_tuple(current)

# Busca A*
def astar(start, heuristic):
    frontier = [(heuristic(start), 0, start)]
    came_from = {state_to_tuple(start): None}
    cost_so_far = {state_to_tuple(start): 0}
    while frontier:
        _, cost, current = heapq.heappop(frontier)
        if is_goal(current):
            path, node = [], state_to_tuple(current)
            while node:
                path.append([[node[i*3+j] for j in range(3)] for i in range(3)])
                node = came_from[node]
            return path[::-1]
        for neighbor in get_neighbors(current):
            t = state_to_tuple(neighbor)
            new_cost = cost_so_far[state_to_tuple(current)] + 1
            if t not in cost_so_far or new_cost < cost_so_far[t]:
                cost_so_far[t] = new_cost
                heapq.heappush(frontier, (new_cost + heuristic(neighbor), new_cost, neighbor))
                came_from[t] = state_to_tuple(current)

# Interface Gráfica com Tkinter
def draw(canvas, state):
    canvas.delete("all")
    for i in range(3):
        for j in range(3):
            x, y = j * 100, i * 100
            val = state[i][j]
            color = "lightblue" if val else "white"
            canvas.create_rectangle(x, y, x+100, y+100, fill=color)
            if val:
                canvas.create_text(x+50, y+50, text=str(val), font=("Arial", 32))

def run(algorithm):
    if algorithm == "BFS":
        path = bfs(initial_state)
    elif algorithm == "Gulosa":
        path = greedy(initial_state, misplaced_tiles)
    elif algorithm == "A* (h1)":
        path = astar(initial_state, misplaced_tiles)
    elif algorithm == "A* (h2)":
        path = astar(initial_state, manhattan)
    else:
        return
    for state in path:
        draw(canvas, state)
        root.update()
        time.sleep(0.5)

# Inicialização da janela
root = tk.Tk()
root.title("8-Puzzle - Algoritmos de Busca")

canvas = tk.Canvas(root, width=300, height=300)
canvas.grid(row=0, column=0, columnspan=4)
draw(canvas, initial_state)

algo_var = tk.StringVar(value="BFS")
ttk.OptionMenu(root, algo_var, "BFS", "BFS", "Gulosa", "A* (h1)", "A* (h2)").grid(row=1, column=0)
ttk.Button(root, text="Executar", command=lambda: run(algo_var.get())).grid(row=1, column=1)
ttk.Button(root, text="Sair", command=root.quit).grid(row=1, column=2)

root.mainloop()
