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
└── qa-matrix.md
scripts/
└── validate_design_flow.py
```

## Validação dos artefatos de uma feature

```bash
python3 scripts/validate_design_flow.py /caminho/do/projeto/.design/minha-feature --json
python3 scripts/validate_design_flow.py /caminho/do/projeto/.design/minha-feature --require-review --json
```

## Escopo

Esta skill é melhor para portais, dashboards, produtos, áreas logadas e fluxos com múltiplas telas ou estados. Para uma landing page simples, apresentação, vídeo ou estudo visual descartável, use uma skill especializada.

## Origem

Este projeto é uma adaptação independente inspirada por:

- https://github.com/julianoczkowski/designer-skills
- artigo “As 7 Skills que Ensinam o Agente de IA a Pensar Como um Designer Profissional”, de Nett0.

Consulte `NOTICE` para atribuição e diferenças de implementação.
