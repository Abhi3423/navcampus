import random
import numpy as np
import tensorflow as tf
from collections import deque
from tkinter import messagebox, simpledialog
from tqdm import tqdm
import heapq
import time
from itertools import permutations

# Define the Deep Q-Learning Agent
class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)  # Replay buffer
        self.gamma = 0.95  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):
        """Build the neural network for Q-value approximation."""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(24, input_dim=self.state_size, activation='relu'),
            tf.keras.layers.Dense(24, activation='relu'),
            tf.keras.layers.Dense(self.action_size, activation='linear')
        ])
        model.compile(loss='mse', optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay buffer."""
        self.memory.append((state, action, reward, next_state, done))

    def choose_action(self, state):
        """Choose an action using epsilon-greedy policy."""
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        state = np.reshape(state, [1, self.state_size])
        q_values = self.model.predict(state, verbose=0)
        return np.argmax(q_values[0])

    def replay(self, batch_size):
        """Train the model using experiences from the replay buffer."""
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                next_state = np.reshape(next_state, [1, self.state_size])
                target = reward + self.gamma * np.amax(self.model.predict(next_state, verbose=0)[0])
            state = np.reshape(state, [1, self.state_size])
            target_f = self.model.predict(state, verbose=0)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        """Load a pre-trained model."""
        self.model.load_weights(name)

    def save(self, name):
        """Save the trained model."""
        self.model.save_weights(name)

# Define the environment for pathfinding
class PathfindingEnv:
    def __init__(self, canvas, start, goal):
        self.canvas = canvas
        self.start = start
        self.goal = goal
        self.state_size = 2  # (x, y) position
        self.action_size = 4  # Up, Down, Left, Right
        self.current_state = start

    def reset(self):
        """Reset the environment to the start state."""
        self.current_state = self.start
        return self.current_state

    def step(self, action):
        """Take an action and return the next state, reward, and done flag."""
        x, y = self.current_state
        if action == 0:  # Up
            y = max(y - 1, 0)
        elif action == 1:  # Down
            y = min(y + 1, self.canvas.size_row - 1)
        elif action == 2:  # Left
            x = max(x - 1, 0)
        elif action == 3:  # Right
            x = min(x + 1, self.canvas.size_col - 1)

        next_state = (x, y)
        self.current_state = next_state

        # Check if the next state is the goal
        done = (next_state == self.goal)
        reward = 1 if done else -0.1  # Reward for reaching the goal or penalize for each step

        return next_state, reward, done

# Function to train the DQN agent
def train_dqn_agent(canvas, start, goal, episodes=100, batch_size=32):
    env = PathfindingEnv(canvas, start, goal)
    agent = DQNAgent(env.state_size, env.action_size)

    for episode in tqdm(range(episodes), desc="Training DQN Agent"):
        state = env.reset()
        state = np.array(state)
        total_reward = 0
        done = False

        while not done:
            action = agent.choose_action(state)
            next_state, reward, done = env.step(action)
            next_state = np.array(next_state)
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward

            if done:
                print(f"Episode: {episode + 1}, Total Reward: {total_reward}, Epsilon: {agent.epsilon:.2f}")
                break

            if len(agent.memory) > batch_size:
                agent.replay(batch_size)

    return agent

# Function to find a path using the trained DQN agent
def find_path_with_dqn(canvas, start, goal, agent):
    env = PathfindingEnv(canvas, start, goal)
    state = env.reset()
    state = np.array(state)
    path = [state]
    done = False

    while not done:
        action = agent.choose_action(state)
        next_state, _, done = env.step(action)
        next_state = np.array(next_state)
        path.append(next_state)
        state = next_state

    return path

# Function to draw the path on the canvas
def draw_path(canvas, path):
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        canvas.canvas.create_line(
            x1 * canvas.grid_size + canvas.grid_size // 2,
            y1 * canvas.grid_size + canvas.grid_size // 2,
            x2 * canvas.grid_size + canvas.grid_size // 2,
            y2 * canvas.grid_size + canvas.grid_size // 2,
            fill="blue", width=2
        )
        canvas.canvas.update()

# Main function to generate paths using DQN
def generate_paths(canvas):
    if len(canvas.selected_cells) < 2:
        messagebox.showwarning("Warning", "You need at least two selected grid points to generate paths.")
        return
    
    # Metrics initialization
    total_time_taken = 0
    total_nodes_explored = 0

    # Start timing
    start_time = time.time()
    
    points = list(canvas.selected_cells)
    for start_point, goal_point in permutations(points, 2):
        start_cell, start_name = start_point
        goal_cell, goal_name = goal_point

        print(f"Attempting path generation from {start_name} to {goal_name}")
        start = (start_cell[0], start_cell[1])
        goal = (goal_cell[0], goal_cell[1])

        # Train the DQN agent
        agent = train_dqn_agent(canvas, start, goal)

        # Find and draw the path
        path = find_path_with_dqn(canvas, start, goal, agent)
        draw_path(canvas, path)

        print(f"Path successfully generated from {start_name} to {goal_name}")
    
    
    total_nodes_explored = sum(len(path) for path, _ in canvas.generated_paths if path)
    print(f"Total nodes explored: {total_nodes_explored}")
    # End timing
    total_time_taken = time.time() - start_time

    # Calculate operation speed
    operation_speed = total_nodes_explored / total_time_taken if total_time_taken > 0 else 0

    # Print or return metrics
    print(f"Total time taken: {total_time_taken:.2f} seconds")
    print(f"Total nodes explored: {total_nodes_explored}")
    print(f"Operation speed: {operation_speed:.2f} nodes/second")

def validate_paths(canvas):
    """Validate all generated paths and remove only the invalid ones from the canvas."""
    print("Validating all paths...")
    valid_paths = []
    for path, line_ids in canvas.generated_paths:
        start_node = path[0]
        goal_node = path[-1]
        current_node = goal_node
        valid = True

        reverse_path = []
        while current_node is not None:
            reverse_path.append((current_node.x, current_node.y))
            current_node = current_node.parent

        if reverse_path[-1] != (start_node.x, start_node.y):
            valid = False
            print(f"Invalid path from {start_node} to {goal_node}, removing it.")

        if valid:
            valid_paths.append((path, line_ids))
        else:
            for line_id in line_ids:
                canvas.canvas.delete(line_id)

    canvas.generated_paths = valid_paths
    print("Path validation completed.")

def create_grid(canvas):
    """Create a 10x10 grid on the canvas."""
    grid_size = canvas.grid_size
    width, height = 1600, 900

    for x in range(0, width, grid_size):
        for y in range(0, height, grid_size):
            rect_id = canvas.canvas.create_rectangle(x, y, x + grid_size, y + grid_size, outline="gray")
            canvas.grid_items.append(rect_id)
            canvas.canvas.tag_bind(rect_id, '<Button-1>', lambda event, x=x, y=y: select_cell(canvas, x, y))

def select_cell(canvas, x, y):
    """Highlight a cell when selected and prompt for a name."""
    cell = (x // canvas.grid_size, y // canvas.grid_size)
    if cell in canvas.selected_cells:
        canvas.selected_cells.remove(cell)
        print(f"Deselected cell at {cell}")
        canvas.canvas.create_rectangle(x, y, x + canvas.grid_size, y + canvas.grid_size, outline="gray", fill='white')
    else:
        point_name = simpledialog.askstring("Point Name", "Enter a name for this point:")
        if point_name:
            canvas.selected_cells.add((cell, point_name))
            print(f"Selected cell at {cell} with name '{point_name}'")
            canvas.canvas.create_rectangle(x, y, x + canvas.grid_size, y + canvas.grid_size, outline="gray", fill='yellow')
        else:
            messagebox.showwarning("Warning", "A name is required for each selected point.")

def disable_grid_mode(canvas):
    """Disable grid selection."""
    canvas.grid_mode = False
    for grid_item in canvas.grid_items:
        canvas.canvas.delete(grid_item)
    canvas.grid_items.clear()
        
    # Print the selected cells
    print("Selected cells:")
    for cell, name in canvas.selected_cells:
        print(f"Cell: {cell}, Name: {name}")
        
    messagebox.showinfo("Grid Mode", "Grid selection completed and saved.")

def dijkstra(canvas, start, goal):
    """Run Dijkstra's algorithm on the graph of loaded paths to find the shortest path."""
    distances = {start: 0}
    previous_nodes = {}
    queue = [(0, start)]
    visited = set()

    while queue:
        current_distance, current_node = heapq.heappop(queue)
        if current_node in visited:
            continue
        visited.add(current_node)

        # If goal is reached, reconstruct the path
        if current_node == goal:
            path = []
            while current_node in previous_nodes:
                path.append(current_node)
                current_node = previous_nodes[current_node]
            path.append(start)
            path.reverse()
            return path

        # Explore neighbors in the path graph
        for neighbor, weight in canvas.path_graph.get(current_node, []):
            if neighbor not in visited:
                distance = current_distance + weight
                if neighbor not in distances or distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(queue, (distance, neighbor))

    return None  # No path found