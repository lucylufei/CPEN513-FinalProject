import os
import time
import datetime
from tkinter import *
from tkinter.ttk import *
from settings import *
from util import *
from netlist_parser import *
from genetics import *


# Initialize the debug log
debug_log.write("\n\n{}\n".format("="*20))
debug_log.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S\n"))
debug_log.write("{}\n".format("="*20))


# If only running 1 circuit
if single_circuit:

    # Open circuit
    debug_print("Reading configurations for {}...".format(circuit_name))
    configs, nets = parse_file("./benchmarks/{}.txt".format(circuit_name))

    # Initialize GUI
    if gui:
        root = Tk()
        frame = Frame(root, width=screensize["width"], height=screensize["height"])
        frame.grid(row=0, column=0)
        grid["x"] = (grid["right"] - grid["left"]) / configs["cells"]
        grid["y"] = (grid["bottom"] - grid["top"]) / configs["cells"]
        c = Canvas(frame, bg=background_colour, width=screensize["width"], height=screensize["height"])
        c.pack()

        c.create_text(
            20,
            20,
            text="Circuit: {}".format(circuit_name),
            fill="black",
            font=('Arial',20,'bold'),
            anchor=W
        )
        
        c.create_line(grid["middlex"], grid["top"], grid["middlex"], grid["bottom"], fill=line_colour)

        # Initialize genetics partitioner
        genetics = Genetics(c)
    
    else:
        # Initialize genetics partitioner
        genetics = Genetics(None)
        
    # Set up genetics partitioner with current circuit
    genetics.setup(configs, nets)

    if gui:
        # Add buttons
        button_frame = Frame(root, width=screensize["width"])
        init_button = Button(button_frame, text ="Initialize", command=genetics.initialize_partition)
        run_button = Button(button_frame, text ="Run Algorithm", command=genetics.run_algorithm)
        
        button_frame.grid(row=1, column=0)
        init_button.grid(row=0, column=0)
        run_button.grid(row=0, column=1)
        
    else:
        # If no GUI, record results in output file
        out_file_name = "logs/Results__{}".format(datetime.datetime.now().strftime("%m-%d_%H-%M-%S"))
        out_file = open(out_file_name, "w+")
        out_file.write("Number of iterations: {}\n".format(n_iterations))
        out_file.write("Population size: {}\n".format(population_size))
        out_file.write("Mutation factor: {}\n".format(mutation_factor))
        
        # Initialize partition
        genetics.initialize_partition()
        
        # Initialize output file
        out_file = open(out_file_name, "a+")
        out_file.write("="*40)
        out_file.write("\nCircuit: {}\n".format(circuit_name))
        start_time = datetime.datetime.now()
        out_file.write("Start time: {}\n".format(start_time.strftime("%m-%d %H:%M:%S")))
        out_file.write("\nInitial Partition\n")
        out_file.write("\tLeft: {}\n".format(genetics.partition["left"]))
        out_file.write("\tRight: {}\n".format(genetics.partition["right"]))
        out_file.write("Initial Cutsize: {}".format(genetics.current_cutsize))
        out_file.close()
        
        # Run algorithm
        genetics.run_algorithm()
        
        if time_limited:
            while datetime.datetime.now() - start_time < datetime.timedelta(minutes=time_limit):
                print(datetime.datetime.now() - start_time)
                genetics.run_algorithm()
        
        # Track time
        end_time = datetime.datetime.now()
        elapsed_time = end_time - start_time
        
        # Update output file with results
        out_file = open(out_file_name, "a+")
        genetics.write_output(out_file)
        out_file.write("End time: {}\n".format(end_time.strftime("%m-%d %H:%M:%S")))
        out_file.write("Elapsed time: {}\n".format(str(elapsed_time)))
        out_file.close()
        
        
    
# Otherwise, run "benchmark"
else:
    # Initialize output file
    out_file_name = "logs/Results__{}".format(time.strftime("%m-%d_%H-%M-%S", time.localtime()))
    out_file = open(out_file_name, "w+")
    out_file.write("Number of iterations: {}\n".format(n_iterations))
    out_file.write("Population size: {}\n".format(population_size))
    out_file.write("Mutation factor: {}\n".format(mutation_factor))
    
    # Get all benchmark files
    benchmarks = [f.replace(".txt", "") for f in os.listdir("benchmarks") if ".txt" in f]
    out_file.write("Benchmarks: {}\n".format(benchmarks))
    out_file.close()
    
    # Initialize GUI
    root = Tk()
    frame = Frame(root, width=screensize["width"], height=screensize["height"])
    frame.grid(row=0, column=0)
    c = Canvas(frame, bg=background_colour, width=screensize["width"], height=screensize["height"])
    c.pack()
    c.create_line(grid["middlex"], grid["top"], grid["middlex"], grid["bottom"], fill=line_colour)

    # Initialize genetics partitioner
    genetics = Genetics(c)

    # Add buttons
    button_frame = Frame(root, width=screensize["width"])
    init_button = Button(button_frame, text ="Initialize", command=genetics.initialize_partition)
    run_button = Button(button_frame, text ="Run", command=genetics.run_algorithm)
    
    button_frame.grid(row=1, column=0)
    init_button.grid(row=0, column=0)
    run_button.grid(row=0, column=1)
    
    for benchmark in benchmarks:
        # Clear the canvas
        c.delete("circuit")
        
        # Open circuit
        debug_print("Reading configurations for {}...".format(benchmark))
        configs, nets = parse_file("./benchmarks/{}.txt".format(benchmark))
        grid["x"] = (grid["right"] - grid["left"]) / configs["cells"]
        grid["y"] = (grid["bottom"] - grid["top"]) / configs["cells"]
        
        # Set up genetics partitioner with current circuit
        genetics.setup(configs, nets)

        # Update canvas
        c.create_text(
            20,
            20,
            text="Circuit: {}".format(benchmark),
            fill="black",
            font=('Arial',20,'bold'),
            anchor=W,
            tag="circuit"
        )
        
        # Initialize algorithm and output file
        genetics.initialize_partition()
        out_file = open(out_file_name, "a+")
        out_file.write("="*40)
        out_file.write("\nCircuit: {}\n".format(benchmark))
        out_file.write("\nInitial Partition\n")
        out_file.write("\tLeft: {}\n".format(genetics.partition["left"]))
        out_file.write("\tRight: {}\n".format(genetics.partition["right"]))
        out_file.close()
        
        # Run algorithm
        genetics.run_algorithm()
        
        # Record results
        out_file = open(out_file_name, "a+")
        genetics.write_output(out_file)
        out_file.close()
        
        # Keep GUI open for a few seconds to view visual results
        time.sleep(5)
        
        # Reset GUI
        genetics.clear()
        
    c.delete("circuit")
    c.create_text(
        20,
        20,
        text="DONE",
        fill="black",
        font=('Arial',20,'bold'),
        anchor=W
    )
    

# Run GUI
if gui:
    root.mainloop()
    
# Close debug log
debug_log.close()