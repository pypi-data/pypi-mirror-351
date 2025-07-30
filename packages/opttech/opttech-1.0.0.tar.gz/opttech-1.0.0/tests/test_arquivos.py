import os
from opttech import map_files

def test_map_files(tmp_path):
    # Cria uma estrutura de pastas de teste
    (tmp_path / "subpasta").mkdir()
    arquivo1 = tmp_path / "arquivo1.txt"
    arquivo2 = tmp_path / "subpasta" / "arquivo2.txt"
    arquivo1.write_text("conteúdo")
    arquivo2.write_text("conteúdo")

    arquivos = map_files(str(tmp_path))
    assert str(arquivo1) in arquivos
    assert str(arquivo2) in arquivos
    assert len(arquivos) == 2
