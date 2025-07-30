import os
from typing import List

def map_files(folder_path: str) -> List[str]:
    """
    Lista todos os arquivos em um diretório, incluindo arquivos em subpastas.

    Parâmetros:
    - diretorio (str): Caminho da pasta que será varrida.

    Retorna:
    - List[str]: Lista completa dos caminhos dos arquivos encontrados.
    """
    found_files = []
    for raiz, _, file_list in os.walk(folder_path):
        for file_name in file_list:
            full_path = os.path.join(raiz, file_name)
            found_files.append(full_path)
    return found_files
