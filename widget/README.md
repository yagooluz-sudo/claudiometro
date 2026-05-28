# Consumo do Claudinho — Widget de Desktop (Windows)

Widget flutuante always-on-top para Windows que exibe o consumo da sua sessão (5h)
e semanal (7d) do Claude Code — sem precisar de hardware ESP32.

Construído sobre o [HermannBjorgvin/Clawdmeter](https://github.com/HermannBjorgvin/Clawdmeter).
Todo o crédito pelo projeto original vai ao seu criador.

![Prévia do widget](../assets/demo.jpeg)

## Funcionalidades

- Animações pixel-art do Clawd vindas de [claudepix.vercel.app](https://claudepix.vercel.app) que reagem ao seu uso:
  - **0–39%** → idle (pisca, respira, olha ao redor)
  - **40–69%** → work (codando, pensando)
  - **70–100%** → dance (bounce, sway, djmix…)
- Duas barras de progresso: **SESSÃO · 5H** e **SEMANAL · 7D** com contagem regressiva para reset
- Cores que mudam de verde → âmbar → vermelho conforme o uso aumenta
- Cantos arredondados transparentes (raio de 12px)
- Ícone na bandeja do sistema com badge de % ao vivo — minimiza e restaura pela bandeja
- Arraste para reposicionar; posição salva entre sessões
- Atualiza automaticamente a cada 60s usando suas credenciais do Claude Code

## Requisitos

- Windows 10/11
- Python 3.9+
- Claude Code instalado e logado (credenciais lidas de `~/.claude/.credentials.json`)

## Instalação

```powershell
cd widget
.\install.ps1
```

O instalador vai:
1. Criar um venv Python em `widget/.venv`
2. Instalar dependências (`httpx`, `pystray`, `Pillow`)
3. Perguntar se quer atalho na Inicialização do Windows (auto-iniciar no login)
4. Opcionalmente abrir o widget imediatamente

## Executar manualmente

```powershell
# Da pasta widget/
.\.venv\Scripts\pythonw.exe claude_widget.py
```

Use `pythonw.exe` (não `python.exe`) para rodar sem janela de console.

## Isso aumenta o consumo do Claude?

Tecnicamente sim, mas de forma negligenciável. A cada 60 segundos o widget faz uma chamada
à API para o `claude-haiku-4-5-20251001` com `max_tokens: 1` — o objetivo são os
headers de rate-limit na resposta, não a resposta em si. O projeto original descreve isso
como *"um token de Haiku, praticamente de graça"*.

## Créditos

- Projeto original, firmware, protocolo BLE, daemon e pipeline de animações: **Hermann Björgvin** — https://github.com/HermannBjorgvin/Clawdmeter
- Sprites pixel-art do Clawd: **[@amaanbuilds](https://x.com/amaanbuilds)** — https://claudepix.vercel.app
- Widget de desktop (esta pasta): fork pessoal, sem fins comerciais
