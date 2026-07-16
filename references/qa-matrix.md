# Matriz de QA visual

## Viewports mínimos

| Contexto | Viewport recomendado | Evidência |
|---|---:|---|
| Mobile | 375 × 812 | screenshot full-page ou fluxo completo |
| Tablet, quando relevante | 768 × 1024 | screenshot das views estruturais |
| Desktop | 1280 × 800 ou maior | screenshot full-page ou view principal |

Quando o produto tiver breakpoint próprio, use-o além dos valores acima.

## Checklist por categoria

### Hierarquia
- A primeira ação e a informação mais importante são identificáveis sem caça visual.
- A ordem de leitura é coerente.
- Títulos, corpo, labels e metadados têm níveis distintos.
- A densidade corresponde à tarefa.

### Marca e consistência
- Símbolo, cores e fontes correspondem ao brandbook.
- Valores usam tokens compartilhados.
- Componentes equivalentes têm aparência e comportamento equivalentes.
- Não há componentes duplicados sem justificativa.

### Responsividade
- O layout reorganiza; não apenas encolhe.
- Não há overflow horizontal não intencional.
- Alvos de toque têm pelo menos 44 × 44 px quando aplicável.
- Corpo de texto mobile não depende de zoom.
- Navegação possui comportamento mobile próprio.

### Estados e interação
- Default, hover, foco, ativo e desabilitado.
- Loading, vazio, erro e sucesso.
- Feedback para ações assíncronas.
- Modal, dropdown e menu com abertura, fechamento e foco coerentes.
- Estados de permissão e acesso quando aplicáveis.

### Acessibilidade
- Contraste WCAG AA: 4.5:1 no corpo, 3:1 em texto grande.
- Ordem de headings e landmarks semânticos.
- Navegação por teclado e foco visível.
- Labels associados a inputs.
- Alt text e nomes acessíveis.
- `prefers-reduced-motion` quando há movimento.

### Conteúdo
- Texto real cabe nos componentes.
- Números longos, nomes extensos e ausência de dados não quebram o layout.
- Microcopy orienta ação e recuperação de erro.
- Placeholder não mascara densidade real.

### Técnica
- Sem erros de console relevantes.
- APIs e assets carregam sem falhas silenciosas.
- Testes relevantes passam.
- Build e lint não introduzem novos erros.
- Desempenho não degrada por mídia ou animação desnecessária.

## Evidência automatizada

O validador aceita evidência visual em **PNG não interlaçado**. A imagem precisa ter estrutura completa, chunks críticos conhecidos e ordenados, CRCs válidos, dimensões positivas, arquivo de até 25 MB, no máximo 50 milhões de pixels e dados de scanline decodificáveis dentro do limite de 128 MB. JPEG, WebP e PNG Adam7/interlaçado devem ser convertidos para PNG não interlaçado antes da validação.

### Playwright CLI

Quando disponível:

```bash
npx playwright screenshot --viewport-size="375,812" --full-page http://127.0.0.1:3000 .design/<feature>/screenshots/mobile-375.png
npx playwright screenshot --viewport-size="1280,800" --full-page http://127.0.0.1:3000 .design/<feature>/screenshots/desktop-1280.png
```

### HyperFrames

```bash
npx hyperframes check . --json --snapshots --at <tempos-relevantes>
```

Copie as imagens geradas para `.design/<feature>/screenshots/` com nomes descritivos. O comando `check` já executa lint; não rode `lint` separadamente sem motivo. Use Browser Vision para avaliação visual e console/terminal para erros e respostas de runtime.

## Severidade

- **Must fix:** quebra funcional, risco de dados, acessibilidade crítica, desvio forte do brief ou marca.
- **Should fix:** inconsistência, estado ausente, responsividade fraca ou fricção importante.
- **Could improve:** refinamento que aumenta clareza, personalidade ou eficiência sem bloquear o uso.
