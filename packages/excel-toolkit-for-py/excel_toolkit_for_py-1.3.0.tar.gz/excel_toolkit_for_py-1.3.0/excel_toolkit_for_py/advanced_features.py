"""
Módulo de funcionalidades avançadas para manipulação de arquivos Excel.
Inclui suporte a senhas, validação de células vazias, formatação condicional,
manipulação de fórmulas e suporte a gráficos.
"""

import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill, Font, Color
from openpyxl.chart import BarChart, Reference
from msoffcrypto import OfficeFile
import io
from typing import Union, List, Dict, Any, Optional
import warnings

def read_protected_excel(file_path: str, password: str) -> pd.DataFrame:
    """
    Lê um arquivo Excel protegido por senha.
    
    Args:
        file_path (str): Caminho do arquivo Excel
        password (str): Senha do arquivo
        
    Returns:
        pd.DataFrame: DataFrame com os dados do arquivo
        
    Raises:
        ValueError: Se a senha estiver incorreta
        FileNotFoundError: Se o arquivo não existir
    """
    try:
        with open(file_path, 'rb') as file:
            office_file = OfficeFile(file)
            office_file.load_key(password=password)
            
            decrypted = io.BytesIO()
            office_file.decrypt(decrypted)
            
            return pd.read_excel(decrypted)
    except Exception as e:
        raise ValueError(f"Erro ao ler arquivo protegido: {str(e)}")

def validate_empty_cells(df: pd.DataFrame, 
                        columns: Optional[List[str]] = None,
                        threshold: float = 0.1) -> Dict[str, Any]:
    """
    Valida células vazias em um DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame a ser validado
        columns (List[str], optional): Lista de colunas para validar. Se None, valida todas.
        threshold (float): Percentual máximo de células vazias permitido (0-1)
        
    Returns:
        Dict[str, Any]: Dicionário com resultados da validação
    """
    if columns is None:
        columns = df.columns.tolist()
    
    results = {
        'total_cells': len(df) * len(columns),
        'empty_cells': {},
        'columns_above_threshold': []
    }
    
    for col in columns:
        empty_count = df[col].isna().sum()
        empty_percent = empty_count / len(df)
        results['empty_cells'][col] = {
            'count': empty_count,
            'percent': empty_percent
        }
        
        if empty_percent > threshold:
            results['columns_above_threshold'].append(col)
    
    return results

def apply_conditional_formatting(file_path: str,
                               rules: List[Dict[str, Any]]) -> None:
    """
    Aplica formatação condicional a um arquivo Excel.
    
    Args:
        file_path (str): Caminho do arquivo Excel
        rules (List[Dict[str, Any]]): Lista de regras de formatação
            Cada regra deve conter:
            - 'range': intervalo de células (ex: 'A1:B10')
            - 'type': tipo de formatação ('cellIs', 'containsText', etc)
            - 'operator': operador ('greaterThan', 'lessThan', etc)
            - 'formula': fórmula ou valor para comparação
            - 'format': dicionário com estilo (ex: {'fill': 'FF0000'})
    """
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active
    
    for rule in rules:
        cell_range = rule['range']
        fmt = rule['format']
        
        for row in ws[cell_range]:
            for cell in row:
                if rule['type'] == 'cellIs':
                    try:
                        # Converte o valor da célula para número se possível
                        cell_value = float(cell.value) if cell.value is not None else 0
                        formula_value = float(rule['formula'])
                        
                        # Mapeia operadores para funções de comparação
                        operators = {
                            '>': lambda x, y: x > y,
                            '<': lambda x, y: x < y,
                            '>=': lambda x, y: x >= y,
                            '<=': lambda x, y: x <= y,
                            '==': lambda x, y: x == y,
                            '!=': lambda x, y: x != y
                        }
                        
                        if operators[rule['operator']](cell_value, formula_value):
                            if 'fill' in fmt:
                                # Adiciona 'FF' no início para opacidade total
                                fill_color = f"FF{fmt['fill']}"
                                cell.fill = PatternFill(start_color=fill_color,
                                                      end_color=fill_color,
                                                      fill_type='solid')
                            if 'font' in fmt:
                                cell.font = Font(**fmt['font'])
                    except (ValueError, TypeError):
                        # Ignora células que não podem ser convertidas para número
                        continue
    
    wb.save(file_path)

def extract_formulas(file_path: str) -> Dict[str, List[str]]:
    """
    Extrai fórmulas de um arquivo Excel.
    
    Args:
        file_path (str): Caminho do arquivo Excel
        
    Returns:
        Dict[str, List[str]]: Dicionário com fórmulas por planilha
    """
    wb = openpyxl.load_workbook(file_path, data_only=False)
    formulas = {}
    
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        sheet_formulas = []
        
        for row in ws.iter_rows():
            for cell in row:
                if cell.value and str(cell.value).startswith('='):
                    sheet_formulas.append({
                        'cell': cell.coordinate,
                        'formula': cell.value
                    })
        
        formulas[sheet_name] = sheet_formulas
    
    return formulas

def add_chart(file_path: str,
              chart_type: str,
              data_range: str,
              title: str,
              output_file: Optional[str] = None) -> None:
    """
    Adiciona um gráfico a um arquivo Excel.
    
    Args:
        file_path (str): Caminho do arquivo Excel
        chart_type (str): Tipo do gráfico ('bar', 'line', 'pie')
        data_range (str): Intervalo de dados (ex: 'A1:B10')
        title (str): Título do gráfico
        output_file (str, optional): Caminho para salvar o arquivo modificado
    """
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active
    
    # Cria o gráfico baseado no tipo
    if chart_type == 'bar':
        chart = BarChart()
    # Adicione outros tipos de gráfico aqui
    
    # Define os dados incluindo o nome da planilha
    data_range_with_sheet = f"{ws.title}!{data_range}"
    data = Reference(ws, range_string=data_range_with_sheet)
    chart.add_data(data, titles_from_data=True)
    
    # Configura o gráfico
    chart.title = title
    chart.style = 13
    
    # Adiciona o gráfico à planilha
    ws.add_chart(chart, "E5")
    
    # Salva o arquivo
    output_path = output_file or file_path
    wb.save(output_path)

def protect_excel(file_path: str,
                 password: str,
                 output_file: Optional[str] = None) -> None:
    """
    Protege um arquivo Excel com senha.
    
    Args:
        file_path (str): Caminho do arquivo Excel
        password (str): Senha para proteger o arquivo
        output_file (str, optional): Caminho para salvar o arquivo protegido
    """
    wb = openpyxl.load_workbook(file_path)
    
    # Protege todas as planilhas
    for ws in wb.worksheets:
        ws.protection.set_password(password)
    
    # Salva o arquivo
    output_path = output_file or file_path
    wb.save(output_path) 