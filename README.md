# Mini-sistema solar 2D — INF1761

Projeto 1 da disciplina de Computação Gráfica (INF1761). A aplicação usa WebGPU e um grafo de cena para representar e animar o Sol, a Terra, a Lua e Mercúrio, com texturas e fundo espacial.

## Requisitos

- Python 3.10 ou superior;
- uma GPU e drivers gráficos compatíveis com o `wgpu`.

## Instalação

Na raiz do repositório, crie e ative um ambiente virtual.

No Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

No Linux ou macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Execução

Com o ambiente virtual ativo, execute:

```bash
python projeto1.py
```

Uma janela de 800 × 800 pixels será aberta e a animação começará automaticamente. Para encerrar, feche a janela.
