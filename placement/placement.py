import os
import time
import datetime
from tkinter import *
from tkinter.ttk import *
from settings import *
from netlist_parser import *
from genetics import *


# Initialize the debug log
debug_log.write("\n\n{}\n".format("="*20))
debug_log.write(time.strftime("%Y-%m-%d %H:%M:%S\n", time.localtime()))
debug_log.write("{}\n".format("="*20))

# Choose circuit
filename = circuit_name

# Open circuit
debug_print("Reading configurations for {}...".format(filename))
configs, nets = parse_file("./benchmarks/{}.txt".format(filename))

if gui:
    # Initialize GUI
    root = Tk()
    grid["x"] = (grid["right"] - grid["left"]) / configs["cols"]
    grid["y"] = (grid["bottom"] - grid["top"]) / (configs["rows"] * 2 - 1)
    frame = Frame(root, width=screensize["width"], height=screensize["height"])
    frame.grid(row=0, column=0)
    c = Canvas(frame, bg=background_colour, width=screensize["width"], height=screensize["height"])
    c.pack()

    c.create_text(
        grid["left"],
        20,
        text="Circuit: {}".format(filename),
        fill="black",
        font=('Arial',20,'bold'),
        anchor=W
    )

    debug_print("Drawing grid...")
    for y in range(configs["rows"] * 2):
        c.create_line(grid["left"], grid["top"] + y * grid["y"], grid["right"], grid["top"] + y * grid["y"], fill=line_colour)
    for x in range(configs["cols"] + 1):
        for y in range(configs["rows"]):
            c.create_line(grid["left"] + x * grid["x"], grid["top"] + (y * 2) * grid["y"], grid["left"] + x * grid["x"], grid["top"] + (y * 2 + 1) * grid["y"], fill=line_colour)

    # Initialize genetics
    genetics = Genetics(c)
    genetics.setup(configs, nets)

    # Add buttons
    button_frame = Frame(root, width=screensize["width"])
    place_button = Button(button_frame, text ="Initialize", command=genetics.initialize)
    run_button = Button(button_frame, text ="Run Algorithm", command=genetics.run_algorithm)

    button_frame.grid(row=1, column=0)
    place_button.grid(row=0, column=0)
    run_button.grid(row=0, column=2)

    # Run GUI
    root.mainloop()
    
else:
    # If no GUI, record results in output file
    out_file_name = "logs/Results__{}".format(datetime.datetime.now().strftime("%m-%d_%H-%M-%S"))
    out_file = open(out_file_name, "w+")
    out_file.write("Number of iterations: {}\n".format(n_iterations))
    out_file.write("Population size: {}\n".format(population_size))
    out_file.write("Mutation factor: {}\n".format(mutation_factor))
    
    # Initialize genetics
    genetics = Genetics(None)
    genetics.setup(configs, nets)
    genetics.initialize()
            
    # Initialize output file
    out_file = open(out_file_name, "a+")
    out_file.write("="*40)
    out_file.write("\nCircuit: {}\n".format(filename))
    start_time = datetime.datetime.now()
    out_file.write("Start time: {}\n".format(start_time.strftime("%m-%d %H:%M:%S")))
    out_file.write("\nInitial Placement\n")
    out_file.write("{}\n".format(genetics.placement))
    out_file.write("Initial Cost: {}\n".format(genetics.current_cost))
    out_file.close()
    
    # Run genetics algorithm
    genetics.run_algorithm()
        
    # Continue running if time limit is not yet reached
    if time_limited:
        while datetime.datetime.now() - start_time < datetime.timedelta(minutes=time_limit):
            genetics.run_algorithm()
    
            
    # Track time
    end_time = datetime.datetime.now()
    elapsed_time = end_time - start_time
    
    # Update output file with results
    out_file = open(out_file_name, "a+")
    out_file.write("\nFinal Placement\n")
    out_file.write("{}\n".format(genetics.placement))
    out_file.write("Final Cost: {}\n".format(genetics.current_cost))
    out_file.write("End time: {}\n".format(end_time.strftime("%m-%d %H:%M:%S")))
    out_file.write("Elapsed time: {}\n".format(str(elapsed_time)))
    out_file.close()


    
# Close debug log
debug_log.close()
