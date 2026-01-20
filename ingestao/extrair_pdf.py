import re  
import json  
import pdfplumber  
from pathlib import Path
from decimal import Decimal
from pydantic import BaseModel, Field, ValidationError
from typing import Optional
from datetime import date


class Produto(BaseModel):
    """Validar cada item do pedido"""
    Nome_Produto: str = Field(..., min_length=1)
    Quantidade: int = Field(..., gt=0)
    Preco_Unitario: Decimal = Field(..., gt=0, decimal_places=2)


class Pedido(BaseModel):
    """Validar o pedido"""
    ID_Pedido: str = Field(..., min_length=1)
    Data:  date  
    ID_Cliente: str = Field(..., min_length=1)
    Tabela_Itens: list[Produto] = Field(..., min_length=1)


class ExtrairPDF:  
    """Extrai dados de PDFs de pedidos e salva em JSON"""
    
    def __init__(self, caminho_pasta: Path):
        """Recebe o caminho da pasta onde estão os PDFs"""
        self.caminho_pasta = caminho_pasta
        
    def extrair_dados_do_texto(self, texto: str) -> dict:
        """Lê o texto do PDF e retorna:  ID do pedido, data, cliente e lista de produtos"""
        dados_extraidos = {}

        # Retorna a Order ID
        pedido = re.search(r"Order ID:\s*(\d+)", texto)
        
        # Retorna a Order Date
        data = re.search(r"Order Date:\s*([\d\-]+)", texto)
        
        # Procura a Customer ID
        cliente = re.search(r"Customer ID:\s*(\w+)", texto)

        # Se encontrou salvamos o valor, se não, não salva
        dados_extraidos["ID_Pedido"] = pedido.group(1) if pedido else None
        dados_extraidos["Data"] = data.group(1) if data else None
        dados_extraidos["ID_Cliente"] = cliente.group(1) if cliente else None

        # Agora extrair a tabela de produtos
        linhas_texto = texto.splitlines()
        tabela_produtos = []
        capturou = False  # Quando começamos a ler os produtos

        for linha in linhas_texto:    
            # Quando achar Product Details, começa a capturar
            if "Product Details:" in linha:
                capturou = True
                continue

            if capturou:
                # Pula o cabeçalho da tabela 
                if re.match(r"Product ID", linha):
                    continue
                    
                # E para quando chegar no total
                if "TotalPrice" in linha or "Total Price" in linha: 
                    break

                # Serve para capturar os valores do nome, quantidade, preço_unitario pelo regex
                produto_match = re.match(r"\d+\s+(.+?)\s+(\d+)\s+([\d.]+)", linha)
                
                if produto_match:
                    nome_produto, quantidade, preco_unitario = produto_match.groups()
                    
                    tabela_produtos.append({
                        "Nome_Produto": nome_produto,
                        "Quantidade": int(quantidade),
                        "Preco_Unitario": Decimal(preco_unitario)  # Convertido para Decimal
                    })
                else:
                    # Log para debug de linhas não capturadas
                    linha_limpa = linha
                    if linha_limpa:  # Ignora linhas vazias
                        pass  # Descomente para debug:  print(f"  [DEBUG] Linha ignorada: {linha}")

        dados_extraidos["Tabela_Itens"] = tabela_produtos
        return dados_extraidos
        
    def validar_dados(self, dados: dict, arquivo:  str = "") -> Optional[Pedido]:
        """Valida os dados extraídos"""
        # Verifica campos obrigatórios
        campos_faltando = []
        if not dados.get("ID_Pedido"):
            campos_faltando.append("ID_Pedido")
        if not dados. get("Data"):
            campos_faltando.append("Data")
        if not dados.get("ID_Cliente"):
            campos_faltando.append("ID_Cliente")
        if not dados.get("Tabela_Itens"):
            campos_faltando.append("Tabela_Itens")
        
        if campos_faltando:
            print(f"{arquivo}: Campos obrigatórios faltando:  {', '.join(campos_faltando)}")
            return None
        
        try:
            pedido_validado = Pedido(**dados)
            print(f"{arquivo}: Validado.")
            return pedido_validado
        except ValidationError as e:
            print(f"{arquivo}:  Erro na validação:")
            for erro in e.errors():
                campo = ' -> '.join(str(loc) for loc in erro['loc'])
                print(f"  - Campo '{campo}': {erro['msg']}")
            return None

    def extrair_conteudo_pdf(self, caminho_pdf: Path) -> Optional[dict]:
        """Abre o(s) PDF(s), junta o texto de todas as páginas e extrai os dados"""
        with pdfplumber.open(caminho_pdf) as pdf:
            texto_completo = ""
            
            for pagina in pdf.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:  
                    texto_completo += texto_pagina + "\n"

        dados_brutos = self.extrair_dados_do_texto(texto_completo)
        
        # Validar antes de retornar
        pedido_validado = self.validar_dados(dados_brutos, caminho_pdf.name)
        if pedido_validado:
            return pedido_validado. model_dump()
        return None
    
    def listar_arquivos_pdf(self) -> list[Path]:
        """Retorna uma lista com todos os PDFs da pasta"""
        return list(self.caminho_pasta.glob("*.pdf"))
    
    def salvar_em_json(self, lista_dados: list[dict], nome_arquivo_saida: str = "database.json") -> None:
        """Salva os dados no arquivo database.json"""
        caminho_saida = Path("..") / nome_arquivo_saida
        
        # Carrega os dados existentes
        if caminho_saida.exists():
            with open(caminho_saida, "r", encoding="utf-8") as arquivo:
                try:
                    dados_existentes = json.load(arquivo)
                except json.JSONDecodeError:
                    dados_existentes = [] 
        else:  
            dados_existentes = []
        
        # Cria um conjunto com os IDs já existentes
        ids_existentes = {pedido["ID_Pedido"] for pedido in dados_existentes if "ID_Pedido" in pedido}
        
        # Filtra apenas os dados que não são duplicados
        dados_novos = []
        duplicados = 0
        
        for dado in lista_dados:
            if dado and dado.get("ID_Pedido") not in ids_existentes: 
                dados_novos.append(dado)
                ids_existentes.add(dado["ID_Pedido"])  # Evita duplicidade
            else:
                duplicados += 1
        
        if duplicados > 0:
            print(f"\n{duplicados} pedido(s) ignorado(s) por duplicidade.")
        
        if not dados_novos:
            print("Nenhum dado novo para salvar.")
            return
        
        # Junta os novos dados com os existentes
        dados_existentes.extend(dados_novos)
        
        # Salva tudo no arquivo
        with open(caminho_saida, "w", encoding="utf-8") as arquivo:
            json.dump(dados_existentes, arquivo, ensure_ascii=False, indent=2, default=str)
        
        print(f"{len(dados_novos)} pedido(s) salvo(s) com sucesso em '{caminho_saida}'.")

    def extrair_arquivo_unico(self, nome_arquivo: str) -> None:
        """Extrai apenas um PDF pelo nome do arquivo"""
        caminho_arquivo = self.caminho_pasta / nome_arquivo
        
        if not caminho_arquivo.exists():
            print(f"Arquivo '{nome_arquivo}' não encontrado.")
            return
        
        print(f"\nProcessando: {nome_arquivo}...")
        dados_extraidos = self.extrair_conteudo_pdf(caminho_arquivo)
        
        if dados_extraidos: 
            self.salvar_em_json([dados_extraidos])
        else:
            print(f"Nenhum dado válido extraído de '{nome_arquivo}'.")
    
    def extrair_multiplos_arquivos(self, numero_de_arquivos: int) -> None:
        """Extrai uma quantidade específica de PDFs"""
        arquivos_pdf = self.listar_arquivos_pdf()
        
        if not arquivos_pdf:  
            print("Nenhum arquivo PDF encontrado.")
            return
        
        arquivos_para_processar = min(max(numero_de_arquivos, 1), len(arquivos_pdf))
        
        print(f"\nProcessando {arquivos_para_processar} de {len(arquivos_pdf)} arquivo(s)...\n")
        
        todos_dados_extraidos = []
        
        for arquivo_pdf in arquivos_pdf[:arquivos_para_processar]:    
            print(f"Processando: {arquivo_pdf.name}...")
            dados = self.extrair_conteudo_pdf(arquivo_pdf)
            if dados:  # Só adiciona se passou na validação
                todos_dados_extraidos.append(dados)

        if todos_dados_extraidos: 
            self.salvar_em_json(todos_dados_extraidos)
        else:
            print("\nNenhum dado válido foi extraído.")
    
    def extrair_todos_arquivos(self) -> None:
        """Extrai todos os PDFs da pasta"""
        arquivos_pdf = self.listar_arquivos_pdf()
        
        if not arquivos_pdf: 
            print("Nenhum arquivo PDF encontrado.")
            return
        
        print(f"\nProcessando {len(arquivos_pdf)} arquivo(s) PDF...\n")
        
        todos_dados_extraidos = []
        
        for arquivo_pdf in arquivos_pdf:  
            print(f"Processando: {arquivo_pdf.name}")
            dados = self.extrair_conteudo_pdf(arquivo_pdf)
            if dados:  # Só adiciona se passou na validação
                todos_dados_extraidos. append(dados)

        if todos_dados_extraidos:
            self.salvar_em_json(todos_dados_extraidos)
        else:
            print("\nNenhum dado válido foi extraído.")


def main():
    extrator = ExtrairPDF(Path("../invoices"))

    opcao_usuario = input(
        "\n"
        "EXTRATOR DE PDFs\n"
        "\n"
        ">   1 - Extrair um PDF específico\n"
        ">   2 - Extrair uma quantidade de PDFs\n"
        ">   3 - Extrair todos os PDFs\n"
        "\n"
        "Opção: "
    ) 
    
    match opcao_usuario:
        case '1': 
            nome_arquivo_pdf = input("\n> Nome do arquivo PDF:  ")
            extrator.extrair_arquivo_unico(nome_arquivo_pdf)
            
        case '2': 
            arquivos_pdf = extrator.listar_arquivos_pdf()
            print(f"\nEncontrado(s) {len(arquivos_pdf)} arquivo(s) PDF")
            
            try: 
                quantidade = int(input("Quantos deseja processar? "))
                extrator.extrair_multiplos_arquivos(quantidade)
            except ValueError:  
                print("Número inválido.")
                
        case '3': 
            extrator.extrair_todos_arquivos()
            
        case _:  
            print("Opção inválida")


if __name__ == "__main__": 
    main()