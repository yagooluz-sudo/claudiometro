# Como Instalar o Consumo do Claudinho

Widget de desktop para Windows que mostra seu consumo do Claude Code em tempo real.  
**Não precisa de permissão de administrador.**

---

## Passo 1 — Instalar o Python

> Se você já tem o Python instalado, pode pular para o Passo 2.

1. Acesse **https://www.python.org/downloads/**
2. Clique no botão amarelo grande **"Download Python 3.x.x"**
3. Abra o arquivo baixado
4. **IMPORTANTE:** Na primeira tela do instalador, marque a caixa **"Add python.exe to PATH"**  
   *(Se não marcar isso, o widget não vai funcionar)*
5. Clique em **"Install Now"**
6. Aguarde terminar e clique em **Close**

---

## Passo 2 — Instalar o widget

1. Abra a pasta **`widget`** (onde está este arquivo)
2. Dê um **duplo clique** no arquivo **`instalar.bat`**
3. Uma janela preta vai abrir — é normal
4. Quando perguntar **"Add to Windows Startup"** → digite `s` e Enter  
   *(isso faz o widget abrir automaticamente quando você liga o PC)*
5. Quando perguntar **"Launch the widget now"** → pressione Enter  
   *(o widget vai abrir na tela)*

Pronto! O widget vai aparecer no canto inferior direito da tela.

---

## Como usar

| Ação | Como fazer |
|------|-----------|
| Mover o widget | Clique e arraste pela barra do topo |
| Minimizar | Clique no **–** no canto superior direito — vai para a bandeja |
| Restaurar | Clique duas vezes no ícone na bandeja do sistema (perto do relógio) |
| Fechar de vez | Clique com botão direito no ícone da bandeja → **Sair** |
| Redimensionar | Arraste o **◢** no canto inferior direito |

O widget atualiza sozinho a cada 60 segundos.

---

## O que as barras significam

- **SESSÃO · 5H** — quanto do seu limite de 5 horas você já usou
- **SEMANAL · 7D** — quanto do seu limite semanal você já usou
- Cores: 🟢 normal → 🟡 atenção → 🔴 quase no limite → ❗ acima do limite

---

## Se o widget não aparecer

O widget pode ter aberto fora da tela. Para resolver:

1. Aperte **Win + R**, cole o caminho abaixo e pressione Enter:
   ```
   %USERPROFILE%\.config\claude-widget
   ```
2. Delete o arquivo **`position.json`**
3. Abra o widget de novo pelo ícone na bandeja ou por `instalar.bat`

---

## Requisitos

- Windows 10 ou 11
- Python 3.9 ou mais novo (gratuito em python.org)
- Claude Code instalado e logado na sua conta Anthropic
