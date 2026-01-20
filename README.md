# Desafio Técnico QCA

![logo qca](assets_readme/qca_logo.png)

## Automação Python de Leitura e Consulta de PDFs

### Construir uma Automação extraia dados de um PDF e retorne um “database.json”

> Extrair dados de um PDF e processar faturas do setor financeiro de uma empresa.

### Instruções de Instalação

*Como foi pedida uma versão do python inferior à atual, seguem os passos para instalação em qualquer máquina Windows e Linux*

```powershell
# Como instalar no Windows
# No Windows o processo é mais fácil

# Instale o Pyenv, caso não tenha a versão do python antiga

winget install pyenv-win

# Instale o python desejado (como no Linux)
pyenv install 3.13.11

# Use essa versão python
pyenv global 3.13.11

# Crie o venv para o projeto
python -m venv venv

# Para usar o venv no windows
venv\Scripts\Activate.ps1

# Verificar se está na versão correta
which python
python --version

# Para instalar as dependencias do projeto, ja no venv rode: (no Windows e Linux)
pip install -r requirements.txt
``` 

```bash
# Para o usar o python 3.13 no Linux projeto siga o tutorial:
# Garanta a instalação das dependencias
sudo apt update
sudo apt install -y \
  build-essential \
  libssl-dev \
  zlib1g-dev \
  libbz2-dev \
  libffi-dev \
  libreadline-dev \
  libsqlite3-dev \
  liblzma-dev \
  libncurses-dev \
  tk-dev \
  curl \
  git

# Instale o pyenv
curl https://pyenv.run | bash

# Edite o Bashrc
nano ~/.bashrc

# com essas linhas:
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# Reinicie o terminal e depois instale a versão do python 3.13
pyenv install 3.13.11

# Use a versão
pyenv local 3.13.11

# Crie um venv com esse Python
python -m venv venv

# Use o venv
source venv/bin/activate

# Verifique se o python está na versão desejada
which python
python --version
```
