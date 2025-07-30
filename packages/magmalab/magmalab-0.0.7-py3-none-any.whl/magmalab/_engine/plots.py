import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from magmalab._core.metrics import calculate_univariate_metrics 
from magmalab._core import calculate_metrics


def boxplots(
    df: pd.DataFrame,
    cols: list,
    hue: str,
    nrows: int,
    ncols: int,
    figsize: tuple,
    wspace: float = 0.4,
    hspace: float = 0.4,
    title: str = None,
    y_title: float = 1.0,
    fontsize_title: int = 16,
    fontsize_label: int = 14,
    fontsize_count: int = 12,
    palette: str = 'tab10',
    background_colors: bool = False,
    legend: bool = True,
    xlim_expand: float = 0.0,
    order: list = None  # <<< ADICIONADO AQUI
):

    """
    Cria múltiplos boxplots horizontais com contagem secundária de amostras no eixo direito.

    Parâmetros:
        df (pd.DataFrame): DataFrame de entrada contendo as colunas numéricas e categóricas
        cols (list): Lista de colunas numéricas a serem plotadas
        hue (str): Coluna categórica para o eixo Y e agrupamento
        nrows (int): Número de linhas na grade de subplots
        ncols (int): Número de colunas na grade de subplots
        figsize (tuple): Tamanho da figura (largura, altura)
        wspace (float): Espaçamento horizontal entre os gráficos
        hspace (float): Espaçamento vertical entre os gráficos
        title (str): Título geral da figura
        y_title (float): Posição vertical do título (entre 0 e 1)
        fontsize_title (int): Tamanho da fonte do título principal
        fontsize_label (int): Tamanho da fonte do rótulo do eixo X
        fontsize_count (int): Tamanho da fonte da contagem no eixo direito
        palette (str): Paleta de cores do seaborn
        background_colors (bool): Lista de cores de fundo para cada subplot (False desativa)
        legend (bool): Se True, exibe legenda do seaborn (embutida no eixo Y)
        xlim_expand (float): Expansão percentual do eixo X (ex: 0.15 para +15%) para evitar sobreposição com legenda

    Retorna:
        fig (matplotlib.figure.Figure): Figura contendo todos os subplots
        axs (np.ndarray): Array de eixos criados
    """
    fig, axs = plt.subplots(nrows, ncols, figsize=figsize)
    fig.subplots_adjust(wspace=wspace, hspace=hspace)
    fig.suptitle(title, y=y_title, fontsize=fontsize_title)

    data = df[cols + [hue]].dropna(subset=[hue]).sort_values(by=hue)

    for i, (x, ax) in enumerate(zip(cols, axs.ravel())):
        x_data = data.dropna(subset=[x])
        sns.boxplot(
            data=x_data,
            x=x,
            y=hue,
            hue=hue,
            order=order,
            palette=palette,
            legend=legend,
            orient='h',
            ax=ax
        )


        # Ajuste dos limites do eixo X
        xmin, xmax = ax.get_xlim()
        delta_x = (xmax - xmin) * xlim_expand
        ax.set_xlim(xmin, xmax + delta_x)

        # Eixos e rótulos
        ax.set_xlabel(x, fontsize=fontsize_label)
        ax.set_ylabel(None)
        ax.tick_params(axis='x', labelsize=fontsize_count)
        ax.tick_params(axis='y', labelsize=fontsize_count)

        # Contagem secundária no eixo direito
        ax2 = ax.twinx()
        ax2.set_ylim(ax.get_ylim())
        sample_counts = x_data[hue].value_counts().sort_index()
        ax2.set_yticks(ax.get_yticks())
        ax2.set_yticklabels(sample_counts, fontsize=fontsize_count)
        ax2.set_ylabel(None)

        if background_colors:
            ax.set_facecolor(background_colors[i])

    return fig, axs


def histplot(
    data: pd.DataFrame,
    x: str,
    ax=None,
    fontsize: int = 8,
    color: str = 'royalblue',
    gap: float = 1.0,
    metrics: list[str] = None,
    xlim_expand: float = 0.0
):
    """
    Histograma com curva KDE e estatísticas configuráveis.

    Parâmetros:
        data (pd.DataFrame): DataFrame de entrada
        x (str): Nome da coluna a plotar
        ax (matplotlib.axes.Axes, opcional): Eixo para desenhar
        fontsize (int): Tamanho da fonte
        color (str): Cor da curva/barra
        gap (float): Fator de expansão horizontal (depreciação futura)
        metrics (list[str]): Lista de métricas univariadas, ex: ['Mean', 'Std']
        xlim_expand (float): Porcentagem de expansão do eixo X (ex: 0.1 para +10%)

    Retorna:
        matplotlib.axes.Axes
    """
    ax = plt.subplots()[1] if not ax else ax
    sns.histplot(data=data, x=x, kde=True, color=color, ax=ax)

    # Expansão do eixo X para dar espaço à legenda
    xmin, xmax = ax.get_xlim()
    delta_x = (xmax - xmin) * xlim_expand
    ax.set_xlim(xmin, xmax + delta_x)

    ax.set_title(x, fontsize=fontsize)
    ax.set_xlabel(None)
    ax.set_ylabel('Quantidade', fontsize=fontsize)

    # Métricas padrão
    if metrics is None:
        metrics = ['N', 'Mean', 'Median', 'Std', 'CV']

    # Cálculo de métricas
    results = calculate_univariate_metrics(data[x], metrics)
    stats = '\n'.join([f'{k}: {v:.2f}' if isinstance(v, (int, float)) else f'{k}: {v}' for k, v in results.items()])

    ax.text(
        s=stats,
        x=ax.get_xlim()[1],
        y=ax.get_ylim()[1] * 0.99,
        fontsize=fontsize,
        ha='right',
        va='top'
    )

    return ax

def scatterplot(
    data: pd.DataFrame,
    x: str,
    y: str,
    ax=None,
    fontsize: int = 8,
    gap: float = 1.3,
    color: str = 'royalblue',
    metrics: list[str] = None
):
    """
    Gráfico de dispersão com métricas configuráveis.

    Parâmetros:
        data (pd.DataFrame): Dados de entrada
        x (str): Variável no eixo X
        y (str): Variável no eixo Y
        ax (matplotlib.axes.Axes): Eixo de destino
        fontsize (int): Tamanho da fonte
        gap (float): Expansão do eixo X
        color (str): Cor dos pontos (padrão: 'royalblue')
        metrics (list[str]): Lista de métricas a exibir (default: ['Pearson', 'Spearman', 'Kendall', 'R²'])

    Retorna:
        matplotlib.axes.Axes
    """
    ax = plt.subplots()[1] if ax is None or ax is False else ax
    df_plot = data[[x, y]].dropna()

    # Scatterplot com cor definida pelo usuário
    sns.scatterplot(data=df_plot, x=x, y=y, color=color, ax=ax)
    ax.set_xlim(ax.get_xlim()[0], ax.get_xlim()[1] * gap)

    # Métricas padrão
    if metrics is None:
        metrics = ['Pearson', 'Spearman', 'Kendall', 'R²']

    # Cálculo de métricas
    y_true = df_plot[y].values
    y_pred = df_plot[x].values
    results = calculate_metrics(y_true, y_pred, metrics)
    stats = [f'{k}: {v:.2f}' if isinstance(v, (int, float)) else f'{k}: {v}' for k, v in results.items()]
    stats_text = f'N: {len(df_plot)}\n' + '\n'.join(stats)

    ax.text(
        s=stats_text,
        x=ax.get_xlim()[1],
        y=ax.get_ylim()[1] * 0.99,
        fontsize=fontsize,
        ha='right',
        va='top'
    )

    ax.set_xlabel(x, fontsize=fontsize)
    ax.set_ylabel(y, fontsize=fontsize)
    return ax



def countplot(
    data: pd.DataFrame,
    x: str,
    ax=None,
    palette: str = 'tab10',
    fontsize: int = 10,
    title: str = None,
    order: list[str] = None
):
    """
    Gera um countplot horizontal com contagens no eixo secundário (direita).

    Parâmetros:
        data (pd.DataFrame): DataFrame de entrada.
        x (str): Nome da coluna categórica.
        ax (matplotlib.axes.Axes, opcional): Eixo para plotagem.
        palette (str): Paleta de cores.
        fontsize (int): Tamanho da fonte.
        title (str): Título do gráfico.
        order (list[str], opcional): Ordem manual das categorias. Se None, usa frequência decrescente.

    Retorna:
        ax (matplotlib.axes.Axes): Eixo com o gráfico desenhado.
    """
    ax = plt.subplots(figsize=(6, 4))[1] if ax is None else ax
    data = data.dropna(subset=[x])

    # Determina a ordem
    if order is None:
        order = data[x].value_counts().index.tolist()

    # Gráfico principal
    sns.countplot(data=data, y=x, order=order, palette=palette, ax=ax)

    ax.set_title(title or f'Contagem de {x}', fontsize=fontsize * 1.2)
    ax.set_xlabel('Contagem', fontsize=fontsize)
    ax.set_ylabel(None)
    ax.tick_params(axis='x', labelsize=fontsize)
    ax.tick_params(axis='y', labelsize=fontsize)

    # Eixo secundário com contagem
    ax2 = ax.twinx()
    ax2.set_ylim(ax.get_ylim())
    sample_counts = data[x].value_counts().reindex(order)
    ax2.set_yticks(ax.get_yticks())
    ax2.set_yticklabels(sample_counts, fontsize=fontsize)
    ax2.set_ylabel(None)

    return ax


def nullData(
    data: pd.DataFrame,
    cols: list = None,
    title: str = 'Valores não nulos por coluna',
    ax=None,
    fontsize: int = 10,
    order: list[str] = None,
    palette: str = 'Blues_d',
    color: str = 'royalblue'
):
    """
    Plota um gráfico de barras horizontais com a contagem de valores não nulos por coluna.

    Parâmetros:
        data (pd.DataFrame): DataFrame de entrada
        cols (list, opcional): Lista de colunas a avaliar. Se None, usa todas.
        title (str): Título do gráfico
        ax (matplotlib.axes.Axes): Eixo a ser usado (opcional)
        fontsize (int): Tamanho da fonte
        order (list[str], opcional): Ordem manual das colunas. Se None, ordena do menor para o maior.
        palette (str): Paleta de cores (usada se color for None)
        color (str): Cor única para as barras (default: 'royalblue')

    Retorna:
        ax (matplotlib.axes.Axes): Eixo com o gráfico desenhado
    """
    if cols is None:
        cols = data.columns.tolist()

    df = data.shape[0] - data[cols].isna().sum()
    df = df[df.index.isin(cols)]

    # Ordenação
    if order is None:
        df = df.sort_values(ascending=True)
    else:
        df = df.reindex(order)

    ax = plt.subplots(figsize=(max(len(df) * 0.6, 6), 4))[1] if ax is None else ax

    # Gráfico principal
    sns.barplot(
        x=df.values, y=df.index,
        palette=None if color else palette,
        color=color if color else None,
        ax=ax
    )

    # Eixo principal
    ax.set_title(title, fontsize=fontsize * 1.5)
    ax.set_xlabel('Não nulos', fontsize=fontsize)
    ax.set_ylabel(None)
    ax.tick_params(axis='both', labelsize=fontsize)

    # Eixo secundário à direita (contagem)
    ax2 = ax.twinx()
    ax2.set_ylim(ax.get_ylim())
    ax2.set_yticks(ax.get_yticks())
    ax2.set_yticklabels([f'{int(v)}' for v in df.values], fontsize=fontsize)
    ax2.set_ylabel(None)

    return ax

