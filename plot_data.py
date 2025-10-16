#!/usr/bin/env python3
"""
Visualize stopping power data for protons in water.

Creates plots showing stopping power vs energy with proper physics scales.
Supports multiple physics models (FTFP_BERT, EM_option4, etc.)
"""

import sys
import csv
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-GUI backend for WSL
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    print("Error: matplotlib is required for plotting")
    print("Install with: pip3 install matplotlib")
    sys.exit(1)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.physics_models import list_available_models


def load_model_data(model_name: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Load stopping power data for a specific physics model.

    Args:
        model_name: Name of physics model (e.g., "FTFP_BERT", "EM_option4")

    Returns:
        Tuple of (energies, dedx_values, mass_dedx_values) as numpy arrays
    """
    csv_file = f"data/proton_water_{model_name}.csv"

    if not Path(csv_file).exists():
        raise FileNotFoundError(
            f"Data file not found: {csv_file}\n"
            f"Run 'python3 generate_data.py --model {model_name}' first to generate data."
        )

    energies = []
    dedx_values = []
    mass_dedx_values = []

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            energies.append(float(row['Energy_MeV']))
            dedx_values.append(float(row['Total_dEdx_MeV_per_cm']))
            mass_dedx_values.append(float(row['Mass_dEdx_MeV_cm2_per_g']))

    return np.array(energies), np.array(dedx_values), np.array(mass_dedx_values)


def load_all_models_data() -> Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """
    Load stopping power data for all available physics models.

    Returns:
        Dictionary mapping model names to (energies, dedx_values, mass_dedx_values) tuples
    """
    models_data = {}
    available_models = list_available_models()

    for model in available_models:
        try:
            models_data[model] = load_model_data(model)
            print(f"✓ Loaded data for {model}")
        except FileNotFoundError as e:
            print(f"⚠ Warning: {e}")

    return models_data


def create_model_plot(energies, dedx_values, mass_dedx_values, model_name):
    """
    Create comprehensive visualization plots for a single physics model.

    Args:
        energies: Energy values array
        dedx_values: Stopping power values array
        mass_dedx_values: Mass stopping power values array
        model_name: Name of the physics model

    Returns:
        matplotlib Figure object
    """
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(14, 10))

    # Plot 1: Total Stopping Power (Linear scale)
    ax1 = plt.subplot(2, 2, 1)
    ax1.plot(energies, dedx_values, 'b-', linewidth=2)
    ax1.set_xlabel('Energy (MeV)', fontsize=12)
    ax1.set_ylabel('dE/dx (MeV/cm)', fontsize=12)
    ax1.set_title(f'Stopping Power - {model_name} (Linear Scale)', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, max(energies))

    # Plot 2: Total Stopping Power (Log-Log scale)
    ax2 = plt.subplot(2, 2, 2)
    ax2.loglog(energies, dedx_values, 'r-', linewidth=2)
    ax2.set_xlabel('Energy (MeV)', fontsize=12)
    ax2.set_ylabel('dE/dx (MeV/cm)', fontsize=12)
    ax2.set_title(f'Stopping Power - {model_name} (Log-Log Scale)', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, which='both')

    # Plot 3: Mass Stopping Power
    ax3 = plt.subplot(2, 2, 3)
    ax3.plot(energies, mass_dedx_values, 'g-', linewidth=2)
    ax3.set_xlabel('Energy (MeV)', fontsize=12)
    ax3.set_ylabel('Mass dE/dx (MeV·cm²/g)', fontsize=12)
    ax3.set_title('Mass Stopping Power', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(0, max(energies))

    # Plot 4: Low Energy Region (Bragg Peak region)
    ax4 = plt.subplot(2, 2, 4)
    # Focus on 0.1 - 10 MeV range
    low_energy_mask = energies <= 10.0
    ax4.plot(energies[low_energy_mask], dedx_values[low_energy_mask], 'm-', linewidth=2)
    ax4.set_xlabel('Energy (MeV)', fontsize=12)
    ax4.set_ylabel('dE/dx (MeV/cm)', fontsize=12)
    ax4.set_title('Low Energy Region (0.1-10 MeV)', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)

    # Add annotations for maximum stopping power
    max_idx = np.argmax(dedx_values[low_energy_mask])
    max_energy = energies[low_energy_mask][max_idx]
    max_dedx = dedx_values[low_energy_mask][max_idx]
    ax4.annotate(f'Max: {max_dedx:.1f} MeV/cm\nat {max_energy:.2f} MeV',
                xy=(max_energy, max_dedx),
                xytext=(max_energy + 2, max_dedx - 100),
                arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
                fontsize=10,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))

    plt.tight_layout()
    return fig


def create_models_comparison_plot(models_data: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]]):
    """
    Create comparison plot showing multiple physics models on the same axes.

    Args:
        models_data: Dictionary mapping model names to (energies, dedx, mass_dedx) tuples

    Returns:
        matplotlib Figure object
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))

    # Define colors for different models
    colors = {'FTFP_BERT': 'blue', 'EM_option4': 'red', 'QGSP_BIC_HP': 'green'}
    line_styles = {'FTFP_BERT': '-', 'EM_option4': '--', 'QGSP_BIC_HP': '-.'}

    # Plot 1: Linear scale comparison
    for model_name, (energies, dedx_values, _) in models_data.items():
        color = colors.get(model_name, 'black')
        style = line_styles.get(model_name, '-')
        ax1.plot(energies, dedx_values,
                 color=color, linestyle=style, linewidth=2.5,
                 label=model_name)

    ax1.set_xlabel('Proton Energy (MeV)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Stopping Power dE/dx (MeV/cm)', fontsize=14, fontweight='bold')
    ax1.set_title('Physics Model Comparison - Proton Stopping Power in Water\n(Linear Scale)',
                  fontsize=16, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(fontsize=12, loc='upper right')
    ax1.set_xlim(0, max(energies))

    # Plot 2: Relative difference plot
    if len(models_data) == 2:
        model_names = list(models_data.keys())
        ref_model = model_names[0]
        cmp_model = model_names[1]

        ref_energies, ref_dedx, _ = models_data[ref_model]
        cmp_energies, cmp_dedx, _ = models_data[cmp_model]

        # Calculate relative difference (%)
        relative_diff = 100 * (cmp_dedx - ref_dedx) / ref_dedx

        ax2.plot(ref_energies, relative_diff, 'purple', linewidth=2)
        ax2.axhline(y=0, color='black', linestyle='--', linewidth=1)
        ax2.set_xlabel('Proton Energy (MeV)', fontsize=14, fontweight='bold')
        ax2.set_ylabel(f'Relative Difference (%)\n({cmp_model} - {ref_model}) / {ref_model}',
                       fontsize=14, fontweight='bold')
        ax2.set_title(f'Model Comparison: {cmp_model} vs {ref_model}',
                      fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.set_xlim(0, max(ref_energies))

        # Highlight energy regions
        ax2.axvspan(0, 2, alpha=0.1, color='red', label='Low E (<2 MeV): ICRU data')
        ax2.axvspan(2, 10, alpha=0.1, color='orange', label='Mid E (2-10 MeV): Shell corrections')
        ax2.axvspan(10, max(ref_energies), alpha=0.1, color='green', label='High E (>10 MeV): Minimal corrections')
        ax2.legend(fontsize=10, loc='best')
    else:
        # For multiple models, show log-log comparison
        for model_name, (energies, dedx_values, _) in models_data.items():
            color = colors.get(model_name, 'black')
            style = line_styles.get(model_name, '-')
            ax2.loglog(energies, dedx_values,
                       color=color, linestyle=style, linewidth=2.5,
                       label=model_name)

        ax2.set_xlabel('Proton Energy (MeV)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Stopping Power dE/dx (MeV/cm)', fontsize=14, fontweight='bold')
        ax2.set_title('Physics Model Comparison (Log-Log Scale)',
                      fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, which='both')
        ax2.legend(fontsize=12, loc='best')

    plt.tight_layout()
    return fig


def create_comparison_plot(energies, dedx_values, model_name='FTFP_BERT'):
    """Create a single comparison plot with key features highlighted."""

    fig, ax = plt.subplots(figsize=(12, 7))

    # Main plot
    ax.plot(energies, dedx_values, 'b-', linewidth=2.5, label=f'Proton in Water ({model_name})')

    # Highlight different energy regions
    mask_low = energies <= 10.0
    mask_mid = (energies > 10.0) & (energies <= 100.0)
    mask_high = energies > 100.0

    ax.fill_between(energies[mask_low], 0, dedx_values[mask_low], alpha=0.2, color='red', label='Low Energy (0.1-10 MeV)')
    ax.fill_between(energies[mask_mid], 0, dedx_values[mask_mid], alpha=0.2, color='orange', label='Medium Energy (10-100 MeV)')
    ax.fill_between(energies[mask_high], 0, dedx_values[mask_high], alpha=0.2, color='green', label='High Energy (100-250 MeV)')

    ax.set_xlabel('Proton Energy (MeV)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Stopping Power dE/dx (MeV/cm)', fontsize=14, fontweight='bold')
    ax.set_title('Proton Stopping Power in Water\n(Bethe-Bloch Formula Implementation)',
                 fontsize=16, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11, loc='upper right')
    ax.set_xlim(0, max(energies))
    ax.set_ylim(0, max(dedx_values) * 1.1)

    # Add text with physics info (positioned in upper left to avoid legend overlap)
    info_text = (
        f'Particle: Proton\n'
        f'Material: Water (ρ = 1.0 g/cm³)\n'
        f'Physics Model: {model_name}\n'
        f'Data Points: {len(energies)}\n'
        f'Energy Range: {energies[0]:.1f} - {energies[-1]:.1f} MeV'
    )
    ax.text(0.02, 0.97, info_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top',
            horizontalalignment='left',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    plt.tight_layout()
    return fig


def main():
    """Main execution function."""

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Visualize Geant4 stopping power data for protons in water"
    )
    parser.add_argument(
        "--model",
        choices=list_available_models(),
        help="Physics model to plot (default: all models)"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Create comparison plot for multiple models"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Create plots for all available physics models"
    )

    args = parser.parse_args()

    print("Geant4 Stopping Power Data Visualization")
    print("=" * 80)
    print()

    # Create output directory for plots
    plot_dir = Path("plots")
    plot_dir.mkdir(exist_ok=True)

    saved_plots = []

    # Determine which models to plot
    if args.model:
        models_to_plot = [args.model]
    elif args.all or args.compare:
        models_to_plot = list_available_models()
    else:
        # Default: plot all available models
        models_to_plot = list_available_models()

    # Load data for requested models
    print("Loading data...")
    models_data = {}
    for model in models_to_plot:
        try:
            models_data[model] = load_model_data(model)
            print(f"✓ Loaded data for {model}: {len(models_data[model][0])} points")
        except FileNotFoundError as e:
            print(f"⚠ Warning: Could not load {model}")
            print(f"  {e}")

    if not models_data:
        print("\n✗ Error: No data files found!")
        print("Run 'python3 generate_data.py' first to generate data.")
        return 1

    print()

    # Create individual plots for each model
    if not args.compare or len(models_data) == 1:
        print("Creating individual model plots...")
        for model_name, (energies, dedx_values, mass_dedx_values) in models_data.items():
            # Multi-panel plot
            print(f"  Creating multi-panel plot for {model_name}...")
            fig1 = create_model_plot(energies, dedx_values, mass_dedx_values, model_name)
            plot_file1 = plot_dir / f"stopping_power_{model_name}_multi_panel.png"
            fig1.savefig(plot_file1, dpi=300, bbox_inches='tight')
            plt.close(fig1)
            print(f"  ✓ Saved: {plot_file1}")
            saved_plots.append(str(plot_file1))

            # Single comparison plot
            print(f"  Creating feature plot for {model_name}...")
            fig2 = create_comparison_plot(energies, dedx_values, model_name)
            plot_file2 = plot_dir / f"stopping_power_{model_name}_features.png"
            fig2.savefig(plot_file2, dpi=300, bbox_inches='tight')
            plt.close(fig2)
            print(f"  ✓ Saved: {plot_file2}")
            saved_plots.append(str(plot_file2))
        print()

    # Create comparison plot if multiple models available
    if len(models_data) > 1:
        print("Creating multi-model comparison plot...")
        fig_comp = create_models_comparison_plot(models_data)
        plot_file_comp = plot_dir / "stopping_power_models_comparison.png"
        fig_comp.savefig(plot_file_comp, dpi=300, bbox_inches='tight')
        plt.close(fig_comp)
        print(f"✓ Saved: {plot_file_comp}")
        saved_plots.append(str(plot_file_comp))
        print()

    print("=" * 80)
    print("✓ Visualization complete!")
    print("=" * 80)
    print(f"\nGenerated {len(saved_plots)} plot file(s) in '{plot_dir}/' directory:")
    for plot_file in saved_plots:
        print(f"  - {Path(plot_file).name}")
    print()
    print("To view the plots, open the PNG files in an image viewer.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
