# Roteamento de marca

## Ordem de consulta

1. Arquivos de instrução do projeto.
2. Brandbooks e tokens descobertos no próprio repositório.
3. Caminho configurado pela variável `JUPITER_BRANDBOOK_PATH`, quando disponível.
4. Implementação existente.
5. Fallback local conhecido.
6. Material humano ou PDF quando os arquivos estruturados não bastarem.

## Júpiter Tech

Procure primeiro por `brand.json`, `brand.md`, `DESIGN.md`, arquivos de tokens e documentação da marca no repositório ativo. Se `JUPITER_BRANDBOOK_PATH` estiver configurada, use esse caminho. Somente como fallback, quando disponível no ambiente da Júpiter, consulte:

```text
/root/workspace/brandbooks/jupiter-tech-manual/
├── agents/brand.json
├── agents/brand.md
└── humans/
```

Leia primeiro `agents/README.md`, depois `agents/brand.json` e `agents/brand.md`. Consulte os materiais humanos somente para detalhes não resolvidos.

## Regras

- Preserve símbolos oficiais; não redesenhe marca por aproximação.
- Use tokens canônicos antes de valores hardcoded.
- Não troque tipografia oficial para atender preferência genérica da skill.
- Não crie dark mode sem requisito ou sistema existente.
- Não confunda referência de mercado com licença para copiar.
- Quando a marca não tiver uma regra, registre a nova decisão como extensão, não como fato histórico.
- Em conteúdo com dados de clientes, use dados fictícios e seguros.

## Evidência mínima no brief

Registre:

- arquivos consultados;
- versão/data quando disponível;
- tokens e componentes reutilizados;
- exceções necessárias;
- elementos da marca que não podem ser alterados.
