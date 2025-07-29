import ray
import numpy as np
import random
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from HPC_GA.core.operators import Crossover, Mutator
from ..common.population import Population
from ..common.chromosome import Chromosome
from ..parallel.utils import split_population

ray.init(ignore_reinit_error=True)

@ray.remote
class IslandActor:
    def __init__(self, ga_class, ga_config: Dict[str, Any], migration_config: Optional[Dict[str, Any]] = None):
        self.ga = ga_class(**ga_config)
        self.migration_config = migration_config if migration_config else {}

    def run_generation(self) -> Population:
        self.ga._evolve()
        return self.ga.population

    def get_best(self) -> Chromosome:
        return self.ga.population.best()

    def receive_migrants(self, migrants: List[Chromosome]):
        strategy = self.migration_config.get('strategy', 'worst')
        individuals = self.ga.population.individuals

        if strategy == 'worst':
            sorted_inds = sorted(individuals)
            for i, migrant in enumerate(migrants):
                if i < len(sorted_inds):
                    sorted_inds[i] = migrant
            self.ga.population = Population(sorted_inds)

        elif strategy == 'random':
            indices = np.random.choice(len(individuals), size=len(migrants), replace=False)
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
                idx = random.randint(0, len(individuals) - 1)
                individuals[idx] = migrant
            self.ga.population = Population(individuals)


class ParallelGA(ABC):
    def __init__(self, ga_class,  ga_config: Dict[str, Any], parallel_config: Dict[str, Any] = None):
        self.ga_class = ga_class
        self.initial_population = ga_config.get('population', Population())
        self.ga_config = ga_config
        self.parallel_config = parallel_config

    @abstractmethod
    def run(self, generations: int) -> Chromosome:
        pass


class IslandModel(ParallelGA):
    def __init__(self, ga_class, ga_config: Dict[str, Any], parallel_config: Dict[str, Any]):
        super().__init__(ga_class, ga_config, parallel_config)
        self.islands = []
        self._setup_islands()

    def _setup_islands(self):
        n_islands = self.parallel_config.get('n_islands', 4)
        sub_pops = split_population(self.initial_population, n_islands)
        self.islands = [
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
            self.islands = [island.run_generation.remote() for island in self.islands]

            if gen > 0 and gen % migration_interval == 0:
                self._migrate()

        return self._get_global_best()

    def _migrate(self):
        topology = self.parallel_config.get('migration_topology', 'ring')
        migration_size = self.parallel_config.get('migration_size', 2)
        n = len(self.islands)

        all_migrants = ray.get([island.get_best.remote() for island in self.islands])

        if topology == 'ring':
            for i in range(n):
                migrants = all_migrants[i:i + migration_size]
                self.islands[(i + 1) % n].receive_migrants.remote(migrants)

        elif topology == 'bidirectional_ring':
            for i in range(n):
                migrants = all_migrants[i:i + migration_size]
                self.islands[(i + 1) % n].receive_migrants.remote(migrants)
                self.islands[(i - 1 + n) % n].receive_migrants.remote(migrants)

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
        bests = ray.get([island.get_best.remote() for island in self.islands])
        return max(bests, key=lambda x: x.fitness)


class CellularModel(ParallelGA):
    def __init__(self, ga_class, ga_config: Dict[str, Any], neighborhood_type='von_neumann'):
        super().__init__(ga_class, ga_config)
        self.neighborhood_type = neighborhood_type

    def run(self, generations: int) -> Chromosome:
        population = self.initial_population
        for _ in range(generations):
            new_individuals = []
            for i in range(len(population.individuals)):
                neighbors = self._get_neighbors(i, population)
                if not neighbors:
                    continue
                elif len(neighbors) > 1:
                    parents = self.ga_class.selection(neighbors, nb_parents=self.ga_class.nb_parents)
                    children = self.ga_class.crossover(*parents)
                    mutated_children = [self.ga_class.mutator(child) for child in children]
                else:
                    mutated_children = [self.ga_class.mutator(neighbors[0])]
                new_individuals.extend(mutated_children)
            population = Population(new_individuals)
            self.ga_class.update_population(population, type=self.ga_class.update_type)
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
        for offset in [-1, 0, 1]:
            idx = index + offset
            if 0 <= idx < len(population.individuals):
                neighbors.append(population.individuals[idx])
        return neighbors


class MasterSlaveModel(ParallelGA):
    def __init__(self, ga_class, ga_config: Dict[str, Any], parallelisme_type: str = 'fitness'):
        super().__init__(ga_class, ga_config)
        self.ga_instance = ga_class(**ga_config)
        self.type = parallelisme_type

    def run(self, generations: int) -> Chromosome:
        if self.type not in ['fitness', 'crossovers', 'mutations', 'crossovers and mutations']:
            raise ValueError("Invalid parallelisme_type.")
        if self.type == 'fitness':
            return self._run_fitness_parallel(generations)
        elif self.type == 'crossovers':
            return self._run_crossover_parallel(generations)
        elif self.type == 'mutations':
            return self._run_mutation_parallel(generations)
        elif self.type == 'crossovers and mutations':
            return self._run_crossover_mutation_parallel(generations)

    def _run_fitness_parallel(self, generations: int) -> Chromosome:
        for _ in range(generations):
            parents = self.ga_instance.selection(self.ga_instance.population, nb_parents=self.ga_instance.nb_parents)
            children = self.ga_instance.crossover(*parents)
            mutated_children = [self.ga_instance.mutator(child) for child in children]
            works = [MasterSlaveModel.evaluate_individual.remote(ind) for ind in mutated_children]
            results = ray.get(works)
            self.ga_instance.update_fitness(mutated_children, results)
        return self.ga_instance.population.best()

    def _run_crossover_parallel(self, generations: int, nb_crossover: int = 1) -> Chromosome:
        for _ in range(generations):
            list_parents = [self.ga_instance.selection(self.ga_instance.population, nb_parents=self.ga_instance.nb_parents) for _ in range(nb_crossover)]
            works = [MasterSlaveModel.crossover_individuals.remote(parents, self.ga_instance.crossover) for parents in list_parents]
            children_batches = ray.get(works)
            children = [child for batch in children_batches for child in batch]
            mutated_children = [self.ga_instance.mutator(child) for child in children]
            self.ga_instance.update_population(Population(mutated_children), type=self.ga_instance.update_type)
        return self.ga_instance.population.best()

    def _run_mutation_parallel(self, generations: int) -> Chromosome:
        for _ in range(generations):
            parents = self.ga_instance.selection(self.ga_instance.population, nb_parents=self.ga_instance.nb_parents)
            children = self.ga_instance.crossover(*parents)
            works = [MasterSlaveModel.mutate_individual.remote(child, self.ga_instance.mutator) for child in children]
            mutated_children = ray.get(works)
            self.ga_instance.update_population(Population(mutated_children), type=self.ga_instance.update_type)
        return self.ga_instance.population.best()

    def _run_crossover_mutation_parallel(self, generations: int) -> Chromosome:
        for _ in range(generations):
            parents = self.ga_instance.selection(self.ga_instance.population, nb_parents=self.ga_instance.nb_parents)
            works = [MasterSlaveModel.crossover_individuals.remote([p1, p2], self.ga_instance.crossover) for p1, p2 in zip(parents[::2], parents[1::2])]
            children_batches = ray.get(works)
            children = [child for batch in children_batches for child in batch]
            works = [MasterSlaveModel.mutate_individual.remote(child, self.ga_instance.mutator) for child in children]
            mutated_children = ray.get(works)
            self.ga_instance.update_population(Population(mutated_children), type=self.ga_instance.update_type)
        return self.ga_instance.population.best()

    @ray.remote
    def evaluate_individual(individual: Chromosome) -> float:
        return individual.evaluate()

    @ray.remote
    def crossover_individuals(parents: List[Chromosome], crossover : Crossover) -> List[Chromosome]:
        return crossover(*parents)

    @ray.remote
    def mutate_individual(individual: Chromosome, mutator : Mutator) -> Chromosome:
        return mutator(individual)
