"""
Geant4 Stopping Power Calculator

This module implements stopping power calculations for charged particles
(primarily protons) in various materials, based on Geant4 physics models.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional


class EnergyRange:
    """
    Generate energy point arrays with variable step sizes.

    Supports different energy regions with different granularities:
    - 0.1-10 MeV: 0.1 MeV steps (finer granularity for low energies)
    - 10-50 MeV: 0.5 MeV steps
    - 50-100 MeV: 1.0 MeV steps
    - 100-250 MeV: 5.0 MeV steps
    """

    def __init__(
        self,
        start: float,
        end: float,
        step: float,
        step_rules: Optional[List[Tuple[float, float]]] = None
    ):
        """
        Initialize energy range generator.

        Args:
            start: Starting energy in MeV
            end: Ending energy in MeV
            step: Default step size in MeV
            step_rules: List of (threshold, new_step) tuples for variable steps
        """
        self.start = start
        self.end = end
        self.step = step
        self.step_rules = step_rules or []

    def generate(self) -> np.ndarray:
        """
        Generate array of energy points.

        Returns:
            NumPy array of energy values in MeV
        """
        energies = []
        current_energy = self.start
        current_step = self.step

        while current_energy <= self.end:
            energies.append(current_energy)

            # Check if we need to change step size
            for threshold, new_step in self.step_rules:
                if current_energy >= threshold and current_step != new_step:
                    current_step = new_step
                    break

            current_energy += current_step

        return np.array(energies)


class StoppingPowerCalculator:
    """
    Calculate stopping power (dE/dx) for charged particles in materials.

    Implements Bethe-Bloch formula and related physics calculations.
    """

    # Physical constants
    ELECTRON_MASS = 0.511  # MeV/c^2
    PROTON_MASS = 938.272  # MeV/c^2
    CLASSICAL_ELECTRON_RADIUS = 2.817940e-13  # cm
    AVOGADRO = 6.02214076e23  # mol^-1

    # Material properties (water: G4_WATER)
    WATER_DENSITY = 1.0  # g/cm^3
    WATER_Z = 7.42  # Effective Z for water (H2O)
    WATER_A = 18.015  # g/mol (molecular weight)
    WATER_I = 75.0e-6  # Mean excitation energy in MeV

    def __init__(
        self,
        particle: str = "proton",
        material: str = "water",
        physics_model: str = "FTFP_BERT"
    ):
        """
        Initialize stopping power calculator.

        Args:
            particle: Particle type (default: "proton")
            material: Target material (default: "water")
            physics_model: Geant4 physics model (default: "FTFP_BERT")
        """
        self.particle = particle
        self.material = material
        self.physics_model = physics_model

        # Set particle properties
        if particle == "proton":
            self.particle_mass = self.PROTON_MASS
            self.particle_charge = 1.0
        else:
            raise NotImplementedError(f"Particle type '{particle}' not yet supported")

        # Set material properties
        if material == "water":
            self.density = self.WATER_DENSITY
            self.Z = self.WATER_Z
            self.A = self.WATER_A
            self.I = self.WATER_I
        else:
            raise NotImplementedError(f"Material '{material}' not yet supported")

    def compute_dedx(self, energy_mev: float) -> float:
        """
        Compute total stopping power (dE/dx) using Bethe-Bloch formula.

        Args:
            energy_mev: Kinetic energy in MeV

        Returns:
            Total stopping power in MeV/cm
        """
        # Calculate relativistic parameters
        beta = self._calculate_beta(energy_mev)
        gamma = self._calculate_gamma(energy_mev)

        if beta <= 0 or beta >= 1:
            raise ValueError(f"Invalid beta value: {beta}")

        # Bethe-Bloch formula
        # dE/dx = K * z^2 * Z/A * 1/beta^2 * [0.5 * ln(2*m_e*c^2*beta^2*gamma^2/I) - beta^2]
        # where K = 4*pi*N_A*r_e^2*m_e*c^2

        K = 0.307075  # MeV cm^2/mol (standard constant)

        z_squared = self.particle_charge ** 2

        # Maximum energy transfer (simplified)
        T_max = (2 * self.ELECTRON_MASS * beta**2 * gamma**2) / \
                (1 + 2*gamma*self.ELECTRON_MASS/self.particle_mass +
                 (self.ELECTRON_MASS/self.particle_mass)**2)

        # Bethe-Bloch formula
        ln_term = np.log(2 * self.ELECTRON_MASS * beta**2 * gamma**2 * T_max / (self.I**2))

        dedx_mass = K * z_squared * (self.Z / self.A) * (1 / beta**2) * \
                    (0.5 * ln_term - beta**2)

        # Convert from MeV cm^2/g to MeV/cm
        dedx = dedx_mass * self.density

        return dedx

    def compute_mass_dedx(self, energy_mev: float) -> float:
        """
        Compute mass stopping power.

        Args:
            energy_mev: Kinetic energy in MeV

        Returns:
            Mass stopping power in MeV·cm²/g
        """
        dedx = self.compute_dedx(energy_mev)
        return dedx / self.density

    def compute_batch(self, energies: List[float]) -> List[Dict[str, float]]:
        """
        Calculate stopping power for multiple energy points.

        Args:
            energies: List of kinetic energies in MeV

        Returns:
            List of dictionaries containing energy, dedx, and mass_dedx
        """
        results = []
        for energy in energies:
            try:
                dedx = self.compute_dedx(energy)
                mass_dedx = self.compute_mass_dedx(energy)
                results.append({
                    'energy': energy,
                    'dedx': dedx,
                    'mass_dedx': mass_dedx
                })
            except (ValueError, ZeroDivisionError) as e:
                # Handle edge cases (very low energies)
                results.append({
                    'energy': energy,
                    'dedx': 0.0,
                    'mass_dedx': 0.0,
                    'error': str(e)
                })
        return results

    def _calculate_beta(self, energy_mev: float) -> float:
        """
        Calculate relativistic beta (v/c).

        Args:
            energy_mev: Kinetic energy in MeV

        Returns:
            Beta value (dimensionless)
        """
        gamma = self._calculate_gamma(energy_mev)
        beta = np.sqrt(1 - 1/gamma**2)
        return beta

    def _calculate_gamma(self, energy_mev: float) -> float:
        """
        Calculate relativistic gamma factor.

        Args:
            energy_mev: Kinetic energy in MeV

        Returns:
            Gamma value (dimensionless)
        """
        gamma = 1 + energy_mev / self.particle_mass
        return gamma

    def format_output(self, results: List[Dict[str, float]]) -> str:
        """
        Format batch calculation results in Geant4-style table format.

        Args:
            results: List of dictionaries from compute_batch()

        Returns:
            Formatted string matching Geant4 output format
        """
        output_lines = []

        # Header
        output_lines.append(f"{'Energy (MeV)':>15}{'Total dE/dx (MeV/cm)':>25}{'Total Mass dE/dx (MeV cm^2/g)':>35}")
        output_lines.append("-" * 75)

        # Data rows
        for result in results:
            if 'error' not in result:
                output_lines.append(
                    f"{result['energy']:>15.4f}"
                    f"{result['dedx']:>25.4f}"
                    f"{result['mass_dedx']:>35.4f}"
                )

        return "\n".join(output_lines)
