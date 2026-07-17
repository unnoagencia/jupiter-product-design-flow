---
name: jupiter-product-design-flow
description: "Use when designing, redesigning, building, or reviewing a branded digital product, portal, dashboard, multi-step flow, complex website, or editorial carousel for Júpiter. Converts business intent into a persistent brief, proportional structure, brand-bound implementation, working artifact, and evidence-based visual QA without ceremonial checkpoints."
version: 1.1.0
author: Júpiter Tech
license: Apache-2.0
metadata:
  hermes:
    tags: [product-design, ui, ux, design-system, visual-qa, carousel, editorial-design, jupiter]
    related_skills: [design-md, writing-plans, sketch, claude-design, b2b-conversion-websites, instagram-carousel-system, humanizer, hyperframes]
---

# Júpiter Product Design Flow

## Visão geral

Este workflow dá processo ao agente antes de dar liberdade estética. Ele transforma uma necessidade de negócio em decisões persistidas, estrutura proporcional à complexidade, implementação aderente à marca e revisão visual baseada em evidências. A mesma disciplina cobre produto digital e carrossel editorial Júpiter, com uma rota específica para narrativa, copy, imagem e exportação.

Princípio central:

> O agente não deve inventar uma interface. Deve reconstruir o problema, respeitar o sistema existente, implementar e provar que o resultado funciona.

O processo padrão é autônomo. Não peça confirmação ao fim de cada fase. Só interrompa para uma decisão que não pode ser recuperada do projeto e que mudaria materialmente escopo, risco ou direção.

## Quando usar

Use para:

- portais, dashboards, produtos SaaS, áreas logadas e fluxos com múltiplas etapas;
- redesign de produto em código existente;
- funcionalidades que atravessam várias telas, estados ou perfis de usuário;
- projetos em que brandbook, tokens e componentes existentes precisam ser preservados;
- revisão visual e funcional antes de publicação;
- trabalhos que precisam deixar memória de design para futuras sessões e agentes;
- carrosséis editoriais Júpiter com copy, fotografia, HTML, PNG, legenda e pacote final.

Não use o fluxo completo para:

- uma landing page simples focada em conversão: carregue `b2b-conversion-websites`;
- uma comparação rápida de ideias visuais: carregue `sketch`;
- um artefato HTML isolado sem necessidade de identidade ou processo Júpiter: carregue `claude-design`;
- apresentações e vídeos: use HyperFrames e as skills correspondentes;
- uma alteração cosmética pequena e inequívoca: inspecione, implemente e teste diretamente.

## Rota especial: carrossel editorial

Quando o pedido explícito for um carrossel, use este fluxo como disciplina principal e carregue `references/carousel-production.md`. Para escolher a tensão e a cadência, use `references/carousel-copy-modes.md`.

O default é:

- 8 slides em 1080 × 1350;
- capa com curiosidade útil, sem entregar o mecanismo cedo;
- progressão por cena, mecanismo, exemplo, controle, exceção, primeiro movimento e consequência;
- copy lida em voz alta e corrigida quando todas as telas tiverem a mesma pressão;
- fotografia ou recorte em dois ou três momentos com aprovação pelo verbo ou estado representado;
- Geist Sans + Geist Mono conforme o manual, Inter apenas como fallback;
- HTML local, PNGs, contact sheet, legenda, README, créditos e ZIP portátil;
- zero dependência remota no artefato final;
- QA visual, DOM, fontes, imagens e integridade do pacote.

Use `templates/carousel-starter.html` como scaffold opcional e `scripts/export_carousel.py` para renderizar e empacotar. O template não deve determinar a direção criativa nem sair com texto de exemplo.

Uma sequência linear simples não exige `INFORMATION_ARCHITECTURE.md`. Persistir brief, tarefas, review e screenshots continua obrigatório para uma entrega completa.

**Concluído quando:** a mudança de percepção, o modo de copy, a função de cada slide, os momentos de imagem, a tipografia e o contrato de saída estão registrados antes da implementação.

## Contrato de artefatos

Para cada feature relevante, mantenha:

```text
.design/<feature-slug>/
├── DESIGN_BRIEF.md
├── INFORMATION_ARCHITECTURE.md   # somente quando necessário
├── TASKS.md
├── DESIGN_REVIEW.md
└── screenshots/
```

Use os modelos de `references/artifact-contract.md`. Não crie documentos vazios para simular processo. Cada arquivo só existe quando contém decisões ou evidências úteis.

## Hierarquia de verdade

Quando houver conflito, siga esta ordem:

1. Instruções do repositório: `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, README e documentação técnica.
2. Brandbook canônico e arquivos estruturados da marca.
3. Componentes, tokens, fontes, padrões de layout e convenções já presentes no código.
4. Brief aprovado da feature.
5. Referências estéticas e preferências conversacionais.
6. Escolha autônoma do agente.

Uma referência visual nunca autoriza apagar a identidade da marca. Filosofia estética é lente, não licença para cosplay de produto alheio.

## Fluxo operacional

### 0. Classificar o trabalho

Determine:

- **Tipo:** landing page, produto, dashboard, portal, componente, fluxo ou artefato editorial.
- **Escala:** uma tela, múltiplas telas, múltiplos perfis ou sistema completo.
- **Estado:** projeto novo, código existente ou redesign parcial.
- **Risco:** baixo, médio ou alto para negócio, dados, acessibilidade e operação.

Se outra skill especializada for melhor, carregue-a e use este fluxo apenas como disciplina complementar.

**Concluído quando:** o tipo de trabalho, o escopo inicial e a rota de execução estão claros.

### 1. Descoberta antes de perguntas

Inspecione antes de entrevistar:

- instruções e documentação do repositório;
- rotas, páginas, layouts e estrutura de navegação;
- componentes reutilizáveis e suas APIs;
- CSS variables, Tailwind, temas, tokens e arquivos `DESIGN.md`;
- fontes carregadas e dependências de UI;
- Storybook, testes visuais e screenshots existentes;
- brandbooks locais ou caminhos canônicos conhecidos;
- conteúdo real disponível; não use lorem ipsum quando o material existir.

Para projetos Júpiter, descubra primeiro brandbooks e tokens dentro do repositório ou em um caminho configurado. Use `/root/workspace/brandbooks/jupiter-tech-manual` apenas como fallback quando existir. Consulte `references/brand-routing.md`.

Faça ao usuário apenas perguntas que:

1. não possam ser respondidas por inspeção;
2. tenham mais de uma resposta plausível;
3. mudem materialmente a solução.

Ao perguntar, apresente sua recomendação. Evite transformar briefing em interrogatório performático.

**Concluído quando:** os fatos recuperáveis foram levantados e as ambiguidades críticas foram resolvidas ou marcadas como hipóteses.

### 2. Escrever o design brief

Crie `.design/<feature-slug>/DESIGN_BRIEF.md` com:

- problema humano e operacional;
- usuário principal e JTBD;
- resultado observável de sucesso;
- princípios de experiência, no máximo três;
- escopo e fora de escopo;
- direção de marca e anti-referências;
- padrões existentes que devem ser reutilizados;
- inventário de componentes: reutilizar, modificar ou criar;
- conteúdo real e estados necessários;
- restrições de responsividade, acessibilidade, desempenho e tecnologia;
- hipóteses ainda não verificadas.

Não confunda objetivo comercial com experiência. “Aumentar conversão” não descreve o que o usuário precisa conseguir fazer.

**Concluído quando:** outro agente consegue implementar a feature sem reconstruir intenção por mensagens antigas.

### 3. Decidir se arquitetura da informação é necessária

Crie `INFORMATION_ARCHITECTURE.md` quando houver pelo menos um destes sinais:

- mais de uma rota ou caminho relevante;
- navegação primária, secundária ou contextual;
- múltiplos perfis ou permissões;
- conteúdo que crescerá com o tempo;
- fluxo com decisões, retornos ou estados persistidos;
- risco de nomenclatura inconsistente.

Pule a IA para componente isolado, formulário curto ou página linear sem escolhas estruturais.

Quando necessária, documente:

- mapa de rotas e views;
- hierarquia de conteúdo por página;
- modelo de navegação desktop e mobile;
- fluxos críticos e pontos de decisão;
- vocabulário da interface;
- crescimento, busca, filtros, paginação e estados vazios;
- componentes estruturais reutilizados.

**Concluído quando:** rotas, hierarquia, navegação e fluxos críticos não dependem mais de interpretação visual.

### 4. Amarrar o sistema visual à marca

Antes de gerar tokens:

1. detecte os tokens e componentes existentes;
2. encontre o brandbook e sua versão estruturada;
3. identifique lacunas reais;
4. estenda o sistema em vez de substituí-lo.

Use `design-md` quando for necessário criar ou validar um contrato de tokens. Não gere dark mode por reflexo. Crie-o apenas quando o produto, o brief ou o sistema existente exigirem.

Não troque fontes oficiais porque uma referência usa outra. Não imponha uma “filosofia estética” sobre uma marca madura. Se a marca não tiver direção suficiente, proponha uma direção e declare a hipótese.

**Concluído quando:** cada decisão visual importante deriva de token existente, regra de marca ou exceção documentada.

### 5. Decompor em fatias verificáveis

Use `writing-plans` ou o planejamento nativo do projeto para produzir `.design/<feature-slug>/TASKS.md`.

Cada tarefa deve:

- entregar uma fatia vertical observável;
- incluir estrutura, estilo, comportamento e estados relacionados;
- indicar componentes reutilizados, modificados ou novos;
- citar arquivos ou áreas prováveis;
- incluir verificação concreta;
- ser pequena o bastante para uma sessão de implementação;
- priorizar risco e elemento central antes de polimento.

Não decomponha em “fazer HTML”, “fazer CSS” e “fazer JS”. Isso organiza tecnologia, não entrega produto.

**Concluído quando:** a ordem reduz incerteza cedo e cada item tem uma definição testável de pronto.

### 6. Implementar o artefato real

Implemente, execute e verifique. Não pare em mockup, plano ou código não exercitado quando o pedido for construir.

Regras:

- reuse antes de criar;
- preserve contratos e comportamento existentes;
- use conteúdo real ou dados fictícios claramente seguros;
- cubra loading, vazio, erro, sucesso, hover, foco, ativo e desabilitado quando aplicáveis;
- faça mobile como decisão de layout, não como desktop encolhido;
- mantenha touch targets adequados e texto legível;
- respeite `prefers-reduced-motion` quando houver animação;
- rode os testes relevantes e registre o resultado real.

Para decisões visuais incertas, construa duas ou três variantes pequenas com `sketch` antes de contaminar a implementação principal.

**Concluído quando:** existe um artefato funcional exercitado no ambiente correto e todos os requisitos declarados foram considerados.

### 7. Revisão visual com evidências

A revisão não pode ser apenas leitura de código. Capture e analise o que o usuário vê.

Rotas de evidência, em ordem de adequação:

1. screenshots automatizados via Playwright disponível no projeto;
2. Browser Vision para inspeção visual e interação;
3. HyperFrames `check --snapshots` para composições HyperFrames;
4. screenshots fornecidos pelo usuário apenas quando o ambiente não puder abrir a aplicação.

Capture ao menos:

- desktop;
- mobile;
- estados críticos;
- dark mode, somente se existir;
- página inteira ou área suficiente para avaliar hierarquia e continuidade.

Para carrossel, substitua a matriz acima por: capa integral, slide mais denso, todos os slides com fotografia, fechamento e contact sheet. Além da inspeção visual, verifique bounds no DOM, fontes computadas, dependências locais e entradas reais do ZIP.

Use `references/qa-matrix.md`. Registre em `DESIGN_REVIEW.md`:

- evidências capturadas e caminhos;
- o que passa;
- **Must fix**, **Should fix** e **Could improve**;
- arquivo ou componente afetado;
- correção proposta;
- resultado da nova verificação após correções.

Não elogie para preencher espaço. Preserve explicitamente o que funciona, porque revisão que só remove defeito também pode remover personalidade.

O agente não pode dispensar um Must-fix. Somente o responsável humano pelo projeto pode aceitar um defeito crítico. O review deve registrar nome, papel, data da autorização, justificativa e impacto conhecido. Falhas de segurança, exposição de dados ou corrupção funcional permanecem bloqueantes até correção.

**Concluído quando:** problemas críticos foram corrigidos ou aceitos pelo responsável humano sob as regras acima, e cada afirmação visual importante aponta para evidência.

### 8. Encerramento e memória do projeto

Antes de finalizar:

- atualize `TASKS.md` com o estado real;
- mantenha hipóteses e decisões relevantes no brief;
- confirme que screenshots e review correspondem à versão final;
- reporte arquivos, testes, limitações e próximo risco;
- não salve progresso temporário em memória global; o diretório `.design/` é o rastro durável do projeto.

**Concluído quando:** outra sessão consegue retomar o trabalho pelo repositório, sem pedir ao usuário que reconte a história.

## Princípios de decisão

### Processo proporcional

Uma página linear não precisa de um tratado de arquitetura. Um portal com permissões não pode depender de um parágrafo. Use somente as fases que reduzem risco real.

### Autonomia sem adivinhação

Recupere o que existe, recomende a melhor resposta e avance. Pergunte quando a escolha for irreversível, cara ou identitária.

### Brandbook antes de estética

A marca é uma restrição produtiva. Não é “inspiração opcional”. Em projetos com brandbook, ele vence tendências, referências e preferências genéricas da skill.

### Evidência antes de opinião

“Parece bom” não fecha QA. Screenshot, interação, contraste, overflow, estado e teste fecham.

### Produto antes de tela

Uma interface bonita que não resolve prioridade, fluxo e estado continua sendo decoração com deploy.

## Armadilhas comuns

1. **Instalar processo como cerimônia.** Pedir aprovação a cada fase drena o usuário. Avance por padrão e exponha apenas decisões importantes.
2. **Gerar design system paralelo.** Estenda tokens e componentes existentes. Não crie outro universo visual dentro do mesmo produto.
3. **Forçar dark mode.** É requisito de produto, não medalha de maturidade.
4. **Escolher estética antes do problema.** Referência visual sem brief produz imitação competente do problema errado.
5. **Revisar sem ver.** Código não revela fonte quebrada, overflow, hierarquia fraca ou estado visual incoerente.
6. **Usar placeholder como verdade.** Conteúdo falso mascara problemas de densidade e hierarquia.
7. **Confundir tarefa técnica com fatia de produto.** A unidade de trabalho deve ser algo que o usuário consegue experimentar.
8. **Ignorar contexto do repositório.** Antes de criar um componente, prove que ele ainda não existe.
9. **Parar antes da execução.** Quando o pedido é construir, o entregável é artefato funcionando e validado.
10. **Resolver a capa cedo demais.** Uma tese completa pode matar a curiosidade antes do primeiro swipe.
11. **Aprovar imagem pelo substantivo.** A foto pode ter o objeto certo e comunicar o verbo errado.
12. **Empacotar apenas a pasta.** Colete assets recursivamente e prove que fontes e imagens estão dentro do ZIP.
13. **Parar no fallback tipográfico.** Para Júpiter, Inter é contingência; Geist Sans e Geist Mono são a escolha final quando disponíveis.

## Checklist de verificação

- [ ] Tipo, escala, estado e risco do trabalho classificados.
- [ ] Instruções do projeto e brandbook inspecionados.
- [ ] Componentes, tokens, fontes e rotas existentes inventariados.
- [ ] `DESIGN_BRIEF.md` contém problema, usuário, sucesso, escopo e restrições.
- [ ] IA criada somente quando a complexidade exige.
- [ ] Decisões visuais derivam da marca ou de exceção documentada.
- [ ] `TASKS.md` usa fatias verticais verificáveis.
- [ ] Artefato executado no ambiente real.
- [ ] Estados críticos e responsividade verificados.
- [ ] Revisão visual possui screenshots ou evidências equivalentes.
- [ ] Must-fix corrigidos ou aceitos pelo responsável humano com justificativa e impacto registrados.
- [ ] Testes e verificações finais registrados.
- [ ] O diretório `.design/` permite retomada sem reconstrução de contexto.
- [ ] Se for carrossel, modo de copy, ritmo, função das imagens e payoff foram verificados.
- [ ] Se for carrossel Júpiter, Geist Sans/Mono foram confirmadas no navegador e a licença acompanha o pacote.
- [ ] Se for carrossel, PNGs, contact sheet, legenda, README e ZIP íntegro foram gerados e abertos.
