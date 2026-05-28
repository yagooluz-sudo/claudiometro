# Clawdmeter

> **Este é um fork pessoal de [HermannBjorgvin/Clawdmeter](https://github.com/HermannBjorgvin/Clawdmeter).**
> Todo o crédito pelo conceito original, firmware, integração com hardware ESP32, protocolo BLE e
> animações pixel-art vai inteiramente para **Hermann Björgvin** ([@HermannBjorgvin](https://github.com/HermannBjorgvin)).
> Este fork adiciona um **widget de desktop para Windows** ("Consumo do Claudinho") sobre o projeto original.
> Não tem nenhuma finalidade comercial.

---

> ⚠️ **Aviso de licença (herdado do original):** Este repositório usa fontes proprietárias da Anthropic
> (Tiempos Text, Styrene B) e o mascote Clawd protegido por direitos autorais sem permissão explícita, exatamente
> como o projeto original faz. Nem este fork nem o original possuem licença para redistribuição ou uso comercial.
> Esteja ciente disso antes de fazer fork ou copiar qualquer código.

---

## O que este fork adiciona

### Widget de Desktop — "Consumo do Claudinho" (Windows)

Overlay flutuante always-on-top para Windows que exibe sua utilização de sessão (5h) e semanal (7d)
do Claude Code diretamente na área de trabalho — sem precisar de hardware ESP32.

- Animações pixel-art do Clawd que reagem ao seu uso (idle → work → dance)
- Duas barras de progresso com contagem regressiva para reset
- Suporte à bandeja do sistema, arraste para reposicionar, posição salva entre sessões
- Ícone gerado a partir dos assets pixel-art já existentes no repositório
- Totalmente em Português 🇧🇷

**Início rápido:**

```powershell
cd widget
.\install.ps1
```

Veja [`widget/`](widget/) para detalhes completos.

---

## 💛 Grande agradecimento ao criador original

Muito obrigado a **Hermann Björgvin** por construir e disponibilizar o Clawdmeter como open-source.
O projeto original é uma obra muito bem feita — a arquitetura do firmware, o protocolo BLE,
o motor de animações pixel-art e o daemon são todos dele.
Este fork não existiria sem ele. Dá uma estrela no original:
👉 **https://github.com/HermannBjorgvin/Clawdmeter**

---

Um pequeno dashboard ESP32 para a mesa, para acompanhar o uso do Claude Code.

Roda em um [Waveshare ESP32-S3-Touch-AMOLED-2.16](https://www.waveshare.com/esp32-s3-touch-amoled-2.16.htm?&aff_id=149786) e conecta ao laptop via Bluetooth. A tela splash exibe animações pixel-art do Clawd que ficam mais agitadas conforme o uso aumenta. Os dois botões laterais enviam Space e Shift+Tab via BLE HID para os atalhos de modo de voz e alternância de modo do Claude Code.

|              Medidor de uso              |              Tela de animação do Clawd              |
| :--------------------------------------: | :-------------------------------------------------: |
| ![Medidor de uso](assets/demo.jpeg) | ![Tela de animação do Clawd](assets/demo.gif) |

As animações do Clawd vêm do [claudepix](https://claudepix.vercel.app), a biblioteca de sprites pixel-art do [@amaanbuilds](https://x.com/amaanbuilds). Vale a pena conferir.

## Telas

O dispositivo inicia na splash e fica lá até você pressionar o botão do meio (PWR), que alterna entre Uso e Bluetooth. Toque na tela em qualquer lugar (exceto a zona de Reset na tela Bluetooth) para voltar à splash; toque novamente para dispensá-la.

|              Splash               |              Uso              |                Bluetooth                |
| :-------------------------------: | :---------------------------: | :-------------------------------------: |
| ![Splash](screenshots/splash.png) | ![Uso](screenshots/usage.png) | ![Bluetooth](screenshots/bluetooth.png) |
|   Splash; toggle por toque a qualquer hora    | Utilização da sessão e semanal  |    Status de conexão e reset de bond     |

Enquanto a splash está aberta, o botão do meio alterna animações em vez de telas. O firmware também faz rotação automática a cada 20s dentro do grupo de mood de uso atual.

## Hardware

Dois boards são suportados:

- [Waveshare ESP32-S3-Touch-AMOLED-2.16](https://www.waveshare.com/esp32-s3-touch-amoled-2.16.htm?&aff_id=149786) — ESP32-S3R8, AMOLED 2.16" 480×480 (CO5300 QSPI), toque capacitivo CST9220, PMU AXP2101 + Li-Po, IMU QMI8658. Três botões laterais, auto-rotação por IMU. Env de build: `waveshare_amoled_216`.
- [Waveshare ESP32-S3-Touch-AMOLED-1.8](https://www.waveshare.com/esp32-s3-touch-amoled-1.8.htm?&aff_id=149786) — ESP32-S3R8, AMOLED portrait 1.8" 368×448 (SH8601 QSPI), toque capacitivo FT3168, PMU AXP2101, IMU QMI8658, expansor IO XCA9554, 16 MB flash. Dois botões (BOOT + PWR), orientação fixa. Env de build: `waveshare_amoled_18`.

Além disso, para cada board:

- Cabo USB-C para gravar firmware e carregar
- Bateria Li-Po 3.7V (conector MX1.25 2 pinos, opcional)

**Portando para outro board:** o firmware tem uma HAL fina com pastas por board em `firmware/src/boards/`. Adicione uma nova pasta e um novo env do PlatformIO — `main.cpp`, `ui.cpp` e `splash.cpp` nunca precisam mudar. Veja [`docs/porting/adding-a-board.md`](docs/porting/adding-a-board.md) para o passo a passo e [`docs/porting/hal-contract.md`](docs/porting/hal-contract.md) para as interfaces que um port deve implementar.

## Pré-requisitos

- Linux (testado no Ubuntu) ou macOS
- [PlatformIO CLI](https://docs.platformio.org/en/latest/core/installation/index.html)
- Linux: `curl`, `bluetoothctl`, `busctl` (stack Bluetooth BlueZ)
- macOS: `python3` (o instalador configura um venv com `bleak` e `httpx`)
- Claude Code com assinatura ativa

## Instalação no macOS

As partes para host no macOS — daemon Python, LaunchAgent e helper de flash — foram portadas por [Chris Davidson (@lorddavidson)](https://github.com/lorddavidson). Valeu, Chris!

### Gravar o firmware

```bash
./flash-mac.sh                       # detecta automaticamente /dev/cu.usbmodem*
./flash-mac.sh /dev/cu.usbmodem1101  # ou passe uma porta USB serial explícita
```

### Parear o dispositivo

Após gravar, abra **Ajustes do Sistema → Bluetooth** e clique em *Conectar* ao lado de "Clawdmeter". O daemon vai descobri-lo no próximo scan (~30s).

### Instalar o daemon

O daemon lê seu token OAuth do Claude do Keychain do macOS (serviço `Claude Code-credentials`), faz polling de uso a cada 60s e envia para o display via BLE.

```bash
./install-mac.sh
```

O instalador cria um venv Python em `daemon/.venv/`, instala `bleak` e `httpx`, gera um LaunchAgent em `~/Library/LaunchAgents/com.user.claude-usage-daemon.plist` e o carrega. A primeira execução é lançada interativamente para que o macOS solicite permissão de Bluetooth.

Comandos úteis:

```bash
launchctl list | grep claude-usage                                          # verificar se está rodando
tail -F ~/Library/Logs/claude-usage-daemon.out.log                          # logs ao vivo
launchctl unload ~/Library/LaunchAgents/com.user.claude-usage-daemon.plist  # parar
launchctl load -w ~/Library/LaunchAgents/com.user.claude-usage-daemon.plist # iniciar
```

## Instalação no Linux

### Gravar o firmware

```bash
cd firmware
pio run -t upload --upload-port /dev/ttyACM0
```

### Parear o dispositivo

Após gravar, o dispositivo anuncia como "Claudemeter". Pareie uma vez:

```bash
# Escanear pelo dispositivo
bluetoothctl scan le

# Quando "Claude Controller" aparecer, parear e confiar
bluetoothctl pair F4:12:FA:C0:8F:E5    # use o MAC do seu dispositivo
bluetoothctl trust F4:12:FA:C0:8F:E5
```

O endereço MAC é mostrado na tela Bluetooth — pressione o botão do meio (PWR) para chegar lá.

### Instalar o daemon

O daemon faz polling do seu uso do Claude a cada 60 segundos e envia para o display via BLE.

```bash
./install.sh
systemctl --user start claude-usage-daemon
```

Verificar status: `systemctl --user status claude-usage-daemon`

Ver logs: `journalctl --user -u claude-usage-daemon -f`

## Como funciona

1. O daemon lê seu token OAuth do Claude Code de `~/.claude/.credentials.json`.
2. Faz uma chamada mínima à API em `api.anthropic.com/v1/messages` — um token de Haiku, praticamente de graça.
3. Os números de uso vêm diretamente dos headers de resposta (`anthropic-ratelimit-unified-5h-utilization` e similares).
4. O daemon conecta ao ESP32 via BLE e escreve um payload JSON na característica GATT RX.
5. O firmware o analisa e atualiza o dashboard LVGL.
6. O firmware também rastreia a taxa de variação da sessão % em uma janela de 5 minutos e escolhe animações splash do grupo de mood correspondente.
7. Os dois botões laterais são independentes de tudo isso — enviam Space e Shift+Tab como entrada de teclado BLE HID diretamente para o host pareado.

## Botões físicos

O board tem três botões laterais. Esquerdo e direito fazem a mesma coisa em qualquer tela; o botão do meio é consciente da tela atual.

| Botão            | GPIO         | Função                                                         |
| ---------------- | ------------ | -------------------------------------------------------------- |
| **Esquerdo**     | GPIO 0       | Segurar para enviar Space (push-to-talk do modo de voz do Claude Code) |
| **Meio** (PWR)   | AXP2101 PKEY | Alterna telas (Uso ↔ Bluetooth); na splash, alterna animações |
| **Direito**      | GPIO 18      | Pressionar para enviar Shift+Tab (alternância de modo do Claude Code) |

Space e Shift+Tab saem como relatórios padrão de teclado BLE HID, então acionam na janela que tiver foco no host pareado — não apenas no Claude Code.

## Protocolo BLE

O dispositivo anuncia um serviço GATT customizado junto com o serviço padrão de teclado HID:

|                            | UUID                                   |
| -------------------------- | -------------------------------------- |
| **Data Service**           | `4c41555a-4465-7669-6365-000000000001` |
| Característica RX (escrita)  | `4c41555a-4465-7669-6365-000000000002` |
| Característica TX (notify) | `4c41555a-4465-7669-6365-000000000003` |
| **HID Service**            | `00001812-0000-1000-8000-00805f9b34fb` |

Formato do payload JSON (escrito no RX):

```json
{ "s": 45, "sr": 120, "w": 28, "wr": 7200, "st": "allowed", "ok": true }
```

Campos: `s` = sessão %, `sr` = reset da sessão (minutos), `w` = semanal %, `wr` = reset semanal (minutos), `st` = status, `ok` = flag de sucesso.

## Recompilando fontes

Os arquivos `firmware/src/font_*.c` são fontes bitmap LVGL pré-compiladas.

```bash
npm install -g lv_font_conv
```

Gere cada uma (uma de cada vez — `lv_font_conv` não gosta de invocações em loop) com `--no-compress` (necessário para LVGL 9):

```bash
# Tiempos Text (títulos, 56px)
lv_font_conv --font assets/TiemposText-400-Regular.otf -r 0x20-0x7E \
  --size 56 --format lvgl --bpp 4 --no-compress \
  -o firmware/src/font_tiempos_56.c --lv-include "lvgl.h"

# Styrene B (números grandes 48, labels de painel 28, texto pequeno 24, mínimo 20)
for size in 48 28 24 20; do
  lv_font_conv --font assets/StyreneB-Regular.otf -r 0x20-0x7E \
    --size $size --format lvgl --bpp 4 --no-compress \
    -o firmware/src/font_styrene_${size}.c --lv-include "lvgl.h"
done

# DejaVu Sans Mono (32px, com chars Unicode de spinner)
lv_font_conv --font assets/DejaVuSansMono.ttf \
  -r 0x20-0x7E,0xB7,0x2026,0x2722,0x2733,0x2736,0x273B,0x273D \
  --size 32 --format lvgl --bpp 4 --no-compress \
  -o firmware/src/font_mono_32.c --lv-include "lvgl.h"
```

**Importante:** `lv_font_conv` v1.5.3 gera formato LVGL 8. Cada arquivo gerado precisa ser corrigido para compatibilidade com LVGL 9:

1. Remover as guards `#if LVGL_VERSION_MAJOR >= 8` em volta de `font_dsc` e da struct da fonte
2. Remover o campo `.cache` de `font_dsc`
3. Adicionar `.release_glyph = NULL`, `.kerning = 0`, `.static_bitmap = 0` à struct da fonte
4. Adicionar `.fallback = NULL`, `.user_data = NULL` à struct da fonte

Sem essas correções, as fontes compilam mas renderizam invisíveis.

## Convertendo ícones Lucide

A UI usa um pequeno conjunto de ícones [Lucide](https://lucide.dev) (bluetooth + estados de bateria) convertidos para arrays C RGB565 / RGB565A8 para LVGL.

```bash
node tools/png_to_lvgl.js assets/icon_bluetooth_48.png icon_bluetooth_data ICON_BLUETOOTH_WIDTH ICON_BLUETOOTH_HEIGHT
```

O tint padrão é branco (`0xFFFFFF`); PNGs do Lucide são preto-sobre-transparente e ficariam invisíveis na UI escura sem ele. Passe `--no-tint` para artwork já colorido como o logo. Ícones de bateria usam RGB565A8 (plano alpha) para misturar limpo sobre a splash; o resto é RGB565 simples sobre a cor do painel. Cole o output do conversor em `firmware/src/icons.h`.

## Animações splash

As animações vêm de [claudepix.vercel.app](https://claudepix.vercel.app),
uma biblioteca de sprites do Clawd. `tools/scrape_claudepix.js` avalia o
JavaScript do site em uma VM Node para extrair dados de frames e paletas, então
`tools/convert_to_c.js` transforma tudo em arrays C RGB565 e escreve
`firmware/src/splash_animations.h`.

Para baixar novamente (ex: quando a biblioteca fonte atualiza):

```bash
node tools/scrape_claudepix.js
node tools/convert_to_c.js
pio run -d firmware -t upload
```

Veja `tools/README.md` para detalhes.

## Créditos

- Animações pixel-art do Clawd por [@amaanbuilds](https://x.com/amaanbuilds), extraídas de [claudepix.vercel.app](https://claudepix.vercel.app). Dados de frames e paletas scrapeados + convertidos pelas ferramentas em `tools/`.
- Set de ícones Lucide ([lucide.dev](https://lucide.dev), MIT) para glifos de bluetooth e bateria na UI.
- Fontes de marca Anthropic (Tiempos Text, Styrene B) — veja aviso de licença abaixo.

## Aviso de área cinzenta de licenciamento

O software neste repositório usa e adere às diretrizes de marca da Anthropic e utiliza as mesmas fontes proprietárias que a Anthropic possui licença, mas que este software usa sem permissão, além de usar assets da Anthropic como o mascote Clawd protegido por direitos autorais. Portanto, embora o código neste repositório não seja proprietário, não vou licenciá-lo sob uma licença copyleft já que este repositório inclui fontes proprietárias e assets com direitos autorais. Esteja ciente disso se fizer fork ou copiar o código deste repositório. **Você foi avisado!**
