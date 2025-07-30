import numpy as np
import pandas as pd
from sklearn import metrics
from scipy.stats import pearsonr, spearmanr, kendalltau

univariate_metric_map = {
    'N': 'N',
    'Nmiss': 'Nₘᵢₛₛ',
    'Mean': 'x̄',
    'Median': 'M',
    'Mode': 'x̂',
    'Std': 'σ',
    'Min': 'min',
    'Max': 'max',
    'Range': 'Δ',
    'Q1': 'Q₁',
    'Q3': 'Q₃',
    'IQR': 'IQR',
    'Skewness': 'γ₁',
    'Kurtosis': 'γ₂',
    'CV': 'CV'
}

univariate_metric_functions = {
    'N': lambda x: x.count(),
    'Nmiss': lambda x: x.isna().sum(),
    'Mean': lambda x: x.mean(),
    'Median': lambda x: x.median(),
    'Mode': lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan,
    'Std': lambda x: x.std(),
    'Min': lambda x: x.min(),
    'Max': lambda x: x.max(),
    'Range': lambda x: x.max() - x.min(),
    'Q1': lambda x: x.quantile(0.25),
    'Q3': lambda x: x.quantile(0.75),
    'IQR': lambda x: x.quantile(0.75) - x.quantile(0.25),
    'Skewness': lambda x: x.skew(),
    'Kurtosis': lambda x: x.kurtosis(),
    'CV': lambda x: x.std() / x.mean() if x.mean() != 0 else np.nan
}

def calculate_univariate_metrics(series: pd.Series, metric_names: list[str]) -> dict:
    """
    Calcula métricas univariadas com nomes comuns como entrada e símbolos como chave de saída.

    Parâmetros:
        series: pd.Series — série de dados numéricos
        metric_names: list[str] — lista como ['Mean', 'Std', 'CV', ...]

    Retorna:
        dict com símbolos como chaves, ex: {'x̄': ..., 'σ': ...}
    """
    results = {}
    available_metrics = list(univariate_metric_functions.keys())

    for name in metric_names:
        if name in univariate_metric_functions:
            symbol = univariate_metric_map[name]
            try:
                results[symbol] = univariate_metric_functions[name](series)
            except Exception as e:
                results[symbol] = f"Erro: {e}"
        else:
            print(f"[!] A métrica '{name}' não existe.")
            print("→ Métricas disponíveis:", ', '.join(available_metrics))
            print()
    
    return results

metric_functions = {
    "R²":      metrics.r2_score,
    "RSE":     lambda y_true, y_pred: np.sqrt(
                   np.sum((y_true - y_pred) ** 2) / (len(y_true) - 2)
               ),
    "MAE":     metrics.mean_absolute_error,
    "MAPE":    metrics.mean_absolute_percentage_error,
    "MSE":     metrics.mean_squared_error,                 # keeps default squared=True
    "RMSE":    metrics.root_mean_squared_error,            # NEW helper
    "MSLE":    metrics.mean_squared_log_error,             # still valid
    "RMSLE":   metrics.root_mean_squared_log_error,        # NEW helper
    "Pearson": lambda y_true, y_pred: pearsonr(y_true, y_pred)[0],
    "Spearman":lambda y_true, y_pred: spearmanr(y_true, y_pred).correlation,
    "Kendall": lambda y_true, y_pred: kendalltau(y_true, y_pred).correlation,
}


def calculate_metrics(y_test: np.ndarray, y_pred: np.ndarray, metric_names: list[str]) -> dict:
    """
    Calcula as métricas especificadas a partir de nomes fornecidos.

    Parâmetros:
        y_test: array com valores reais
        y_pred: array com valores preditos
        metric_names: lista de nomes das métricas a calcular

    Retorna:
        Dicionário com os resultados das métricas válidas.
        Em caso de métrica inválida, informa ao usuário no console.
    """
    results = {}
    available_metrics = list(metric_functions.keys())

    for name in metric_names:
        if name in metric_functions:
            try:
                results[name] = metric_functions[name](y_test, y_pred)
            except Exception as e:
                results[name] = f"Erro: {e}"
        else:
            print(f"[!] A métrica '{name}' não existe.")
            print("→ Métricas disponíveis:", ', '.join(available_metrics))
            print()

    return results
