#!/usr/bin/env python3
"""
Generate stopping power data for protons in water.

This script uses the StoppingPowerCalculator to generate comprehensive
stopping power data and saves it in multiple formats.

Supports multiple physics models: FTFP_BERT and EM_option4
"""

import sys
import csv
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.stopping_power import StoppingPowerCalculator, EnergyRange
from src.physics_models import list_available_models


def generate_proton_water_data(physics_model="FTFP_BERT"):
    """
    Generate proton stopping power data in water.

    Args:
        physics_model: Physics model to use (default: "FTFP_BERT")

    Returns:
        Tuple of (calculator, results)
    """

    print("Geant4 Stopping Power Calculator")
    print("=" * 80)
    print(f"Physics Model: {physics_model}")
    print("Generating proton stopping power data in water...")
    print()

    # Initialize calculator
    calc = StoppingPowerCalculator(
        particle="proton",
        material="water",
        physics_model=physics_model
    )

    # Generate energy range with variable step sizes
    energy_range = EnergyRange(
        start=0.1,
        end=250.0,
        step=0.1,
        step_rules=[
            (10.0, 0.5),   # 0.5 MeV steps from 10-50 MeV
            (50.0, 1.0),   # 1.0 MeV steps from 50-100 MeV
            (100.0, 5.0)   # 5.0 MeV steps from 100-250 MeV
        ]
    )

    energies = energy_range.generate()
    print(f"Energy points generated: {len(energies)}")
    print(f"Energy range: {energies[0]:.1f} - {energies[-1]:.1f} MeV")
    print()

    # Calculate stopping power for all energy points
    print("Calculating stopping power values...")
    results = calc.compute_batch(energies.tolist())
    print(f"Calculations completed: {len(results)} data points")
    print()

    return calc, results


def save_geant4_format(calc, results, model_name=None):
    """
    Save data in Geant4-style format.

    Args:
        calc: StoppingPowerCalculator instance
        results: List of calculation results
        model_name: Physics model name (optional, uses calc.physics_model if None)
    """
    if model_name is None:
        model_name = calc.physics_model

    filename = f"data/proton_water_{model_name}.txt"
    Path(filename).parent.mkdir(parents=True, exist_ok=True)

    with open(filename, 'w') as f:
        # Header information
        f.write("# Geant4 Stopping Power Data\n")
        f.write(f"# Particle: {calc.particle}\n")
        f.write(f"# Material: {calc.material}\n")
        f.write(f"# Physics Model: {calc.physics_model}\n")
        f.write(f"# Density: {calc.density} g/cm³\n")
        f.write("#\n")
        f.write("# Energy units: MeV\n")
        f.write("# dE/dx units: MeV/cm\n")
        f.write("# Mass dE/dx units: MeV·cm²/g\n")
        f.write("#\n")

        # Data table
        formatted_output = calc.format_output(results)
        f.write(formatted_output)
        f.write("\n")

    print(f"✓ Saved Geant4-style format: {filename}")
    return filename


def save_csv_format(results, model_name):
    """
    Save data in CSV format.

    Args:
        results: List of calculation results
        model_name: Physics model name for filename
    """
    filename = f"data/proton_water_{model_name}.csv"
    Path(filename).parent.mkdir(parents=True, exist_ok=True)

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'Energy_MeV',
            'Total_dEdx_MeV_per_cm',
            'Mass_dEdx_MeV_cm2_per_g'
        ])

        # Data rows
        for result in results:
            if 'error' not in result:
                writer.writerow([
                    f"{result['energy']:.4f}",
                    f"{result['dedx']:.6f}",
                    f"{result['mass_dedx']:.6f}"
                ])

    print(f"✓ Saved CSV format: {filename}")
    return filename


def save_summary_statistics(calc, results, model_name):
    """
    Save summary statistics.

    Args:
        calc: StoppingPowerCalculator instance
        results: List of calculation results
        model_name: Physics model name for filename
    """
    filename = f"data/summary_statistics_{model_name}.txt"
    Path(filename).parent.mkdir(parents=True, exist_ok=True)

    # Calculate statistics
    energies = [r['energy'] for r in results if 'error' not in r]
    dedx_values = [r['dedx'] for r in results if 'error' not in r]
    mass_dedx_values = [r['mass_dedx'] for r in results if 'error' not in r]

    max_dedx_idx = dedx_values.index(max(dedx_values))
    min_dedx_idx = dedx_values.index(min(dedx_values))

    with open(filename, 'w') as f:
        f.write("Stopping Power Summary Statistics\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Physics Model: {calc.physics_model}\n")
        f.write(f"Total data points: {len(results)}\n")
        f.write(f"Energy range: {energies[0]:.2f} - {energies[-1]:.2f} MeV\n\n")

        f.write("Total Stopping Power (dE/dx):\n")
        f.write(f"  Maximum: {max(dedx_values):.4f} MeV/cm at {energies[max_dedx_idx]:.2f} MeV\n")
        f.write(f"  Minimum: {min(dedx_values):.4f} MeV/cm at {energies[min_dedx_idx]:.2f} MeV\n")
        f.write(f"  Average: {sum(dedx_values)/len(dedx_values):.4f} MeV/cm\n\n")

        f.write("Mass Stopping Power:\n")
        f.write(f"  Maximum: {max(mass_dedx_values):.4f} MeV·cm²/g\n")
        f.write(f"  Minimum: {min(mass_dedx_values):.4f} MeV·cm²/g\n")
        f.write(f"  Average: {sum(mass_dedx_values)/len(mass_dedx_values):.4f} MeV·cm²/g\n\n")

        f.write("Sample Data Points:\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Energy (MeV)':>15}{'dE/dx (MeV/cm)':>20}{'Mass dE/dx':>25}\n")
        f.write("-" * 80 + "\n")

        # Show sample points
        sample_energies = [0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0, 200.0, 250.0]
        for e in sample_energies:
            for r in results:
                if abs(r['energy'] - e) < 0.01:
                    f.write(f"{r['energy']:>15.2f}{r['dedx']:>20.4f}{r['mass_dedx']:>25.4f}\n")
                    break

    print(f"✓ Saved summary statistics: {filename}")
    return filename


def print_sample_data(results):
    """Print sample data points to console."""

    print("\n" + "=" * 80)
    print("Sample Stopping Power Data (Protons in Water)")
    print("=" * 80)
    print(f"{'Energy (MeV)':>15}{'dE/dx (MeV/cm)':>20}{'Mass dE/dx (MeV·cm²/g)':>30}")
    print("-" * 80)

    # Show sample points
    sample_energies = [0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0, 200.0, 250.0]
    for e in sample_energies:
        for r in results:
            if abs(r['energy'] - e) < 0.01:
                print(f"{r['energy']:>15.2f}{r['dedx']:>20.4f}{r['mass_dedx']:>30.4f}")
                break

    print("=" * 80)
    print("\nNote: Complete data available in output files")


def main():
    """Main execution function."""

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Generate Geant4 stopping power data for protons in water"
    )
    parser.add_argument(
        "--model",
        choices=list_available_models(),
        help="Physics model to use (default: all models)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate data for all available physics models"
    )

    args = parser.parse_args()

    # Determine which models to run
    if args.model:
        models = [args.model]
    elif args.all:
        models = list_available_models()
    else:
        # Default: generate for all models
        models = list_available_models()

    all_output_files = []

    try:
        for model in models:
            print(f"\n{'=' * 80}")
            print(f"Processing physics model: {model}")
            print(f"{'=' * 80}\n")

            # Generate data
            calc, results = generate_proton_water_data(physics_model=model)

            # Save in multiple formats
            print("Saving data files...")
            txt_file = save_geant4_format(calc, results, model)
            csv_file = save_csv_format(results, model)
            stats_file = save_summary_statistics(calc, results, model)

            all_output_files.extend([txt_file, csv_file, stats_file])

            # Print sample to console
            print_sample_data(results)

        print(f"\n{'=' * 80}")
        print("✓ Data generation complete!")
        print(f"{'=' * 80}\n")
        print("Generated files:")
        for filepath in all_output_files:
            print(f"  - {filepath}")

    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
