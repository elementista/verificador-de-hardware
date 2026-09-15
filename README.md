# 🛠️ Verificador de Hardware por Elementista

Um utilitário portátil, leve e multiplataforma desenvolvido em Python para auxiliar técnicos em manutenção de computadores no diagnóstico rápido de componentes diretamente na bancada.

---

## 🚀 Funcionalidades Principais

- **Diagnóstico Multiplataforma:** Coleta informações de hardware tanto no Windows quanto no Linux usando rotas nativas e seguras.
- **Mapeamento da Linha do Tempo:** Estima o ano aproximado de lançamento do processador e da placa-mãe (com base na data de firmware da BIOS).
- **Análise Inteligente de CPU (Instruções):** Checa a presença de instruções como AVX e AVX2 para recomendar o melhor Kernel Linux atual para a máquina.
- **Suporte a Sistemas Legados:** Identifica computadores antigos (ex: Dual Core com 2GB de RAM DDR1/DDR2) e sugere distribuições e interfaces ultra-leves (como AntiX, Puppy Linux, IceWM, LXDE).
- **Emissão de Relatório:** Opção de salvar o diagnóstico completo em um arquivo de texto (.txt) para a Ordem de Serviço do cliente.

---

## 📦 Como Executar os Arquivos Portáteis

Os executáveis prontos para uso (sem necessidade de instalar o Python) estão disponíveis na aba **Releases** deste repositório.

### 🐧 No Linux (LiveCD ou Sistema Instalado)
1. Baixe o arquivo `DiagnosticoBancada.AppImage`.
2. Clique com o botão direito no arquivo, vá em **Propriedades > Permissões** e marque a caixa *"Permitir executar este arquivo como um programa"*.
3. Dê dois cliques para rodar. Uma janela de terminal se abrirá automaticamente com o painel técnico.

### 💻 No Windows (7, 10 ou 11)
1. Baixe o arquivo `DiagnosticoBancadaWin.exe`.
2. Dê dois cliques para rodar diretamente (Não requer instalação).

---

## 🛠️ Tecnologias Utilizadas
- **Linguagem:** Python 3
- **Bibliotecas:** `psutil`, `platform`, `subprocess`, `os`, `datetime`
- **Empacotadores:** PyInstaller (com Wine para cross-compilation no Linux) e AppImageKit.

---
_Desenvolvido por **Elementista**_
