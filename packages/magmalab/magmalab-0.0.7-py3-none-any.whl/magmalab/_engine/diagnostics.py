import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from magmalab._core import xlim, ylim, calculate_metrics


def FeatureImportances(
    data: pd.DataFrame,
    regressor,
    target: str,
    n: int = 7,
    ax=None
):
    """
    Displays feature importances with correlation direction.

    Parameters:
        data (pd.DataFrame): Dataset including target and features.
        regressor: A fitted model with feature_importances_ attribute.
        target (str): Name of the target column.
        n (int): Number of features to display.
        ax (matplotlib.axes.Axes, optional): Axis to plot on.
    """
    ax = plt.subplots()[1] if ax is None else ax

    df = pd.DataFrame()
    df['Features'] = data.drop(target, axis=1).columns
    df['Importances'] = abs(regressor.feature_importances_)
    df['Correlation'] = df['Features'].map(data.corr()[target]).apply(
        lambda x: 'Positive' if x >= 0 else 'Negative'
    )

    df = df.sort_values(by='Importances', ascending=False).iloc[:n].T
    df['Others'] = ['Others', 1 - df.loc['Importances'].sum(), '']

    sns.barplot(data=df.T, x='Features', y='Importances', hue='Correlation', ax=ax)
    ax.set_title(f'Feature Importances ({data.shape[1]})')
    return ax


def PredictionError(y_test, y_pred, metric_names=None, ax=None, cdot='forestgreen', cline='red'):
    """
    Gera um gráfico de erro de predição com métricas exibidas como texto.

    Parâmetros:
        y_test: Valores reais.
        y_pred: Valores previstos.
        metric_names: Lista de métricas a serem exibidas.
        ax: Eixo matplotlib opcional.
        cdot: Cor dos pontos.
        cline: Cor da linha de referência.
    """
    if metric_names is None:
        metric_names = ['MAE', 'MSE', 'RMSE', 'Pearson']

    metrics_results = calculate_metrics(y_test, y_pred, metric_names)
    ax = plt.subplots()[1] if not ax else ax
    sns.scatterplot(x=y_test, y=y_pred, color=cdot, ax=ax)
    ax.plot(xlim(ax), xlim(ax), linestyle='--', color=cline)

    metric_text = "\n  " + f'N: {len(y_test)}\n  ' + "\n  ".join(
        [f"{name}: {value:.2f}" if isinstance(value, float) else f"{name}: {value}"
         for name, value in metrics_results.items()]
    )
    ax.text(s=metric_text, x=xlim(ax)[0], y=ylim(ax)[1], fontsize=10, ha='left', va='top')
    ax.set_title('Prediction Error')
    ax.set_xlabel('True Value')
    ax.set_ylabel('Predicted Value')
    return ax
