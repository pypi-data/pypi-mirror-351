        
        

snippets= {}


snippets ['DFS'] = r"""" \
def dfs(graph, start, goal, path=None, visited=None):
    if path is None:
        path = [start]
    if visited is None:
        visited = set()
    visited.add(start)
    
    if start == goal:
        return path

    for neighbor in graph.get(start, []):
        if neighbor not in visited:
            result = dfs(graph, neighbor, goal, path + [neighbor], visited)
            if result is not None:
                return result
    return None

graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': [],
    'E': ['F'],
    'F': []
}

print("DFS path:", dfs(graph, 'A', 'F'))

"""

snippets['BFS'] = r"""

from collections import deque

def bfs(graph, start, goal):
    queue = deque([[start]])
    visited = set([start])
    
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == goal:
            return path
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)
    return None

print("BFS path:", bfs(graph, 'A', 'F'))

"""

snippets['Iterative IDS'] = r"""
def depth_limited_search(graph, current, goal, limit, path):
    if current == goal:
        return path
    if limit <= 0:
        return None
    for neighbor in graph.get(current, []):
        if neighbor not in path: 
            result = depth_limited_search(graph, neighbor, goal, limit - 1, path + [neighbor])
            if result is not None:
                return result
    return None

def ids(graph, start, goal, max_depth=10):
    for depth in range(max_depth):
        result = depth_limited_search(graph, start, goal, depth, [start])
        if result is not None:
            return result
    return None

print("IDS path:", ids(graph, 'A', 'F'))
" 
"""

snippets ['uniform cost search'] = r"""
import heapq

def ucs(graph, start, goal):
    queue = [(0, [start])]
    visited = {}
    
    while queue:
        cost, path = heapq.heappop(queue)
        node = path[-1]
        if node == goal:
            return path, cost
        if node in visited and visited[node] <= cost:
            continue
        visited[node] = cost
        
        for neighbor, weight in graph.get(node, []):
            new_cost = cost + weight
            new_path = path + [neighbor]
            heapq.heappush(queue, (new_cost, new_path))
    return None

weighted_graph = {
    'A': [('B', 1), ('C', 4)],
    'B': [('D', 2), ('E', 5)],
    'C': [('E', 1)],
    'D': [('F', 3)],
    'E': [('F', 1)],
    'F': []
}

result = ucs(weighted_graph, 'A', 'F')
if result:
    path, cost = result
    print("UCS path:", path, "with total cost:", cost)
"""

snippets ['hill climbing Search'] = r"""
def hill_climbing(start_state, get_neighbors, evaluate):
    current = start_state
    while True:
        neighbors = get_neighbors(current)
        next_state = max(neighbors, key=evaluate, default=None)
        if next_state is None or evaluate(next_state) <= evaluate(current):
            break
        current = next_state
    return current

def get_neighbors(x):
    return [x - 1, x + 1]

def evaluate(x):
    return -(x - 5) ** 2 + 25

start = 0
result = hill_climbing(start, get_neighbors, evaluate)
print("Hill Climbing result:", result, "with value:", evaluate(result))
"""

snippets ['Best First Search'] = r"""
    
def best_first_search(start, goal, get_neighbors, heuristic):
    from heapq import heappush, heappop
    queue = []
    heappush(queue, (heuristic(start, goal), [start]))
    visited = set()
    
    while queue:
        h_val, path = heappop(queue)
        current = path[-1]
        if current == goal:
            return path
        if current in visited:
            continue
        visited.add(current)
        for neighbor in get_neighbors(current):
            if neighbor not in visited:
                new_path = path + [neighbor]
                heappush(queue, (heuristic(neighbor, goal), new_path))
    return None

def heuristic(node, goal):
    return abs(goal - node)

def get_neighbors_1d(x):
    return [x - 1, x + 1]

print("Best First Search path:", best_first_search(0, 10, get_neighbors_1d, heuristic))
"""

snippets ['A* algo'] = r"""" \
def a_star_search(start, goal, get_neighbors, heuristic, cost_function):
    from heapq import heappush, heappop
    queue = []
    heappush(queue, (heuristic(start, goal), 0, [start]))
    visited = {}
    
    while queue:
        f, g, path = heappop(queue)
        current = path[-1]
        if current == goal:
            return path, g
        if current in visited and visited[current] <= g:
            continue
        visited[current] = g
        for neighbor in get_neighbors(current):
            step_cost = cost_function(current, neighbor)
            new_g = g + step_cost
            new_f = new_g + heuristic(neighbor, goal)
            heappush(queue, (new_f, new_g, path + [neighbor]))
    return None

def get_neighbors_1d(x):
    return [x - 1, x + 1]

def cost_function(a, b):
    return 1

print("A* Search path:", a_star_search(0, 10, get_neighbors_1d, heuristic, cost_function))
"""


snippets ['AlphaBeta Purning'] = r"""
"import math

class GameNode:
    def __init__(self, state, children=None, score=None):
        self.state = state
        self.children = children if children is not None else []
        self.score = score

def minimax(node, depth, maximizingPlayer):
    if depth == 0 or not node.children:
        return node.score
    
    if maximizingPlayer:
        maxEval = -math.inf
        for child in node.children:
            eval = minimax(child, depth - 1, False)
            maxEval = max(maxEval, eval)
        return maxEval
    else:
        minEval = math.inf
        for child in node.children:
            eval = minimax(child, depth - 1, True)
            minEval = min(minEval, eval)
        return minEval

def alphabeta(node, depth, alpha, beta, maximizingPlayer):
    if depth == 0 or not node.children:
        return node.score
    
    if maximizingPlayer:
        value = -math.inf
        for child in node.children:
            value = max(value, alphabeta(child, depth-1, alpha, beta, False))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = math.inf
        for child in node.children:
            value = min(value, alphabeta(child, depth-1, alpha, beta, True))
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value


leaf1 = GameNode(state="L1", score=3)
leaf2 = GameNode(state="L2", score=5)
leaf3 = GameNode(state="L3", score=2)
leaf4 = GameNode(state="L4", score=9)

node1 = GameNode(state="N1", children=[leaf1, leaf2])
node2 = GameNode(state="N2", children=[leaf3, leaf4])
root = GameNode(state="Root", children=[node1, node2])

print("Minimax value at root:", minimax(root, depth=3, maximizingPlayer=True))
print("Alpha-Beta value at root:", alphabeta(root, depth=3, alpha=-math.inf, beta=math.inf, maximizingPlayer=True))
"""\

snippets['generate moves'] = r"""

def generate_moves(state):
    return [state - 1, state + 1]

def evaluate_state(state):
    return -abs(state)

def adversarial_search(state, depth, maximizingPlayer):
    if depth == 0 or abs(state) > 10:
        return evaluate_state(state)
    
    moves = generate_moves(state)
    if maximizingPlayer:
        best_value = -math.inf
        for move in moves:
            value = adversarial_search(move, depth - 1, False)
            best_value = max(best_value, value)
        return best_value
    else:
        best_value = math.inf
        for move in moves:
            value = adversarial_search(move, depth - 1, True)
            best_value = min(best_value, value)
        return best_value

initial_state = 0
print("Adversarial search evaluation:", adversarial_search(initial_state, depth=4, maximizingPlayer=True))
"""

snippets['Lab 5'] = r"""
def initial_state():
    return [[None, None, None],
            [None, None, None],
            [None, None, None]]
def player(board):
    countX = sum(row.count("X") for row in board)
    countO = sum(row.count("O") for row in board)
    return "X" if countX <= countO else "O"


def actions(board):
    return {(i, j) for i in range(3) for j in range(3) if board[i][j] is None}


def result(board, action):
    i, j = action
    if board[i][j] is not None:
        raise Exception("Invalid move")
    new_board = [row.copy() for row in board]
    new_board[i][j] = player(board)
    return new_board


def winner(board):
    for i in range(3):
        if board[i][0] is not None and board[i][0] == board[i][1] == board[i][2]:
            return board[i][0]
    for j in range(3):
        if board[0][j] is not None and board[0][j] == board[1][j] == board[2][j]:
            return board[0][j]
    if board[0][0] is not None and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] is not None and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]
    return None


def terminal(board):
    if winner(board) is not None:
        return True
    if all(cell is not None for row in board for cell in row):
        return True
    return False


def utility(board):
    win = winner(board)
    if win == "X":
        return 1
    elif win == "O":
        return -1
    else:
        return 0


def minimax_ab(board, alpha, beta):
    if terminal(board):
        return utility(board)
    
    current = player(board)
    if current == "X":
        value = float("-inf")
        for action in actions(board):
            value = max(value, minimax_ab(result(board, action), alpha, beta))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = float("inf")
        for action in actions(board):
            value = min(value, minimax_ab(result(board, action), alpha, beta))
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value


def alpha_beta_pruining(board):
    if terminal(board):
        return None
    
    current = player(board)
    best_move = None
    
    if current == "X":
        best_value = float("-inf")
        alpha = float("-inf")
        beta = float("inf")
        for action in actions(board):
            move_value = minimax_ab(result(board, action), alpha, beta)
            if move_value > best_value:
                best_value = move_value
                best_move = action
            alpha = max(alpha, best_value)
    else:
        best_value = float("inf")
        alpha = float("-inf")
        beta = float("inf")
        for action in actions(board):
            move_value = minimax_ab(result(board, action), alpha, beta)
            if move_value < best_value:
                best_value = move_value
                best_move = action
            beta = min(beta, best_value)
    return best_move


if __name__ == "__main__":
    board = initial_state()
    print("Initial Board:")
    for row in board:
        print(row)
    
    move = alpha_beta_pruining(board)
    print("\nAI recommends move:", move)
    
    board = result(board, move)
    print("\nBoard after AI move:")
    for row in board:
        print(row)

""" \

snippets['GA'] = r"""
import random

POP_SIZE = 500
MUT_RATE = 0.1
TARGET = 'aq'
GENES = ' abcdefghijklmnopqrstuvwxyz'

def initialize_pop(TARGET):
    population = list()
    tar_len = len(TARGET)

    for i in range(POP_SIZE):
        temp = list()
        for j in range(tar_len):
            temp.append(random.choice(GENES))
        population.append(temp)

    return population

def crossover(selected_chromo, CHROMO_LEN, population):
    offspring_cross = []
    for i in range(int(POP_SIZE)):
        parent1 = random.choice(selected_chromo)
        parent2 = random.choice(population[:int(POP_SIZE*50)])

        p1 = parent1[0]
        p2 = parent2[0]

        crossover_point = random.randint(1, CHROMO_LEN-1)
        child =  p1[:crossover_point] + p2[crossover_point:]
        offspring_cross.extend([child])
    return offspring_cross

def mutate(offspring, MUT_RATE):
    mutated_offspring = []

    for arr in offspring:
        for i in range(len(arr)):
            if random.random() < MUT_RATE:
                arr[i] = random.choice(GENES)
        mutated_offspring.append(arr)
    return mutated_offspring

def selection(population, TARGET):
    sorted_chromo_pop = sorted(population, key= lambda x: x[1])
    return sorted_chromo_pop[:int(0.5*POP_SIZE)]

def fitness_cal(TARGET, chromo_from_pop):
    difference = 0
    for tar_char, chromo_char in zip(TARGET, chromo_from_pop):
        if tar_char != chromo_char:
            difference+=1
    
    return [chromo_from_pop, difference]

def replace(new_gen, population):
    for _ in range(len(population)):
        if population[_][1] > new_gen[_][1]:
          population[_][0] = new_gen[_][0]
          population[_][1] = new_gen[_][1]
    return population

def main(POP_SIZE, MUT_RATE, TARGET, GENES):
    initial_population = initialize_pop(TARGET)
    found = False
    population = []
    generation = 1

    for _ in range(len(initial_population)):
        population.append(fitness_cal(TARGET, initial_population[_]))

    while not found:
      selected = selection(population, TARGET)

      population = sorted(population, key= lambda x:x[1])
      crossovered = crossover(selected, len(TARGET), population)
            
      mutated = mutate(crossovered, MUT_RATE)

      new_gen = []
      for _ in mutated:
          new_gen.append(fitness_cal(TARGET, _))

      population = replace(new_gen, population)

      
      if (population[0][1] == 0):
        print('Target found')
        print('String: ' + str(population[0][0]) + ' Generation: ' + str(generation) + ' Fitness: ' + str(population[0][1]))
        break
      print('String: ' + str(population[0][0]) + ' Generation: ' + str(generation) + ' Fitness: ' + str(population[0][1]))
      generation+=1

main(POP_SIZE, MUT_RATE, TARGET,GENES)
"""

snippets["perceptron"] = r"""
import numpy as np


class pt():
    def __init__(self, learning_rate, n_iterations=1000):
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations

    def activation_function(self, z):
        if z > 0: return 1
        return 0

    def fit(self):
        X = np.array([(0,0),(0,1),(1,0),(1,1)])
        Y = np.array([0,1,1,0])
        self.weights = np.zeros(2)
        self.bias = 0
        for _ in range(self.n_iterations):
            for i,j in zip(X,Y):
                net = np.dot(self.weights, i) + self.bias
                y_pred = self.activation_function(net)
                self.weights = self.learning_rate * (j - y_pred) * i + self.weights
                self.bias = self.learning_rate * (j - y_pred) + self.bias

    def predict(self, X):
        return self.activation_function(np.dot(X,self.weights)+self.bias)
    
p = pt(0.1)
p.fit()        
p.predict([1,0])
"""

snippets["neural"] = r"""
import numpy as np

class nn():
    def __init__(self, input_size, hidden_size, output_size, learning_rate, n_iterations=1000):
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.w1 = np.random.rand(input_size, hidden_size)
        self.w2 = np.random.rand(hidden_size, output_size)
        self.b1 = np.zeros((1, hidden_size))
        self.b2 = np.zeros((1, output_size))


    def forward(self, X):
        z1 = X @ self.w1 + self.b1
        self.a1 = self.activation_function(z1)
        z2 = self.a1 @ self.w2 + self.b2
        y_pred = self.activation_function(z2)
        return y_pred
    

    def backward(self, X, y_pred, y_true):
        e = (y_true - y_pred)
        delta_output = e * self.sig_der(y_pred)
        grad_w2 = self.learning_rate * self.a1.T @ delta_output / X.shape[0]
        grad_b2 = self.learning_rate * np.sum(delta_output, axis=0, keepdims=True) / X.shape[0]
        err_hidden = delta_output @ self.w2.T
        delta_hidden = err_hidden * self.sig_der(self.a1)
        grad_w1 = self.learning_rate * X.T @ delta_hidden / X.shape[0]
        grad_b1 = self.learning_rate * np.sum(delta_hidden, axis=0, keepdims=True)

        self.w1 += grad_w1
        self.b1 += grad_b1
        self.b2 += grad_b2
        self.w2 += grad_w2

    def activation_function(self, z):
        return 1 / (1 + np.exp(-z))
    
    def sig_der(self,z):
        return z * (1 - z)
    


n = nn(input_size = 2, hidden_size=4, output_size=1, learning_rate=0.1)
X_in = np.array([[0,0],[0,1],[1,0],[1,1]])
Y_in = np.array([[1],[0],[0],[0]])
for _ in range(10_000):
    n.backward(X_in, n.forward(X_in), Y_in)
a = n.forward([0, 0])
print(1 if a[0][0] > 0.5 else 0)
"""

snippets["metric_imp"] = r"""
from sklearn.metrics import confusion_matrix, mean_squared_error, median_absolute_error, r2_score, classification_report, roc_curve, precision_score, recall_score, f1_score, accuracy_score
"""



snippets['Python Functions'] = r"""
def greet(name="Guest"):
   
    print(f"Hello, {name}!")

greet("Alice")
greet()
"""

snippets['Pandas Data Loading'] = r"""
import pandas as pd
# Assuming a file named 'sample.csv' exists with some data
# Or create a dummy DataFrame
try:
    df = pd.read_csv('sample.csv')
except FileNotFoundError:
    data = {'col1': [1, 2, 3, 4], 'col2': ['A', 'B', 'C', 'D']}
    df = pd.DataFrame(data)
    print("Created a sample DataFrame instead of loading file.")

print(df.head())
"""

snippets['Pandas Data Manipulation'] = r"""
import pandas as pd
data = {'col1': [1, 2, 3, 4, 5], 'col2': [10, 20, 30, 40, 50]}
df = pd.DataFrame(data)

# Select a column
col2_data = df['col2']
print("\nSelected column 'col2':")
print(col2_data)

# Filter rows
filtered_df = df[df['col1'] > 2]
print("\nFiltered DataFrame (col1 > 2):")
print(filtered_df)

# Add a new column
df['col3'] = df['col1'] + df['col2']
print("\nDataFrame with new column 'col3':")
print(df)
"""

snippets['Pandas Shape and Info'] = r"""
import pandas as pd
data = {'col1': [1, 2, 3], 'col2': ['A', 'B', 'C']}
df = pd.DataFrame(data)

print("DataFrame Shape (Rows, Columns):")
print(df.shape)

print("\nDataFrame Info:")
df.info()
"""

snippets['Pandas Null Value Checks'] = r"""
import pandas as pd
import numpy as np

data = {'col1': [1, 2, np.nan, 4], 'col2': ['A', 'B', 'C', np.nan]}
df = pd.DataFrame(data)

print("Check for null values (boolean DataFrame):")
print(df.isnull())

print("\nSum of null values per column:")
print(df.isnull().sum())

print("\nCheck for non-null values (boolean DataFrame):")
print(df.notnull())
"""

snippets['Basic Plotting Matplotlib'] = r"""
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.plot(x, y)
plt.title("Sine Wave")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.show()
"""

snippets['Basic Plotting Plotly'] = r"""
# Plotly requires installation: pip install plotly pandas
# This snippet might require a compatible environment (e.g., Jupyter) to display
import plotly.express as px
import pandas as pd

data = {'x': [1, 2, 3, 4, 5], 'y': [10, 12, 5, 15, 8]}
df = pd.DataFrame(data)

fig = px.scatter(df, x="x", y="y", title="Simple Scatter Plot")
fig.show()
"""

snippets['Sklearn Regression Import'] = r"""
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Example Usage (requires data)
# X = [[1], [2], [3], [4]]
# y = [2, 4, 5, 4]
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# model = LinearRegression()
# model.fit(X_train, y_train)
# predictions = model.predict(X_test)
# print(f"MSE: {mean_squared_error(y_test, predictions)}")
print("Successfully imported LinearRegression and train_test_split from sklearn.")
"""

snippets['BFS Pathfinding'] = r"""
from collections import deque

def bfs(graph, start):
    visited = set()
    queue = deque([start])
    visited.add(start)

    while queue:
        vertex = queue.popleft()
        print(vertex, end=" ") # Process node

        for neighbor in graph.get(vertex, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

# Example Graph (Adjacency List)
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D', 'E'],
    'C': ['A', 'F'],
    'D': ['B'],
    'E': ['B', 'F'],
    'F': ['C', 'E']
}

print("BFS Traversal (starting from A):")
bfs(graph, 'A')
print()
"""

snippets['DFS Pathfinding'] = r"""
def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    print(start, end=" ") # Process node

    for neighbor in graph.get(start, []):
        if neighbor not in visited:
            dfs(graph, neighbor, visited)

# Example Graph (Adjacency List)
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D', 'E'],
    'C': ['A', 'F'],
    'D': ['B'],
    'E': ['B', 'F'],
    'F': ['C', 'E']
}

print("DFS Traversal (starting from A):")
dfs(graph, 'A')
print()
"""

snippets['A* Search Structure'] = r"""
# A* search is complex; this is a basic structure outline.
# Requires a priority queue, a heuristic function, and cost tracking.

# import heapq

# class Node:
#     def __init__(self, state, parent=None, cost=0, heuristic=0):
#         self.state = state
#         self.parent = parent
#         self.cost = cost # g-score
#         self.heuristic = heuristic # h-score
#         self.f_score = cost + heuristic # f-score = g + h

#     def __lt__(self, other):
#         return self.f_score < other.f_score

# def astar(graph, start, goal, heuristic):
#     open_set = []
#     heapq.heappush(open_set, Node(start, cost=0, heuristic=heuristic(start, goal)))
#     came_from = {} # To reconstruct path
#     g_score = {start: 0} # Cost from start along best path found

#     while open_set:
#         current_node = heapq.heappop(open_set)
#         current_state = current_node.state

#         if current_state == goal:
#             # Path reconstruction logic here
#             path = []
#             while current_node:
#                 path.append(current_node.state)
#                 current_node = current_node.parent
#             return path[::-1]

#         for neighbor_state, edge_cost in graph.get(current_state, {}).items(): # graph needs to store edge costs
#             tentative_g_score = g_score[current_state] + edge_cost

#             if neighbor_state not in g_score or tentative_g_score < g_score[neighbor_state]:
#                 g_score[neighbor_state] = tentative_g_score
#                 new_node = Node(neighbor_state, parent=current_node,
#                                 cost=tentative_g_score, heuristic=heuristic(neighbor_state, goal))
#                 heapq.heappush(open_set, new_node)
#                 came_from[neighbor_state] = current_state # Optional: store parent state

#     return None # Goal not reached

# Example Usage requires a graph with edge costs and a heuristic function
# graph = {
#     'A': {'B': 1, 'C': 2},
#     'B': {'A': 1, 'D': 3},
#     'C': {'A': 2, 'D': 1},
#     'D': {'B': 3, 'C': 1}
# }
# def simple_heuristic(state, goal):
#    # Needs domain knowledge; dummy example
#    heuristic_values = {'A': 5, 'B': 4, 'C': 2, 'D': 0} # Example distances to 'D'
#    return heuristic_values.get(state, float('inf'))

# path = astar(graph, 'A', 'D', simple_heuristic)
# print(f"A* Path from A to D: {path}")
print("A* search structure outline provided.")
print("Full implementation requires graph with edge weights, heuristic, and Node class with __lt__.")
"""

snippets['Hill Climbing Local Search Structure'] = r"""
# Hill climbing is a simple local search algorithm.

# def hill_climbing(problem):
#     current_state = problem.initial_state()

#     while True:
#         neighbors = problem.neighbors(current_state)
#         if not neighbors:
#             break # No neighbors to move to

#         next_state = max(neighbors, key=problem.value) # Find neighbor with highest value (assuming maximization)

#         if problem.value(next_state) <= problem.value(current_state):
#             break # Reached a peak or plateau

#         current_state = next_state

#     return current_state, problem.value(current_state)

# # Example Problem Definition (Requires Problem class/object)
# class SimpleHillClimbingProblem:
#     def initial_state(self):
#         return 0 # Start at state 0

#     def neighbors(self, state):
#         # Example: Neighbors are state -1 and state +1
#         potential_neighbors = [state - 1, state + 1]
#         # Filter for valid states if needed
#         valid_neighbors = [n for n in potential_neighbors if 0 <= n <= 10] # Assuming states 0-10
#         return valid_neighbors

#     def value(self, state):
#         # Example value function (e.g., - (x-5)^2 representing a peak at x=5)
#         return -(state - 5)**2

# problem = SimpleHillClimbingProblem()
# final_state, final_value = hill_climbing(problem)
# print(f"Hill Climbing Result: State = {final_state}, Value = {final_value}")
print("Hill Climbing structure outline provided.")
print("Full implementation requires defining Problem with initial_state, neighbors, and value/cost functions.")
"""

snippets['Min-Max Algorithm Structure'] = r"""
# Min-Max algorithm structure for a simple game tree.

# def minmax(node, depth, maximizing_player):
#     if depth == 0 or node.is_terminal(): # Base case: terminal state or depth limit
#         return node.evaluate()

#     if maximizing_player:
#         max_eval = float('-inf')
#         for child in node.get_children():
#             eval = minmax(child, depth - 1, False)
#             max_eval = max(max_eval, eval)
#         return max_eval
#     else:
#         min_eval = float('inf')
#         for child in node.get_children():
#             eval = minmax(child, depth - 1, True)
#             min_eval = min(min_eval, eval)
#         return min_eval

# # Example usage requires a Game Tree structure (Node class with is_terminal, evaluate, get_children)
# class ExampleGameNode:
#    def __init__(self, value=None, children=None):
#        self._value = value # Value if terminal
#        self._children = children if children is not None else []

#    def is_terminal(self):
#        return self._children == []

#    def evaluate(self):
#        if not self.is_terminal():
#            # In a real game, this would evaluate non-terminal states heuristically
#            raise ValueError("Cannot evaluate non-terminal node in this simple example")
#        return self._value

#    def get_children(self):
#        return self._children

# # Simple tree: Max wants to maximize, Min wants to minimize
# #      (Max)
# #     /  \
# #    (Min)(Min)
# #   / | \  | \
# #  4  2 8  1  3  (Terminal values)
# node8 = ExampleGameNode(value=8)
# node2 = ExampleGameNode(value=2)
# node4 = ExampleGameNode(value=4)
# node3 = ExampleGameNode(value=3)
# node1 = ExampleGameNode(value=1)

# min_node1 = ExampleGameNode(children=[node4, node2, node8])
# min_node2 = ExampleGameNode(children=[node1, node3])
# root = ExampleGameNode(children=[min_node1, min_node2])

# optimal_value = minmax(root, depth=2, maximizing_player=True)
# print(f"Min-Max Optimal Value for Maximizer: {optimal_value}")
print("Min-Max algorithm structure outline provided.")
print("Full implementation requires a Game Tree structure with state representation and evaluation.")
"""

snippets['Alpha Beta Pruning Structure'] = r"""
# Alpha-Beta Pruning structure (enhancement of Min-Max).

# def alphabeta(node, depth, alpha, beta, maximizing_player):
#     if depth == 0 or node.is_terminal():
#         return node.evaluate()

#     if maximizing_player:
#         max_eval = float('-inf')
#         for child in node.get_children():
#             eval = alphabeta(child, depth - 1, alpha, beta, False)
#             max_eval = max(max_eval, eval)
#             alpha = max(alpha, eval)
#             if beta <= alpha:
#                 break # Beta cut-off
#         return max_eval
#     else:
#         min_eval = float('inf')
#         for child in node.get_children():
#             eval = alphabeta(child, depth - 1, alpha, beta, True)
#             min_eval = min(min_eval, eval)
#             beta = min(beta, eval)
#             if beta <= alpha:
#                 break # Alpha cut-off
#         return min_eval

# # Example usage requires the same Game Tree structure as Min-Max
# # Initialize alpha = float('-inf'), beta = float('inf')
# # root = ExampleGameNode(...) # Use the same structure as Min-Max example
# # optimal_value = alphabeta(root, depth=2, alpha=float('-inf'), beta=float('inf'), maximizing_player=True)
# # print(f"Alpha-Beta Optimal Value for Maximizer: {optimal_value}")
print("Alpha-Beta Pruning algorithm structure outline provided.")
print("Requires Game Tree structure and initial alpha/beta values.")
"""

snippets['Tic Tac Toe Game Structure'] = r"""
# Basic Tic Tac Toe board representation and winning check.

def create_board():
    return [[' ' for _ in range(3)] for _ in range(3)]

def display_board(board):
    for row in board:
        print("|" + "|".join(row) + "|")
        print("-" * 7)

def is_winner(board, player):
    # Check rows
    for row in board:
        if all(cell == player for cell in row):
            return True
    # Check columns
    for col in range(3):
        if all(board[row][col] == player for row in range(3)):
            return True
    # Check diagonals
    if all(board[i][i] == player for i in range(3)) or \
       all(board[i][2-i] == player for i in range(3)):
        return True
    return False

def is_board_full(board):
    return all(cell != ' ' for row in board for cell in row)

# Example Usage
# board = create_board()
# board[0][0] = 'X'
# board[1][1] = 'X'
# board[2][2] = 'X'
# display_board(board)
# print(f"Is X a winner? {is_winner(board, 'X')}")
# print(f"Is board full? {is_board_full(board)}")
print("Tic Tac Toe board representation and win/full check functions provided.")
print("Game logic (moves, turns) would be built around these.")
"""

snippets['N Queen Problem Backtracking'] = r"""
# N-Queens problem using backtracking.

def solve_nqueens(n):
    board = [[0 for _ in range(n)] for _ in range(n)]
    solutions = []
    solve_nqueens_util(board, 0, solutions)
    return solutions

def is_safe(board, row, col):
    # Check this row on left side
    for i in range(col):
        if board[row][i] == 1:
            return False
    # Check upper diagonal on left side
    for i, j in zip(range(row, -1, -1), range(col, -1, -1)):
        if board[i][j] == 1:
            return False
    # Check lower diagonal on left side
    for i, j in zip(range(row, len(board), 1), range(col, -1, -1)):
        if board[i][j] == 1:
            return False
    return True

def solve_nqueens_util(board, col, solutions):
    # Base case: If all queens are placed
    if col >= len(board):
        # Add a copy of the current board configuration to solutions
        solutions.append([row[:] for row in board])
        return True # Found a solution

    # Consider this column and try placing this queen in all rows one by one
    for i in range(len(board)):
        if is_safe(board, i, col):
            board[i][col] = 1 # Place queen

            # Recur to place the rest of the queens
            solve_nqueens_util(board, col + 1, solutions) # Continue searching for solutions

            # Backtrack: Remove queen if placing it here didn't lead to a solution
            board[i][col] = 0

    # If the queen cannot be placed in any row in this column
    return False # Backtrack

def print_solution(board):
    for row in board:
        print(" ".join("Q" if cell == 1 else "." for cell in row))
    print()

# Example Usage
# n = 4
# solutions = solve_nqueens(n)
# print(f"Found {len(solutions)} solutions for {n}-Queens:")
# for sol in solutions:
#    print_solution(sol)
print("N-Queens problem solver using backtracking provided.")
print("Set n and call solve_nqueens(n) to get solutions.")
"""

snippets['Genetic Algorithm Structure'] = r"""
# Genetic Algorithm structure outline.

# import random

# def create_individual(solution_length):
#     # Create a random initial solution (chromosome)
#     return [random.randint(0, 1) for _ in range(solution_length)] # Example: binary chromosome

# def calculate_fitness(individual):
#     # Define how good an individual solution is
#     # Example: simple sum of bits for maximization
#     return sum(individual)

# def select_parents(population, fitness_scores, num_parents):
#     # Select individuals based on fitness (e.g., tournament selection, roulette wheel)
#     # Example: simple selection of top individuals
#     sorted_population = [x for _, x in sorted(zip(fitness_scores, population), reverse=True)]
#     return sorted_population[:num_parents]

# def crossover(parent1, parent2):
#     # Combine parts of parents to create new offspring
#     # Example: single-point crossover
#     point = random.randint(1, len(parent1) - 1)
#     child1 = parent1[:point] + parent2[point:]
#     child2 = parent2[:point] + parent1[point:]
#     return child1, child2

# def mutate(individual, mutation_rate):
#     # Randomly change parts of an individual
#     # Example: flip a bit with a given probability
#     mutated_individual = list(individual)
#     for i in range(len(mutated_individual)):
#         if random.random() < mutation_rate:
#             mutated_individual[i] = 1 - mutated_individual[i] # Flip bit
#     return mutated_individual

# def genetic_algorithm(population_size, solution_length, generations, mutation_rate):
#     population = [create_individual(solution_length) for _ in range(population_size)]

#     for generation in range(generations):
#         fitness_scores = [calculate_fitness(individual) for individual in population]

#         # Selection
#         parents = select_parents(population, fitness_scores, population_size // 2)

#         # Reproduction (Crossover and Mutation)
#         next_generation = []
#         while len(next_generation) < population_size:
#             p1, p2 = random.sample(parents, 2) # Select two random parents
#             child1, child2 = crossover(p1, p2)
#             next_generation.append(mutate(child1, mutation_rate))
#             if len(next_generation) < population_size:
#                 next_generation.append(mutate(child2, mutation_rate))

#         population = next_generation

#         # Optional: Print best fitness in this generation
#         # best_fitness = max([calculate_fitness(ind) for ind in population])
#         # print(f"Generation {generation}: Best Fitness = {best_fitness}")

#     # Return the best individual found
#     best_individual = max(population, key=calculate_fitness)
#     return best_individual, calculate_fitness(best_individual)

# # Example Usage: Try to find a string of all 1s
# # best_solution, best_fitness = genetic_algorithm(
# #     population_size=100,
# #     solution_length=10,
# #     generations=50,
# #     mutation_rate=0.01
# # )
# # print(f"\nGenetic Algorithm Result: Best Solution = {best_solution}, Fitness = {best_fitness}")
print("Genetic Algorithm structure outline provided.")
print("Requires defining create_individual, calculate_fitness, select_parents, crossover, and mutate.")
"""

snippets['Knapsack Problem Dynamic Programming'] = r"""
# 0/1 Knapsack problem solved using dynamic programming.

def knapsack_dp(weights, values, capacity):
    n = len(weights)
    # dp[i][w] will store the maximum value that can be obtained
    # with the first i items and a capacity of w
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]

    # Build DP table
    for i in range(n + 1):
        for w in range(capacity + 1):
            if i == 0 or w == 0:
                dp[i][w] = 0
            elif weights[i-1] <= w:
                # Option 1: Include item i-1
                value_including = values[i-1] + dp[i-1][w - weights[i-1]]
                # Option 2: Exclude item i-1
                value_excluding = dp[i-1][w]
                dp[i][w] = max(value_including, value_excluding)
            else:
                # Cannot include item i-1 as its weight exceeds current capacity w
                dp[i][w] = dp[i-1][w]

    # The maximum value is in the bottom-right corner
    max_value = dp[n][capacity]

    # Optional: Find which items are included
    included_items = []
    w = capacity
    for i in range(n, 0, -1):
        # If the current value is not the same as the value without item i-1,
        # it means item i-1 was included
        if dp[i][w] != dp[i-1][w]:
            included_items.append(i-1) # Item index
            w -= weights[i-1]

    included_items.reverse() # Get items in original order

    return max_value, included_items

# Example Usage
# weights = [10, 20, 30]
# values = [60, 100, 120]
# capacity = 50
# max_value, items = knapsack_dp(weights, values, capacity)
# print(f"Knapsack Capacity: {capacity}")
# print(f"Weights: {weights}")
# print(f"Values: {values}")
# print(f"\nMaximum Value: {max_value}")
# print(f"Included Item Indices: {items}")
print("0/1 Knapsack problem solved using dynamic programming.")
print("Input weights, values lists and capacity.")
"""

snippets['Perceptron for Logic Gate'] = r"""
import numpy as np

class Perceptron:
    def __init__(self, num_inputs, learning_rate=0.1):
        self.weights = np.random.rand(num_inputs) # Random initial weights
        self.bias = np.random.rand(1)[0] # Random initial bias
        self.learning_rate = learning_rate

    def predict(self, inputs):
        # Activation function (step function)
        summation = np.dot(inputs, self.weights) + self.bias
        return 1 if summation > 0 else 0

    def train(self, training_inputs, labels, epochs):
        for _ in range(epochs):
            for inputs, label in zip(training_inputs, labels):
                prediction = self.predict(inputs)
                error = label - prediction
                # Update weights and bias
                self.weights += self.learning_rate * error * inputs
                self.bias += self.learning_rate * error

# Example: Implementing AND gate
# Inputs: (x1, x2)
# Outputs: 0 0 -> 0, 0 1 -> 0, 1 0 -> 0, 1 1 -> 1
training_inputs = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
labels_and = np.array([0, 0, 0, 1])

# Create and train the perceptron for AND
perceptron_and = Perceptron(num_inputs=2)
perceptron_and.train(training_inputs, labels_and, epochs=10)

# Test the trained perceptron
print("Perceptron for AND Gate:")
print(f"0 and 0: {perceptron_and.predict(np.array([0, 0]))}")
print(f"0 and 1: {perceptron_and.predict(np.array([0, 1]))}")
print(f"1 and 0: {perceptron_and.predict(np.array([1, 0]))}")
print(f"1 and 1: {perceptron_and.predict(np.array([1, 1]))}")

# Example: Implementing OR gate
# Outputs: 0 0 -> 0, 0 1 -> 1, 1 0 -> 1, 1 1 -> 1
labels_or = np.array([0, 1, 1, 1])
perceptron_or = Perceptron(num_inputs=2)
perceptron_or.train(training_inputs, labels_or, epochs=10)

print("\nPerceptron for OR Gate:")
print(f"0 or 0: {perceptron_or.predict(np.array([0, 0]))}")
print(f"0 or 1: {perceptron_or.predict(np.array([0, 1]))}")
print(f"1 or 0: {perceptron_or.predict(np.array([1, 0]))}")
print(f"1 or 1: {perceptron_or.predict(np.array([1, 1]))}")
"""

snippets['MLP Forward Pass Structure'] = r"""
import numpy as np

# Sigmoid activation function
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# Example of a simple 2-layer MLP (Input -> Hidden -> Output)
# Assume 2 input neurons, 3 hidden neurons, 1 output neuron

# Initialize weights and biases (example random initialization)
# Weights from input to hidden layer (shape: num_inputs x num_hidden)
W1 = np.random.rand(2, 3)
b1 = np.random.rand(3) # Bias for hidden layer

# Weights from hidden to output layer (shape: num_hidden x num_output)
W2 = np.random.rand(3, 1)
b2 = np.random.rand(1) # Bias for output layer

def forward_pass(inputs, W1, b1, W2, b2):
    # Input layer is just the input data
    layer0_output = inputs # Shape: (batch_size, num_inputs) or (num_inputs,)

    # Hidden layer calculation
    # Linear transformation: inputs @ W1 + b1
    # Apply activation function
    layer1_input = np.dot(layer0_output, W1) + b1
    layer1_output = sigmoid(layer1_input) # Shape: (batch_size, num_hidden) or (num_hidden,)

    # Output layer calculation
    # Linear transformation: layer1_output @ W2 + b2
    # Apply activation function (e.g., sigmoid for binary classification)
    layer2_input = np.dot(layer1_output, W2) + b2
    layer2_output = sigmoid(layer2_input) # Shape: (batch_size, num_output) or (num_output,)

    return layer2_output, layer1_output # Return hidden output too, needed for backward pass

# Example Usage (single input)
input_data = np.array([0.5, -0.1]) # Example input for 2 neurons
output, hidden_output = forward_pass(input_data, W1, b1, W2, b2)

print("MLP Forward Pass Example:")
print(f"Input: {input_data}")
print(f"Hidden Layer Output: {hidden_output}")
print(f"Output Layer Output: {output}")
"""

snippets['MLP Backward Pass Structure'] = r"""
import numpy as np

# Sigmoid activation function and its derivative
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def sigmoid_derivative(x):
    s = sigmoid(x)
    return s * (1 - s)

# Assume we have weights, biases, and intermediate values from forward pass
# W1, b1, W2, b2, layer1_input, layer1_output, layer2_input, layer2_output
# And a target label 'y'

# Example values (should come from forward pass and training data)
# (using arbitrary values for demonstration)
W1 = np.random.rand(2, 3)
b1 = np.random.rand(3)
W2 = np.random.rand(3, 1)
b2 = np.random.rand(1)

inputs = np.array([0.5, -0.1])
y = np.array([1.0]) # Target label

layer2_output, layer1_output = None, None # Placeholder - these must come from forward pass
layer1_input, layer2_input = None, None # Placeholder - these must come from forward pass (pre-activation)

# --- Perform Forward Pass to get necessary values ---
layer1_input = np.dot(inputs, W1) + b1
layer1_output = sigmoid(layer1_input)
layer2_input = np.dot(layer1_output, W2) + b2
layer2_output = sigmoid(layer2_input) # Assuming sigmoid output layer

# --- Backward Pass Calculation ---

# 1. Calculate error at the output layer (e.g., using MSE derivative)
# For sigmoid output with MSE cost: dLoss/dOutput = 2 * (output - y) / N (batch size)
# Or simply (output - y) for a single sample gradient
output_error = layer2_output - y

# 2. Calculate gradient of loss w.r.t. output layer inputs (dLoss/d(layer2_input))
# Apply chain rule: dLoss/d(layer2_input) = dLoss/dOutput * dOutput/d(layer2_input)
# dOutput/d(layer2_input) is the derivative of the output activation function
output_delta = output_error * sigmoid_derivative(layer2_input) # Element-wise multiplication

# 3. Calculate gradients for W2 and b2
# dLoss/dW2 = dLoss/d(layer2_input) * d(layer2_input)/dW2
# d(layer2_input)/dW2 = layer1_output (transposed)
# Note: Handles batch dimension if inputs were (batch_size, ...)
# For single sample: dLoss/dW2 = layer1_output.T @ output_delta
grad_W2 = np.outer(layer1_output, output_delta) # Outer product for single sample

# dLoss/db2 = dLoss/d(layer2_input) * d(layer2_input)/db2
# d(layer2_input)/db2 = 1
grad_b2 = output_delta # For single sample, the gradient is just the delta

# 4. Calculate error/delta at the hidden layer (dLoss/d(layer1_output))
# Apply chain rule: dLoss/d(layer1_output) = dLoss/d(layer2_input) * d(layer2_input)/d(layer1_output)
# d(layer2_input)/d(layer1_output) = W2 (transposed)
hidden_error = np.dot(output_delta, W2.T) # Propagate error backward through W2

# 5. Calculate gradient of loss w.r.t. hidden layer inputs (dLoss/d(layer1_input))
# Apply chain rule: dLoss/d(layer1_input) = dLoss/d(layer1_output) * d(layer1_output)/d(layer1_input)
# d(layer1_output)/d(layer1_input) is derivative of hidden activation function
hidden_delta = hidden_error * sigmoid_derivative(layer1_input) # Element-wise multiplication

# 6. Calculate gradients for W1 and b1
# dLoss/dW1 = dLoss/d(layer1_input) * d(layer1_input)/dW1
# d(layer1_input)/dW1 = inputs (transposed)
grad_W1 = np.outer(inputs, hidden_delta) # Outer product for single sample

# dLoss/db1 = dLoss/d(layer1_input) * d(layer1_input)/db1
# d(layer1_input)/db1 = 1
grad_b1 = hidden_delta # For single sample

# These gradients (grad_W1, grad_b1, grad_W2, grad_b2) are used for updating weights and biases
# Update step: W1 -= learning_rate * grad_W1, etc.

print("MLP Backward Pass Gradient Calculation Structure:")
print(f"Output Delta: {output_delta}")
print(f"Gradient W2 (for update): {grad_W2}")
print(f"Gradient b2 (for update): {grad_b2}")
print(f"Hidden Delta: {hidden_delta}")
print(f"Gradient W1 (for update): {grad_W1}")
print(f"Gradient b1 (for update): {grad_b1}")
"""

snippets['Complete NN From Scratch Structure'] = r"""
import numpy as np

# Structure for a simple multi-layer neural network.
# Building a complete NN from scratch involves combining Forward and Backward Pass,
# implementing training loops, batching, loss functions, optimizers.

# class Layer:
#     def __init__(self, num_inputs, num_neurons, activation):
#         self.weights = np.random.rand(num_inputs, num_neurons) * 0.01 # Small random weights
#         self.biases = np.zeros(num_neurons) # Zero biases
#         self.activation = activation # Function like sigmoid, relu, etc.
#         self.input = None # To store input for backward pass
#         self.output = None # To store output for backward pass
#         self.activated_output = None # Output after activation

#     def forward(self, input_data):
#         self.input = input_data
#         self.output = np.dot(input_data, self.weights) + self.biases
#         self.activated_output = self.activation(self.output)
#         return self.activated_output

#     def backward(self, output_error, activation_derivative):
#         # Calculate gradient of activation
#         input_error = output_error * activation_derivative(self.output)
#         # Calculate gradients for weights and biases
#         weights_gradient = np.dot(self.input.T, input_error) # Handle batch dimension
#         biases_gradient = np.sum(input_error, axis=0) # Sum over batch dimension
#         # Propagate error backward to the previous layer
#         prev_layer_error = np.dot(input_error, self.weights.T)
#         return prev_layer_error, weights_gradient, biases_gradient

# class Network:
#     def __init__(self, layers):
#         self.layers = layers

#     def forward(self, input_data):
#         output = input_data
#         for layer in self.layers:
#             output = layer.forward(output)
#         return output

#     def backward(self, output_error, activation_derivatives):
#         # Propagate error backward through layers
#         grad_W, grad_b = [], []
#         error = output_error
#         for i in reversed(range(len(self.layers))):
#             layer = self.layers[i]
#             # Need derivative of the activation function for this layer's *output*
#             # If last layer has different activation, handle it separately
#             deriv = activation_derivatives[i] # Assumes list matches layer order
#             error, weights_grad, biases_grad = layer.backward(error, deriv)
#             grad_W.insert(0, weights_grad) # Insert at the beginning to keep order
#             grad_b.insert(0, biases_grad)
#         return grad_W, grad_b

#     def train(self, X_train, y_train, epochs, learning_rate):
#         # Needs loss function, optimizer (like SGD), batching
#         pass # Training loop implementation

# # Example Usage requires Activation functions and their derivatives
# # def sigmoid(x): ... ; def sigmoid_derivative(x): ...
# # network = Network([
# #     Layer(2, 3, sigmoid), # Input 2, Hidden 3, Sigmoid
# #     Layer(3, 1, sigmoid)  # Hidden 3, Output 1, Sigmoid
# # ])
# # predictions = network.forward(X_data)
# # ... then implement training loop with loss and backward pass

print("Complete Neural Network From Scratch structure outline provided.")
print("Requires implementing Layer and Network classes, forward/backward methods, activation functions/derivatives, loss function, optimizer, and training loop.")
"""

snippets['Sklearn Linear Regression'] = r"""
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np

# Sample data
X = np.array([[1], [2], [3], [4], [5]]) # Features (needs to be 2D)
y = np.array([2, 4, 5, 4, 5])        # Target

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=42)

# Create and train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
predictions = model.predict(X_test)

print("Sklearn Linear Regression Example:")
print(f"Training data shape: {X_train.shape}")
print(f"Testing data shape: {X_test.shape}")
print(f"Coefficients: {model.coef_}")
print(f"Intercept: {model.intercept_}")
print(f"Predictions on test set: {predictions}")
print(f"Actual values on test set: {y_test}")
"""

snippets['Sklearn Logistic Regression'] = r"""
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris
import numpy as np

# Load sample data (Iris dataset, binary classification)
iris = load_iris()
X, y = iris.data, iris.target

# Use only two classes for binary classification example (e.g., Setosa vs Versicolor)
X_binary = X[y < 2]
y_binary = y[y < 2]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X_binary, y_binary, test_size=0.3, random_state=42)

# Create and train the model
model = LogisticRegression()
model.fit(X_train, y_train)

# Make predictions
predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test) # Get probabilities

print("Sklearn Logistic Regression Example (Binary Classification):")
print(f"Training data shape: {X_train.shape}")
print(f"Testing data shape: {X_test.shape}")
print(f"Coefficients: {model.coef_}")
print(f"Intercept: {model.intercept_}")
print(f"Predictions on test set: {predictions}")
print(f"Actual values on test set: {y_test}")
print(f"Predicted probabilities (first 5): \n{probabilities[:5]}")
"""

snippets['Sklearn K-Means Clustering'] = r"""
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
import matplotlib.pyplot as plt
import numpy as np

# Generate sample data
X, _ = make_blobs(n_samples=300, centers=4, cluster_std=0.60, random_state=0)

# Apply K-Means
n_clusters = 4
kmeans = KMeans(n_clusters=n_clusters, random_state=0, n_init=10) # n_init is recommended in recent sklearn
kmeans.fit(X)

# Get cluster assignments and centroids
labels = kmeans.labels_
centers = kmeans.cluster_centers_

print("Sklearn K-Means Clustering Example:")
print(f"Number of clusters: {n_clusters}")
print(f"Cluster assignments (first 10): {labels[:10]}")
print(f"Cluster centroids:\n{centers}")

# Optional: Plotting the clusters (requires matplotlib)
# plt.scatter(X[:, 0], X[:, 1], c=labels, s=50, cmap='viridis')
# plt.scatter(centers[:, 0], centers[:, 1], c='red', s=200, alpha=0.7, marker='X')
# plt.title("K-Means Clustering")
# plt.xlabel("Feature 1")
# plt.ylabel("Feature 2")
# plt.show()
print("\nK-Means results calculated. Optional plotting code included.")
"""

snippets['Sklearn Evaluation Measures (Regression)'] = r"""
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

# Example true and predicted values (regression)
y_true = np.array([3, -0.5, 2, 7])
y_pred = np.array([2.5, 0.0, 2, 8])

# Calculate metrics
mse = mean_squared_error(y_true, y_pred)
mae = mean_absolute_error(y_true, y_pred)
r2 = r2_score(y_true, y_pred)

print("Sklearn Evaluation Measures (Regression Example):")
print(f"True values: {y_true}")
print(f"Predicted values: {y_pred}")
print(f"\nMean Squared Error (MSE): {mse}")
print(f"Mean Absolute Error (MAE): {mae}")
print(f"R-squared (R2) Score: {r2}")
"""

snippets['Sklearn Evaluation Measures (Classification)'] = r"""
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report, roc_curve, auc
import numpy as np
import matplotlib.pyplot as plt # For ROC curve

# Example true and predicted values (binary classification)
# 0: Negative class, 1: Positive class
y_true = np.array([0, 1, 0, 1, 0, 1, 1, 0, 0, 1])
y_pred = np.array([0, 1, 1, 1, 0, 0, 1, 0, 1, 1]) # Some incorrect predictions
y_scores = np.array([0.1, 0.8, 0.6, 0.9, 0.3, 0.2, 0.7, 0.4, 0.55, 0.95]) # Probabilities for positive class

# Calculate metrics using y_true and y_pred
accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred)
recall = recall_score(y_true, y_pred)
f1 = f1_score(y_true, y_pred)
conf_matrix = confusion_matrix(y_true, y_pred)
class_report = classification_report(y_true, y_pred)

print("Sklearn Evaluation Measures (Classification Example):")
print(f"True labels: {y_true}")
print(f"Predicted labels: {y_pred}")
print(f"\nAccuracy: {accuracy}")
print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1 Score: {f1}")
print(f"\nConfusion Matrix:\n{conf_matrix}")
print(f"\nClassification Report:\n{class_report}")

# ROC Curve requires probability scores (y_scores)
# Calculate ROC curve points (False Positive Rate, True Positive Rate)
fpr, tpr, thresholds = roc_curve(y_true, y_scores)
# Calculate Area Under the Curve (AUC)
roc_auc = auc(fpr, tpr)

print(f"\nROC AUC Score: {roc_auc}")

# Optional: Plotting the ROC curve (requires matplotlib)
# plt.figure()
# plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
# plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--') # Random guess line
# plt.xlim([0.0, 1.0])
# plt.ylim([0.0, 1.05])
# plt.xlabel('False Positive Rate')
# plt.ylabel('True Positive Rate')
# plt.title('Receiver Operating Characteristic (ROC) Curve')
# plt.legend(loc="lower right")
# plt.show()
print("\nROC AUC calculated. Optional plotting code for ROC curve included.")
"""