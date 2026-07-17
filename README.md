# Júpiter Product Design Flow

Workflow de design de produto para Hermes e outros agentes compatíveis com `SKILL.md`.

Ele adapta o melhor mecanismo do projeto `julianoczkowski/designer-skills` ao stack operacional da Júpiter:

- menos cerimônia e mais autonomia;
- brandbook antes de preferência estética;
- reutilização obrigatória de tokens e componentes;
- arquitetura da informação somente quando a complexidade exige;
- implementação real, não apenas documentação;
- revisão visual com screenshots e evidências;
- memória persistente por feature em `.design/<feature>/`.
- produção de carrossel editorial Júpiter com copy, imagem, HTML, PNG e ZIP.

## Instalação no Hermes

Copie o conteúdo deste repositório para:

```text
~/.hermes/skills/business/jupiter-product-design-flow/
```

Ou use o gerenciador de skills do Hermes para criar a skill e seus arquivos vinculados.

## Estrutura

```text
SKILL.md
references/
├── artifact-contract.md
├── brand-routing.md
├── carousel-copy-modes.md
├── carousel-production.md
└── qa-matrix.md
scripts/
├── export_carousel.py
├── render_carousel.mjs
└── validate_design_flow.py
templates/
└── carousel-starter.html
tests/
└── playwright_smoke.py
package.json
package-lock.json
pyproject.toml
requirements.txt
```

## Ambiente reproduzível

Use Python 3.11 ou 3.12 e o Node 22 indicado pela CI. As versões de Pillow e Playwright estão fixadas nos manifests; `package-lock.json` preserva a árvore Node resolvida.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --requirement requirements.txt
npm ci
npx playwright install chromium
```

## Validação dos artefatos de uma feature

```bash
python3 scripts/validate_design_flow.py /caminho/do/projeto/.design/minha-feature --json
python3 scripts/validate_design_flow.py /caminho/do/projeto/.design/minha-feature --require-review --json
python3 -m py_compile scripts/validate_design_flow.py scripts/export_carousel.py tests/playwright_smoke.py
npm run check:node
npm run test:unit
npm run test:e2e
```

## Carrossel editorial

A rota de carrossel inclui sete modos de copy, capa orientada por curiosidade, passe de ritmo oral, imagem aprovada pelo estado ou ação representada, Geist Sans/Mono, exportação 1080 × 1350, contact sheet e pacote recursivo de assets.

```bash
npm ci
npx playwright install chromium
npx playwright --version
python3 -c "import PIL; print(PIL.__version__)"

python3 scripts/export_carousel.py /caminho/do/carrossel \
  --zip carousel-meu-slug.zip
```

Pré-requisitos: Python 3.11 ou 3.12, dependências Python de `requirements.txt`, dependências Node instaladas com `npm ci` e Chromium do Playwright disponível. O exportador usa a dependência local fixada; ele não instala dependências silenciosamente durante a entrega.

Por segurança, a exportação desativa JavaScript escrito pela página. O controlador confiável seleciona cada slide, aplica `body.export` e aguarda fontes e imagens; conteúdo gerado dinamicamente deve ser materializado em HTML/CSS local antes da captura. HTTP e WebSocket são bloqueados como defesa em profundidade, service workers ficam desativados e o HAR de cada slide é preservado em `.design/carousel-export/network/`.

Use `references/carousel-production.md` para o fluxo completo e `references/carousel-copy-modes.md` para escolher entre diagnóstico operacional, tese de founder, caso narrativo, framework, reframe, objeção e prova comentada.

O diretório `.design/` deve ser versionado junto com o projeto para preservar decisões e evidências entre agentes, colaboradores e novos clones.

## Escopo

Esta skill é melhor para portais, dashboards, produtos, áreas logadas, fluxos com múltiplas telas ou estados e carrosséis editoriais Júpiter. Para uma landing page simples, apresentação, vídeo ou estudo visual descartável, use uma skill especializada.

## Origem

Este projeto é uma adaptação independente inspirada por:

- https://github.com/julianoczkowski/designer-skills
- artigo “As 7 Skills que Ensinam o Agente de IA a Pensar Como um Designer Profissional”, de Nett0.

Consulte `NOTICE` para atribuição e diferenças de implementação.
