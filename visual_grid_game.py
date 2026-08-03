# visual_grid_game.py
import random
import tkinter as tk  


class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""
    # Add inside VisualGridHuntGame class

    DIRECTIONS = ["Up", "Right", "Down", "Left"]

    DIRECTION_VECTORS = {
        "Up": (0, 1),
        "Right": (1, 0),
        "Down": (0, -1),
        "Left": (-1, 0)
    }
    # Add inside VisualGridHuntGame class

    def turn_direction(self, direction, turn):
        index = self.DIRECTIONS.index(direction)

        if turn == "left":
            return self.DIRECTIONS[(index - 1) % 4]

        if turn == "right":
            return self.DIRECTIONS[(index + 1) % 4]

        return direction


    def adjacent_position(self, direction):
        dx, dy = self.DIRECTION_VECTORS[direction]

        return (
            self.agent_pos[0] + dx,
            self.agent_pos[1] + dy
        )


    def is_blocked(self, position):
        x, y = position

        return (
            x < 0
            or x >= self.width
            or y < 0
            or y >= self.height
            or position in self.walls
        )


    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]  # Starting position (x, y)

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            # Generate some default scattered walls for a larger grid
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

        # Add inside VisualGridHuntGame.__init__()

        self.agent_facing = "Up"
        self.last_move_hit_wall = False

        # Dynamically generate random food positions avoiding walls and agent start
        self.food_positions = set()
        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            pos_tuple = (fx, fy)
            if pos_tuple != (0, 0) and pos_tuple not in self.walls:
                self.food_positions.add(pos_tuple)

        # Generate adversarial opponents
        self.opponents = []
        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)
            op_pos = [ox, oy]
            if tuple(op_pos) != (0, 0) and tuple(op_pos) not in self.walls and tuple(op_pos) not in self.food_positions:
                self.opponents.append(op_pos)

        self.score = 0
        self.steps = 0
        self.collision = False
        self.toxic_traps = set()

        while len(self.toxic_traps) < 5:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)

            trap_pos = (tx, ty)

            if (
                trap_pos != (0, 0)
                and trap_pos not in self.walls
                and trap_pos not in self.food_positions
                and trap_pos not in [tuple(op) for op in self.opponents]
            ):
                self.toxic_traps.add(trap_pos)

  

    def get_percept(self) -> dict:
        left_direction = self.turn_direction(
            self.agent_facing,
            "left"
        )

        right_direction = self.turn_direction(
            self.agent_facing,
            "right"
        )

        ahead_position = self.adjacent_position(
            self.agent_facing
        )

        left_position = self.adjacent_position(
            left_direction
        )

        right_position = self.adjacent_position(
            right_direction
        )

        current_position = tuple(self.agent_pos)

        return {
            "wall_ahead": self.is_blocked(ahead_position),
            "wall_left": self.is_blocked(left_position),
            "wall_right": self.is_blocked(right_position),
            "food_here": current_position in self.food_positions,
            "toxin_here": current_position in self.toxic_traps,
            "opponent_ahead": ahead_position in [
                tuple(opponent) for opponent in self.opponents
            ],
            "last_move_hit_wall": self.last_move_hit_wall,
            "collision": self.collision
        }

        # Replace execute_action() with this

    def execute_action(self, action: str):
        self.steps += 1
        self.last_move_hit_wall = False

        if action == "TurnLeft":
            self.agent_facing = self.turn_direction(
                self.agent_facing,
                "left"
            )

        elif action == "TurnRight":
            self.agent_facing = self.turn_direction(
                self.agent_facing,
                "right"
            )

        elif action == "Forward":
            next_position = self.adjacent_position(
                self.agent_facing
            )

            if self.is_blocked(next_position):
                self.score -= 5
                self.last_move_hit_wall = True
            else:
                self.agent_pos = [
                    next_position[0],
                    next_position[1]
                ]

                if tuple(self.agent_pos) in self.toxic_traps:
                    self.score -= 15

        elif action == "Eat":
            current_position = tuple(self.agent_pos)

            if current_position in self.food_positions:
                self.food_positions.remove(current_position)
                self.score += 20

        for opponent in self.opponents:
            move = random.choice(
                ["Up", "Down", "Left", "Right", "Stay"]
            )

            if move == "Stay":
                continue

            dx, dy = self.DIRECTION_VECTORS[move]

            new_position = (
                opponent[0] + dx,
                opponent[1] + dy
            )

            if not self.is_blocked(new_position):
                opponent[0] = new_position[0]
                opponent[1] = new_position[1]

            if opponent == self.agent_pos:
                self.score -= 50
                self.collision = True

            # Add before GridGameGUI class

class ModelBasedAgent:

    DIRECTIONS = ["Up", "Right", "Down", "Left"]

    DIRECTION_VECTORS = {
        "Up": (0, 1),
        "Right": (1, 0),
        "Down": (0, -1),
        "Left": (-1, 0)
    }

    def __init__(self):
        self.relative_position = (0, 0)
        self.facing = "Up"
        self.visited_cells = {(0, 0)}

        self.last_action = None
        self.last_percept = None

    def turn_direction(self, direction, turn):
        index = self.DIRECTIONS.index(direction)

        if turn == "left":
            return self.DIRECTIONS[(index - 1) % 4]

        if turn == "right":
            return self.DIRECTIONS[(index + 1) % 4]

        return direction

    def relative_neighbour(self, direction):
        dx, dy = self.DIRECTION_VECTORS[direction]

        return (
            self.relative_position[0] + dx,
            self.relative_position[1] + dy
        )

    def update_internal_state(self, percept):
        if self.last_action == "TurnLeft":
            self.facing = self.turn_direction(
                self.facing,
                "left"
            )

        elif self.last_action == "TurnRight":
            self.facing = self.turn_direction(
                self.facing,
                "right"
            )

        elif self.last_action == "Forward":
            movement_succeeded = (
                self.last_percept is not None
                and not self.last_percept["wall_ahead"]
                and not percept["last_move_hit_wall"]
            )

            if movement_succeeded:
                self.relative_position = (
                    self.relative_neighbour(self.facing)
                )

        self.visited_cells.add(
            self.relative_position
        )

    def sense_and_act(self, percept):
        self.update_internal_state(percept)

        if percept["food_here"]:
            action = "Eat"

        elif percept["opponent_ahead"]:
            action = "TurnRight"

        else:
            left_direction = self.turn_direction(
                self.facing,
                "left"
            )

            right_direction = self.turn_direction(
                self.facing,
                "right"
            )

            forward_cell = self.relative_neighbour(
                self.facing
            )

            left_cell = self.relative_neighbour(
                left_direction
            )

            right_cell = self.relative_neighbour(
                right_direction
            )

            if (
                not percept["wall_ahead"]
                and forward_cell not in self.visited_cells
            ):
                action = "Forward"

            elif (
                not percept["wall_left"]
                and left_cell not in self.visited_cells
            ):
                action = "TurnLeft"

            elif (
                not percept["wall_right"]
                and right_cell not in self.visited_cells
            ):
                action = "TurnRight"

            elif not percept["wall_ahead"]:
                action = "Forward"

            elif not percept["wall_right"]:
                action = "TurnRight"

            else:
                action = "TurnLeft"

        self.last_action = action
        self.last_percept = dict(percept)

        return action

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision

    # Add before GridGameGUI class

class SimpleReflexAgent:

    def sense_and_act(self, percept):
        if percept["food_here"]:
            return "Eat"

        if percept["opponent_ahead"]:
            return "TurnRight"

        if percept["wall_ahead"]:
            return "TurnLeft"

        return "Forward"


class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, walls=None):
        self.root = root
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")

        self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food, num_opponents=num_opponents,
                                      custom_walls=walls)
        self.agent = SimpleReflexAgent()
        # Dynamically calculate cell size so the total canvas fits nicely within a 600x600 window ceiling
        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#000066",
                             fg="white")
        self.btn.pack(pady=5)

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")

        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1")

                # Only draw text if cell is large enough
                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text="W", fill="white",
                                            font=("Arial", 8, "bold"))
                # Draw toxic traps
        for tx, ty in self.env.toxic_traps:
            offset = self.cell_size * 0.25
            x1 = tx * self.cell_size + offset
            y1 = (self.env.height - 1 - ty) * self.cell_size + offset

            self.canvas.create_oval(
                x1,
                y1,
                x1 + self.cell_size * 0.5,
                y1 + self.cell_size * 0.5,
                fill="purple",
                outline="black"
            )

        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b",
                                    outline="#d97706")

        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6, fill="#990000",
                                         outline="#7a0000")

        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066",
                                outline="#1e3a8a")

    def run_loop(self):
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():
               # With these lines

                percept = self.env.get_percept()
                action = self.agent.sense_and_act(percept)
                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}")
                self.root.after(250, step)
            else:
                end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}"
                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()


if __name__ == "__main__":
    root = tk.Tk()
    # Try a larger grid size like 12x12 with 15 food and 3 opponents!
    app = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=2)
    root.mainloop()