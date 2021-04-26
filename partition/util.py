from settings import *
import random
import matplotlib
from matplotlib import cm

def debug_print(content):
    '''
    Special print statement (prints only in debug mode, otherwise logs to file)
    Input:
        content - content to be printed
    '''
    if debug:
        print(content)
    else:
        pass
        # debug_log.write(str(content))
        # debug_log.write("\n")
        
        
def initialize_partition(n_cells):
    '''
    Basic random initialization
    '''
    cells = list(range(0, n_cells))
    partition = {}
    partition["left"] = set()
    partition["right"] = set()
    
    while len(cells) > 0:
        # Randomly choose a cell for left partition
        cell = random.choice(cells)
        cells.remove(cell)
        partition["left"].add(cell)
        
        if len(cells) > 0:
            # Randomly choose a cell for right partition
            cell = random.choice(cells)
            cells.remove(cell)
            partition["right"].add(cell)
            
    # Check that the partition is legal
    assert check_legality(partition, n_cells)
    
    debug_print("Partition Left: {}".format(partition["left"]))
    debug_print("Partition Right: {}".format(partition["right"]))
    
    return partition     
        
        
def draw_partition(canvas, partition, configs, nets):
    '''
    Draw partition on GUI canvas
    '''
    
    # Make a list of possible locations for cells in each partition
    half = int(round(configs["cells"] / 2))
    left_partition = [(x, y) for x in range(0, half) for y in range(0, configs["cells"])]
    right_partition = [(x, y) for x in range(0, half) for y in range(0, configs["cells"])]
    
    cells = {}
    
    # Assign coordinates for each cell in the left partition randomly
    for cell in partition["left"]:
        coord = random.choice(left_partition)
        left_partition.remove(coord)
        # Draw the cell
        draw_circle(canvas, coord[0], coord[1], tag="cell")
        cells[cell] = coord
        write_cell(canvas, coord[0], coord[1], cell)
        
    # Assign coordinates for each cell in the right partition randomly
    for cell in partition["right"]:
        coord = random.choice(right_partition)
        right_partition.remove(coord)
        # Draw the cell
        draw_circle(canvas, coord[0]+half, coord[1], tag="cell")
        cells[cell] = (coord[0]+half, coord[1])
        write_cell(canvas, coord[0]+half, coord[1], cell)
            
    debug_print(cells)
    
    # Set up the colour palette to draw connections
    colour_range = 1.0 / len(nets)
            
    # Draw connections
    for i, net in enumerate(nets):
        # Set the first cell as the origin and draw lines to all other cells for the net
        orig = net[0]
        for cell in net[1:]:
            dest = cell
            draw_line(cells[orig], cells[dest], canvas, grid, colour=matplotlib.colors.to_hex(cm.hsv(i*colour_range)), tag="wire")
        

def write_cell(c, x, y, text, color="red", tag="cell"):
    '''
    Write the label for each cell
    '''
    # Convert coordinates to canvas grid
    x_left = grid["left"] + x * grid["x"]
    y_top = grid["top"] + y * grid["y"]
    
    c.create_text(
        x_left,
        y_top,
        text=text,
        font=('Arial',20,'bold'),
        fill=color,
        tag=tag
    )
    
        
def draw_circle(c, x, y, color="black", tag=None, size=20):
    '''
    Draw a circle
    '''
    
    # Convert coordinates to canvas grid
    x_left = grid["left"] + x * grid["x"]
    y_top = grid["top"] + y * grid["y"]
    x_right = x_left + size
    y_bottom = y_top + size
    
    c.create_oval(
        x_left, y_top, x_right, y_bottom, 
        fill=color,
        tag=tag
    )
    
    
        
def draw_line(orig, dest, c, grid, colour="gray", tag="", size=20):
    '''
    Draw a line from (orig) to (dest) on canvas (c) using (grid) with (colour) and (tag)
    extra_point to draw a curve instead of a straight line 
    '''
    
    # Calculate starting position and end positions on the canvas grid
    start_x = grid["left"] + orig[0] * grid["x"] + size/2
    start_y = grid["top"] + orig[1] * grid["y"] + size/2
    end_x = grid["left"] + dest[0] * grid["x"] + size/2
    end_y = grid["top"] + dest[1] * grid["y"] + size/2
    
    # Draw line
    c.create_line(
        start_x, 
        start_y, 
        end_x,
        end_y,
        width=3,
        fill=colour,
        tag=tag
    )


def cut_size(partition, nets):
    '''
    Calculate the cut size
    '''
    # Initialize to 0
    cut_size = 0
    
    # Iterate through each net
    for net in nets:
        left = False
        right = False
        
        for node in net:
            node_left = node in partition["left"]
            node_right = node in partition["right"]
            
            # Add to cut size if any nodes cross the partition
            if left and node_right or right and node_left:
                cut_size += 1
                break
            
            left = left or node_left
            right = right or node_right
            
    return cut_size
    
    
def write_cutsize(c, cut_size):
    '''
    Write cutsize on GUI canvas
    '''
    # Clear any previous text
    c.delete("cost")
    
    c.create_text(
        grid["right"] - 100,
        20,
        text="Cost: {}".format(cut_size),
        fill="black",
        font=('Arial',20,'bold'),
        tag="cost"
    )
    
    
def check_legality(partition, n_cells):
    '''
    Check whether the partition is legal
    '''
    # Check for even split
    if not abs(len(partition["left"]) - len(partition["right"])) <= 1:
        return False
    # Check that all nodes have been assigned
    if not len(partition["left"]) + len(partition["right"]) == n_cells:
        return False
        
    return True
    
    
def format_partition(partition):
    '''
    Format the partition string for printing
    '''
    string = ""
    
    string += "{}".format(partition["left"])
    string += "  ||  "
    string += "{}".format(partition["right"])
    
    return string
    
    
def draw_node(c, path, cost, colour="gray"):
    '''
    Draw node for branch and bound tree
    '''
    # Calculate grid coordinates for node
    depth = len(path)
    n_options = pow(2, depth)
    
    location = 0
    n = n_options
    for i in range(depth):
        n = n / 2
        location += n if path[i] == "right" else 0
        
    # Get x,y coordinates for node
    location_x = grid2["left"] + (1 + 2*location) * (grid2["right"] - grid2["left"]) / pow(2, depth+1)
    location_y = grid2["top"] + depth * grid["y"]
    
    c.create_oval(
        location_x, location_y, location_x + 20, location_y + 20, 
        fill=colour,
        tag="node"
    )
    
    c.create_text(
        location_x + 10,
        location_y + 10,
        text="{}".format(cost),
        fill="black",
        # font=('Arial',10,'bold'),
        tag="node"
    )
    

def draw_path(c, path, n_cells, colour="green"):
    '''
    Draw the path to the final selected partition on the tree
    '''
    
    # Ignore if the best option was the initial partition and not from the tree
    if (path == []):
        return
    
    # Find root node coordinates
    prev_node_x = grid2["left"] + (grid2["right"] - grid2["left"]) / 2
    prev_node_y = grid2["top"]
    
    # Draw line to each node
    for t in range(n_cells):
        cell = t + 1
        location = 0
        n = pow(2, cell)
        for i in range(cell):
            n = n / 2
            location += n if path[i] == "right" else 0
            
        # Get x,y coordinates to draw line to
        location_x = grid2["left"] + (1 + 2*location) * (grid2["right"] - grid2["left"]) / pow(2, cell+1)
        location_y = grid2["top"] + cell * grid["y"]
            
        # Draw line
        c.create_line(
            prev_node_x + 10, 
            prev_node_y + 10, 
            location_x + 10,
            location_y + 10,
            width=3,
            fill=colour,
            tag="node"
        )
        
        prev_node_x = location_x
        prev_node_y = location_y
        
        
def partition_to_gene(partition, n_cells):
    '''
    Convert partition data type to a gene representation
    Input:
        partition - tracks which partition each cell is in 
    Output:
        gene - a vector of partitions
    '''
    
    gene = ""
    for i in range(n_cells):
        if i in partition["left"]:
            gene += "0"
        elif i in partition["right"]:
            gene += "1"
        else:
            raise Exception
            
    return gene
    
    
def gene_to_partition(gene):
    '''
    Convert gene representation to original partition data type
    Input:
        gene - a vector of partitions
    Output:
        partition - dictionary tracking which partition each cell is in
    '''
    partition = {}
    partition["left"] = []
    partition["right"] = []
    
    for i, cell in enumerate(gene):
        if cell == "0":
            partition["left"].append(i)
        elif cell == "1":
            partition["right"].append(i)
        else:
            raise Exception
            
    return partition
        