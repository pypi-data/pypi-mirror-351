import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from magmalab._core.stats import xlim, ylim

class Correlation:
    def __init__(self, data: pd.DataFrame, round_digits: int = 2, columns: list[str] = None):
        """
        Classe para análise e visualização de correlações entre variáveis numéricas.

        Parâmetros:
        - data: DataFrame com dados.
        - round_digits: casas decimais para exibir nos valores das correlações.
        - columns: colunas a incluir; se None, detecta todas as colunas numéricas.
        """
        if columns is None:
            columns = data.select_dtypes(include='number').columns.tolist()
        self.data = data[columns]
        self.corr = self.data.corr(numeric_only=True)
        self.cmap = sns.diverging_palette(10, 150, n=1000, center='light')
        self.fmt = f".{round_digits}f"

    def heatmap(self, figsize=(10, 8), fontsize=14, ticksfontsize=10) -> plt.Axes:
        ax = sns.heatmap(
            data=self.corr,
            vmin=-1, vmax=1,
            annot=True,
            cmap=self.cmap,
            fmt=self.fmt,
            xticklabels=self.corr.columns,
            yticklabels=self.corr.columns,
            annot_kws={"size": ticksfontsize}
        )
        ax.figure.set_size_inches(figsize)
        ax.set_title('Matriz de Correlação', fontdict={'fontsize': fontsize}, pad=16)
        ax.set_xticklabels(ax.get_xticklabels(), fontsize=ticksfontsize, rotation=-75)
        ax.set_yticklabels(ax.get_yticklabels(), fontsize=ticksfontsize)
        return ax

    def columns(self, cols_x=None, cols_y=None, lim=0.5,
                figsize=(5, 6), wspace=4.0) -> tuple[plt.Figure, np.ndarray]:
        if cols_x is None:
            cols_x = self.data.columns.tolist()
        if cols_y is None:
            cols_y = self.data.columns.tolist()

        fig, axs = plt.subplots(1, len(cols_y), figsize=figsize)
        if len(cols_y) == 1:
            axs = np.array([axs])
        fig.subplots_adjust(hspace=0.3, wspace=wspace)

        for col, ax in zip(cols_y, axs.ravel()):
            corr_data = self.data[list(set(cols_x + [col]))].corr(numeric_only=True)
            corrs = corr_data[col].sort_values(ascending=False)[1:]
            filtered = corrs[(corrs < -lim) | (corrs > lim)].to_frame()
            sns.heatmap(filtered, vmin=-1, vmax=1, annot=True,
                        cmap=self.cmap, fmt=self.fmt, cbar=False, ax=ax)
            ax.set_title(col, fontsize=14, y=1.02)

        return fig, axs

    def group_query(self, group1=None, group2=None, lim=0.2, rotation=0, ax=None) -> plt.Axes:
        if group1 is None:
            group1 = self.data.columns.tolist()
        if group2 is None:
            group2 = self.data.columns.tolist()

        if ax is None:
            _, ax = plt.subplots(figsize=(1, 7))

        c = self.corr.loc[group1, group2].stack().reset_index()
        c.columns = ['Variable 1', 'Variable 2', 'Correlation']
        c = c[c['Variable 1'] < c['Variable 2']]
        c = c.query('Correlation > @lim or Correlation < -@lim').sort_values(by='Correlation', ascending=False)
        c['Not Null Samples'] = c.apply(
            lambda row: self.data[[row['Variable 1'], row['Variable 2']]].dropna().shape[0],
            axis=1
        )

        sns.heatmap(
            c[['Correlation']],
            vmin=-1, vmax=1,
            annot=True, cmap=self.cmap, fmt=self.fmt, cbar=False, ax=ax
        )

        ax_ = ax.twinx()
        ax_.set_ylim(ax.get_ylim())
        ax_.set_yticks(ax.get_yticks())
        ax.set_yticklabels(c['Not Null Samples'], rotation=rotation)
        ax.set_yticklabels(c['Variable 1'] + " / " + c['Variable 2'], rotation=rotation)

        return ax

from magmalab._engine.plots import scatterplot

def main_correlations(df: pd.DataFrame, feed: list[str], mineralogy: list[str], top_n: int = 20):
    """
    Mostra os pares com maiores correlações absolutas entre colunas do feed e da mineralogia.
    Exibe os scatterplots coloridos por tipo de variável (feed, mineralogia ou misto).

    Parâmetros:
    - df: DataFrame com os dados.
    - feed: colunas relacionadas aos elementos de entrada.
    - mineralogy: colunas mineralógicas.
    - top_n: número de pares a serem exibidos (default=20).

    Retorno:
    - fig, axs: figura matplotlib e eixos com os gráficos.
    """
    corr_obj = Correlation(df[feed + mineralogy])
    abs_corr = corr_obj.corr.abs()
    np.fill_diagonal(abs_corr.values, 0)

    # Pega pares únicos (parte superior da matriz)
    mask = np.triu(np.ones(abs_corr.shape), k=1).astype(bool)
    upper_corr = abs_corr.where(mask)

    # Seleciona os top_n pares com maior correlação absoluta
    top_pairs = upper_corr.unstack().dropna().sort_values(ascending=False).head(top_n)

    # Cria figura
    ncols = 4
    nrows = int(np.ceil(top_n / ncols))
    fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(5 * ncols, 5 * nrows))
    fig.subplots_adjust(wspace=0.4, hspace=0.4)

    for ax, (col1, col2) in zip(axs.ravel(), top_pairs.index):
        if col1 in mineralogy and col2 in mineralogy:
            color = 'indianred'
        elif col1 in feed and col2 in feed:
            color = 'skyblue'
        else:
            color = 'orange'

        scatterplot(data=df, x=col1, y=col2, ax=ax, fontsize=16, color=color)

    # Esconde eixos não usados
    for ax in axs.ravel()[len(top_pairs):]:
        ax.axis('off')

    return fig, axs

