# Debug mode
debug = False

# Single circuit mode
single_circuit = True
circuit_name = "cm138a"

# Update GUI (True for full speed, False for delayed updates)
gui = True

# Debug file
debug_log = open("logs/debug_log.txt", "a+")

# GUI settings
screensize = {
    "width": 1000, 
    "height": 500
}
canvas_border = 50

# Genetics algorithm parameters
population_size = 100
n_iterations = 10000
mutation_factor = 5

# Control whether algorithm stops at iteration limit or time limit
time_limited = False
time_limit = 60

grid = {}
grid["left"] = canvas_border
grid["right"] = screensize["width"] - canvas_border
grid["top"] = canvas_border
grid["bottom"] = screensize["height"] - canvas_border

background_colour = "white"
line_colour = "black"
line_curve = False

wire_colour_palette = [
    "pink",
    "plum", 
    "turquoise",
    "lightblue",
    "salmon",
    "lightgreen",
    "lavender",
    "DarkSeaGreen",
    "coral",
    "blue", 
    "green",
    "yellow"
]

# Display settings
display_delay = 0
graph_delay = 2000

# Cost function settings ("1" to ignore assumption 1, "2" to ignore assumption 2, "12" to ignore both)
no_assumptions = ""

