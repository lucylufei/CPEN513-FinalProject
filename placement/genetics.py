from util import *
from settings import *
import numpy as np
import random



class Genetics:
    '''
    Implementation of genetics algorithm for placement
    '''
    
    def __init__(self, canvas):
        '''
        Initialize class with permanent variables
        '''
        self.c = canvas
        
        
    def setup(self, configs, nets):
        '''
        Setup the simulation with the current circuit
        '''
        
        # Circuit parameters
        self.configs = configs
        self.nets = nets
        
        # Initialize placement map (NaN for empty cells)
        self.placement = np.zeros((configs["cols"], configs["rows"]))
        self.placement[:] = np.NaN
        random.seed()
        
        # Initialize simulation variables
        self.cells = {}
        self.current_cost = 0
        self.cost = {}
        
        self.population = []
        self.population_cost = {}
        
        
    def initialize(self):
        '''
        Generate initial population
        '''
        
        # Track lowest cost
        lowest_cost = -1
        
        # Generate genes for the population
        for i in range(population_size):
            
            # Choose a random placement
            placement = self.random_placement()
            
            # Add to population as string
            self.population.append(str(placement).replace("[", "").replace("]","").replace(" ", ""))
            
            # Calculate cost of random placement and track
            cost = self.calculate_cost(self.cells)
            self.population_cost[str(placement).replace("[", "").replace("]","").replace(" ", "")] = cost
            
            # Check for best placement with the lowest cost
            if cost < lowest_cost or lowest_cost == -1:
                best_placement = placement
                lowest_cost = cost
                
        # Use lowest cost placement as the initial best option
        self.cells = gene_to_placement(best_placement, self.configs)
        
        # Update global cost
        self.current_cost = lowest_cost
                
        # Update cost label on GUI
        if gui:
            self.c.delete("cost")
            self.c.create_text(
                grid["right"] - 100,
                20,
                text="Cost: {}".format(self.current_cost),
                fill="black",
                font=('Arial',20,'bold'),
                tag="cost"
            )
            
        # Reset all placement
        self.placement[:] = np.NaN
        
        for i in self.cells:
            # Track which cell is in which coordinate
            self.placement[self.cells[i][0], self.cells[i][1]] = i
                
        # Update the GUI
        if gui:
            self.draw_connections()
            self.update_labels()
        
        # Mark circuit as initialized
        self.initalized = True
        
        
    def random_placement(self):
        '''
        Initialize circuit with a random placement
        '''
        # Make a list of possible coordinates
        possible_placements = [(x, y) for x in range(0, self.configs["cols"]) for y in range(0, self.configs["rows"])]
        
        # Place every cell
        for i in range(self.configs["cells"]):
            (x, y) = random.choice(possible_placements)
            possible_placements.remove((x, y))
            # Track which coordinate each cell is at
            self.cells[i] = (x, y)
            
        # Double check that all cells have been accounted for
        assert len(self.cells) == self.configs["cells"]
        
        # Convert placement to a gene
        placement = placement_to_gene(self.cells, self.configs)
        
        debug_print("Current Placement:")
        debug_print(placement)
        
        return placement


                
    def update_labels(self):
        '''
        Update cell labels on GUI
        '''
        
        # Delete all previous labels
        self.c.delete("cell")
        # Add new labels
        for cell in self.cells:
            add_text(self.cells[cell][0], self.cells[cell][1], self.c, grid, cell, tag="cell")
        
        
    def draw_connections(self):
        '''
        Update connections on GUI
        '''
        
        # Delete all previous wires
        self.c.delete("wires")
        # Draw new wires
        for i, net in enumerate(self.nets):
            # Draw from first cell to the rest
            orig = self.cells[net[0]]
            for cell in net[1:]:
                dest = self.cells[cell]
                # Draw a curve
                if line_curve:
                    draw_line(orig, dest, self.c, grid, colour=wire_colour_palette[i % len(wire_colour_palette)], tag="wires", extra_point=i)
                # Draw a line
                else:
                    draw_line(orig, dest, self.c, grid, colour=wire_colour_palette[i % len(wire_colour_palette)], tag="wires")
        
            
    def calculate_cost(self, cells):
        '''
        Calculate the half perimeter cost
        '''
        
        # Track the cost for each net
        for i, net in enumerate(self.nets):
            self.cost[i] = calculate_half_perimeter(net, cells)

        # Sum up total cost
        total_cost = sum(self.cost[i] for i in range(self.configs["nets"]))
        debug_print("Total Cost: {}".format(total_cost))
        
        return total_cost
        

            
    def run_algorithm(self):
        '''
        Run the genetics algorithm
        '''
        
        for i in range(0, n_iterations):
            
            # Determine fit function
            debug_print("Determine fit function.")
            self.population_fit = {}
            self.set_fit_function()
            
            debug_print(self.population_fit)
            
            # Select 2 parents
            debug_print("Select parents.")
            parent1, parent2 = self.select_gene()
            
            # Create a child
            debug_print("Generate children. ")
            child = self.crossover(parent1, parent2)
            
            # Apply mutations
            debug_print("Mutate children.")
            child = self.mutate(child)
            
            # Replace weakest member of population
            debug_print("Update population")
            self.replace_population(child)
            
            debug_print("New population")
            for gene in self.population:
                debug_print("{g}: {c}".format(g=gene, c=self.population_cost[gene]))
            
        # Choose the best gene out of the current population
        self.choose_best_gene()
        
        print("Done! Cost = {}".format(self.current_cost))
        
        # Update final GUI
        if gui:
            self.draw_connections()
            self.update_labels()
            self.c.update()
            
            # Update temperature label on GUI
            self.c.delete("cost")
            self.c.create_text(
                grid["right"] - 100,
                20,
                text="Cost: {}".format(self.current_cost),
                fill="black",
                font=('Arial',20,'bold'),
                tag="cost"
            )
        
            
        
    def set_fit_function(self):
        '''
        Calculate the fit function to determine probability for each gene
        '''
        self.highest_cost = 0
        self.lowest_cost = -1
        
        # Find the higest and the lowest costs
        for gene in self.population_cost:
            if self.lowest_cost == -1:
                self.lowest_cost = self.population_cost[gene]
            
            if self.population_cost[gene] < self.lowest_cost:
                self.lowest_cost = self.population_cost[gene]
            elif self.population_cost[gene] > self.highest_cost:
                self.highest_cost = self.population_cost[gene]
        
        # Track the total fit (to proportionally select a gene)
        self.total = 0                
        for gene in self.population:
            # Calculate fit
            fit = (self.highest_cost - self.population_cost[gene])
            fit += (self.highest_cost - self.lowest_cost) / 3
            
            # Special edge case when all genes have the same fit
            if fit == 0:
                fit = 1
            
            assert fit > 0
            
            # Track total
            self.total += fit
            
            # Track fit
            self.population_fit[gene] = fit
                
        # Update current lowest cost
        self.current_cost = self.lowest_cost
        
        
    def select_gene(self):
        '''
        Choose parents randomly
        '''
        
        # Calculate fitness distribution (normalize)
        distribution = []
        for gene in self.population:
            distribution.append(self.population_fit[gene] / self.total)

        # Randomly select parents
        parent1 = random.choices(self.population, weights=distribution)[0]
        parent2 = random.choices(self.population, weights=distribution)[0]
        
        # Check that the parents are different (unless the entire population is identical)
        if len(set(self.population)) > 1:
            while parent2 == parent1:
                parent2 = random.choices(self.population, weights=distribution)[0]
        
        return parent1, parent2    
        
    
    def crossover(self, parent1, parent2):
        '''
        Create child
        '''
        
        # Reformat parent gene representation
        parent1 = [int(n) for n in parent1.split(",")]
        parent2 = [int(n) for n in parent2.split(",")]
        
        # Choose a random split
        split = random.randint(1, len(parent1)-1)
        
        debug_print("P1: {p1}|{p2}".format(p1=parent1[0:split], p2=parent1[split:]))
        debug_print("P2: {p1}|{p2}".format(p1=parent2[0:split], p2=parent2[split:]))
        
        # Create first part of the child
        child = parent1[0:split]
        
        # Create second part of the child
        for i, location in enumerate(parent2[split:]):
            
            # Copy from parent 2
            if location not in child:
                child.append(location)
                
            # Otherwise copy from parent 1
            elif parent1[split+i] not in child:
                child.append(parent1[split+i])
                
            # Otherwise choose randomly
            else:
                # Find out which locations are still empty
                all_locations = set(range(0, self.configs["cols"] * self.configs["rows"]))
                options = list(all_locations - set(child))
                # Choose a location
                new_location = random.choice(options)
                child.append(new_location)
                
                
        debug_print("C : {c1}|{c2}".format(c1=child[0:split], c2=child[split:]))
        
        # Double check that the child has no issues (duplicates)
        assert len(child) == len(set(child))
        
        return child
        
        
    def mutate(self, child):
        '''
        Apply mutations
        '''
        
        # Randomly choose how many mutations to perform (based on mutation factor)
        m = random.randint(0, int(len(child)/mutation_factor))
        
        debug_print("{} mutations.".format(m))
        debug_print("C : {}".format(child))
        
        # Get a list of all possible locations
        all_locations = set(range(0, self.configs["cols"] * self.configs["rows"]))
        
        # Perform m mutations
        for i in range(m):
            # Randomly choose a cell to move
            bit = random.randint(0, len(child)-1)
            
            # Determine which cells are still empty and choose
            options = list(all_locations - set(child))
            new_location = random.choice(options)
            
            # Move to new cell
            child[bit] = new_location
            
        debug_print("C : {}".format(child))
        
        # Double check that the child has no issues (duplicates)
        assert len(child) == len(set(child))
        return child
        
        
    def replace_population(self, child):
        '''
        Replace the weakest member with newly generated child
        '''
        highest_cost = 0
        
        # Find the worst gene
        for gene in self.population:
            if self.population_cost[gene] > highest_cost:
                worst_gene = gene
                highest_cost = self.population_cost[gene]
                
        # Remove worst gene
        debug_print("Remove worst gene: {}".format(worst_gene))
        self.population.remove(worst_gene)
        if worst_gene not in self.population:
            del self.population_cost[worst_gene]
        
        debug_print("Add child gene: {}".format(child))
        
        # Calculate cost of child
        child_partition = gene_to_placement(child, self.configs)
        child_cost = self.calculate_cost(child_partition)
        
        # Add child gene
        child = str(child).replace("[", "").replace("]","").replace(" ", "")
        self.population.append(child)
        self.population_cost[child] = child_cost
        
        
    def choose_best_gene(self):
        '''
        Choose the best gene from the population
        '''
        found = False
        
        # Search through population
        for gene in self.population:
            
            # Look for any gene with the same or lower cost than previous best
            if self.population_cost[gene] <= self.current_cost:
                self.current_cost = self.population_cost[gene]
                gene = [int(n) for n in gene.split(",")]
                self.cells = gene_to_placement(gene, self.configs)
                found = True
                
        # Must be found
        assert found
        
        # Reset all placement
        self.placement[:] = np.NaN
        
        for i in self.cells:
            # Track which cell is in which coordinate
            self.placement[self.cells[i][0], self.cells[i][1]] = i
        
        