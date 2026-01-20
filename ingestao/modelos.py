from decimal import Decimal
from datetime import date
from pydantic import BaseModel, Field

# Modelos do Pydantic: Validam os dados do json antes de salvar

class Produto(BaseModel):
    """Valida a Tabela de Itens: Product Details"""
    Nome_Produto: str = Field(..., min_length=1) # String com pelo menos um char
    Quantidade: int = Field(..., gt=0) # Um inteiro maior que 0
    Preco_Unitario: Decimal = Field(..., gt=0, decimal_places=2) # Decimal maior que 0, com 2 casas decimais

class Pedido(BaseModel):
    """Valida o Customer Details"""
    ID_Pedido: str = Field(..., min_length=1) # String com pelo menos um char
    Data: date # Data
    ID_Cliente: str = Field(..., min_length=1) # String com pelo menos um char
    Tabela_Itens: list[Produto] = Field(..., min_length=1) # Lista com pelo menos 1 produto da classe Produto