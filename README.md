# Análise de Meta Ads com HYPD AI

Skill em português para guiar a conexão do **HYPD AI — Paid Ads & Analytics** no Cowork e configurar dois relatórios de Meta Ads entregues no ChatGPT.

- **9h:** resultado de ontem completo.
- **17h:** resultado de hoje até a consulta, identificado como parcial.
- **Ambos:** tendência dos últimos 7 dias completos contra os 7 anteriores.
- **Somente análise:** nunca altera campanhas, anúncios, conjuntos ou orçamento.

## O que você precisa

Um ambiente do ChatGPT/Cowork que suporte instalação de skills, acesso ao repositório e agendamento com o conector HYPD. A disponibilidade depende do produto, plano, região e permissões. A skill não fornece acesso ao HYPD nem garante compatibilidade com qualquer ambiente.

Você precisa conectar sua própria conta pelo fluxo oficial e confirmar a conta Meta Ads, moeda, fuso, metas, evento de contato e atribuição. Login e permissões são concluídos pelo usuário. Não cole senhas ou tokens no chat.

## Prompt para copiar e colar

Cole o prompt abaixo no ambiente compatível:

```text
Estou no Cowork. Instale a skill configurar-analise-meta-ads a partir de https://github.com/jcarlosamorim/hypd-meta-ads-skill, pasta skills/configurar-analise-meta-ads.

Primeiro leia o README e o SKILL.md, inspecione os arquivos e use o mecanismo de instalação de skills suportado neste ambiente. Instale apenas essa skill, incluindo references, scripts, assets e agents. Não execute código externo sem revisar sua finalidade e respeitar as permissões do ambiente. Confirme que a skill foi instalada e está disponível. Se o ambiente não permitir instalar skills, explique o bloqueio e o menor próximo passo, sem afirmar que instalou.

Depois use a skill para me guiar na conexão oficial do HYPD AI — Paid Ads & Analytics. Eu concluirei login e autorização. Verifique com uma consulta real qual conta Meta Ads está conectada.

Adapte o contrato canônico ao meu perfil: pergunte somente o que faltar sobre conta, moeda, fuso, limite por novo cliente, limite por contato, conversa iniciada OU lead cadastrado e o evento correspondente. Os exemplos de R$ 50 e R$ 10 precisam ser confirmados comigo. Compras atribuídas não devem ser tratadas como novos clientes sem confirmação confiável.

Depois de validar conexão, perfil e um relatório inicial, configure dois relatórios diários no ChatGPT: às 9h, ontem completo; às 17h, hoje parcial. Em ambos, compare os últimos 7 dias completos com os 7 anteriores, usando o mesmo evento e atribuição e respeitando o fuso da conta. Confirme comigo qualquer diferença entre meu fuso e o da conta. Verifique agendas existentes para não duplicar. Confirme os horários e o estado de cada rotina após criar.

Não altere campanhas, anúncios, conjuntos ou orçamento. Apresente recomendações para minha decisão. Não salve contas reais, credenciais ou relatórios privados neste repositório público.
```

## Conteúdo

- `skills/configurar-analise-meta-ads/SKILL.md`: procedimento de conexão, personalização e instalação das rotinas.
- `references/prompt-canonico.md`: contrato original preservado.
- `references/contrato-execucao.md`: regras de comparação, agregação, janelas e qualidade dos dados.
- `references/perfil-template.json`: modelo vazio; o perfil preenchido deve permanecer privado.
- `scripts/render_rotinas.py`: valida o perfil e gera dois contratos autossuficientes. **Não conecta apps e não cria agendas.**
- `scripts/test_render_rotinas.py`: testes sintéticos locais, sem rede ou conta real.

Os caminhos de `references` e `scripts` são relativos à pasta da skill.

## Validação local

Python 3.9 ou superior, com base de fusos horários disponível:

```sh
python3 -m unittest discover -s skills/configurar-analise-meta-ads/scripts -p 'test_*.py' -v
```

Para gerar os contratos a partir de um perfil privado já confirmado:

```sh
python3 skills/configurar-analise-meta-ads/scripts/render_rotinas.py /caminho/privado/perfil.json /caminho/privado/saida
```

Os testes verificam o contrato e a renderização. Não comprovam conexão HYPD, disponibilidade do agendador nem funcionamento de rotinas reais.

## Limites importantes

Custo agregado usa gasto total dividido pelos resultados totais do mesmo tipo. Dados ausentes não viram zero. CPC não é CAC. Compras atribuídas não comprovam novos clientes. CTR, frequência e contato barato não demonstram, isoladamente, vendas saudáveis ou a causa de um problema. A skill não promete resultados de marketing.

Este projeto é independente e não representa Meta, OpenAI ou HYPD AI. As marcas pertencem aos respectivos titulares.
