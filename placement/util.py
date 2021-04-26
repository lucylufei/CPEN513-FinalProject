from settings import *
import time
import math

def debug_print(content):
    '''
    Special print statement (prints only in debug mode, otherwise logs to file)
    Input:
        content - content to be printed
    '''
    if debug:
        print(content)
    else:
        # debug_log.write(str(content))
        # debug_log.write("\n")
        pass

def calculate_half_perimeter(net, cells):
    '''
    Calculate the half perimeter for a net
    Input:
        net - [cell0, cell1, ...]
        cells - {cell0: (x0, y0), cell1: (x1, y1), ...}
    Output:
        half_perimeter - calculated half perimeter
    '''
    
    # Initialize bounds to the first cell
    smallest_x = cells[net[0]][0]
    smallest_y = cells[net[0]][1]
    largest_x = cells[net[0]][0]
    largest_y = cells[net[0]][1]
    
    # Search for the smallest and largest bound of the bounding box
    for cell in net:
        if cells[cell][0] < smallest_x:
            smallest_x = cells[cell][0]
            
        elif cells[cell][0] > largest_x:
            largest_x = cells[cell][0]
            
        if cells[cell][1] < smallest_y:
            smallest_y = cells[cell][1]
            
        elif cells[cell][1] > largest_y:
            largest_y = cells[cell][1]
            
    # Calculate half perimenter
    if "2" in no_assumptions:
        # No assumption 2
        half_perimeter = (largest_x - smallest_x + 1) + (largest_y - smallest_y + 1)
    else:
        half_perimeter = (largest_x - smallest_x) + (largest_y - smallest_y)
        
    # No assumption 1
    if "1" in no_assumptions:
        # Add in routing track (only in the vertical dimension)
        half_perimeter += (largest_y - smallest_y)
    
    # debug_print("Half perimeter calculated from ({x1}, {y1}) to ({x2}, {y2}) = {h}".format(x1=smallest_x, y1=smallest_y, x2=largest_x, y2=largest_y, h=half_perimeter))
    return half_perimeter
    
    
def add_text(x, y, c, grid, text, colour="black", tag=""):
    """
    Add (text) on the canvas (c) at (x, y) coordinates with (grid) size in (colour) with (tag)
    """
    c.create_text(
        grid["left"] + x * grid["x"] + grid["x"] / 2,
        grid["top"] + (y * 2) * grid["y"] + grid["y"] / 2,
        text=text,
        fill=colour,
        tag=tag,
    )
    
    
def draw_line(orig, dest, c, grid, colour="gray", tag="", extra_point=None):
    '''
    Draw a line from (orig) to (dest) on canvas (c) using (grid) with (colour) and (tag)
    extra_point to draw a curve instead of a straight line 
    '''
    
    # Calculate starting position and end positions on the canvas grid
    start_x = grid["left"] + orig[0] * grid["x"] + grid["x"]/2
    start_y = grid["top"] + (orig[1] * 2) * grid["y"] + grid["y"]/2
    end_x = grid["left"] + dest[0] * grid["x"] + grid["x"]/2
    end_y = grid["top"] + (dest[1] * 2) * grid["y"] + grid["y"]/2
    
    # Draw line
    if extra_point == None:
        c.create_line(
            start_x, 
            start_y, 
            end_x,
            end_y,
            width=3,
            fill=colour,
            tag=tag
        )
        
    # Draw curve
    else:
        # Determine midpoint from start to end and offset
        midpoint_x = start_x + (end_x - start_x)/2 + extra_point * 10
        midpoint_y = start_y + (end_y - start_y)/2 + extra_point * 10
        
        # Draw the curve
        c.create_line(
            start_x, 
            start_y, 
            midpoint_x,
            midpoint_y,
            end_x,
            end_y,
            width=2,
            fill=colour,
            tag=tag,
            smooth=1
        )
        
        
def check_add_cells(cell, additional_cells):
    '''
    Check if a (cell) has already been added to the list of (additional_cells)
    Input:
        cell - the cell to check for
        additional_cells - [{"cell": cell, "cell_xy": (x, y)}, ...]
    Output:
        True if cell is already in the list
        False otherwise
    '''
    for additional_cell in additional_cells:
        if additional_cell["cell"] == cell:
            return True
            
    return False
    

def initalize_results_file(filename):
    '''
    Write header for output file to record settings
    '''
    
    results_log = open("logs/{}".format(filename), "w+")

    results_log.write("\n\n{}\n".format("="*20))
    results_log.write(time.strftime("%Y-%m-%d %H:%M:%S\n", time.localtime()))
    results_log.write("{}\n".format("="*20))

    results_log.write("Settings\n")
    results_log.write("Population Size: {}\n".format(population_size))
    results_log.write("n Iterations: {}\n".format(n_iterations))
    results_log.write("Mutation Factor: {}\n".format(mutation_factor))
    results_log.close()
    
    
def placement_to_gene(cells, configs):
    '''
    Convert original placement data type to a gene representation
    Input:
        cells - lists all the cells and their (x, y) locations
        configs - holds configurations of the circuit such as the dimensions
    Output:
        gene - a vector of cell placements
    '''
    
    # Initialize gene
    gene = []
    
    # Append location for each cell
    for i in range(configs["cells"]):
        gene.append(cells[i][0] * configs["rows"] + cells[i][1])
        
    return gene
        
def gene_to_placement(gene, configs):
    '''
    Convert gene representation to original placement data type
    Input:
        gene - a vector of cell placements
        configs - holds configurations of the circuit such as the dimensions
    Output:
        cells - lists all the cells and their (x, y) locations
    '''
    
    # Initialize cells
    cells = {}
    
    # Double check that the gene is proper (no repeated locations)
    assert len(gene) == len(set(gene))
    
    # Append location to cell
    for i, g in enumerate(gene):
        
        # Calculate (x, y) coordinates from cell ID
        g = int(g)
        x = math.floor(g / configs["rows"])
        y = g % configs["rows"]
        
        # Add to cells
        cells[i] = (x, y)
        
    return cells