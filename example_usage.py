"""Example usage for Token Cost Forecaster & Context Budgeter."""
from client import TokenCostForecaster

if __name__ == "__main__":
    prompt = "Detailed user instructions and conversation history..."
    report = TokenCostForecaster.forecast_and_budget(prompt, 1000, 14.50, 20.00)
    print("Budget Forecast:", report)
