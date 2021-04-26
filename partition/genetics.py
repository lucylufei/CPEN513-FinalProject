from util import *
from settings import *
import random


class Genetics():
    '''
    Implementation of Genetics Partitioner
    '''
    
    def __init__(self, canvas):
        '''
        Initialize with canvas
        '''
        self.c = canvas
        
        
    def setup(self, configs, nets):
        '''
        Set up the class with the current circuit parameters
        '''
        self.configs = configs
        self.nets = nets
        
        
    def clear(self):
        '''
        Clear the canvas
        '''
        self.c.delete("cell")
        self.c.delete("wire")
        self.c.delete("cost")
        self.c.delete("node")
        
        
    def initialize_partition(self):
        '''
        Initialize the algorithm with a partition (the cost of this partition prunes the tree)
        '''
        
        # Clear the GUI canvas
        if gui:
            self.c.delete("cell")
            self.c.delete("wire")
            self.c.delete("cost")
        
        
        # Reset/Initialie variables
        self.population = []
        self.population_cutsize = {}
        
        # Generate a random population of partitions
        self.random_population()
        
        # Calculate the cut size for each member of the population
        self.match_cutsize()
            
        debug_print("Initial population generated.")
        for gene in self.population:
            debug_print("{g}: {c}".format(g=gene, c=self.population_cutsize[gene]))
            
        # Choose the best initial partition
        debug_print("Choose best initial partition.")
        self.choose_best_gene()
        
        # Draw partition and write cost
        if gui:
            draw_partition(self.c, self.partition, self.configs, self.nets)
            write_cutsize(self.c, self.current_cutsize)
        
        
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
            
            # Choose 2 parents
            debug_print("Select parents.")
            parent1, parent2 = self.select_gene()
            
            # Generate 2 children
            debug_print("Generate children. ")
            child1, child2 = self.crossover(parent1, parent2)
            
            # Apply mutations
            debug_print("Mutate children.")
            child1, child2 = self.mutate(child1, child2)
            
            # Replace weakest members of the population with children
            debug_print("Update population")
            self.replace_population(child1, child2)
            
            debug_print("New population")
            for gene in self.population:
                debug_print("{g}: {c}".format(g=gene, c=self.population_cutsize[gene]))
            
        # Choose the best solution in the population
        self.choose_best_gene()
        
        # Double check that the partition is legal
        assert(check_legality(self.partition, self.configs["cells"]))
        
        print("DONE")
        self.print_results()
        
        # Update the canvas with the final results
        if gui:
            self.c.delete("cell")
            self.c.delete("wire")
            self.c.delete("cost")
            draw_partition(self.c, self.partition, self.configs, self.nets)
            write_cutsize(self.c, self.current_cutsize)
        
            self.c.update()
        
        
    def random_population(self):
        '''
        Generate a random initial population
        '''
        
        for i in range(population_size):
            # Create a partition
            partition = initialize_partition(self.configs["cells"])
            # Convert to gene
            gene = partition_to_gene(partition, self.configs["cells"])
            # Add to population
            self.population.append(gene)
            
            
    def match_cutsize(self):
        '''
        Calculate cut size for each member in the population
        '''
        self.current_cutsize = self.configs["cells"]
        
        for gene in self.population:
            # Convert to partition
            partition = gene_to_partition(gene)
            # Calculate cut size
            cutsize = cut_size(partition, self.nets)
            # Track cut size
            self.population_cutsize[gene] = cutsize
            
            # Track smallest cut size (best solution)
            if cutsize < self.current_cutsize:
                self.current_cutsize = cutsize
            
        
    def set_fit_function(self):
        '''
        Calculate the fit function to determine probability for each gene
        '''
        self.worst_cutsize = 0
        self.best_cutsize = self.configs["cells"]
        
        # Find the higest and the lowest costs
        for gene in self.population_cutsize:
            if self.population_cutsize[gene] < self.best_cutsize:
                self.best_cutsize = self.population_cutsize[gene]
            elif self.population_cutsize[gene] > self.worst_cutsize:
                self.worst_cutsize = self.population_cutsize[gene]
        
        # Track the total fit (to proportionally select a gene)
        self.total = 0                
        for gene in self.population:
            # Calculate fit
            fit = (self.worst_cutsize - self.population_cutsize[gene])
            fit += (self.worst_cutsize - self.best_cutsize) / 3
            
            # Special edge case when all genes have the same fit
            if fit == 0:
                fit = 1
            
            # Track total
            self.total += fit
            # Track fit
            self.population_fit[gene] = fit
                
        # Update current lowest cut size
        self.current_cutsize = self.best_cutsize
        
        
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
        # Choose a random split
        split = random.randint(1, len(parent1)-1)
        
        debug_print("P1: {p1}|{p2}".format(p1=parent1[0:split], p2=parent1[split:]))
        debug_print("P2: {p1}|{p2}".format(p1=parent2[0:split], p2=parent2[split:]))
        
        # Create first part of the children
        child1 = parent1[0:split]
        child2 = parent1[0:split]
        
        # First child copies from parent 2
        child1 += parent2[split:]
        
        # Second child copies inverse of parent 2
        for bit in parent2[split:]:
            if bit == "0":
                child2 += "1"
            elif bit == "1":
                child2 += "0"
            else:
                raise Exception
                
        debug_print("C1: {p1}|{p2}".format(p1=child1[0:split], p2=child1[split:]))
        debug_print("C2: {p1}|{p2}".format(p1=child2[0:split], p2=child2[split:]))
                
        # Double check children are correct
        assert len(child1) == len(child2)
        assert len(child1) == len(parent1)
        
        return child1, child2
        
        
    def mutate(self, child1, child2):
        '''
        Apply mutations
        '''
        
        # Randomly choose how many mutations to perform (based on mutation factor)
        m = random.randint(0, int(len(child1)/mutation_factor))
        
        debug_print("{} mutations.".format(m))
        debug_print("C1: {}".format(child1))
        
        # Apply mutations to child 1
        child1 = list(child1)
        
        # Perform m mutations
        for i in range(m):
            # Randomly choose a pin to move
            bit = random.randint(0, len(child1))
            if child1[i] == "0":
                child1[i] = "1"
            elif child1[i] == "1":
                child1[i] = "0"
            else:
                raise Exception
        
        debug_print("C1: {}".format(child1))
        
        # Make sure child is legal (balanced partition)
        child1 = self.make_legal(child1)
        debug_print("C1: {}".format(child1))
        
        debug_print("C2: {}".format(child2))
                
        # Apply mutations to child 2
        child2 = list(child2)
        
        # Perform m mutations
        for i in range(m):
            # Randomly choose a pin to move
            bit = random.randint(0, len(child2))
            if child2[i] == "0":
                child2[i] = "1"
            elif child2[i] == "1":
                child2[i] = "0"
            else:
                raise Exception
                
        debug_print("C2: {}".format(child2))
        
        # Make sure child is legal (balanced partition)
        child2 = self.make_legal(child2) 
        debug_print("C2: {}".format(child2))
                
        return child1, child2
                
        
    def make_legal(self, child):
        '''
        Make sure child is a balanced partition
        '''
        debug_print("Confirm legality.")
        
        # Count nodes in left partition and right partition
        left = child.count("0")
        right = child.count("1")
        
        # Choose a random starting index
        start = random.randint(0, len(child))
        
        # If already balanced, skip
        if abs(left - right) <= 1:
            pass
            
        # Othersise if more on left than right
        elif left > right:
            count = 0
            
            # Convert left nodes into right nodes starting from starting index
            while True:
                # Convert
                if child[start % len(child)] == "0":
                    child[start % len(child)] = "1"
                    count += 1
                
                # Check if enough have been converted
                if count == int((left - right) / 2):
                    break
                start += 1
                
        # Othersise if more on right than left
        elif right > left:
            count = 0
            
            # Convert left nodes into right nodes starting from starting index
            while True:
                # Convert
                if child[start % len(child)] == "1":
                    child[start % len(child)] = "0"
                    count += 1
                
                # Check if enough have been converted
                if count == int((right - left) / 2):
                    break
                start += 1
            
        else:
            raise Exception
        
        # Convert child back to string
        child = "".join(child)
        return child
        
        
    def replace_population(self, child1, child2):
        '''
        Replace the weakest members with newly generated children
        '''
        worst_cutsize = 0
        
        # Find the worst gene
        for gene in self.population:
            if self.population_cutsize[gene] > worst_cutsize:
                worst_gene = gene
                worst_cutsize = self.population_cutsize[gene]
                
        # Remove worst gene
        debug_print("Remove worst gene: {}".format(worst_gene))
        self.population.remove(worst_gene)
        if worst_gene not in self.population:
            del self.population_cutsize[worst_gene]
        
        # Add child gene
        debug_print("Add child gene: {}".format(child1))
        self.population.append(child1)
        child1_partition = gene_to_partition(child1)
        
        # Calculate cut size of child
        child1_cutsize = cut_size(child1_partition, self.nets)
        self.population_cutsize[child1] = child1_cutsize
        
        # Repeat for child 2
        worst_cutsize = 0
        # Find the worst gene
        for gene in self.population:
            if self.population_cutsize[gene] > worst_cutsize:
                worst_gene = gene
                worst_cutsize = self.population_cutsize[gene]
                
        # Remove worst gene
        debug_print("Remove worst gene: {}".format(worst_gene))
        self.population.remove(worst_gene)
        if worst_gene not in self.population:
            del self.population_cutsize[worst_gene]
        
        # Add child gene
        debug_print("Add child gene: {}".format(child2))
        self.population.append(child2)
        child2_partition = gene_to_partition(child2)
        
        # Calculate cut size of child
        child2_cutsize = cut_size(child2_partition, self.nets)
        self.population_cutsize[child2] = child2_cutsize
        
        
    def choose_best_gene(self):
        '''
        Choose the best gene from the population
        '''
        found = False
        
        # Search through population
        for gene in self.population:
            # Look for any gene with the same or lower cut size than previous best
            if self.population_cutsize[gene] <= self.current_cutsize:
                self.partition = gene_to_partition(gene)
                self.current_cutsize = self.population_cutsize[gene]
                found = True
                
        # Must be found
        assert found
            
        
    def print_results(self):
        '''
        Print the relevant stats after algorithm is complete
        '''
        print("\nFinal Cutsize: {}\n".format(self.current_cutsize))
        
        # print("Left: {}".format(self.partition["left"]))
        # print("Right: {}".format(self.partition["right"]))
        
        
            
    def write_output(self, out_file):
        '''
        Write the relevant stats to an output file 
        '''
        out_file.write("\nFinal Partition\n")
        out_file.write("\tLeft: {}\n".format(self.partition["left"]))
        out_file.write("\tRight: {}\n".format(self.partition["right"]))
        
        out_file.write("\nFinal Cutsize: {}\n\n".format(self.current_cutsize))