import random
from typing import Callable, List, Optional
import numpy as np
from ..common.chromosome import Chromosome

class Population:
    def __init__(self, individuals: List['Chromosome'] = None, initialize : Optional[Callable[[int], List['Chromosome']]] = None, population_size : int = 50):
        self.population_size = population_size
        if initialize:
            self.individuals = initialize(self.population_size)
        self.individuals = individuals

        
    def copy(self) -> 'Population':
        return Population([ind.copy() for ind in self.individuals])
    
    def best(self) -> 'Chromosome':
        return max(self.individuals, key=lambda ind: ind._fitness)

    def average_fitness(self) -> float:
        return np.mean([ind.fitness for ind in self.individuals])

    def tournament_selection(self, k: int = 2) -> 'Chromosome':
        candidates = np.random.choice(self.individuals, size=k)
        return max(candidates, key=lambda ind: ind.evaluate())
    
    def _update_population(self, new_individuals: List['Chromosome'], 
                      type: str = 'replace', elitism_rate: float = 0.1) -> 'Population':
        """
        Met à jour la population selon différentes stratégies.
        """

        if type == 'replace':
            self.individuals = new_individuals
            return self.population.copy()

        elif type == 'union':
            self.individuals.extend(new_individuals)
            return self.population.copy()

        elif type == 'intersection':
            self.individuals = [ind for ind in self.individuals if ind in new_individuals]
            return self.population.copy()
        
        elif type == 'replace_worst':
            # Remplace les pires individus par les nouveaux
            sorted_individuals = sorted(self.individuals, key=lambda x: x.evaluate())
            n_replace = min(len(new_individuals), len(sorted_individuals))
            self.individuals = sorted_individuals[:-n_replace] + new_individuals[:n_replace]
            return self.population.copy()
        
        elif type == 'elit':
            n_elite = int(len(self.individuals) * elitism_rate)
            elite = sorted(self.individuals, key=lambda x: x.fitness)[:n_elite]
            new_sorted = sorted(new_individuals, key=lambda x: x.fitness)
            self.individuals = elite + new_sorted[:len(self.individuals) - n_elite]
            return self.population.copy()
        elif type == 'elit_union':
            combined = self.individuals + new_individuals
            combined_sorted = sorted(combined, key=lambda x: x.fitness)
            self.individuals = combined_sorted[:len(self.individuals)]
            return self.population.copy()
        
        elif type == 'truncation':
            all_individuals = self.individuals + new_individuals
            self.individuals = sorted(all_individuals, key=lambda x: x.fitness)[:len(self.individuals)]
            return self.population.copy()
        
        elif type == 'tournament':
            def tournament_selection(pop, k=2):
                return min(random.sample(pop, k), key=lambda x: x.fitness)
            total = len(self.individuals)
            combined = self.individuals + new_individuals
            self.individuals = [tournament_selection(combined) for _ in range(total)]
            return self.population.copy()
        
        elif type == 'rank':
            combined = self.individuals + new_individuals
            ranked = sorted(combined, key=lambda x: x.fitness)
            self.individuals = ranked[:len(self.individuals)]
            return self.population.copy()
        
        elif type == 'roulette':
            combined = self.individuals + new_individuals
            total_fitness = sum(1.0 / (x.fitness + 1e-6) for x in combined)
            probs = [(1.0 / (x.fitness + 1e-6)) / total_fitness for x in combined]
            self.individuals = random.choices(combined, weights=probs, k=len(self.individuals))
            return self.population.copy()
        elif type == 'steady_state':
            # Replace only a fraction of the worst individuals
            n_replace = int(len(self.individuals) * (1 - elitism_rate))
            survivors = sorted(self.individuals, key=lambda x: x.fitness)[:len(self.individuals) - n_replace]
            new_best = sorted(new_individuals, key=lambda x: x.fitness)[:n_replace]
            self.individuals = survivors + new_best
            return self.population.copy()
        elif type == 'random_replace':
            self.individuals = random.sample(self.individuals + new_individuals, len(self.individuals))
            return self.population.copy()
        elif type == 'age_based':
            # Supposons que chaque individu a un attribut 'age'
            all_individuals = self.individuals + new_individuals
            self.individuals = sorted(all_individuals, key=lambda x: x.age)[:len(self.individuals)]
            return self.population.copy()
        
        elif type == 'crowding':
            # Stratégie simple de remplacement par similarité
            self.individuals = [
                new if random.random() < 0.5 else old
                for old, new in zip(self.individuals, new_individuals)
            ]
            return self.population.copy()
        elif type == 'no_update':
            return self.population.copy()
        
        else:
            raise ValueError(f"Unknown update type: {type}")
    
    def sort_individuals(self) -> 'Population':
        """
        Trie les individus de la population par fitness décroissant.
        """
        self.individuals.sort(key=lambda x: x.fitness, reverse=True)
        return self.individuals   