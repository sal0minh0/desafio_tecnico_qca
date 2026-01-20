import json
from pathlib import Path


class SalvarJSON:
    """Salva os dados no database.json"""
    
    def __init__(self, caminho_saida: Path = Path(__file__).parent.parent / "database.json"):
        self.caminho_saida = caminho_saida
    
    def carregar(self) -> list[dict]:
        """Carrega dados existentes do arquivo"""
        if not self.caminho_saida.exists():
            return []
        
        with open(self.caminho_saida, "r", encoding="utf-8") as arquivo:
            try:
                return json.load(arquivo)
            except json.JSONDecodeError:
                return []
    
    def salvar(self, dados: list[dict]) -> None:
        """Salva dados no arquivo"""
        with open(self.caminho_saida, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2, default=str)
    
    def salvar_novos(self, lista_dados: list[dict]) -> None:
        """Salva apenas dados novos, evitando dados que já existem"""
        dados_existentes = self.carregar()
        ids_existentes = {p["ID_Pedido"] for p in dados_existentes if "ID_Pedido" in p}
        
        dados_novos = []
        duplicados = 0
        
        for dado in lista_dados:
            if dado and dado.get("ID_Pedido") not in ids_existentes:
                dados_novos.append(dado)
                ids_existentes.add(dado["ID_Pedido"])
            else:
                duplicados += 1
        
        if duplicados > 0:
            print(f"\n...Ignoramos {duplicados} PDF(s), já existem no JSON.")
        
        if not dados_novos:
            print("Não há dados novos para salvar.")
            return
        
        dados_existentes.extend(dados_novos)
        self.salvar(dados_existentes)
        print(f"{len(dados_novos)} dado(s) de PDF(s) salvo(s).") # Salva automaticamente os PDFs, caso você queira interromper o programa
