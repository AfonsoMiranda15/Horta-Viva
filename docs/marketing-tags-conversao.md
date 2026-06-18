# Tags de Conversao (GA4 + Meta + LinkedIn)

Este documento descreve a implementacao de eventos de conversao no site, com foco em:
- centralizacao tecnica;
- compatibilidade com consentimento RGPD;
- rastreio correto do funil comercial sem hardcode disperso.

## Principios aplicados
- Tags carregadas somente apos consentimento (`cms_consentimento=cookie-autorizado`).
- Eventos disparados por JavaScript central (`window.MIAnalytics`), evitando snippets inline nos templates.
- Dados dinamicos vindos de atributos `data-*` dos templates (slug, valor, moeda, transacao).
- Conversoes finais com deduplicacao por sessao via `sessionStorage`.

## Arquivos principais
- `software/home/static/home/js/consent/core.js`
  - Centraliza estado do consentimento e eventos `cms:consentimento`.
- `software/home/static/home/js/tracking/core.js`
  - Registry de providers, configuracao e readiness.
- `software/home/static/home/js/tracking/providers.js`
  - Providers de GA4, Meta, LinkedIn, Mautic e JS extra.
- `software/home/static/home/js/tracking/loader.js`
  - Carrega providers somente apos consentimento.
- `software/home/static/home/js/tracking/events.js`
  - API global `window.MIAnalytics`.
  - `emitEvent(...)`, `emitEventOnce(...)`, normalizacao numerica, fila de retentativa e roteamento para GA4/Meta/LinkedIn.
- `software/comercial/static/comercial/js/ofertas-analytics.js`
  - Eventos da vitrine publica `/comprar/`.
- `software/comercial/static/comercial/js/checkout.js`
  - Eventos do checkout de oferta.
- `software/comercial/static/comercial/js/checkout-processar.js`
  - Evento no passo de processamento de pagamento.
- `software/comercial/static/comercial/js/checkout-retorno.js`
  - Evento de compra confirmada.
- `software/home/static/home/js/captura-leads.js`
  - Evento `generate_lead` em envio concluido.

## Mapa de eventos implementados
1. `view_item_list`
- Pagina: `/comprar/`
- Disparo: carregamento da lista de ofertas.
- Meta: `trackCustom('ViewItemList')`

2. `select_item`
- Pagina: `/comprar/`
- Disparo: clique no CTA "Comprar Agora".
- Meta: `trackCustom('SelectItem')`

3. `view_item`
- Pagina: `/checkout/<slug>/`
- Disparo: carregamento do checkout da oferta.
- Meta: `ViewContent`

4. `begin_checkout`
- Pagina: `/checkout/<slug>/`
- Disparo: inicio de checkout concluido com sucesso (resposta OK do backend antes do redirect).
- Meta: `InitiateCheckout`
- LinkedIn: `lintrk('track', { conversion_id: ... })` se `LINKEDIN_CONVERSAO_BEGIN_CHECKOUT_ID` estiver configurado.
- Fallback: se o ID especifico estiver vazio, usa `LINKEDIN_CONVERSAO_PADRAO_ID`, quando definido.

5. `add_payment_info`
- Pagina: `/checkout/processar/<transaction_id>/`
- Disparo: carregamento do passo de pagamento.
- Deduplicacao: `ga4:add_payment_info:<transaction_id>`.
- Meta: `AddPaymentInfo`
- Event ID: o mesmo identificador unico da transacao.
- LinkedIn: `lintrk('track', { conversion_id: ... })` se `LINKEDIN_CONVERSAO_ADD_PAYMENT_INFO_ID` estiver configurado.
- Fallback: se o ID especifico estiver vazio, usa `LINKEDIN_CONVERSAO_PADRAO_ID`, quando definido.

6. `purchase`
- Pagina: `/checkout/retorno/`
- Disparo: somente quando `status_retorno == sucesso`.
- Deduplicacao: `ga4:purchase:<transaction_id>`.
- Meta: `Purchase`
- Event ID: o mesmo identificador unico da transacao.
- LinkedIn: `lintrk('track', { conversion_id: ... })` se `LINKEDIN_CONVERSAO_PURCHASE_ID` estiver configurado.
- Fallback: se o ID especifico estiver vazio, usa `LINKEDIN_CONVERSAO_PADRAO_ID`, quando definido.

7. `generate_lead`
- Paginas com formulario `.js-formulario-captura`.
- Disparo: envio concluido com sucesso.
- Meta: `Lead`
- LinkedIn: `lintrk('track', { conversion_id: ... })` se `LINKEDIN_CONVERSAO_LEAD_ID` estiver configurado.
- Fallback: se o ID especifico estiver vazio, usa `LINKEDIN_CONVERSAO_PADRAO_ID`, quando definido.

8. `PageView`
- Paginas publicas com consentimento autorizado.
- Disparo: no carregamento do Meta Pixel apos `fbq('init', ...)`.
- LinkedIn: pageview/audiencia via Insight Tag, carregada com `LINKEDIN_PARTNER_ID`.

## Validacao rapida (QA)
1. Autorizar cookies no banner RGPD.
2. Abrir GA4 `DebugView`.
3. Abrir `Test Events` no Meta Events Manager.
4. Abrir o diagnostico/Insight Tag no LinkedIn Campaign Manager.
5. Percorrer funil:
   - `/comprar/` -> selecionar oferta;
   - `/checkout/<slug>/` -> iniciar checkout;
   - `/checkout/processar/<transaction_id>/`;
   - `/checkout/retorno/` com status de sucesso.
6. Confirmar eventos em ordem:
   - `view_item_list`, `select_item`, `view_item`, `begin_checkout`, `add_payment_info`, `purchase`.
7. Confirmar deduplicacao:
   - atualizar pagina de retorno sucesso e verificar que `purchase` nao duplica.

## Como obter os IDs de conversao do LinkedIn
1. Aceder ao `Campaign Manager` da conta certa.
2. Confirmar em `Data > Signals manager` que o `Insight Tag` da conta esta ativo.
3. Ir a `Measurement > Conversion tracking`.
4. Clicar em `Create conversion`.
5. Criar a conversao com nome e categoria coerentes com o funil:
   - `Lead`
   - `Purchase`
   - opcionalmente `Begin Checkout`
   - opcionalmente `Add Payment Info`
6. Na configuracao da conversao, escolher `Insight Tag`.
7. Na etapa de instalacao/manual setup, copiar o snippet gerado pelo LinkedIn.
8. Procurar no snippet o valor:
   - `lintrk('track', { conversion_id: 12345678 });`
9. Usar esse numero no `.env`.

### Estrategias recomendadas
- Estrategia simples:
  - preencher apenas `LINKEDIN_CONVERSAO_PADRAO_ID`
  - usar a mesma conversao para `lead`, `checkout` e `purchase`
- Estrategia minima recomendada para vendas:
  - preencher `LINKEDIN_CONVERSAO_LEAD_ID`
  - preencher `LINKEDIN_CONVERSAO_PURCHASE_ID`
- Estrategia completa de funil:
  - preencher tambem `LINKEDIN_CONVERSAO_BEGIN_CHECKOUT_ID`
  - preencher `LINKEDIN_CONVERSAO_ADD_PAYMENT_INFO_ID`

### Regra aplicada no codigo
- Se existir ID especifico da etapa, o site usa esse ID.
- Se nao existir ID especifico, o site usa `LINKEDIN_CONVERSAO_PADRAO_ID`.
- Se nao existir nenhum `conversion_id`, o LinkedIn continua apenas com audiencia/pageview via `LINKEDIN_PARTNER_ID`.

## Notas de manutencao
- O ID GA4 vem de `GA4_MEASUREMENT_ID` no ambiente.
- O ID do Meta vem de `META_PIXEL_ID` no ambiente.
- O ID base do LinkedIn vem de `LINKEDIN_PARTNER_ID`.
- Conversoes do LinkedIn podem ser configuradas de duas formas:
  - simplificada: `LINKEDIN_CONVERSAO_PADRAO_ID`
  - granular por etapa do funil:
  - `LINKEDIN_CONVERSAO_BEGIN_CHECKOUT_ID`
  - `LINKEDIN_CONVERSAO_ADD_PAYMENT_INFO_ID`
  - `LINKEDIN_CONVERSAO_PURCHASE_ID`
  - `LINKEDIN_CONVERSAO_LEAD_ID`
- Nao adicionar snippet GA4/Meta/LinkedIn diretamente em templates.
- O bloco `noscript` do Meta Pixel nao foi implementado, porque ele contornaria o consentimento RGPD.
- O bloco `noscript` do LinkedIn tambem nao foi implementado pelo mesmo motivo.
- Novos eventos de conversao devem usar `window.MIAnalytics` para manter padrao.
