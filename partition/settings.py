# Print debug messages
debug = False
debug_log = open("logs/debug.txt", "a+")

# Run a 1 circuit only
single_circuit = True
# Circuit to run (if running 1 circuit only)
circuit_name = "cm150a"

# Show GUI
gui = True

# Global variable for output file (ignore)
out_file = None

# Genetics algorithm parameters
n_iterations = 10000
population_size = 50
mutation_factor = 10

# Control whether algorithm stops at iteration limit or time limit
time_limited = True
time_limit = 60

# GUI settings
screensize = {
    "width": 1500, 
    "height": 800
}
canvas_border = 50

background_colour = "white"
line_colour = "black"

# Grid calculations
grid = {}
grid["left"] = canvas_border
grid["right"] = screensize["width"] - canvas_border
grid["top"] = canvas_border
grid["bottom"] = screensize["height"] - canvas_border
grid["middlex"] = grid["left"] + (grid["right"] - grid["left"]) / 2.0
grid["middley"] = grid["top"] + (grid["bottom"] - grid["top"]) / 2.0

