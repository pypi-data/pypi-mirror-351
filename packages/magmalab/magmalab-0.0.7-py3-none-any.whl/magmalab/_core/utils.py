import pandas as pd


def dict_value_counts(series: pd.Series, normalize: bool = False) -> dict[str, float]:
    """
    Retorna a contagem (ou proporção) dos valores únicos de uma série como dicionário.

    Parâmetros:
    - series: pd.Series de interesse.
    - normalize: se True, retorna proporções; caso contrário, contagens absolutas.

    Retorna:
    - dict com valores como strings e suas contagens ou proporções.
    """
    data = series.value_counts(normalize=normalize).to_dict()
    return {str(key): value for key, value in data.items()}

def reencoder(data: pd.DataFrame, columns: list[str], sep: str = '-') -> tuple[pd.DataFrame, list[str]]:
    """
    Agrupa variáveis dummies em colunas únicas codificadas com o sufixo.

    Exemplo:
    - Se as colunas forem: ['color-red', 'color-blue', 'color-green']
    - Resultado: nova coluna 'color' com valores 'red', 'blue', 'green'

    Parâmetros:
    - data: DataFrame de entrada.
    - columns: lista de colunas no formato 'grupo-sufixo'.
    - sep: caractere separador (default = '-').

    Retorna:
    - df transformado
    - lista de novas colunas criadas
    """
    items = {}
    for col in columns:
        key, _ = col.split(sep, 1)
        items.setdefault(key, []).append(col)

    df = data.copy()
    for key in items:
        df[key] = (
            df[items[key]] == 1
        ).idxmax(axis=1).apply(lambda x: x.split(sep, 1)[1] if pd.notnull(x) else None)

    return df, list(items.keys())

