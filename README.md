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
└── validate_design_flow.py
templates/
└── carousel-starter.html
```

## Validação dos artefatos de uma feature

```bash
python3 scripts/validate_design_flow.py /caminho/do/projeto/.design/minha-feature --json
python3 scripts/validate_design_flow.py /caminho/do/projeto/.design/minha-feature --require-review --json
python3 -m unittest discover -s tests -v
```

## Carrossel editorial

A rota de carrossel inclui sete modos de copy, capa orientada por curiosidade, passe de ritmo oral, imagem aprovada pelo estado ou ação representada, Geist Sans/Mono, exportação 1080 × 1350, contact sheet e pacote recursivo de assets.

```bash
python3 scripts/export_carousel.py /caminho/do/carrossel \
  --zip carousel-meu-slug.zip
```

Use `references/carousel-production.md` para o fluxo completo e `references/carousel-copy-modes.md` para escolher entre diagnóstico operacional, tese de founder, caso narrativo, framework, reframe, objeção e prova comentada.

O diretório `.design/` deve ser versionado junto com o projeto para preservar decisões e evidências entre agentes, colaboradores e novos clones.

## Escopo

Esta skill é melhor para portais, dashboards, produtos, áreas logadas, fluxos com múltiplas telas ou estados e carrosséis editoriais Júpiter. Para uma landing page simples, apresentação, vídeo ou estudo visual descartável, use uma skill especializada.

## Origem

Este projeto é uma adaptação independente inspirada por:

- https://github.com/julianoczkowski/designer-skills
- artigo “As 7 Skills que Ensinam o Agente de IA a Pensar Como um Designer Profissional”, de Nett0.

Consulte `NOTICE` para atribuição e diferenças de implementação.
