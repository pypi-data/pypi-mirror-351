# -*- coding: utf-8 -*-
"""
Ferramentas para conversão mineralógica e manipulação de composições
químicas em massa.

Principais correções em relação à versão anterior
-------------------------------------------------
1.  `mass_percentage_distribution` agora valida entradas vazias e símbolos
    inexistentes na biblioteca *periodictable*.
2.  `Fragmentate` passa a iterar sobre as composições (colunas) — e não mais
    sobre os elementos (linhas) — evitando erros de chave.
3.  `MineralogicalConversion`
    • imports ausentes adicionados (numpy, typing)  
    • opção de impor balanço de massa `∑w = 1` (parâmetro `mass_balance`)  
    • inicialização de parâmetros em blocos, mais eficiente  
    • verificação de `self.w` antes de gerar o resumo.
"""

from __future__ import annotations

import periodictable
import numpy as np
import pandas as pd
import pyomo.environ as pyo
from typing import Dict, Tuple


# --------------------------------------------------------------------------- #
# 1. Cálculo de distribuição percentual em massa                              #
# --------------------------------------------------------------------------- #
def mass_percentage_distribution(
    chemical_composition: Dict[str, float]
) -> Dict[str, float]:
    """
    Converte uma composição molar em distribuição percentual em massa.

    Parâmetros
    ----------
    chemical_composition : dict[str, float]
        Dicionário {símbolo → quantidade molar (mol)}.

    Retorno
    -------
    dict[str, float]
        {símbolo → % em massa}.
    """
    if not chemical_composition:
        raise ValueError("A composição química não pode ser vazia.")

    masses = {}
    total_mass = 0.0

    for element, quantity in chemical_composition.items():
        try:
            atom = getattr(periodictable, element)
        except AttributeError as exc:
            raise KeyError(f"Elemento '{element}' não reconhecido.") from exc

        element_mass = atom.mass * quantity
        masses[element] = element_mass
        total_mass += element_mass

    # Normalização para 100 %
    return {el: (m / total_mass) * 100 for el, m in masses.items()}


# --------------------------------------------------------------------------- #
# 2. DataFrame com várias composições                                         #
# --------------------------------------------------------------------------- #
def calculate_compositions(
    compositions: Dict[str, Dict[str, float]]
) -> pd.DataFrame:
    """
    Constrói um DataFrame (elementos × composições) em % massa.

    Parâmetros
    ----------
    compositions : dict
        {nome → {elemento → quantidade molar}}

    Retorno
    -------
    pd.DataFrame
        Índice = elementos, colunas = nomes das composições.
    """
    data = {
        name: mass_percentage_distribution(comp)
        for name, comp in compositions.items()
    }

    df = (
        pd.DataFrame(data)
        .fillna(0.0)
        .round(2)
        .rename_axis("Elementos")
        .sort_index()
    )
    return df


# --------------------------------------------------------------------------- #
# 3. Fragmentação de um DataFrame original pelas composições                  #
# --------------------------------------------------------------------------- #
def Fragmentate(
    df: pd.DataFrame,
    compositions: Dict[str, Dict[str, float]],
) -> pd.DataFrame:
    """
    Adiciona, ao DataFrame original, colunas correspondentes às composições
    químicas fornecidas.

    Cada nova coluna é: ∑ (fração_massa_elemento × coluna_elemento_original).

    Parâmetros
    ----------
    df : pd.DataFrame
        Colunas representam elementos químicos (em mesma base de unidade).
    compositions : dict
        {nome → {elemento → quantidade molar}}

    Retorno
    -------
    pd.DataFrame
        DataFrame com as novas colunas das composições e sem duplicar
        as colunas de elementos usadas no cálculo.
    """
    weight_df = calculate_compositions(compositions)  # elementos × composições

    for comp in weight_df.columns:  # itera sobre cada composição
        weights = weight_df[comp] / 100.0          # Series indexado por elemento
        df[comp] = (df[weights.index] * weights).sum(axis=1)

    # Remove colunas de elementos (opcional) e reorganiza em ordem alfabética
    return (
        df.drop(columns=weight_df.index, errors="ignore")
        .reindex(sorted(df.columns), axis=1)
    )


# --------------------------------------------------------------------------- #
# 4. Conversão Mineralógica por Programação Linear                            #
# --------------------------------------------------------------------------- #
class MineralogicalConversion:
    """
    Ajusta um modelo de regressão linear restrita (não-negativa) para estimar
    composição FRX a partir de frações mineralógicas.

    Minimiza o erro quadrático médio:  y ≈ X · w
    """

    def __init__(self, X: pd.DataFrame, y: pd.Series):
        """
        Parâmetros
        ----------
        X : pd.DataFrame
            (amostras × minerais) — frações mineralógicas.
        y : pd.Series
            Composição FRX (mesmas amostras).
        """
        self.X = X
        self.y = y
        self.w: np.ndarray | None = None

    # ------------------------- funções internas ---------------------------- #
    @staticmethod
    def _mse(model) -> float:
        return sum(
            (model.y[i] - sum(model.X[i, j] * model.w[j] for j in model.J)) ** 2
            for i in model.I
        )

    # --------------------------- solução ----------------------------------- #
    def solve(
        self,
        bounds: Tuple[float, float] = (0, 1),
        mass_balance: bool = False,
        tee: bool = False,
    ) -> None:
        """
        Resolve o problema de mínimos quadrados restritos via IPOPT.

        Parâmetros
        ----------
        bounds : (float, float)
            Limites (inferior, superior) para cada peso `w_j`.
        mass_balance : bool, default=False
            Se True, impõe ∑ w_j = 1.0 (balanço de massa).
        tee : bool
            Exibe log completo do solver.
        """
        model = pyo.ConcreteModel()
        m, n = self.X.shape

        model.I = pyo.RangeSet(m)
        model.J = pyo.RangeSet(n)

        # Inicialização eficiente com dicionários
        model.X = pyo.Param(
            model.I, model.J,
            initialize={(i + 1, j + 1): self.X.iat[i, j] for i in range(m) for j in range(n)}
        )
        model.y = pyo.Param(
            model.I,
            initialize={i + 1: self.y.iat[i] for i in range(m)}
        )

        model.w = pyo.Var(model.J, within=pyo.NonNegativeReals, bounds=bounds)
        model.obj = pyo.Objective(rule=self._mse, sense=pyo.minimize)

        if mass_balance:
            model.mass = pyo.Constraint(expr=sum(model.w[j] for j in model.J) == 1.0)

        solver = pyo.SolverFactory("ipopt", executable="ipopt")
        solver.solve(model, tee=tee)

        self.w = np.fromiter((model.w[j]() for j in model.J), dtype=float)

    # --------------------------- resumo ------------------------------------ #
    def summary(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Retorna (FRX verdadeiro × previsto, contribuições % dos minerais).
        """
        if self.w is None:
            raise RuntimeError("Chame '.solve()' antes de solicitar o resumo.")

        frx_pred = self.X.dot(self.w)

        frx_df = (
            pd.DataFrame([self.y, frx_pred], index=["FRX_true", "FRX_pred"])
            .round(2)
        )
        frx_df["[SUM]"] = frx_df.sum(axis=1).round(2)

        mineral_df = (
            pd.DataFrame(self.w * 100, index=self.X.columns, columns=["Predicted(%)"])
            .T.round(2)
        )
        mineral_df["[SUM]"] = mineral_df.sum(axis=1).round(2)

        return frx_df, mineral_df
