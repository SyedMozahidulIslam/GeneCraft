"""
src/genetics/mutation_processor.py
=====================================
MutationProcessor — applies various mutation strategies to genomes.
Separates mutation logic from the Genome class for extensibility.
"""
from __future__ import annotations
import random
import math
from typing import Optional
from genetics.genome import Genome


class MutationProcessor:
    """
    Applies targeted and random mutations to Genome objects.

    Strategies
    ----------
    gaussian   — standard normal perturbation (default evolution)
    directional — push a specific gene toward a target value
    neutral     — mutation with no fitness effect (genetic drift)
    catastrophic — large-scale mutation simulating radiation/disease
    """

    def __init__(self, base_rate: float = 0.05) -> None:
        self.base_rate = base_rate

    def gaussian(self, genome: Genome, rate: Optional[float] = None) -> Genome:
        """Standard Gaussian mutation — used in natural evolution each generation."""
        r = rate if rate is not None else genome.genetic.mutation_rate
        for gene, value in genome.all_genes().items():
            if random.random() < r:
                from genetics.genome import _GENE_RANGES
                lo, hi = _GENE_RANGES.get(gene, (0.0, 10.0))
                delta  = random.gauss(0.0, (hi - lo) * 0.05)
                genome.set(gene, value + delta)
        return genome

    def directional(self, genome: Genome, gene: str,
                    direction: float = 1.0, strength: float = 0.2) -> Genome:
        """Push a specific gene in a direction (adaptation pressure)."""
        current = genome.get(gene)
        if current is not None:
            genome.set(gene, current + direction * strength)
        return genome

    def catastrophic(self, genome: Genome, intensity: float = 0.5) -> Genome:
        """Large-scale mutation — models radiation event or mutagenic agent."""
        for gene, value in genome.all_genes().items():
            if random.random() < intensity:
                from genetics.genome import _GENE_RANGES
                lo, hi = _GENE_RANGES.get(gene, (0.0, 10.0))
                genome.set(gene, random.uniform(lo, hi))
        return genome

    def controlled(self, genome: Genome, gene: str, target: float,
                   step: float = 0.3) -> Genome:
        """
        Player-triggered controlled mutation — move gene toward target value.
        Used by Research unlock: 'creature_targeted_mutation'.
        """
        current = genome.get(gene)
        if current is None:
            return genome
        diff     = target - current
        delta    = math.copysign(min(abs(diff), step), diff)
        genome.set(gene, current + delta)
        return genome
