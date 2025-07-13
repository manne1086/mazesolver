import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import random
import heapq
from datetime import datetime

st.set_page_config(page_title="Maze Generator & Solver", layout="wide")

# Initialize session state variables
if 'show_modal' not in st.session_state:
    st.session_state.show_modal = False

# Directions: N, S, E, W
DIRS = [(0, -1), (0, 1), (1, 0), (-1, 0)]

# Visualization function
def draw_maze(grid, path=None, is_solving=False):
    fig, ax = plt.subplots(figsize=(2, 2))
    # Set dark background for the grid
    ax.set_facecolor('#0a0a0a')  # Dark background
    fig.patch.set_facecolor('#0a0a0a')
    
    # Create custom colormap for the maze
    if is_solving:
        cmap = plt.cm.colors.ListedColormap(['#0a0a0a', '#ffffff', '#4a4a4a'])  # Dark background, white walls, gray visited
    else:
        cmap = plt.cm.colors.ListedColormap(['#0a0a0a', '#ffffff'])  # Dark background, white walls
    
    ax.imshow(grid, cmap=cmap)
    if path:
        y_coords, x_coords = zip(*path)
        # Draw shadow first
        ax.plot(x_coords, y_coords, color='#ff0000', linewidth=1.2, alpha=0.3)  # Shadow effect
        # Draw main path
        ax.plot(x_coords, y_coords, color='#ff0000', linewidth=0.8, alpha=0.8)  # Main glowing red path
        ax.plot(path[0][1], path[0][0], marker='o', color='#00ffff', label='Start', markersize=1)  # Cyan start
        ax.plot(path[-1][1], path[-1][0], marker='$\u2691$', color='#ffff00', label='End', markersize=5)  # Yellow end
        ax.legend(loc='upper right', fontsize=2, facecolor='#0a0a0a', edgecolor='#ffffff', labelcolor='#ffffff')
    ax.set_xticks([])
    ax.set_yticks([])
    plt.tight_layout(pad=0.05)
    return fig

# Recursive Backtracking Maze Generator
def recursive_backtracking(width, height, visualize=False, speed=0.0001):
    maze = np.ones((height, width), dtype=int)
    # Start from a single point (1,1)
    start_y, start_x = 1, 1
    maze[start_y][start_x] = 0
    stack = [(start_y, start_x)]
    canvas = st.empty()
    while stack:
        y, x = stack[-1]
        # Get unvisited neighbors
        neighbors = []
        for dx, dy in DIRS:
            nx, ny = x + dx*2, y + dy*2
            if 0 < ny < height-1 and 0 < nx < width-1 and maze[ny][nx] == 1:
                neighbors.append((nx, ny, dx, dy))
        if neighbors:
            # Choose a random unvisited neighbor
            nx, ny, dx, dy = random.choice(neighbors)
            # Carve a path to the neighbor
            maze[y + dy][x + dx] = 0
            maze[ny][nx] = 0
            # Move to the neighbor
            stack.append((ny, nx))
            if visualize:
                fig = draw_maze(maze.copy(), is_solving=False)
                canvas.pyplot(fig)
                plt.close(fig)
                time.sleep(speed)
        else:
            # Backtrack
            stack.pop()
    # Add some random paths to create multiple solutions
    for _ in range(width * height // 20):  # Reduced number of additional paths
        y, x = random.randint(1, height-2), random.randint(1, width-2)
        if maze[y][x] == 1:
            maze[y][x] = 0

    return maze

# Prim's Algorithm Maze Generator (Improved Efficiency)
def prims_algorithm(width, height, visualize=False, speed=0.0001):
    maze = np.ones((height, width), dtype=int)
    maze[1][1] = 0
    walls = []
    canvas = st.empty()
    # Add multiple starting points
    start_points = [(1, 1), (1, width-2), (height-2, 1), (height-2, width-2)]
    for start in start_points:
        maze[start] = 0
        for dx, dy in DIRS:
            nx, ny = start[1] + dx * 2, start[0] + dy * 2
            if 0 < nx < width and 0 < ny < height:
                walls.append((start[1] + dx, start[0] + dy, start[1], start[0], nx, ny))
    while walls:
        wx, wy, x1, y1, x2, y2 = walls.pop(random.randint(0, len(walls) - 1))
        if maze[y2][x2] == 1:
            maze[wy][wx] = 0
            maze[y2][x2] = 0
            for dx, dy in DIRS:
                nx, ny = x2 + dx * 2, y2 + dy * 2
                if 0 < nx < width and 0 < ny < height and maze[ny][nx] == 1:
                    walls.append((x2 + dx, y2 + dy, x2, y2, nx, ny))
            if visualize:
                fig = draw_maze(maze.copy(), is_solving=False)
                canvas.pyplot(fig)
                plt.close(fig)
                time.sleep(speed)
    # Add some random paths to create multiple solutions
    for _ in range(width * height // 10):  # Add paths proportional to maze size
        y, x = random.randint(1, height-2), random.randint(1, width-2)
        if maze[y][x] == 1:
            maze[y][x] = 0
    return maze

# Kruskal's Algorithm Maze Generator
def kruskals_algorithm(width, height, visualize=False, speed=0.0001):
    maze = np.ones((height, width), dtype=int)
    canvas = st.empty()
    
    # Create a list of all possible walls
    walls = []
    for y in range(1, height-1, 2):
        for x in range(1, width-1, 2):
            # Add walls to the right and bottom of each cell
            if x < width-2:
                walls.append(((y, x), (y, x+2), (y, x+1)))
            if y < height-2:
                walls.append(((y, x), (y+2, x), (y+1, x)))
    
    # Shuffle the walls
    random.shuffle(walls)
    
    # Initialize disjoint set
    parent = {}
    rank = {}
    
    def find(x):
        if x not in parent:
            parent[x] = x
            rank[x] = 0
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        px, py = find(x), find(y)
        if px == py:
            return False
        if rank[px] < rank[py]:
            parent[px] = py
        elif rank[px] > rank[py]:
            parent[py] = px
        else:
            parent[py] = px
            rank[px] += 1
        return True
    
    # Process each wall
    for (cell1, cell2, wall) in walls:
        if union(cell1, cell2):
            # Remove the wall
            maze[wall] = 0
            # Make the cells paths
            maze[cell1] = 0
            maze[cell2] = 0
            
            if visualize:
                fig = draw_maze(maze.copy(), is_solving=False)
                canvas.pyplot(fig)
                plt.close(fig)
                time.sleep(speed)
    
    # Add some random paths to create multiple solutions
    for _ in range(width * height // 20):
        y, x = random.randint(1, height-2), random.randint(1, width-2)
        if maze[y][x] == 1:
            maze[y][x] = 0
    
    return maze

# BFS Maze Solver
def solve_maze_bfs(maze, start, end, visualize=False, speed=0.0001):
    start_time = time.time()
    height, width = maze.shape
    visited = np.zeros_like(maze)
    prev = {}
    queue = [start]
    visited[start] = 1
    canvas = st.empty()
    while queue:
        y, x = queue.pop(0)
        if (y, x) == end:
            break
        for dx, dy in DIRS:
            nx, ny = x + dx, y + dy
            if 0 <= ny < height and 0 <= nx < width and maze[ny][nx] == 0 and not visited[ny][nx]:
                visited[ny][nx] = 1
                prev[(ny, nx)] = (y, x)
                queue.append((ny, nx))
                if visualize:
                    temp_maze = maze.copy()
                    temp_maze[visited == 1] = 2
                    for (py, px) in queue:
                        temp_maze[py][px] = 2
                    fig = draw_maze(temp_maze, is_solving=True)
                    canvas.pyplot(fig)
                    plt.close(fig)
                    time.sleep(speed)
    path = []
    curr = end
    while curr in prev:
        path.append(curr)
        curr = prev[curr]
    path.append(start)
    path.reverse()
    if visualize:
        for i in range(len(path)):
            current_path = path[:i+1]
            temp_maze = maze.copy()
            temp_maze[visited == 1] = 2
            fig = draw_maze(temp_maze, path=current_path, is_solving=True)
            canvas.pyplot(fig)
            plt.close(fig)
            time.sleep(speed)
    end_time = time.time()
    return path, end_time - start_time

# A* Maze Solver
def solve_maze_astar(maze, start, end, visualize=False, speed=0.0001):
    start_time = time.time()
    height, width = maze.shape
    g_score = {start: 0}
    f_score = {start: abs(end[0] - start[0]) + abs(end[1] - start[1])}
    open_set = [(f_score[start], start)]
    came_from = {}
    visited = np.zeros_like(maze)
    canvas = st.empty()
    while open_set:
        _, current = heapq.heappop(open_set)
        visited[current] = 1
        if current == end:
            break
        for dx, dy in DIRS:
            nx, ny = current[1] + dx, current[0] + dy
            neighbor = (ny, nx)
            if 0 <= ny < height and 0 <= nx < width and maze[ny][nx] == 0:
                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + abs(end[0] - ny) + abs(end[1] - nx)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    if visualize:
                        temp_maze = maze.copy()
                        temp_maze[visited == 1] = 2
                        for _, (py, px) in open_set:
                            temp_maze[py][px] = 2
                        fig = draw_maze(temp_maze, is_solving=True)
                        canvas.pyplot(fig)
                        plt.close(fig)
                        time.sleep(speed)
    path = []
    curr = end
    while curr in came_from:
        path.append(curr)
        curr = came_from[curr]
    path.append(start)
    path.reverse()
    if visualize:
        for i in range(len(path)):
            current_path = path[:i+1]
            temp_maze = maze.copy()
            temp_maze[visited == 1] = 2
            fig = draw_maze(temp_maze, path=current_path, is_solving=True)
            canvas.pyplot(fig)
            plt.close(fig)
            time.sleep(speed)

    end_time = time.time()
    return path, end_time - start_time

# Dijkstra's Maze Solver
def solve_maze_dijkstra(maze, start, end, visualize=False, speed=0.0001):
    start_time = time.time()
    height, width = maze.shape
    dist = {start: 0}
    prev = {}
    visited_set = set()
    visited = np.zeros_like(maze)
    queue = [(0, start)]
    canvas = st.empty()
    while queue:
        d, current = heapq.heappop(queue)
        if current in visited_set:
            continue
        visited_set.add(current)
        visited[current] = 1
        if current == end:
            break
        for dx, dy in DIRS:
            nx, ny = current[1] + dx, current[0] + dy
            neighbor = (ny, nx)
            if 0 <= ny < height and 0 <= nx < width and maze[ny][nx] == 0:
                new_dist = dist[current] + 1
                if new_dist < dist.get(neighbor, float('inf')):
                    dist[neighbor] = new_dist
                    prev[neighbor] = current
                    heapq.heappush(queue, (new_dist, neighbor))
                    if visualize:
                        temp_maze = maze.copy()
                        temp_maze[visited == 1] = 2
                        for _, (py, px) in queue:
                            temp_maze[py][px] = 2
                        fig = draw_maze(temp_maze, is_solving=True)
                        canvas.pyplot(fig)
                        plt.close(fig)
                        time.sleep(speed)
    path = []
    curr = end
    while curr in prev:
        path.append(curr)
        curr = prev[curr]
    path.append(start)
    path.reverse()
    if visualize:
        for i in range(len(path)):
            current_path = path[:i+1]
            temp_maze = maze.copy()
            temp_maze[visited == 1] = 2
            fig = draw_maze(temp_maze, path=current_path, is_solving=True)
            canvas.pyplot(fig)
            plt.close(fig)
            time.sleep(speed)
    end_time = time.time()
    return path, end_time - start_time

# --- UI Layout ---
# Add vertical space at the top
st.markdown("""
    <style>
        .stApp {
            background-image: url("https://t3.ftcdn.net/jpg/03/23/88/08/360_F_323880864_TPsH5ropjEBo1ViILJmcFHJqsBzorxUB.jpg");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }
        .main .block-container {
            background-color: rgba(26, 26, 26, 0.75);
            padding: 2rem;
            border-radius: 10px;
            margin-top: 2rem;
            margin-bottom: 2rem;
        }
        h1 {
            color: #ffffff;
            text-shadow: 0 0 10px #ffffff;
        }
        h3 {
            color: #00ffff;
            text-shadow: 0 0 5px #00ffff;
        }
        .stSlider > div > div > div {
            color: #00ffff;
        }
        .stSelectbox > div > div > div {
            color: #00ffff;
        }
        .stCheckbox > label {
            color: #00ffff;
        }
        .stButton>button {
            background-color: #ff00ff;
            color: white;
            border: none;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #ff00ff;
            transform: scale(1.02);
            box-shadow: 0 0 10px #ff00ff;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

# Create a container for the main content
main_container = st.container()

with main_container:
    # Create columns with adjusted ratios
    col1, col2 = st.columns([1, 1.1])
    
    with col1:
        st.markdown("<div style='margin-top: 4rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
            <h1 style='font-size: 44px; margin-bottom: 0.1rem;'>🧩 Maze Generator & Solver</h1>
        """, unsafe_allow_html=True)
        
        # Add some space between title and controls
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='font-size: 32px; margin-bottom: 0.1rem;'>Grid Size</h3>", unsafe_allow_html=True)
        col_slider1, col_slider2 = st.columns(2)
        with col_slider1:
            size = st.slider("Grid Size (odd numbers only)", 5, 51, 21, step=2)
        with col_slider2:
            st.empty()  # Empty column to maintain layout
        st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)  # Add space before checkboxes
        visualize = st.checkbox("Animate Generation & Solving")
        
        # Place dropdowns side by side
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            st.markdown("<h3 style='font-size: 30px; margin-bottom: 0.1rem;'>Generation Algorithm</h3>", unsafe_allow_html=True)
            gen_algo = st.selectbox(
                "",
                ["Recursive Backtracking", "Prim's Algorithm", "Kruskal's Algorithm"],
                label_visibility="collapsed"
            )
        with col1_2:
            st.markdown("<h3 style='font-size: 32px; margin-bottom: 0.1rem;'>Solving Algorithm</h3>", unsafe_allow_html=True)
            solve_algo = st.selectbox(
                "",
                ["BFS", "A*", "Dijkstra"],
                label_visibility="collapsed"
            )
            efficient = st.checkbox("Show Efficiency Analysis")
            
        # Place buttons below dropdowns
        st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
            <style>
                div[data-testid="stButton"] button {
                    width: 100%;
                    height: 3rem;
                    font-size: 7rem;
                    font-weight: 900;
                    margin: 0;
                    padding: 0;
                }
            </style>
        """, unsafe_allow_html=True)
        col1_3, col1_4 = st.columns(2)
        with col1_3:
            gen_btn = st.button("🔧 Generate")
        with col1_4:
            solve_btn = st.button("🚀 Solve")
            
        # Add Compare Algorithms button below
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        compare_btn = st.button("📊 Compare Algorithms")

    with col2:
        maze_state = st.session_state
        if 'maze' not in maze_state:
            maze_state.maze = np.ones((size, size))

        if gen_btn:
            if gen_algo == "Recursive Backtracking":
                maze_state.maze = recursive_backtracking(size, size, visualize)
            elif gen_algo == "Prim's Algorithm":
                maze_state.maze = prims_algorithm(size, size, visualize)
            elif gen_algo == "Kruskal's Algorithm":
                maze_state.maze = kruskals_algorithm(size, size, visualize)
            st.pyplot(draw_maze(maze_state.maze.copy()), use_container_width=True)
            st.success("Maze Generated!")

        if solve_btn:
            times = {}
            paths = {}
            
            # Solve with BFS
            path_bfs, time_bfs = solve_maze_bfs(maze_state.maze.copy(), (1,1), (size-2, size-2), visualize)
            times["BFS"] = time_bfs
            paths["BFS"] = path_bfs
            
            # Solve with A*
            path_astar, time_astar = solve_maze_astar(maze_state.maze.copy(), (1,1), (size-2, size-2), visualize)
            times["A*"] = time_astar
            paths["A*"] = path_astar
            
            # Solve with Dijkstra
            path_dijkstra, time_dijkstra = solve_maze_dijkstra(maze_state.maze.copy(), (1,1), (size-2, size-2), visualize)
            times["Dijkstra"] = time_dijkstra
            paths["Dijkstra"] = path_dijkstra
            
            # Find the fastest algorithm
            fastest_algo = min(times, key=times.get)
            
            # Display the path for the selected algorithm
            path = paths[solve_algo]
            st.pyplot(draw_maze(maze_state.maze.copy(), path=path), use_container_width=True)
            
            # Show toast notification for maze solving
            st.toast(f"🎉 Maze Solved! Path length: {len(path)}", icon="✅")

            # Display results only if efficiency analysis is enabled
            if efficient:
                st.markdown("### Algorithm Performance Comparison")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("BFS", f"{time_bfs:.4f}s", f"{'Fastest' if fastest_algo == 'BFS' else ''}")
                with col2:
                    st.metric("A*", f"{time_astar:.4f}s", f"{'Fastest' if fastest_algo == 'A*' else ''}")
                with col3:
                    st.metric("Dijkstra", f"{time_dijkstra:.4f}s", f"{'Fastest' if fastest_algo == 'Dijkstra' else ''}")

        if compare_btn:
            # Generate comparison data
            times = {}
            paths = {}
            memory_usage = {}
            
            # Solve with BFS
            path_bfs, time_bfs = solve_maze_bfs(maze_state.maze.copy(), (1,1), (size-2, size-2), False)
            times["BFS"] = time_bfs
            paths["BFS"] = path_bfs
            memory_usage["BFS"] = len(path_bfs) * 2
            
            # Solve with A*
            path_astar, time_astar = solve_maze_astar(maze_state.maze.copy(), (1,1), (size-2, size-2), False)
            times["A*"] = time_astar
            paths["A*"] = path_astar
            memory_usage["A*"] = len(path_astar) * 3
            
            # Solve with Dijkstra
            path_dijkstra, time_dijkstra = solve_maze_dijkstra(maze_state.maze.copy(), (1,1), (size-2, size-2), False)
            times["Dijkstra"] = time_dijkstra
            paths["Dijkstra"] = path_dijkstra
            memory_usage["Dijkstra"] = len(path_dijkstra) * 3
            
            # Find the best performers
            fastest_algo = min(times, key=times.get)
            shortest_path = min(paths, key=lambda x: len(paths[x]))
            most_efficient = min(memory_usage, key=memory_usage.get)
            
            st.session_state.show_modal = True

            with col2:
                # Display the maze with the fastest algorithm's path
                st.pyplot(draw_maze(maze_state.maze.copy(), path=paths[fastest_algo]), use_container_width=True)

                st.markdown("""
                    <style>
                        .maze-modal {
                            position: fixed;
                            top: 50%;
                            left: 50%;
                            transform: translate(-50%, -50%);
                            width: 350px;
                            background-color: rgba(26, 26, 26, 0.95);
                            padding: 1.5rem;
                            border-radius: 15px;
                            border: 2px solid #00ffff;
                            box-shadow: 0 0 30px rgba(0, 255, 255, 0.4);
                            z-index: 1000;
                            backdrop-filter: blur(8px);
                        }
                        .maze-modal::before {
                            content: '';
                            position: fixed;
                            top: 0;
                            left: 0;
                            right: 0;
                            bottom: 0;
                            background-color: rgba(0, 0, 0, 0.7);
                            backdrop-filter: blur(3px);
                            z-index: -1;
                        }
                        .algorithm-title {
                            color: #00ffff;
                            text-align: center;
                            font-size: 20px;
                            margin-bottom: 1rem;
                            text-shadow: 0 0 8px #00ffff;
                        }
                        .algorithm-summary {
                            background-color: rgba(0, 255, 255, 0.1);
                            padding: 1rem;
                            border-radius: 10px;
                            margin: 0.5rem 0;
                        }
                        .algorithm-item {
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            padding: 0.5rem 0;
                            border-bottom: 1px solid rgba(0, 255, 255, 0.2);
                            color: #ffffff;
                            font-size: 0.9rem;
                        }
                        .algorithm-item:last-child {
                            border-bottom: none;
                        }
                        .algorithm-name {
                            color: #00ffff;
                            font-weight: bold;
                        }
                        .algorithm-value {
                            color: #ffffff;
                        }
                        .best-performance {
                            color: #00ff00;
                            font-weight: bold;
                        }
                    </style>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                    <div class="maze-modal">
                        <div class="algorithm-title">Algorithm Analysis Summary</div>
                        <div class="algorithm-summary">
                            <div class="algorithm-item">
                                <span class="algorithm-name">Fastest Algorithm</span>
                                <span class="algorithm-value best-performance">{fastest_algo}</span>
                            </div>
                            <div class="algorithm-item">
                                <span class="algorithm-name">Shortest Path</span>
                                <span class="algorithm-value best-performance">{shortest_path}</span>
                            </div>
                            <div class="algorithm-item">
                                <span class="algorithm-name">Most Memory Efficient</span>
                                <span class="algorithm-value best-performance">{most_efficient}</span>
                            </div>
                            <div class="algorithm-item">
                                <span class="algorithm-name">Path Length</span>
                                <span class="algorithm-value">{len(paths[shortest_path])}</span>
                            </div>
                            <div class="algorithm-item">
                                <span class="algorithm-name">Time Taken</span>
                                <span class="algorithm-value">{times[fastest_algo]:.4f}s</span>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)