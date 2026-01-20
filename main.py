from pathlib import Path
from ingestao.extrair_pdf import ExtrairPDF
from consulta.consulta import ConsultaPDF


def exibir_menu_principal():
    """Primeiro menu que aparece no programa"""
    print("Você deseja:")

    print(">   1) Extrair dados de PDFs") # /ingestao/
    print(">   ou")
    print(">   2) Consultar dados de PDFs") # consulta.py
    print(">   ou")
    print(">   0) Sair")

def menu_ingestao():
    """Menu de Ingestão de Dados"""
    extrator = ExtrairPDF(Path("invoices"))
    
    print("\n\n\n\n\n\n\n\nEXTRAÇÃO DE PDFs")

    print(">   1) Somente um PDF específico")
    print(">   2) Uma quantidade de PDFs")
    print(">   3) Todos os PDFs")
    print(">   0) Voltar")

    
    opcao = input("Escolha uma opção: ")
    
    match opcao:
        case "1": # Menu de escolha de um PDF
            nome_arquivo = input("\nNome do PDF: ")
            extrator.extrair_arquivo_unico(nome_arquivo)
            print("\n")
            aguardar_continuar()
        
        case "2": # Menu de escolha de uma quantidade de PDFs
            arquivos_pdf = extrator.leitor.listar_arquivos_pdf()
            print(f"\nEncontrou-se {len(arquivos_pdf)} PDF(s) na pasta")
            try:
                quantidade = int(input("Quantos PDFs processar? "))
                extrator.extrair_multiplos_arquivos(quantidade)
            except ValueError:
                print("Número inválido.")
            aguardar_continuar()
        
        case "3": # Menu de ingestão de todos os PDFs
            extrator.extrair_todos_arquivos()
            aguardar_continuar()
        
        case "0": # Menu de Saída
            return
        
        case _: # Menu de Erros
            print("Opção inválida!")
            aguardar_continuar()


def menu_consulta():
    """Menu de Consulta de Dados"""
    caminho_db = Path("database.json")
    
    if not caminho_db.exists():
        print("\nO Arquivo 'database.json' não foi encontrado!")
        print("> Você precisa extrair dados de um PDF primeiro!")
        aguardar_continuar()
        return
    
    consulta = ConsultaPDF(str(caminho_db))
    consulta.executar_menu()


def main():
    """Menu de Escolha entre os dois programas"""
    while True:
        exibir_menu_principal()
        opcao = input("Escolha uma opção: ")
        
        match opcao:
            case "1":
                menu_ingestao()
            
            case "2":
                menu_consulta()
            
            case "0":
                print("Encerrando o sistema...")
                break
            
            case _:
                print("Opção inválida!")
                aguardar_continuar()

def aguardar_continuar():
    """Método para o programa esperar o usuário para continuar"""
    input("\nPressione Enter para continuar... ")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrograma interrompido pelo usuário.") # Para caso o usuário interrompa com o CTRL + C