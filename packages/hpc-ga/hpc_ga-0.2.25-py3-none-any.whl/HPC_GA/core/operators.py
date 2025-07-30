from abc import ABC, abstractmethod
import numpy as np
from ..common.chromosome import Chromosome

class Crossover(ABC):
    @abstractmethod
    def __call__(self, *parents: 'Chromosome', rate: float = 1.0) -> list['Chromosome']:
        """Perform crossover on two or more parents and return offspring."""
        pass

class UniformCrossover(Crossover):
    def __call__(self, *parents: 'Chromosome', rate: float = 1.0) -> list['Chromosome']:
        if len(parents) < 2:
            raise ValueError("UniformCrossover requires at least two parents.")
        
        num_genes = len(parents[0].genes)
        num_parents = len(parents)
        # Stack all parent genes into a matrix (shape: num_parents x num_genes)
        parent_genes = np.array([p.genes for p in parents])
        
        # Create new genes by selecting gene i from a random parent
        indices = np.random.randint(0, num_parents, size=num_genes)
        new_genes = np.array([parent_genes[i, j] for j, i in enumerate(indices)])
        
        child = parents[0].__class__(new_genes)
        return [child]

class Mutator(ABC):
    def __init__(self, rate: float = 0.01):
        self.rate = rate

    @abstractmethod
    def __call__(self, chrom: 'Chromosome') -> 'Chromosome':
        pass

class GaussianMutator(Mutator):
    def __call__(self, chrom: 'Chromosome') -> 'Chromosome':
        noise = np.random.normal(0, 0.1, size=len(chrom.genes))
        mask = np.random.random(size=len(chrom.genes)) < self.rate
        new_genes = np.where(mask, chrom.genes + noise, chrom.genes)
        return chrom.__class__(new_genes)
