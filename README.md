# Calculato Microservice

Calculato is a specialized mathematical computation RESTful microservice built with Python and Flask. It leverages the power of the SymPy symbolic mathematics library to perform complex mathematical operations, returning both the final results and detailed, step-by-step resolution processes formatted in LaTeX.

## Core Capabilities

The microservice currently exposes three primary computational engines:

1. **Symbolic Derivation**: Computes derivatives of mathematical expressions, providing granular steps demonstrating the application of fundamental calculus rules (e.g., Power Rule, Chain Rule, Product Rule).
2. **Symbolic Integration**: Calculates definite and indefinite integrals, breaking down the resolution into constituent mathematical steps.
3. **Equation Resolution and Algebra**: Performs algebraic manipulation and solving (e.g., polynomial factorization, expansion, simplification, and root finding via general formulas) with explicit textual and mathematical steps.

## System Architecture

- **Language**: Python 3.x
- **Web Framework**: Flask
- **Mathematical Engine**: SymPy
- **LaTeX Parsing**: latex2sympy2
- **Data Interchange Format**: JSON

## Installation and Setup

### Prerequisites
- Python 3.10+
- pip (Python package installer)

### Local Development Environment

1. **Clone the repository and navigate to the project directory:**
   ```bash
   cd calculato_microservice
   ```

2. **Activate the virtual environment:**
   - **Windows:**
     ```powershell
     .\venv\Scripts\activate
     ```
   - **Unix/macOS:**
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies:**
   Ensure your virtual environment is active, then install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```
   The server will start by default on `http://127.0.0.1:5000`.

## API Documentation

Detailed API endpoint specifications, including request structures, allowed operations, and response payloads, are available in the references directory:

- [API Reference Guide](references/api_reference.md)
- [Microservice Architecture Documentation](references/microservice_documentation.md)
- [Methodological Development Guidelines](references/development_guidelines.md)

## Development and Contribution Guidelines

This project adheres to strict coding and communication standards:
- **Code Language**: All source code, variables, and documentation must be written in English.
- **Formatting**: Adherence to standard Python styling (PEP 8).
- **Communication Tone**: Technical, concise, and professional. Emojis are strictly prohibited across all documentation and comments.

Please consult the `references/development_guidelines.md` file before proposing major structural changes to ensure alignment with the established Application Factory and Blueprint routing patterns.
