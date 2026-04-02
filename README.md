# 🧩 Maze Generator & Solver

An interactive web app built with **Streamlit** that generates mazes using classic algorithms and solves them in real time with animated visualizations.

## ✨ Features

- **Three maze generation algorithms**
  - Recursive Backtracking
  - Prim's Algorithm
  - Kruskal's Algorithm
- **Three solving algorithms**
  - BFS (Breadth-First Search)
  - A\* (A-Star)
  - Dijkstra's Algorithm
- **Step-by-step animation** of both generation and solving
- **Algorithm performance comparison** — view execution time and path length side by side
- **Configurable grid size** (5 × 5 up to 51 × 51)
- Dark neon-themed UI

## 🖥️ Live Demo

> Deploy the app on [Streamlit Community Cloud](https://streamlit.io/cloud) and paste your URL here.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+

### Installation

```bash
git clone https://github.com/manne1086/mazesolver.git
cd mazesolver
pip install streamlit numpy matplotlib
```

### Run

```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

## 🗂️ Project Structure

```
mazesolver/
├── app.py        # Main Streamlit application
├── docs/         # GitHub Pages landing page
└── README.md
```

## 🔧 How It Works

### Maze Generation

| Algorithm | Description |
|---|---|
| **Recursive Backtracking** | DFS-based carving; produces long, winding corridors |
| **Prim's Algorithm** | Randomised Prim's MST; produces more branching mazes |
| **Kruskal's Algorithm** | Randomised Kruskal's MST using a disjoint-set union |

### Maze Solving

| Algorithm | Strategy | Guarantees shortest path |
|---|---|---|
| **BFS** | Level-by-level exploration | ✅ Yes |
| **A\*** | Heuristic-guided search (Manhattan distance) | ✅ Yes |
| **Dijkstra** | Uniform-cost search | ✅ Yes |

## 📄 License

This project is licensed under the terms of the [LICENSE](LICENSE) file.
