# Receber de fora a partir do Brasil: o que as páginas oficiais dizem (consulta 2026-10-07)

Método: WebFetch e curl em páginas oficiais; o texto do artigo do Gumroad veio do JSON embutido no HTML. Rótulos: [F] lido na página oficial; [T] só terceiros; [NV] não verificado.

| Plataforma | O que a página oficial diz | URL | Rótulo |
|---|---|---|---|
| Gumroad | Venda direta "10% + $0.50" por transação; Discover "30%". "Since January 1, 2025, Gumroad handles ALL your tax obligations" (comerciante de registro) | https://gumroad.com/pricing | [F] |
| Gumroad (saque) | Lista de países com saque em conta bancária local **não inclui o Brasil** (entre Botswana e Brunei não há Brasil). "If bank payouts aren't supported in your country, we will pay you via PayPal"; saques por PayPal em USD com "2% processing fee"; "We do not support alternative payout modes like Payoneer, Wise, check, money order, wire transfer"; "PayPal does not allow accounts registered in some countries to receive money" | https://gumroad.com/help/article/13-getting-paid | [F] |
| Lemon Squeezy | Lista "Bank payouts supported in the following countries" (~100+ países) não traz o Brasil; "PayPal payouts are supported in 200+ countries and regions" (Brasil não é citado nominalmente). Página sem data | https://docs.lemonsqueezy.com/help/getting-started/supported-countries | [F] (via leitor de página; a lista completa não foi relida linha a linha) |
| Payhip | Plano grátis "$0 /mo" com "+5% transaction fee"; Plus "$29 /mo" com "+2%"; Pro "$99 /mo" sem taxa por transação. "Payhip is fully compliant to collect and remit EU VAT and UK on your behalf automatically". Países do vendedor e forma de saque não constam da página de preços | https://payhip.com/pricing | [F]; saque [NV] |
| Hotmart | Brasil: "9,9% + R$ 2,49 por venda aprovada" ("até 8,9%" em faixas maiores). A página cita "+40 métodos de pagamento", "22 opções de moedas" e "Tradução automática do checkout". **Não diz** a taxa de venda internacional, se pessoa física (CPF) pode vender ao exterior nem se recebe em reais. Saque: 2 dias 3,59%, 14 dias 2,19%, padrão em 30 dias sem taxa. O artigo de ajuda sobre moedas só carrega por script | https://hotmart.com/pt-br/taxa-hotmart | [F] taxas; resto [NV] |
| Kiwify | A página inicial só traz "8,99% + R$2,49"; **não afirma** venda internacional nem outras moedas | https://kiwify.com.br/ | [F]; internacional [NV] |
| Stripe (Brasil) | Pessoa física (CPF) pode abrir conta: "the CNPJ is optional" para empresário individual; saque exige "A Brazilian-based bank account, BRL denominated and associated to the tax ID (CPF or CNPJ) registered in your Stripe account". A página não trata de cartões ou moedas internacionais. Stripe não é loja: exige integração própria | https://support.stripe.com/questions/brazil-specific-information-to-open-a-stripe-account | [F] |
| Impostos e câmbio da venda ao exterior | Só blogs de contabilidade (por exemplo contabilidadezen.com.br) falam de contrato de câmbio, ISS e PIS/COFINS em exportação; nenhuma página oficial foi lida | — | [T]; **perguntar a um contador** |

## Leitura
- [F] Gumroad e Lemon Squeezy não listam o Brasil para saque em conta bancária. No Gumroad o caminho é o PayPal em USD, com 2% de taxa de saque, e depende de o PayPal aceitar a conta; a regra do PayPal para o Brasil NÃO foi lida em página oficial.
- [F] Hotmart e Payhip declaram recursos internacionais (moedas, impostos europeus), mas as páginas lidas não dizem se um vendedor brasileiro recebe em reais ou em dólar.
- [NV] A viabilidade fiscal (CPF ou CNPJ, câmbio, imposto sobre receita do exterior) não foi pesquisada em fonte oficial. É pergunta para contador antes da primeira venda.
