"""
src/genetics/genome_factory.py
================================
GenomeFactory — creates Genome instances from templates, random seeds,
and player-defined Gene Lab configurations.
"""
from __future__ import annotations
import random
import uuid
from typing import Dict, List, Optional
from genetics.genome import Genome, PhysicalGenes, BehavioralGenes, GeneticGenes, MetabolicGenes


class GenomeFactory:
    """
    Central factory for constructing Genome objects.

    Methods
    -------
    from_template(template_dict)  — build from a genes.json template
    from_lab_config(config_dict)  — build from Gene Lab UI values
    random(trophic_level)         — random genome biased by trophic role
    herbivore() / predator() / apex()  — convenience presets
    """

    def from_template(self, template: dict) -> Genome:
        """Build a Genome from a species_templates entry in genes.json."""
        raw = template.get("genome", {})
        g = Genome(
            physical   = PhysicalGenes.from_dict(  raw.get("physical",   {})),
            behavioral = BehavioralGenes.from_dict(raw.get("behavioral", {})),
            genetic    = GeneticGenes.from_dict(   raw.get("genetic",    {})),
            metabolic  = MetabolicGenes.from_dict( raw.get("metabolic",  {})),
        )
        # Small initial variance so a population isn't perfectly uniform
        for gene, val in g.all_genes().items():
            g.set(gene, val + random.gauss(0, 0.08))
        g.genome_id = str(uuid.uuid4())[:8]
        return g

    def from_lab_config(self, lab_values: Dict[str, float]) -> Genome:
        """
        Build a Genome from a flat dict of gene_name → value,
        as produced by the Gene Lab UI sliders.
        """
        g = Genome()
        for gene, value in lab_values.items():
            g.set(gene, float(value))
        g.genome_id = str(uuid.uuid4())[:8]
        return g

    def random(self, trophic_level: int = 2, biome: Optional[str] = None) -> Genome:
        """Random genome with soft biases by trophic role."""
        g = Genome()

        if trophic_level == 1:          # Producer — minimal traits
            g.genetic.reproduction_rate = random.uniform(3.0, 8.0)
            g.physical.size = random.uniform(0.5, 2.0)

        elif trophic_level == 2:        # Herbivore
            g.physical.speed       = random.uniform(3.0, 7.0)
            g.physical.size        = random.uniform(1.5, 5.0)
            g.behavioral.fearfulness    = random.uniform(5.0, 9.0)
            g.behavioral.social_behavior= random.uniform(5.0, 9.0)
            g.genetic.reproduction_rate = random.uniform(2.0, 5.0)

        elif trophic_level == 3:        # Omnivore
            g.physical.speed       = random.uniform(4.0, 7.0)
            g.behavioral.aggression     = random.uniform(3.0, 6.0)
            g.behavioral.intelligence   = random.uniform(3.0, 7.0)

        elif trophic_level == 4:        # Carnivore
            g.physical.speed       = random.uniform(5.0, 9.0)
            g.physical.strength    = random.uniform(5.0, 9.0)
            g.physical.bite_force  = random.uniform(4.0, 8.0)
            g.behavioral.aggression     = random.uniform(5.0, 9.0)
            g.behavioral.fearfulness    = random.uniform(1.0, 4.0)
            g.genetic.reproduction_rate = random.uniform(0.8, 2.0)

        else:                           # Apex
            g.physical.speed       = random.uniform(7.0, 10.0)
            g.physical.strength    = random.uniform(7.0, 10.0)
            g.physical.size        = random.uniform(5.0, 10.0)
            g.physical.bite_force  = random.uniform(6.0, 10.0)
            g.behavioral.aggression     = random.uniform(7.0, 10.0)
            g.behavioral.fearfulness    = random.uniform(0.5, 2.0)
            g.genetic.reproduction_rate = random.uniform(0.3, 1.5)
            g.genetic.lifespan          = random.uniform(150, 400)

        # Biome-specific tweaks
        if biome == "desert":
            g.metabolic.water_need         = random.uniform(0.1, 0.4)
            g.metabolic.temp_tolerance_max = random.uniform(45, 60)
        elif biome == "arctic":
            g.metabolic.temp_tolerance_min = random.uniform(-50, -20)
            g.metabolic.energy_efficiency  = random.uniform(1.5, 2.5)
        elif biome in ("river", "lake"):
            g.physical.speed = min(10.0, g.physical.speed * 1.3)

        g.genome_id = str(uuid.uuid4())[:8]
        return g

    # ── Convenience presets ────────────────────────────────────────────────

    def herbivore(self) -> Genome:
        return self.random(trophic_level=2)

    def omnivore(self) -> Genome:
        return self.random(trophic_level=3)

    def predator(self) -> Genome:
        return self.random(trophic_level=4)

    def apex(self) -> Genome:
        return self.random(trophic_level=5)

    def balanced_ecosystem(self, n_species: int = 4) -> List[Genome]:
        """Return a balanced set of genomes covering multiple trophic levels."""
        result = []
        levels = [2, 2, 3, 4] if n_species == 4 else \
                 [2, 2, 2, 3, 4, 5][:n_species]
        for lvl in levels:
            result.append(self.random(trophic_level=lvl))
        return result
