import ray
import numpy as np
import random
from typing import List, Dict, Any, Optional, Type, Tuple
from abc import ABC, abstractmethod

from HPC_GA.core.operators import Crossover, Mutator
from ..common.population import Population 
from ..common.chromosome import Chromosome
from ..parallel.utils import split_population

@ray.remote
class IslandActor:
    def __init__(self, ga_class: Type, ga_config: Dict[str, Any], migration_config: Optional[Dict[str, Any]] = None):
        self.ga = ga_class(**ga_config)
        self.migration_config = migration_config if migration_config else {}

    def run_generation(self) -> Population:
        self.ga._evolve()
        self.ga._update_history()
        return self.ga.population

    def get_best(self) -> Chromosome:
        return self.ga.population.best()

    def receive_migrants(self, migrants: List[Chromosome]) -> None:
        strategy = self.migration_config.get('strategy', 'worst')
        individuals = self.ga.population.individuals
        
        if len(migrants) == 0:
            return

        if strategy == 'worst':
            sorted_inds = sorted(individuals)
            for i, migrant in enumerate(migrants):
                if i < len(sorted_inds):
                    sorted_inds[i] = migrant
            self.ga.population = Population(sorted_inds)

        elif strategy == 'random':
            n_replace = min(len(migrants), len(individuals))
            indices = np.random.choice(len(individuals), size=n_replace, replace=False)
            for i, idx in enumerate(indices):
                individuals[idx] = migrants[i]
            self.ga.population = Population(individuals)

        elif strategy == 'replace_best':
            sorted_inds = sorted(individuals, reverse=True)
            for i, migrant in enumerate(migrants):
                if i < len(sorted_inds):
                    sorted_inds[i] = migrant
            self.ga.population = Population(sorted_inds)

        elif strategy == 'replace_random':
            for migrant in migrants:
                if len(individuals) > 0:
                    idx = random.randint(0, len(individuals) - 1)
                    individuals[idx] = migrant
            self.ga.population = Population(individuals)


class ParallelGA(ABC):
    def __init__(self, ga_class: Type, ga_config: Dict[str, Any], parallel_config: Optional[Dict[str, Any]] = None):
        self.ga_class = ga_class
        self.initial_population = ga_config.get('population', Population())
        self.ga_config = ga_config
        self.parallel_config = parallel_config or {}

    @abstractmethod
    def run(self, generations: int) -> Chromosome:
        pass


class IslandModel(ParallelGA):
    def __init__(self, ga_class: Type, ga_config: Dict[str, Any], parallel_config: Dict[str, Any]):
        super().__init__(ga_class, ga_config, parallel_config)
        self.island_refs: List[ray.ObjectRef] = []  # Store references to the actors
        self._setup_islands()

    def _setup_islands(self) -> None:
        n_islands = self.parallel_config.get('n_islands', 4)
        sub_pops = split_population(self.initial_population, n_islands)
        self.island_refs = [  # Store the actor references
            IslandActor.remote(
                self.ga_class,
                {**self.ga_config, 'population': sub_pop},
                migration_config=self.parallel_config.get('migration_config', {})
            )
            for sub_pop in sub_pops
        ]

    def run(self, generations: int) -> Chromosome:
        migration_interval = self.parallel_config.get('migration_interval', 5)

        for gen in range(generations):
            # Run generation on all islands and wait for completion
            ray.get([island.run_generation.remote() for island in self.island_refs])

            if gen > 0 and gen % migration_interval == 0:
                self._migrate()

        return self._get_global_best()

    def _migrate(self) -> None:
        topology = self.parallel_config.get('migration_topology', 'ring')
        migration_size = min(
            self.parallel_config.get('migration_size', 2),
            len(self.initial_population.individuals) // len(self.island_refs)
        )
        n = len(self.island_refs)

        all_migrants = ray.get([island.get_best.remote() for island in self.island_refs])

        if topology == 'ring':
            for i in range(n):
                migrants = all_migrants[i:i + migration_size]
                self.island_refs[(i + 1) % n].receive_migrants.remote(migrants)

        elif topology == 'bidirectional_ring':
            for i in range(n):
                migrants = all_migrants[i:i + migration_size]
                self.island_refs[(i + 1) % n].receive_migrants.remote(migrants)
                self.island_refs[(i - 1) % n].receive_migrants.remote(migrants)

        elif topology == 'complete':
            for i, island in enumerate(self.islands):
                migrants = [m for j, m in enumerate(all_migrants) if j != i]
                island.receive_migrants.remote(migrants[:migration_size])

        elif topology == 'random':
            for _ in range(n):
                src = random.randint(0, n - 1)
                dst = random.randint(0, n - 1)
                while dst == src:
                    dst = random.randint(0, n - 1)
                migrants = all_migrants[src:src + migration_size]
                self.islands[dst].receive_migrants.remote(migrants)

        elif topology == 'broadcast':
            for i in range(n):
                for j in range(n):
                    if i != j:
                        migrants = all_migrants[i:i + migration_size]
                        self.islands[j].receive_migrants.remote(migrants)

        elif topology == 'custom':
            custom_topology_func = self.parallel_config.get('custom_topology_func')
            if custom_topology_func:
                custom_topology_func(self.islands, all_migrants, migration_size)

    def _get_global_best(self) -> Chromosome:
        bests = ray.get([island.get_best.remote() for island in self.island_refs])
        return max(bests, key=lambda x: x.fitness)
    
class CellularModel(ParallelGA):
    def __init__(self, ga_class: Type, ga_config: Dict[str, Any], parallel_config: Dict[str, Any]):
        super().__init__(ga_class, ga_config, parallel_config)
        self.neighborhood_type = parallel_config.get('neighborhood_type', 'von_neumann')
        self.ga_instance = ga_class(**ga_config)

    def run(self, generations: int) -> Chromosome:
        population = self.initial_population
        for _ in range(generations):
            new_individuals = []
            for i in range(len(population.individuals)):
                neighbors = self._get_neighbors(i, population)
                if not neighbors:
                    continue
                
                if len(neighbors) >= self.ga_instance.nb_parents:
                    parents = random.sample(neighbors, self.ga_instance.nb_parents)
                    children = self.ga_instance.crossover(*parents)
                else:
                    children = neighbors  # Fallback if not enough parents
                
                mutated_children = [self.ga_instance.mutator(child) for child in children]
                new_individuals.extend(mutated_children)
            
            population = Population(new_individuals)
            self.ga_instance.population = population
        return population.best()

    def _get_neighbors(self, index: int, population: Population) -> List[Chromosome]:
        if self.neighborhood_type == 'von_neumann':
            return self._von_neumann_neighbors(index, population)
        elif self.neighborhood_type == 'moore':
            return self._moore_neighbors(index, population)
        else:
            raise ValueError("Invalid neighborhood type. Choose 'von_neumann' or 'moore'.")

    def _von_neumann_neighbors(self, index: int, population: Population) -> List[Chromosome]:
        neighbors = []
        if index > 0:
            neighbors.append(population.individuals[index - 1])
        if index < len(population.individuals) - 1:
            neighbors.append(population.individuals[index + 1])
        return neighbors

    def _moore_neighbors(self, index: int, population: Population) -> List[Chromosome]:
        neighbors = []
        grid_size = int(np.sqrt(len(population.individuals)))
        if grid_size * grid_size != len(population.individuals):
            return self._von_neumann_neighbors(index, population)
            
        row, col = index // grid_size, index % grid_size
        for r_offset in [-1, 0, 1]:
            for c_offset in [-1, 0, 1]:
                if r_offset == 0 and c_offset == 0:
                    continue  # Skip self
                r, c = row + r_offset, col + c_offset
                if 0 <= r < grid_size and 0 <= c < grid_size:
                    neighbors.append(population.individuals[r * grid_size + c])
        return neighbors


class MasterSlaveModel(ParallelGA):
    def __init__(self, ga_class: Type, ga_config: Dict[str, Any], parallel_config: Dict[str, Any]):
        super().__init__(ga_class, ga_config, parallel_config)
        self.parallelism_type = parallel_config.get('parallelism_type', 'fitness')
        self.ga_instance = ga_class(**ga_config)

    def run(self, generations: int) -> Chromosome:
        if self.parallelism_type == 'fitness':
            return self._run_fitness_parallel(generations)
        elif self.parallelism_type == 'crossovers':
            return self._run_crossover_parallel(generations)
        elif self.parallelism_type == 'mutations':
            return self._run_mutation_parallel(generations)
        elif self.parallelism_type == 'crossovers_and_mutations':
            return self._run_crossover_mutation_parallel(generations)
        else:
            raise ValueError("Invalid parallelism_type. Choose from: 'fitness', 'crossovers', 'mutations', 'crossovers_and_mutations'")

    def _run_fitness_parallel(self, generations: int) -> Chromosome:
        for _ in range(generations):
            parents = [self.ga_instance.selection() for _ in range(self.ga_instance.nb_parents)]
            children = self.ga_instance.crossover(*parents)
            mutated_children = [self.ga_instance.mutator(child) for child in children]
            works = [self.evaluate_individual.remote(ind) for ind in mutated_children]
            results = ray.get(works)
            for child, fitness in zip(mutated_children, results):
                child.fitness = fitness
            self.ga_instance.update_population(Population(mutated_children))
        return self.ga_instance.population.best()

    def _run_crossover_parallel(self, generations: int) -> Chromosome:
        for _ in range(generations):
            parents = [self.ga_instance.selection() for _ in range(self.ga_instance.nb_parents)]
            works = [self.crossover_individuals.remote(parents, self.ga_instance.crossover)]
            children = ray.get(works)[0]
            mutated_children = [self.ga_instance.mutator(child) for child in children]
            self.ga_instance.update_population(Population(mutated_children))
        return self.ga_instance.population.best()

    def _run_mutation_parallel(self, generations: int) -> Chromosome:
        for _ in range(generations):
            parents = [self.ga_instance.selection() for _ in range(self.ga_instance.nb_parents)]
            children = self.ga_instance.crossover(*parents)
            works = [self.mutate_individual.remote(child, self.ga_instance.mutator) for child in children]
            mutated_children = ray.get(works)
            self.ga_instance.update_population(Population(mutated_children))
        return self.ga_instance.population.best()

    def _run_crossover_mutation_parallel(self, generations: int) -> Chromosome:
        for _ in range(generations):
            parents = [self.ga_instance.selection() for _ in range(self.ga_instance.nb_parents)]
            works = [self.crossover_individuals.remote(parents, self.ga_instance.crossover)]
            children = ray.get(works)[0]
            works = [self.mutate_individual.remote(child, self.ga_instance.mutator) for child in children]
            mutated_children = ray.get(works)
            self.ga_instance.update_population(Population(mutated_children))
        return self.ga_instance.population.best()

    @ray.remote
    def evaluate_individual(individual: Chromosome) -> float:
        return individual.evaluate()

    @ray.remote
    def crossover_individuals(parents: List[Chromosome], crossover: Crossover) -> List[Chromosome]:
        return crossover(*parents)

    @ray.remote
    def mutate_individual(individual: Chromosome, mutator: Mutator) -> Chromosome:
        return mutator(individual)