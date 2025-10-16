"""
Physics models for Geant4 stopping power calculations.

This module defines model-specific parameters for different Geant4 physics lists.
Different models use different correction factors and data sources for stopping power.
"""

from typing import Dict, Any


class PhysicsModel:
    """Base class for physics model parameters."""

    def __init__(self, name: str):
        """
        Initialize physics model.

        Args:
            name: Model name (e.g., "FTFP_BERT", "EM_option4")
        """
        self.name = name

    def get_correction_factor(self, energy_mev: float) -> float:
        """
        Get model-specific correction factor for stopping power.

        Different models use different corrections based on:
        - Shell corrections
        - Barkas effect
        - Bloch correction
        - Density effect

        Args:
            energy_mev: Kinetic energy in MeV

        Returns:
            Correction factor (dimensionless)
        """
        raise NotImplementedError("Subclasses must implement get_correction_factor")

    def get_parameters(self) -> Dict[str, Any]:
        """
        Get model-specific parameters.

        Returns:
            Dictionary of model parameters
        """
        raise NotImplementedError("Subclasses must implement get_parameters")


class FTFP_BERT_Model(PhysicsModel):
    """
    FTFP_BERT physics model implementation.

    Uses standard G4EmStandardPhysics for electromagnetic processes.
    - Below 2 MeV: Uses ICRU73 parametrization
    - Above 2 MeV: Uses Bethe-Bloch with standard corrections
    """

    def __init__(self):
        super().__init__("FTFP_BERT")
        self.transition_energy = 2.0  # MeV, transition from ICRU to Bethe-Bloch
        self.em_version = "ICRU73"

    def get_correction_factor(self, energy_mev: float) -> float:
        """
        Get FTFP_BERT correction factor.

        Standard EM physics uses moderate corrections:
        - Low energy (< 2 MeV): ICRU73 correction ~ 1.00-1.02
        - Mid energy (2-10 MeV): Shell corrections ~ 0.98-1.00
        - High energy (> 10 MeV): Minimal corrections ~ 0.99-1.00

        Args:
            energy_mev: Kinetic energy in MeV

        Returns:
            Correction factor
        """
        if energy_mev < self.transition_energy:
            # Low energy: ICRU73 data shows slightly higher stopping power
            # Linear interpolation from 1.02 at 0.5 MeV to 1.00 at 2 MeV
            return 1.02 - 0.02 * (energy_mev - 0.5) / 1.5
        elif energy_mev < 10.0:
            # Mid energy: Shell corrections reduce stopping power slightly
            return 0.99 + 0.01 * (10.0 - energy_mev) / 8.0
        else:
            # High energy: Minimal corrections
            return 1.00

    def get_parameters(self) -> Dict[str, Any]:
        """Get FTFP_BERT model parameters."""
        return {
            "name": self.name,
            "em_constructor": "G4EmStandardPhysics",
            "em_version": self.em_version,
            "transition_energy": self.transition_energy,
            "hadronic_models": ["Fritiof", "Precompound", "Bertini"],
            "energy_range": "0.5-250 MeV",
            "recommended_for": "General physics and collider applications"
        }


class EM_option4_Model(PhysicsModel):
    """
    G4EmStandardPhysics_option4 model implementation.

    Uses enhanced EM physics with ICRU90 data for higher accuracy.
    - Below 2 MeV: Uses ICRU90 parametrization (more accurate)
    - Above 2 MeV: Uses Bethe-Bloch with enhanced corrections
    - Includes Barkas effect and Bloch corrections
    """

    def __init__(self):
        super().__init__("EM_option4")
        self.transition_energy = 2.0  # MeV
        self.em_version = "ICRU90"

    def get_correction_factor(self, energy_mev: float) -> float:
        """
        Get EM_option4 correction factor.

        Enhanced EM physics uses more sophisticated corrections:
        - Low energy (< 2 MeV): ICRU90 correction ~ 1.03-1.05 (higher accuracy)
        - Mid energy (2-10 MeV): Enhanced shell + Barkas ~ 0.97-0.99
        - High energy (> 10 MeV): Density effect corrections ~ 0.98-1.00

        ICRU90 data generally shows slightly different stopping power
        compared to ICRU73, particularly at low energies.

        Args:
            energy_mev: Kinetic energy in MeV

        Returns:
            Correction factor
        """
        if energy_mev < self.transition_energy:
            # Low energy: ICRU90 data with enhanced accuracy
            # Shows slightly higher stopping power than ICRU73
            return 1.05 - 0.05 * (energy_mev - 0.5) / 1.5
        elif energy_mev < 10.0:
            # Mid energy: Enhanced corrections (Barkas + shell)
            # These reduce stopping power more than standard model
            return 0.97 + 0.02 * (10.0 - energy_mev) / 8.0
        else:
            # High energy: Density effect becomes important
            # Gradually increases correction with energy
            if energy_mev < 100.0:
                return 0.98 + 0.02 * (energy_mev - 10.0) / 90.0
            else:
                return 1.00

    def get_parameters(self) -> Dict[str, Any]:
        """Get EM_option4 model parameters."""
        return {
            "name": self.name,
            "em_constructor": "G4EmStandardPhysics_option4",
            "em_version": self.em_version,
            "transition_energy": self.transition_energy,
            "corrections": ["Shell", "Barkas", "Bloch", "Density effect"],
            "energy_range": "0.1-250 MeV",
            "recommended_for": "Medical physics and proton therapy"
        }


# Model registry
_MODEL_REGISTRY = {
    "FTFP_BERT": FTFP_BERT_Model,
    "EM_option4": EM_option4_Model,
}


def get_physics_model(model_name: str) -> PhysicsModel:
    """
    Get physics model instance by name.

    Args:
        model_name: Name of physics model ("FTFP_BERT" or "EM_option4")

    Returns:
        PhysicsModel instance

    Raises:
        ValueError: If model name is not recognized
    """
    if model_name not in _MODEL_REGISTRY:
        available = ", ".join(_MODEL_REGISTRY.keys())
        raise ValueError(
            f"Unknown physics model '{model_name}'. "
            f"Available models: {available}"
        )

    model_class = _MODEL_REGISTRY[model_name]
    return model_class()


def list_available_models() -> list:
    """
    Get list of available physics models.

    Returns:
        List of model names
    """
    return list(_MODEL_REGISTRY.keys())
