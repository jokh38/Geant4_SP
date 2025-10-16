#!/usr/bin/env python3
"""
Visualize stopping power data for protons in water.

Creates plots showing stopping power vs energy with proper physics scales.
"""

import sys
import csv
from pathlib import Path

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


def load_data(csv_file="data/proton_water_stopping_power.csv"):
    """Load stopping power data from CSV file."""

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


def create_plots(energies, dedx_values, mass_dedx_values):
    """Create comprehensive visualization plots."""

    # Create figure with multiple subplots
    fig = plt.figure(figsize=(14, 10))

    # Plot 1: Total Stopping Power (Linear scale)
    ax1 = plt.subplot(2, 2, 1)
    ax1.plot(energies, dedx_values, 'b-', linewidth=2)
    ax1.set_xlabel('Energy (MeV)', fontsize=12)
    ax1.set_ylabel('dE/dx (MeV/cm)', fontsize=12)
    ax1.set_title('Proton Stopping Power in Water (Linear Scale)', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, max(energies))

    # Plot 2: Total Stopping Power (Log-Log scale)
    ax2 = plt.subplot(2, 2, 2)
    ax2.loglog(energies, dedx_values, 'r-', linewidth=2)
    ax2.set_xlabel('Energy (MeV)', fontsize=12)
    ax2.set_ylabel('dE/dx (MeV/cm)', fontsize=12)
    ax2.set_title('Proton Stopping Power in Water (Log-Log Scale)', fontsize=14, fontweight='bold')
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


def create_comparison_plot(energies, dedx_values):
    """Create a single comparison plot with key features highlighted."""

    fig, ax = plt.subplots(figsize=(12, 7))

    # Main plot
    ax.plot(energies, dedx_values, 'b-', linewidth=2.5, label='Proton in Water')

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
        f'Physics Model: FTFP_BERT\n'
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

    print("Geant4 Stopping Power Data Visualization")
    print("=" * 80)

    # Check if data file exists
    data_file = "data/proton_water_stopping_power.csv"
    if not Path(data_file).exists():
        print(f"Error: Data file not found: {data_file}")
        print("Run generate_data.py first to create the data.")
        return 1

    # Load data
    print(f"Loading data from {data_file}...")
    energies, dedx_values, mass_dedx_values = load_data(data_file)
    print(f"Loaded {len(energies)} data points")
    print()

    # Create output directory for plots
    plot_dir = Path("plots")
    plot_dir.mkdir(exist_ok=True)

    # Create multi-panel plot
    print("Creating multi-panel plot...")
    fig1 = create_plots(energies, dedx_values, mass_dedx_values)
    plot_file1 = plot_dir / "stopping_power_multi_panel.png"
    fig1.savefig(plot_file1, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {plot_file1}")

    # Create comparison plot
    print("Creating comparison plot...")
    fig2 = create_comparison_plot(energies, dedx_values)
    plot_file2 = plot_dir / "stopping_power_comparison.png"
    fig2.savefig(plot_file2, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {plot_file2}")

    print()
    print("✓ Visualization complete!")
    print(f"\nPlot files saved in '{plot_dir}/' directory:")
    print(f"  - stopping_power_multi_panel.png")
    print(f"  - stopping_power_comparison.png")
    print()
    print("To view the plots, open the PNG files in an image viewer.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
