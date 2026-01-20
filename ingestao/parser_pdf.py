import re
from decimal import Decimal


class ParserPDF:
    """Extrair somente os dados que queremos pelo regex"""
    
    def extrair(self, texto: str) -> dict:
        """Retorna: ID do pedido, Data, Cliente e Lista de produtos"""
        dados = {}
        
        # Captura o texto que queremos
        pedido = re.search(r"Order ID:\s*(\d+)", texto) 
        data = re.search(r"Order Date:\s*([\d\-]+)", texto)
        cliente = re.search(r"Customer ID:\s*(\w+)", texto)
        
        dados["ID_Pedido"] = pedido.group(1) if pedido else None
        dados["Data"] = data.group(1) if data else None
        dados["ID_Cliente"] = cliente.group(1) if cliente else None
        dados["Tabela_Itens"] = self._extrair_produtos(texto)
        
        return dados
    
    def _extrair_produtos(self, texto: str) -> list[dict]:
        """Extrai a Tabela: com Nome do Produto, Quantidade e preço"""
        produtos = []
        capturou = False
        
        for linha in texto.splitlines():
            if "Product Details:" in linha:
                capturou = True
                continue
            
            if not capturou:
                continue
            
            if re.match(r"Product ID", linha):
                continue
            
            if "TotalPrice" in linha or "Total Price" in linha:
                break
            
            match = re.match(r"\d+\s+(.+?)\s+(\d+)\s+([\d.]+)", linha)
            if match:
                nome, qtd, preco = match.groups()
                produtos.append({
                    "Nome_Produto": nome,
                    "Quantidade": int(qtd),
                    "Preco_Unitario": Decimal(preco)
                })
        
        return produtos
