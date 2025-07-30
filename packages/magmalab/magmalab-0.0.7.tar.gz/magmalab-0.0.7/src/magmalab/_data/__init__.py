import pandas as pd
from pathlib import Path

# Caminho do arquivo CSV
_DATA_DIR = Path(__file__).parent
mine = pd.read_csv(_DATA_DIR / "mine.csv")
