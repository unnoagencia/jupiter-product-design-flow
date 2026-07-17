# Produção de carrossel editorial Júpiter

Use esta rota quando o entregável explícito for um carrossel. Ela traz para dentro do `jupiter-product-design-flow` a disciplina que funcionou no teste real: copy com progressão, capa com curiosidade, fotografia semântica, tipografia oficial, render verificável e pacote portátil.

## Contrato padrão

Salvo pedido diferente:

- formato: 1080 × 1350, proporção 4:5;
- total: 8 slides;
- arquivo-fonte: HTML/CSS local;
- saídas: 8 PNGs, contact sheet, legenda, README e ZIP;
- memória de design: `.design/<slug>/`;
- tipografia Júpiter: Geist Sans + Geist Mono;
- imagens: congeladas localmente e creditadas;
- zero dependência remota no grafo estático e nas requisições observadas durante o render.

Arquivos esperados:

```text
<projeto>/
├── .design/<slug>/
│   ├── DESIGN_BRIEF.md
│   ├── TASKS.md
│   ├── DESIGN_REVIEW.md
│   └── screenshots/
├── assets/
│   ├── photos/
│   ├── mark-white.svg
│   ├── Geist-Regular.woff2
│   ├── Geist-Medium.woff2
│   ├── Geist-SemiBold.woff2
│   ├── GeistMono-Medium.woff2
│   └── GEIST-LICENSE.txt
├── slides/
├── index.html
├── LEGENDA.txt
├── README.md
├── preview-contact-sheet.png
└── carousel-<slug>.zip
```

Pule `INFORMATION_ARCHITECTURE.md` para uma sequência linear simples. Crie IA somente se houver ramificações, versões por audiência, navegação ou sistema editorial mais amplo.

## 1. Definir a mudança de percepção

O brief deve registrar:

- fonte editorial ou tese;
- público;
- estado inicial do leitor;
- percepção que precisa mudar;
- consequência concreta;
- mecanismo que será revelado;
- ação final;
- anti-referências de copy e visual.

Escolha um modo dominante em `carousel-copy-modes.md`. Não misture sete estilos para parecer versátil. Isso costuma produzir um Frankenstein com boa gramática.

**Concluído quando:** existe uma frase que descreve o que o leitor deve acreditar depois do último slide.

## 2. Construir a sequência antes da copy final

Ritmo padrão de oito slides:

1. **Capa:** abre uma lacuna reconhecível.
2. **Cena:** mostra onde o problema aparece no trabalho real.
3. **Mecanismo:** revela o que estava escondido.
4. **Exemplo:** torna a abstração executável.
5. **Controle:** organiza critérios, níveis ou decisões.
6. **Exceção:** muda o tempo e mostra quando não agir.
7. **Primeiro movimento:** reduz medo de implementação.
8. **Consequência + CTA:** retorna ao impacto humano ou de negócio.

Essa sequência é um default, não uma liturgia. O modo de copy pode alterá-la, mas precisa preservar progressão e payoff.

**Concluído quando:** cada slide tem uma função diferente e a ordem cria avanço, não uma coleção de frases corretas.

## 3. Tratar a capa como produto separado

A capa merece atenção desproporcional. Ela deve ser entendida em um segundo e gerar uma pergunta útil.

Teste:

1. o tema é reconhecível sem legenda?
2. a frase expõe consequência, tensão ou contradição?
3. o mecanismo ainda está escondido?
4. existe motivo real para deslizar?
5. a linha funciona lida em voz alta?

Uma tese resolvida pode ser ótima no artigo e fraca na capa.

Fraca para curiosidade:

> O follow-up falha antes da mensagem.

Mais útil para deslize:

> É por isso que o follow-up falha na sua operação comercial.

Não transforme o exemplo em fórmula. O princípio é **consequência visível, mecanismo retido**.

**Concluído quando:** a capa cria curiosidade sem depender de clickbait ou esconder o assunto.

## 4. Fazer o passe de ritmo

Leia os oito slides em voz alta. Se todos soarem como declarações igualmente pesadas, a copy está dura.

Corrija com:

- uma cena observável antes do framework;
- alternância entre sentença curta e explicação mais fluida;
- substantivos concretos: proposta, WhatsApp, data, CRM, reunião, aprovação;
- rótulos técnicos subordinados a linguagem falada;
- uma exceção ou pausa no meio-final;
- fechamento na consequência, não em outro slogan de sistema.

Evite:

- artigo cortado em oito pedaços;
- manchete telegráfica em todos os slides;
- “não é sobre X, é sobre Y” por reflexo;
- travessões em série;
- “mais do que”, “no mundo atual” e perfume de IA;
- promessa grandiosa sem mecanismo.

**Concluído quando:** a sequência tem variação de pressão, cadência oral e uma ideia dominante por tela.

## 5. Fazer o passe de imagem semântica

Use fotografia ou recorte em dois ou três momentos, não em todos:

- capa: ambiente e stakes humanos;
- cena: objeto ou contexto nomeado pela copy;
- exceção: estado de espera, bloqueio ou decisão.

Aprovação por verbo:

1. qual ação ou estado a imagem comunica?
2. esse verbo apoia a frase?
3. o recorte preserva a pista semântica?
4. sem o título, a imagem ainda aponta na direção certa?

Uma foto com celular não basta. Se mostra alguém enviando e o slide diz para esperar, a imagem contradiz a copy. Prefira o telefone apoiado e sem interação.

Tratamento Júpiter:

- monocromia ou dessaturação controlada;
- recorte assimétrico, máscara ou bleed parcial;
- um detalhe Signal Blue com função;
- contraste preservado para leitura;
- fonte congelada localmente e URL de origem no README.

Evite equipe sorrindo como decoração, robô, holograma, circuito, neon, uma imagem por slide e interface falsa.

**Concluído quando:** cada imagem tem função narrativa nomeável e não apenas o substantivo correto.

## 6. Aplicar a marca de verdade

Use o manual e os tokens canônicos. Para Júpiter:

- Jupiter Black `#0A0A0B`;
- Graphite `#1F2124`;
- Mist `#F5F5F7`;
- Paper `#FAFAFA`;
- Steel `#8A8D93`;
- Signal Blue `#2F6FED`;
- Amber `#C8612C` somente em ênfase rara.

Tipografia:

- Geist Sans Semibold: títulos;
- Geist Sans Regular/Medium: corpo e apoio;
- Geist Mono Medium: eyebrows, metadados e marcadores técnicos;
- Inter: fallback, não escolha final quando Geist estiver disponível.

Congele fontes e licença no pacote. Verifique no navegador com `document.fonts.check()` e estilo computado. Declarar Geist no CSS e renderizar Arial é cosplay tipográfico.

**Concluído quando:** cores, fontes, símbolo e hierarquia derivam do manual, e o navegador confirma as famílias carregadas.

## 7. Produzir e exportar

Comece por `templates/carousel-starter.html` ou pelo sistema existente do projeto. O template é estrutura, não direção criativa pronta.

Exportador reutilizável:

```bash
python3 <skill-dir>/scripts/export_carousel.py /caminho/do/carrossel \
  --zip carousel-meu-slug.zip
```

Dependências:

- Node + Playwright fixado em `package-lock.json`;
- Chromium do Playwright;
- Pillow para o contact sheet.

Smoke check:

```bash
npm ci
npx playwright install chromium
npx playwright --version
python3 -c "import PIL; print(PIL.__version__)"
```

O exportador usa somente a versão local fixada e não baixa dependências durante a entrega. Prepare Playwright e Chromium com os comandos acima.

O HTML deve oferecer:

- uma seção `.slide` por quadro;
- `data-slide` único;
- HTML e CSS estáticos que funcionem quando `body.export` for aplicado;
- canvas fixo de 1080 × 1350 no modo export;
- assets locais.

Durante a captura, JavaScript escrito pela página fica desativado. Um controlador Playwright confiável aplica `body.export`, seleciona o `data-slide` solicitado, espera `document.fonts.ready`, força o carregamento das fontes declaradas, executa `img.decode()` e só então libera o screenshot. Rotas HTTP e WebSocket continuam bloqueadas como defesa em profundidade, service workers ficam desativados e um HAR por slide é preservado em `.design/carousel-export/network/`.

**Limite de compatibilidade:** gráficos, DOM ou conteúdo gerados por JavaScript da própria página não serão executados no export. Materialize esses elementos em HTML/CSS local antes da captura. Isso é deliberado para impedir egress por `fetch`, WebSocket, WebRTC/STUN e APIs semelhantes que não compartilham uma única rota de rede do Playwright.

O contrato padrão exige `README.md`, `LEGENDA.txt` e `assets/GEIST-LICENSE.txt`. Use `--relaxed-contract` somente quando a ausência desses itens for deliberada e registrada no brief.

**Concluído quando:** PNGs, preview e ZIP foram realmente gerados e abrem corretamente.

## 8. QA visual e de pacote

Inspecione:

- capa em tamanho integral;
- slide mais denso;
- todos os slides com imagem;
- fechamento;
- contact sheet.

Verifique por DOM:

- oito slides ou o total do brief;
- zero elementos fora do canvas;
- fontes e imagens carregadas;
- família computada correta;
- ausência de números quando proibidos;
- ausência de travessões e fórmulas proibidas;
- dependências locais existentes.

Verifique por arquivo:

- PNG 1080 × 1350 e não interlaçado;
- nested assets presentes no ZIP;
- nome do ZIP restrito ao diretório do projeto;
- licença tipográfica incluída;
- créditos de imagem no README;
- `zipfile.testzip()` sem erro;
- validador do design flow aprovado com review.

O ZIP deve coletar `assets.rglob("*")`, não apenas `assets.iterdir()`. Incluir a pasta sem os arquivos é o tipo de bug que passa em reunião e falha na entrega.

**Concluído quando:** artefato, evidências, fontes, imagens e pacote foram exercitados, não presumidos.
