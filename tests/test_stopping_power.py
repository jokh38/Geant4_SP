"""
Unit tests for Geant4 stopping power calculator.
"""
import pytest
import numpy as np
from src.stopping_power import StoppingPowerCalculator, EnergyRange


class TestEnergyRange:
    """Test energy range generation functionality."""

    def test_simple_range_creation(self):
        """Test creating a simple energy range."""
        energy_range = EnergyRange(start=0.5, end=10.0, step=0.5)
        energies = energy_range.generate()

        assert len(energies) > 0
        assert energies[0] == 0.5
        assert energies[-1] <= 10.0

    def test_variable_step_range(self):
        """Test energy range with variable steps."""
        energy_range = EnergyRange(
            start=0.1,
            end=250.0,
            step=0.1,
            step_rules=[(10.0, 0.5), (50.0, 1.0), (100.0, 5.0)]
        )
        energies = energy_range.generate()

        assert len(energies) > 0
        assert energies[0] == 0.1  # Updated start point
        assert energies[0] < 0.5
        assert any(e >= 10.0 for e in energies)
        assert any(e >= 50.0 for e in energies)
        assert any(e > 100.0 for e in energies)


class TestStoppingPowerCalculator:
    """Test stopping power calculation functionality."""

    def test_calculator_initialization(self):
        """Test calculator can be initialized."""
        calc = StoppingPowerCalculator(
            particle="proton",
            material="water",
            physics_model="FTFP_BERT"
        )

        assert calc.particle == "proton"
        assert calc.material == "water"
        assert calc.physics_model == "FTFP_BERT"

    def test_bethe_bloch_formula(self):
        """Test Bethe-Bloch stopping power calculation."""
        calc = StoppingPowerCalculator(
            particle="proton",
            material="water"
        )

        # Test at a known energy point
        energy_mev = 100.0
        dedx = calc.compute_dedx(energy_mev)

        assert dedx > 0
        assert isinstance(dedx, float)

    def test_mass_stopping_power(self):
        """Test mass stopping power calculation."""
        calc = StoppingPowerCalculator(
            particle="proton",
            material="water"
        )

        energy_mev = 100.0
        mass_dedx = calc.compute_mass_dedx(energy_mev)

        assert mass_dedx > 0
        assert isinstance(mass_dedx, float)

    def test_batch_calculation(self):
        """Test calculating stopping power for multiple energies."""
        calc = StoppingPowerCalculator(
            particle="proton",
            material="water"
        )

        energies = [1.0, 10.0, 50.0, 100.0]
        results = calc.compute_batch(energies)

        assert len(results) == len(energies)
        assert all('energy' in r for r in results)
        assert all('dedx' in r for r in results)
        assert all('mass_dedx' in r for r in results)

    def test_stopping_power_decreases_with_energy(self):
        """Test that stopping power generally decreases with increasing energy."""
        calc = StoppingPowerCalculator(
            particle="proton",
            material="water"
        )

        low_energy_dedx = calc.compute_dedx(1.0)
        high_energy_dedx = calc.compute_dedx(100.0)

        # At low energies, stopping power is generally higher
        assert low_energy_dedx > high_energy_dedx
