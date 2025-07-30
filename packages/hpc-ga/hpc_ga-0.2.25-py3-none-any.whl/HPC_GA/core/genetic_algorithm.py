from ast import arg
from typing import List, Callable, Optional
from ..common.population import Population
from .operators import Crossover, Mutator
from ..common.chromosome import Chromosome

class GeneticAlgorithm:
    def __init__(
        self,
        population: Population,
        crossover: Crossover,
        mutator: Mutator,
        nb_parents: int = 2,
        update_population: Optional[Callable[[Population], Population]] = None,
        update_type: str = 'replace',
        selection: Optional[Callable[..., Chromosome]] = None,
        max_generations: int = 100,
        k_tournament: int = 3
        
    ):
        self.population = population
        self.crossover = crossover
        self.mutator = mutator
        self.selection = selection if selection else population.tournament_selection
        self._update_population = update_population if update_population else population._update_population
        self.update_type = update_type
        self.max_generations = max_generations
        self.history = {"best": [], "avg": []}
        self.nb_parents = nb_parents
        self.k_tournament = k_tournament
        
    def run(self) -> Chromosome:
        for _ in range(self.max_generations):
            self._evolve()
            self._update_history()
        return self.population.best()

    def _evolve(self) -> None:
        offspring = []
        for _ in range(self.max_generations):
            parents = []
            for _ in range(self.nb_parents):
                parents.append(self.selection())
            children = self.crossover(*parents)
            offspring.extend([self.mutator(child) for child in children])

            # Mise à jour de la population
            population = self._update_population(offspring, self.update_type, self.k_tournament)
            self.population = population.copy()
        
    def _update_history(self) -> None:
        self.history["best"].append(self.population.best().fitness)
        self.history["avg"].append(self.population.average_fitness())
