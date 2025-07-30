# Ferramentas analíticas
from magmalab._core import calculate_univariate_metrics, univariate_metric_functions, calculate_metrics, metric_functions, Drillhole

# Visualizações
from magmalab._engine import (
    boxplots, histplot, scatterplot, countplot, nullData,
    Correlation, main_correlations,
    MiningVisualizer, plot_drillholes_3d,
    FeatureImportances, PredictionError
)

from magmalab._data import mine

__all__ = [
    "calculate_metrics", "metric_functions", "calculate_univariate_metrics", "univariate_metric_functions",
    "Drillhole",
    "boxplots", "histplot", "scatterplot", "countplot", "nullData",
    "Correlation", "main_correlations",
    "MiningVisualizer", "plot_drillholes_3d"
]
