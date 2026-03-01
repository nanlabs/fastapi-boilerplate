import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# Configuración
n_rows = 1200  # Entre 500 y 2000
file_path = "customer_churn_data.csv"

# Generación de datos básicos
data = {
    "customer_id": [f"CUST-{1000 + i}" for i in range(n_rows)],
    "age": np.random.randint(18, 81, size=n_rows),
    "gender": np.random.choice(["M", "F", "Other"], size=n_rows),
    "tenure_months": np.random.randint(1, 121, size=n_rows),
    "monthly_charges": np.round(np.random.uniform(20.0, 150.0, size=n_rows), 2),
    "contract_type": np.random.choice(["Month-to-month", "One year", "Two year"], size=n_rows),
    "payment_method": np.random.choice(
        ["Credit card", "Bank transfer", "Electronic check", "Mailed check"], size=n_rows
    ),
    "internet_service": np.random.choice(["DSL", "Fiber optic", "No"], size=n_rows),
    "support_tickets": np.random.randint(0, 21, size=n_rows),
    "churn": np.random.choice(["Yes", "No"], size=n_rows, p=[0.25, 0.75]),
}

df = pd.DataFrame(data)

# Cálculo de total_charges basado en tenure y monthly
df["total_charges"] = np.round(df["tenure_months"] * df["monthly_charges"], 2)

# Fechas aleatorias en el último año
start_date = datetime(2023, 1, 1)
df["last_interaction_date"] = [
    start_date + timedelta(days=random.randint(0, 365))
    for _ in range(n_rows)  # nosec B311
]

# Inyección de valores nulos (~7% de celdas aleatorias)
for col in df.columns:
    if col != "customer_id":  # Mantener ID limpio
        mask = np.random.random(n_rows) < 0.07
        df.loc[mask, col] = np.nan

# Guardar
df.to_csv(file_path, index=False, encoding="utf-8")
print(f"Archivo {file_path} generado con éxito.")
