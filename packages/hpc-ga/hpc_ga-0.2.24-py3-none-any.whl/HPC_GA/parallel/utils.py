import numpy as np
from typing import List
from ..common.population import Population

# Fonction utilitaire pour diviser la population
def split_population(pop: Population, n: int) -> List[Population]:
    # Crée une copie de la liste des individus pour éviter de modifier l'original
    individuals = pop.individuals.copy()
    np.random.shuffle(individuals)  # Mélange aléatoirement
    
    # Divise les indices en n groupes approximativement égaux
    split_indices = np.array_split(np.arange(len(individuals)), n)
    
    islands = []
    for indices in split_indices:
        # Crée une sous-population avec les individus correspondants
        sub_population = Population([individuals[i] for i in indices])
        islands.append(sub_population)
    
    return islands