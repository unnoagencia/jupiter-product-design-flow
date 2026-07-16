# Contrato de artefatos

Use estes modelos como estrutura mínima. Remova seções que não se aplicam; não mantenha headings vazios.

## DESIGN_BRIEF.md

```markdown
# Design Brief: [Feature]

- **Feature slug:** [slug]
- **Status:** draft | active | reviewed | shipped
- **Última atualização:** YYYY-MM-DD

## Problema
[Problema do ponto de vista do usuário e da operação.]

## Usuário principal e JTBD
- **Usuário:**
- **Quando:**
- **Quero:**
- **Para conseguir:**

## Resultado de sucesso
[Comportamento observável, não apenas métrica abstrata.]

## Princípios de experiência
1. [Tensão resolvida e implicação prática]
2. [Tensão resolvida e implicação prática]
3. [Opcional]

## Escopo
- [Incluído]

## Fora de escopo
- [Excluído]

## Marca e direção visual
- **Brandbook consultado:** [arquivo/caminho]
- **Tokens/componentes existentes:** [arquivos]
- **Direção:**
- **Anti-referências:**
- **Exceções documentadas:**

## Inventário de componentes
| Componente | Ação | Origem/arquivo | Observação |
|---|---|---|---|
| [nome] | reutilizar / modificar / criar | [arquivo] | [nota] |

## Conteúdo e estados
- Conteúdo real disponível:
- Loading:
- Vazio:
- Erro:
- Sucesso:
- Permissões:

## Restrições
- Responsividade:
- Acessibilidade:
- Desempenho:
- Tecnologia:
- Dados e privacidade:

## Hipóteses abertas
- [Hipótese — forma de validar]
```

## INFORMATION_ARCHITECTURE.md

```markdown
# Information Architecture: [Feature]

## Mapa de rotas e views
- [View] `[rota]`
  - [Sub-view] `[rota]`

## Modelo de navegação
- Primária:
- Secundária/contextual:
- Utilitária:
- Mobile:

## Hierarquia por view
### [View]
1. [Prioridade]
2. [Prioridade]
3. [Prioridade]

## Fluxos críticos
### [Fluxo]
1. Usuário chega em...
2. Vê...
3. Executa...
   - Se [condição] → [resultado]
4. Confirma...

## Vocabulário da interface
| Conceito | Nome na UI | Evitar | Motivo |
|---|---|---|---|

## Crescimento e recuperação
- Busca:
- Filtros:
- Ordenação:
- Paginação:
- Arquivo/histórico:
- Estado vazio:

## Reuso estrutural
| Componente | Views | Variações |
|---|---|---|
```

## TASKS.md

```markdown
# Build Tasks: [Feature]

Gerado a partir de: `.design/[slug]/DESIGN_BRIEF.md`

## Risco central
- [Maior incerteza a resolver primeiro]

## Implementação
- [ ] **[Fatia vertical]** — [resultado observável]. Reutiliza/modifica/cria: [componentes]. Verificar com: [teste/evidência].

## QA
- [ ] Capturar desktop e mobile.
- [ ] Exercitar estados críticos.
- [ ] Rodar testes relevantes.
- [ ] Produzir `DESIGN_REVIEW.md`.
```

## DESIGN_REVIEW.md

```markdown
# Design Review: [Feature]

- **Revisado contra:** `DESIGN_BRIEF.md`
- **Versão/commit:** [identificador]
- **Data:** YYYY-MM-DD

## Evidências
| Arquivo | Viewport/estado | O que comprova |
|---|---|---|

## Síntese
[Leitura direta da qualidade e do maior risco.]

## Must fix
1. **[Problema]** — Evidência: [arquivo]. Afeta: [componente/arquivo]. Correção: [ação].

## Should fix
1. **[Problema]** — Evidência e correção.

## Could improve
1. **[Oportunidade]** — Benefício esperado.

## O que preservar
- [Decisão forte que não deve ser perdida durante correções]

## Verificação após correções
| Item | Verificação executada | Resultado |
|---|---|---|
```
