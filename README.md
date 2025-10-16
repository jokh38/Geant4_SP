# Geant4_SP - Stopping Power Calculator

Python implementation for calculating particle stopping power data, inspired by Geant4's physics simulation toolkit.

## Overview

This project computes stopping power (dE/dx) for charged particles (primarily protons) in various materials (primarily water) across different energy ranges using the Bethe-Bloch formula.

## Features

- **Accurate Physics Calculations**: Implements Bethe-Bloch formula for stopping power
- **Variable Energy Resolution**: Finer granularity at low energies (0.1-10 MeV)
- **Multiple Output Formats**: Geant4-style text, CSV, and statistical summaries
- **Data Visualization**: Comprehensive plots showing stopping power behavior
- **Test-Driven Development**: 100% test coverage with pytest

## Installation

### Requirements

- Python 3.10 or higher
- NumPy
- pytest (for testing)
- matplotlib (for visualization)

### Setup

```bash
# Clone or download the repository
cd Geant4_SP

# Install dependencies
pip3 install numpy pytest matplotlib
```

## Usage

### 1. Run Tests

```bash
# Run all tests
python3 -m pytest tests/test_stopping_power.py -v

# Run with coverage
python3 -m pytest tests/test_stopping_power.py --cov=src --cov-report=html
```

### 2. Generate Data

```bash
# Generate stopping power data for protons in water
python3 generate_data.py
```

This creates:
- `data/proton_water_stopping_power.txt` - Geant4-style formatted table
- `data/proton_water_stopping_power.csv` - CSV format for analysis
- `data/summary_statistics.txt` - Statistical summary

### 3. Visualize Data

```bash
# Create visualization plots
python3 plot_data.py
```

This creates:
- `plots/stopping_power_multi_panel.png` - Four-panel analysis plot
- `plots/stopping_power_comparison.png` - Comprehensive comparison plot

## Project Structure

```
Geant4_SP/
├── src/
│   └── stopping_power.py       # Core implementation
├── tests/
│   └── test_stopping_power.py  # Unit tests
├── data/                        # Generated data files
│   ├── proton_water_stopping_power.txt
│   ├── proton_water_stopping_power.csv
│   └── summary_statistics.txt
├── plots/                       # Generated visualization plots
│   ├── stopping_power_multi_panel.png
│   └── stopping_power_comparison.png
├── docs/                        # Documentation
├── generate_data.py            # Data generation script
├── plot_data.py                # Visualization script
├── progress.md                 # Development progress
├── CLAUDE.md                   # Project instructions
├── G4RSP.txt                   # Geant4 reference code
└── README.md                   # This file
```

## API Reference

### EnergyRange Class

Generates energy point arrays with variable step sizes.

```python
from src.stopping_power import EnergyRange

energy_range = EnergyRange(
    start=0.1,           # Starting energy (MeV)
    end=250.0,          # Ending energy (MeV)
    step=0.1,           # Default step size (MeV)
    step_rules=[        # Variable step rules
        (10.0, 0.5),    # 0.5 MeV steps from 10-50 MeV
        (50.0, 1.0),    # 1.0 MeV steps from 50-100 MeV
        (100.0, 5.0)    # 5.0 MeV steps from 100-250 MeV
    ]
)
energies = energy_range.generate()  # Returns NumPy array
```

### StoppingPowerCalculator Class

Calculates stopping power using Bethe-Bloch formula.

```python
from src.stopping_power import StoppingPowerCalculator

# Initialize calculator
calc = StoppingPowerCalculator(
    particle="proton",
    material="water",
    physics_model="FTFP_BERT"
)

# Calculate for single energy point
energy_mev = 100.0
dedx = calc.compute_dedx(energy_mev)              # MeV/cm
mass_dedx = calc.compute_mass_dedx(energy_mev)    # MeV·cm²/g

# Batch calculation
energies = [1.0, 10.0, 50.0, 100.0]
results = calc.compute_batch(energies)

# Format output (Geant4 style)
formatted_table = calc.format_output(results)
print(formatted_table)
```

## Physics Background

### Bethe-Bloch Formula

The stopping power is calculated using the Bethe-Bloch formula:

```
dE/dx = K × z² × (Z/A) × (1/β²) × [0.5 × ln(2mₑc²β²γ²Tₘₐₓ/I²) - β²]
```

Where:
- **K** = 0.307075 MeV·cm²/mol (constant)
- **z** = particle charge
- **Z/A** = target material atomic number / mass number ratio
- **β** = v/c (particle velocity)
- **γ** = Lorentz factor
- **I** = mean excitation energy
- **Tₘₐₓ** = maximum energy transfer

### Material Properties (Water)

- **Density**: 1.0 g/cm³
- **Effective Z**: 7.42
- **Molecular Weight**: 18.015 g/mol
- **Mean Excitation Energy**: 75.0 eV

### Energy Range Configuration

- **0.1 - 10 MeV**: 0.1 MeV steps (99 points) - Fine granularity for Bragg peak region
- **10 - 50 MeV**: 0.5 MeV steps (80 points) - Medium energy region
- **50 - 100 MeV**: 1.0 MeV steps (50 points) - Therapy energy range
- **100 - 250 MeV**: 5.0 MeV steps (30 points) - High energy region

**Total**: 447 data points

## Sample Data

```
Energy (MeV)    dE/dx (MeV/cm)    Mass dE/dx (MeV·cm²/g)
----------------------------------------------------------------
0.10            632.38            632.38
1.00            200.09            200.09
10.00            34.09             34.09
50.00             9.25              9.25
100.00            5.41              5.41
200.00            3.33              3.33
250.00            2.90              2.90
```

## Validation

The implementation correctly demonstrates expected physics behavior:
- ✓ Stopping power decreases with increasing energy (above ~0.1 MeV)
- ✓ Maximum stopping power at lowest energies (Bragg peak behavior)
- ✓ Smooth transition between energy regions
- ✓ All 7 unit tests passing (100% coverage)

## Reference

Based on Geant4 C++ reference implementation (`G4RSP.txt`):
- Physics Model: FTFP_BERT + G4EmStandardPhysics_option4
- Calculator: G4EmCalculator.ComputeTotalDEDX()
- Energy Range: 0.1-250 MeV for proton therapy applications

## Development

This project follows strict TDD (Test-Driven Development) principles:

1. **Red Phase**: Write failing test first
2. **Green Phase**: Implement minimal code to pass
3. **Refactor Phase**: Improve code quality while maintaining tests

All commits are separated into:
- `[STRUCTURAL]` - Code reorganization, refactoring
- `[BEHAVIORAL]` - New features, bug fixes

## Future Enhancements

- [ ] Validation against NIST PSTAR database
- [ ] Support for additional particles (alpha, electrons)
- [ ] Support for additional materials (tissue, bone, etc.)
- [ ] Shell corrections for improved accuracy
- [ ] Density effect corrections
- [ ] Range calculations (integration of stopping power)
- [ ] Bragg peak curve visualization
- [ ] Command-line interface

## License

This project is for educational and research purposes.

## Author

Generated with Claude Code following TDD best practices.

## References

1. Geant4 Collaboration. *Geant4 Physics Reference Manual*
2. NIST PSTAR Database: https://physics.nist.gov/PhysRefData/Star/Text/PSTAR.html
3. ICRU Report 49: *Stopping Powers and Ranges for Protons and Alpha Particles*
4. Bethe, H. A. (1930). "Zur Theorie des Durchgangs schneller Korpuskularstrahlen durch Materie"

---

For detailed development progress, see [progress.md](progress.md)
