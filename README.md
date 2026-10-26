# InsightForge — AI-Powered Business Data Analyst

InsightForge is a Python-based business analytics dashboard designed to help users explore sales data, understand business performance, and obtain insights through natural-language questions.

## Overview

The project combines interactive data visualization with an AI-assisted question-answering workflow to make business data easier to analyze and interpret.

## Features

- **Business KPI Dashboard:** Displays key sales metrics, including revenue, profit, order count, and customer information.
- **Sales Analytics:** Explores product performance, regional trends, revenue, and profitability.
- **AI-Powered Questions:** Supports natural-language questions about business data through an LLM integration.
- **Management Reporting:** Supports the generation of concise business summaries and actionable insights.

## Tech Stack

- **Language:** Python
- **Dashboard:** Streamlit
- **Data Processing:** Pandas
- **LLM Integration:** Ollama

## Getting Started

### Prerequisites

Install Python and Ollama. Ensure that the model used by the application is available locally.

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Anushkas245/InsightForge.git
   cd InsightForge
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   ```

   On Windows:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

3. Install the project's dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the application:

   ```bash
   streamlit run app.py
   ```

   Ensure Ollama is running and the configured model is available before using the AI question-answering feature.

## Project Structure

The application is organized around the Streamlit interface, data-processing logic, and AI-assisted question-answering components.

Refer to the repository files for the current implementation details.

## Future Improvements

- Add automated tests for data processing and question answering.
- Improve error handling and validation for user queries.
- Add deployment support and more comprehensive documentation.

## Author

**Anushka Salkar**

- GitHub: https://github.com/Anushkas245
- LinkedIn: https://linkedin.com/in/anushkas245
