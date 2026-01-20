import pdfplumber
from pathlib import Path

class LerPDF:
    """Lê os PDFs e extrai dados para o parsing"""
    
    def __init__(self, caminho_pasta: Path):
        self.caminho_pasta = caminho_pasta
    
    def ler_pdf(self, caminho_pdf: Path) -> str:
        with pdfplumber.open(caminho_pdf) as pdf:
            texto_completo = ""
            
            for pagina in pdf.pages: # Extrai dados de todas os PDFs e retorna
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_completo += texto_pagina + "\n"
        
        return texto_completo
    
    def listar_arquivos_pdf(self) -> list[Path]:
        """Retorna uma lista com todos os PDFs que existem dentro da pasta"""
        return list(self.caminho_pasta.glob("*.pdf"))
