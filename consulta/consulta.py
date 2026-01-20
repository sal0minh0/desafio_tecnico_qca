import pandas as pd
import json

class ConsultaPDF:
    """Método Principal da Consulta dos PDFs
    Operações: 
       - Media das Faturas; 
       - Produto mais vendido; 
       - Valor Total Gasto em cada Produto; 
       - Lista de Produtos (Nome e Preço).
    """
    def __init__(self, caminho_arquivo: str):
        self.caminho_arquivo = caminho_arquivo
        self.df = self._carregar_dados()
    
    def _carregar_dados(self) -> pd.DataFrame:
        """Carregar os todos os dados contido no JSON com o Pandas"""
        with open(self.caminho_arquivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        itens_list = []
        for pedido in data:
            for item in pedido['Tabela_Itens']:
                itens_list.append({
                    'ID_Pedido': pedido['ID_Pedido'],
                    'Data': pedido['Data'],
                    'ID_Cliente': pedido['ID_Cliente'],
                    'Nome_Produto': item['Nome_Produto'],
                    'Quantidade': item['Quantidade'],
                    'Preco_Unitario': float(item['Preco_Unitario'])
                })
        
        df = pd.DataFrame(itens_list)
        df['Valor_Total_Item'] = df['Quantidade'] * df['Preco_Unitario']
        return df
    
    def media_do_valor_total_das_faturas(self) -> float:
        """Calcula a média do valor total de todas as faturas"""
        valor_total_por_fatura = self.df.groupby('ID_Pedido')['Valor_Total_Item'].sum()
        return valor_total_por_fatura.mean()
    
    def o_produto_com_maior_frequencia_de_compra(self) -> tuple:
        """Verifica qual Produto foi o mais vendido"""
        frequencia = self.df['Nome_Produto'].value_counts()
        return frequencia.idxmax(), frequencia.max()
    
    def valor_total_gasto_por_cada_produto(self) -> pd.Series:
        """Retorna o valor total gasto em cada produto"""
        return self.df.groupby('Nome_Produto')['Valor_Total_Item'].sum().sort_values(ascending=False)
    
    def listagem_produtos_contendo_nome_e_preco_unitario(self) -> pd.DataFrame:
        """Retorna uma Lista contendo Nome do produto e seu Preço"""
        return self.df[['Nome_Produto', 'Preco_Unitario']].drop_duplicates().sort_values('Nome_Produto')
    
    def exibir_resultados(self):
        """Exibir a análise completa de uma vez"""
        print("ANÁLISE DA CONSULTA")

        print("\n1. MÉDIA DO VALOR TOTAL DAS FATURAS:")
        print(f"   R$ {self.media_do_valor_total_das_faturas():.2f}")
        
        print("\n2. PRODUTO COM MAIOR FREQUÊNCIA DE COMPRA:")
        produto, freq = self.o_produto_com_maior_frequencia_de_compra()
        print(f"   {produto} ({freq} ocorrências)")
        
        print("\n3. VALOR TOTAL GASTO POR CADA PRODUTO:")
        for produto, valor in self.valor_total_gasto_por_cada_produto().items():
            print(f"   {produto}: R$ {valor:.2f}")
        
        print("\n4. LISTA DE PRODUTOS (NOME E PREÇO UNITÁRIO):")
        for _, row in self.listagem_produtos_contendo_nome_e_preco_unitario().iterrows():
            print(f"   {row['Nome_Produto']}: R$ {row['Preco_Unitario']:.2f}")
        
    
    def exibir_menu(self):

        print("\n\n\n\n\n\n\n\nMENU DE CONSULTAS")

        print("1) Exibir a Análise Completa")
        print("ou separadamente:\n")
        print("2) Exibir somente a Média do total das faturas")
        print("3) Exibir somente o Produto mais vendido")
        print("4) Exibir somente o Valor total gasto por cada produto")
        print("5) Exibir somente a Listagem de produtos contendo Nome e seu Preço")
        
        print("0) Sair")

    
    def _aguardar_continuar(self):
        """Método para o programa esperar o usuário para continuar"""
        input("\nPressione Enter para continuar...")
    
    def executar_menu(self):
        while True:
            self.exibir_menu()
            opcao = input("Escolha uma opção: ")
            
            match opcao:
                
                case "1":
                    self.exibir_resultados()
                    self._aguardar_continuar()
                    
                case "2":
                    print("\n--- MÉDIA DO VALOR TOTAL DAS FATURAS ---")
                    print(f"R$ {self.media_do_valor_total_das_faturas():.2f}")
                    self._aguardar_continuar()
                
                case "3":
                    print("\n--- PRODUTO COM MAIOR FREQUÊNCIA DE COMPRA ---")
                    produto, freq = self.o_produto_com_maior_frequencia_de_compra()
                    print(f"{produto} ({freq} ocorrências)")
                    self._aguardar_continuar()
                
                case "4":
                    print("\n--- VALOR TOTAL GASTO POR CADA PRODUTO ---")
                    for produto, valor in self.valor_total_gasto_por_cada_produto().items():
                        print(f"{produto}: R$ {valor:.2f}")
                    self._aguardar_continuar()
                
                case "5":
                    print("\n--- LISTAGEM DE PRODUTOS (NOME E PREÇO UNITÁRIO) ---")
                    for _, row in self.listagem_produtos_contendo_nome_e_preco_unitario().iterrows():
                        print(f"{row['Nome_Produto']}: R$ {row['Preco_Unitario']:.2f}")
                    self._aguardar_continuar()
                
                case "0":
                    print("Saindo...\n")
                    break
                
                case _:
                    print("Opção inválida! Tente novamente.")
                    self._aguardar_continuar()
