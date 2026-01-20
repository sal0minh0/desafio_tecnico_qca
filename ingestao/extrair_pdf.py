import re
from pathlib import Path
from pydantic import ValidationError
from typing import Optional

from ingestao.modelos import Pedido, Produto
from ingestao.ler_pdf import LerPDF
from ingestao.parser_pdf import ParserPDF
from ingestao.salvar_json import SalvarJSON


class ExtrairPDF:  
    """Classe Principal de Extração de dados e salva-os em JSON"""
    
    def __init__(self, caminho_pasta: Path):
        self.caminho_pasta = caminho_pasta
        self.leitor = LerPDF(caminho_pasta)
        self.parser = ParserPDF()
        self.persistencia = SalvarJSON()
        
    def validar_dados(self, dados: dict, arquivo: str = "") -> Optional[Pedido]:
        """Validação dos dados extraídos"""
        campos_obrigatorios = ["ID_Pedido", "Data", "ID_Cliente", "Tabela_Itens"]
        campos_faltando = [c for c in campos_obrigatorios if not dados.get(c)]
        
        if campos_faltando:
            print(f"{arquivo}: Campos obrigatórios faltando: {', '.join(campos_faltando)}")
            return None
        
        try:
            pedido_validado = Pedido(**dados)
            print(f"> {arquivo}: Validado.")
            return pedido_validado
        except ValidationError as e:
            print(f"{arquivo}: Erro na validação:")
            for erro in e.errors():
                campo = ' -> '.join(str(loc) for loc in erro['loc'])
                print(f"  - Campo '{campo}': {erro['msg']}")
            return None

    def extrair_conteudo_pdf(self, caminho_pdf: Path) -> Optional[dict]:
        """Obtém o texto e extrai os dados"""
        texto = self.leitor.ler_pdf(caminho_pdf)
        dados = self.parser.extrair(texto)
        
        pedido_validado = self.validar_dados(dados, caminho_pdf.name)
        if pedido_validado:
            return pedido_validado.model_dump()
        return None

    def extrair_arquivo_unico(self, nome_arquivo: str) -> None:
        """Extrai apenas um PDF pelo nome do arquivo"""
        caminho = self.caminho_pasta / nome_arquivo
        
        if not caminho.exists():
            print(f"O Arquivo: '{nome_arquivo}' não foi encontrado.")
            return
        
        print(f"\n- Processando: {nome_arquivo}...")
        dados = self.extrair_conteudo_pdf(caminho)
        
        if dados:
            self.persistencia.salvar_novos([dados])
        else:
            print(f"Nenhum dado válido extraído do PDF: '{nome_arquivo}'.")
    
    def extrair_multiplos_arquivos(self, numero_de_arquivos: int, tamanho_lote: int = 50) -> None:
        """Extrai uma quantidade específica de PDFs, salvando em lotes"""
        arquivos = self.leitor.listar_arquivos_pdf()
        
        if not arquivos:
            print("Nenhum arquivo PDF encontrado.")
            return
        
        qtd = min(max(numero_de_arquivos, 1), len(arquivos))
        print(f"\nProcessando {qtd} de {len(arquivos)} arquivo(s)...\n")
        
        self._processar_em_lotes(arquivos[:qtd], tamanho_lote)
    
    def extrair_todos_arquivos(self, tamanho_lote: int = 50) -> None:
        """Extrai todos os PDFs da pasta, salvando em lotes"""
        arquivos = self.leitor.listar_arquivos_pdf()
        
        if not arquivos:
            print("Nenhum arquivo PDF encontrado.")
            return
        
        print(f"\nProcessando {len(arquivos)} arquivo(s) PDF...\n")
        
        self._processar_em_lotes(arquivos, tamanho_lote)
    
    def _processar_em_lotes(self, arquivos: list[Path], tamanho_lote: int) -> None:
        """Processa arquivos em lotes e salva progressivamente"""
        total = len(arquivos)
        total_salvos = 0
        
        for i in range(0, total, tamanho_lote):
            lote = arquivos[i:i + tamanho_lote]
            dados_lote = []
            
            for arquivo in lote:
                dado = self.extrair_conteudo_pdf(arquivo)
                if dado:
                    dados_lote.append(dado)
            
            if dados_lote:
                self.persistencia.salvar_novos(dados_lote)
                total_salvos += len(dados_lote)
        
        if total_salvos == 0:
            print("\nNenhum dado válido foi extraído.")