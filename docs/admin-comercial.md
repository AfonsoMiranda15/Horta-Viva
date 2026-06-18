# Admin Comercial: Guia de Submenus

## Objetivo
Este guia descreve, em detalhe, cada submenu do app `comercial` no Django Admin e como ele deve ser usado no dia a dia de operação.

## Visão geral do fluxo
1. Cadastro de catálogo em `Produtos e serviços`.
2. Montagem de pacotes em `Ofertas de compra`.
3. Definição da oferta principal em `Configurações de compra do site`.
4. Venda pública em `/comprar/` e checkout.
5. Acompanhamento em `Pedidos de compra` (com pagamentos vinculados no próprio pedido).
6. Faturação em `Faturas-recibo dos pedidos`.

## Produtos e serviços
Finalidade:
- Cadastrar itens vendáveis, tanto produto quanto serviço.

Campos principais:
- `codigo`: identificador único e estável para integrações.
- `tipo_item`: `produto` ou `servico`.
- `nome_pt` e `nome_en`: nome exibido no site.
- `descricao_pt` e `descricao_en`: descrição comercial.
- `descricao_produto_fatura`: texto que vai na linha da fatura-recibo.
- `imagem_item`: capa do item no catálogo.
- `ativo`: controla se o item pode ser ofertado.
- `controla_stock`: habilita/desabilita controle de quantidade.
- `stock_total`, `stock_reservado`, `stock_disponivel`: controle operacional.
- `preco`, `moeda`, `iva_percentual`: base de cálculo do checkout.
- `toconline_item_id`: vínculo opcional com item fiscal externo.

Uso recomendado:
- Criar primeiro os itens, depois montar ofertas.
- Em serviços com vagas limitadas, manter `controla_stock=true`.

## Ofertas de compra
Finalidade:
- Agrupar itens do catálogo em ofertas públicas de checkout.

Campos principais:
- `slug`: URL pública da oferta.
- `nome_pt` e `nome_en`: nome comercial.
- `descricao_pt` e `descricao_en`: texto de vitrine.
- `imagem_capa`: imagem principal da oferta.
- `ativa`: controla publicação na vitrine.
- `exibir_urgencia_stock_card`: exibe mensagem dinâmica de urgência no card de compra.
- `tempo_reserva_minutos`: validade da reserva antes do pagamento.
  Este prazo também é usado como validade da Referência Multibanco no gateway.

Inline importante:
- `Itens da oferta`: define quais itens entram na oferta.
- `quantidade`: quantidade de cada item no pacote.
- `ordem`: ordenação de exibição.

Uso recomendado:
- Sempre validar preço final e composição da oferta após editar itens.
- Desativar (`ativa=false`) para retirar oferta do ar sem apagar histórico.
- Manter `exibir_urgencia_stock_card=true` quando quiser reforçar escassez por stock real.
- Ajustar `tempo_reserva_minutos` de acordo com a estratégia de stock, pois o mesmo prazo governa a janela de pagamento por referência.

## Configurações de compra do site
Finalidade:
- Definir qual oferta aparece como CTA principal nas páginas institucionais.

Campo principal:
- `oferta_checkout_cta`: oferta usada no botão/CTA de compra.

Uso recomendado:
- Manter um registro principal (`nome=principal`).
- Trocar a oferta aqui para mudar o CTA sem alterar templates.

## Pedidos de compra
Finalidade:
- Operação do ciclo do pedido e visão fiscal do cliente.

O que mostra:
- Dados do cliente, estado do pedido, totais líquido/impostos/bruto.
- Prazo de expiração (`expira_em`) e marcação de pagamento (`pago_em`).
- Itens do pedido em snapshot (preço e imposto congelados).
- Pagamentos vinculados ao pedido em inline (status, método, valor, transaction IDs e datas).

Ação disponível:
- `Expirar pedidos selecionados e liberar reservas`.

Quando usar:
- Para liberar reserva de pedidos não pagos que já expiraram.
- Para auditoria de dados de faturação coletados no checkout.

## Pagamentos dos pedidos
Finalidade:
- Acompanhar transações de pagamento (SIBS) com foco operacional.

Campos-chave:
- `pedido` e `cliente`.
- `transaction_id` e `merchant_transaction_id`.
- `status`, `metodo_pagamento`, `valor`, `moeda`.
- `entidade_multibanco` e `referencia_multibanco` quando o método for referência MB.

Quando usar:
- Pesquisar pagamentos por cliente, pedido ou transaction id.
- Abrir o pedido relacionado para contexto completo da compra.

Observação operacional:
- Para pagamentos por referência MB, a entidade e a referência ficam visíveis tanto em `Pagamentos dos pedidos` quanto no inline de pagamentos dentro de `Pedidos de compra`.

## Faturas-recibo dos pedidos
Finalidade:
- Monitorar emissão e envio de documento fiscal.

Campos-chave:
- `status`: pendente, emitido, enviado, erro.
- `numero_documento`, `identificador_externo`, `url_pdf`.
- `caminho_pdf_privado`: caminho interno no bucket privado fiscal.
- `erro_ultima_tentativa` para diagnóstico.
- `Baixar PDF`: gera link temporário assinado (acesso protegido) direto no admin.

Quando usar:
- Confirmar se pagamento gerou fatura-recibo.
- Reconciliar casos de falha de emissão.
- Baixar cópia fiscal do cliente sem expor bucket/public URL.

## Menus técnicos removidos da operação
Para reduzir ruído no admin operacional, os menus `Movimentos de stock` e `Tokens de integração externa` foram retirados da navegação padrão.
Esses dados continuam sendo geridos internamente pelos serviços e comandos do framework.

## Sequência operacional recomendada
1. Cadastrar `Produtos e serviços`.
2. Montar `Ofertas de compra`.
3. Definir `Configurações de compra do site`.
4. Testar compra fim a fim.
5. Acompanhar `Pedidos`, `Pagamentos` e `Faturas-recibo`.
