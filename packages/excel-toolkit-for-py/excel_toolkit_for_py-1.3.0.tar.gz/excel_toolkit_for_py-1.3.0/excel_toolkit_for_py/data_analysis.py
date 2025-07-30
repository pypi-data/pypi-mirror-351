"""
Módulo para análise de dados em arquivos Excel e CSV.
"""

from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
from scipy import stats


def calculate_basic_stats(df: pd.DataFrame, columns: Optional[List[str]] = None) -> Dict[str, Dict[str, float]]:
    """
    Calcula estatísticas básicas para as colunas numéricas do DataFrame.
    
    Args:
        df: DataFrame pandas
        columns: Lista opcional de colunas para análise. Se None, usa todas as colunas numéricas.
    
    Returns:
        Dicionário com estatísticas para cada coluna
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    stats_dict = {}
    for col in columns:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            stats_dict[col] = {
                'mean': df[col].mean(),
                'median': df[col].median(),
                'mode': df[col].mode().iloc[0] if not df[col].mode().empty else None,
                'std': df[col].std(),
                'min': df[col].min(),
                'max': df[col].max(),
                'q1': df[col].quantile(0.25),
                'q3': df[col].quantile(0.75)
            }
    
    return stats_dict

def detect_outliers(df: pd.DataFrame, columns: Optional[List[str]] = None, 
                   method: str = 'zscore', threshold: float = 3.0) -> Dict[str, List[int]]:
    """
    Detecta outliers em colunas numéricas usando diferentes métodos.
    
    Args:
        df: DataFrame pandas
        columns: Lista opcional de colunas para análise
        method: Método de detecção ('zscore' ou 'iqr')
        threshold: Limiar para detecção de outliers
    
    Returns:
        Dicionário com índices dos outliers para cada coluna
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    outliers = {}
    for col in columns:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            if method == 'zscore':
                z_scores = np.abs(stats.zscore(df[col].dropna()))
                outliers[col] = df[col].index[z_scores > threshold].tolist()
            elif method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers[col] = df[col].index[
                    (df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))
                ].tolist()
    
    return outliers

def calculate_correlations(df: pd.DataFrame, columns: Optional[List[str]] = None, 
                         method: str = 'pearson') -> pd.DataFrame:
    """
    Calcula correlações entre colunas numéricas.
    
    Args:
        df: DataFrame pandas
        columns: Lista opcional de colunas para análise
        method: Método de correlação ('pearson', 'spearman' ou 'kendall')
    
    Returns:
        DataFrame com matriz de correlação
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    return df[columns].corr(method=method)

def create_pivot_table(df: pd.DataFrame, 
                      index: Union[str, List[str]],
                      columns: Optional[Union[str, List[str]]] = None,
                      values: Optional[Union[str, List[str]]] = None,
                      aggfunc: str = 'mean') -> pd.DataFrame:
    """
    Cria uma tabela dinâmica a partir do DataFrame.
    
    Args:
        df: DataFrame pandas
        index: Coluna(s) para usar como índice
        columns: Coluna(s) para usar como colunas
        values: Coluna(s) para usar como valores
        aggfunc: Função de agregação ('mean', 'sum', 'count', etc.)
    
    Returns:
        DataFrame com a tabela dinâmica
    """
    return pd.pivot_table(
        df,
        index=index,
        columns=columns,
        values=values,
        aggfunc=aggfunc
    ) 