# Regra de Negócio — Venda Condicionada a Saldo de Pontos

## Regra
- Somente pode ser registrada nova venda se o cliente tiver saldo de pontos >= valor total da venda.
- Relação: 1 ponto = R$ 1,00.
- Os pontos exigidos são DEBITADOS no momento da criação da venda (entrada da compra).
- A baixa de cada parcela CREDITA pontos ao cliente (1 ponto por real pago).
- A regra é ABSOLUTA para todos os perfis, inclusive Administrador. Sem exceção.
- NÃO há devolução de pontos em nenhuma hipótese (cancelamento, estorno, inadimplência).
- Cliente com saldo zero nunca compra.
- Venda originada por QR: leitor redireciona; formulário bloqueia com motivo.
- Área do cliente: exibe saldo e nota explicativa (1 ponto = R$ 1,00).

## Mensagens
- Operador (saldo insuficiente): "Saldo insuficiente. Cliente tem X pts, venda exige Y pts. Faltam Z pts."
- Operador (regra absoluta): "Esta regra não admite exceção."
- Cliente (nota): "1 ponto = R$ 1,00. Compras exigem pontos equivalentes ao valor total. Não há devolução de pontos em cancelamentos, estornos ou inadimplência."
