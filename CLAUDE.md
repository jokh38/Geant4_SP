# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Geant4_SP** (Geant4 Stopping Power) is a Python implementation for calculating particle stopping power data, inspired by Geant4's physics simulation toolkit. The project aims to compute stopping power (dE/dx) for charged particles (primarily protons) in various materials (primarily water) across different energy ranges.

## Architecture

This project follows a physics simulation architecture with clear separation of concerns:

### Core Components

1. **StoppingPowerCalculator** (`src/stopping_power.py`):
   - Main physics calculation engine
   - Implements Bethe-Bloch formula and related stopping power calculations
   - Computes both total stopping power (dE/dx in MeV/cm) and mass stopping power (MeV·cm²/g)
   - Supports batch calculations for multiple energy points
   - Configurable physics models (e.g., FTFP_BERT, QGSP_BIC_HP)

2. **EnergyRange** (`src/stopping_power.py`):
   - Generates energy point arrays with variable step sizes
   - Supports different energy regions with different granularities:
     - 0.5-50 MeV: 0.5 MeV steps
     - 50-100 MeV: 1.0 MeV steps
     - 100-250 MeV: 5.0 MeV steps

### Physics Context

The reference C++ code (in G4RSP.txt) uses Geant4's `G4EmCalculator` with:
- Physics models: FTFP_BERT with G4EmStandardPhysics_option4 for high precision
- Energy range: 0.5 to 250 MeV for proton therapy applications
- Target material: Water (G4_WATER) with density-dependent calculations

## Development Commands

### Environment Setup
```bash
# Always use python3/pip3 in WSL environment
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt  # when requirements.txt exists
pip3 install pytest numpy scipy  # core dependencies
```

### Testing
```bash
# Run all tests
python3 -m pytest tests/

# Run specific test file
python3 -m pytest tests/test_stopping_power.py

# Run specific test class
python3 -m pytest tests/test_stopping_power.py::TestStoppingPowerCalculator

# Run specific test method
python3 -m pytest tests/test_stopping_power.py::TestStoppingPowerCalculator::test_bethe_bloch_formula

# Run with verbose output
python3 -m pytest tests/ -v

# Run with coverage
python3 -m pytest tests/ --cov=src --cov-report=html
```

### Code Quality
```bash
# Format code (when ruff is configured)
python3 -m ruff format src/ tests/

# Lint code
python3 -m ruff check src/ tests/

# Type checking (when mypy is configured)
python3 -m mypy src/
```

## Development Workflow

This project follows **strict TDD principles**:

1. **Red Phase**: Write failing test first in `tests/test_stopping_power.py`
2. **Green Phase**: Implement minimal code in `src/` to pass the test
3. **Refactor Phase**: Improve code quality while keeping tests green

### Commit Guidelines

- Separate structural and behavioral changes
- Commit format: `[STRUCTURAL]` or `[BEHAVIORAL]` prefix
- Only commit when all tests pass
- Example: `[BEHAVIORAL] Add Bethe-Bloch stopping power calculation`

## Physics Formulas and Validation

The stopping power calculations should be validated against:
- NIST PSTAR database for protons
- ICRU Report 49 for heavy charged particles
- Geant4 physics reference manual

Key physics relationships to maintain:
- Stopping power generally decreases with increasing particle energy (except at very low energies)
- Bragg peak behavior for protons in water
- Mass stopping power independence from material density

## Output Format

The calculator should produce tabular output matching Geant4's format:
```
Energy (MeV)    Total dE/dx (MeV/cm)    Total Mass dE/dx (MeV cm^2/g)
-----------------------------------------------------------------------
0.5000          value1                   value2
1.0000          value3                   value4
...
```

## Critical Notes

- **Always use `python3` and `pip3`** in WSL/Linux environment (never `python` or `pip`)
- Physics calculations require high numerical precision (float64/double)
- Energy units: MeV (mega-electron volts)
- Length units: cm (centimeters)
- Density units: g/cm³
- Material properties (density, composition) significantly affect stopping power

## Subagent Configuration

This project leverages Claude Code's specialized subagents to handle complex multi-step tasks efficiently:

### 1. General-Purpose Agent
**When to use**: Complex searches, multi-file code exploration, multi-step research tasks
**Examples**:
- Searching for physics formula implementations across multiple files
- Investigating how Geant4 physics models are referenced throughout the codebase
- Finding all locations where energy range calculations are performed

### 2. Python Code Modifier Agent
**When to use**: Targeted code modifications that require careful impact analysis
**Examples**:
- Refactoring the Bethe-Bloch formula implementation while preserving test compatibility
- Optimizing energy range calculations for performance
- Adding new physics models without breaking existing functionality
- Modifying material property handling with minimal side effects

**Critical**: This agent should be used during TDD refactor phase for safe code improvements

### 3. Problem-Solver Triple Approach Agent
**When to use**: Architecture decisions, performance optimization, design challenges
**Examples**:
- Deciding how to extend the calculator to support multiple particle types
- Optimizing batch calculations for large energy ranges
- Designing the material database architecture
- Choosing between different numerical integration methods

**Benefit**: Provides conservative, innovative, and efficient solution approaches with pros/cons

### 4. Research Verifier Agent
**When to use**: Validating physics formulas, researching standards, gathering technical information
**Examples**:
- Verifying Bethe-Bloch formula implementation against NIST standards
- Researching ICRU Report 49 specifications for validation
- Finding authoritative sources for stopping power calculation methods
- Investigating Geant4 physics model documentation

**Critical**: Essential for ensuring physics accuracy and compliance with standards

### Subagent Workflow Integration

#### TDD Red Phase (Write Test)
1. Use **Research Verifier** to validate physics requirements from standards
2. Use **General-Purpose** to search for similar test patterns in codebase
3. Write failing test with verified physics expectations

#### TDD Green Phase (Implement)
1. Use **Problem-Solver** if implementation approach is unclear
2. Implement minimal code to pass test
3. Use **Research Verifier** to validate numerical accuracy

#### TDD Refactor Phase (Improve)
1. Use **Python Code Modifier** for safe refactoring operations
2. Use **General-Purpose** to check impact across codebase
3. Ensure all tests remain green

#### Design Decisions
1. Use **Problem-Solver** to get multiple architectural approaches
2. Use **Research Verifier** to validate against best practices
3. Use **General-Purpose** to understand current implementation patterns

### Parallel Subagent Execution

For complex tasks, launch multiple subagents in parallel:
```
Task: "Add support for alpha particles with full validation"

Parallel execution:
- Research Verifier: Gather alpha particle stopping power formulas from NIST
- General-Purpose: Search codebase for particle type handling patterns
- Problem-Solver: Analyze best approach for multi-particle architecture
```

### Subagent Usage Examples

**Example 1: Adding new physics model**
```
1. Research Verifier: "Find Geant4 documentation for QGSP_BIC_HP physics model"
2. Problem-Solver: "Design approach to add new physics model to StoppingPowerCalculator"
3. Python Code Modifier: "Add model selection parameter with backward compatibility"
```

**Example 2: Performance optimization**
```
1. General-Purpose: "Find all energy range calculation bottlenecks"
2. Problem-Solver: "Optimize batch stopping power calculations for 1000+ energy points"
3. Python Code Modifier: "Implement vectorized calculations using NumPy"
```

**Example 3: Physics validation**
```
1. Research Verifier: "Verify Bragg peak behavior implementation against ICRU standards"
2. General-Purpose: "Search for all validation tests in test suite"
3. Python Code Modifier: "Add comprehensive validation tests for edge cases"
```
