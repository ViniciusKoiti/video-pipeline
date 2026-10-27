---
name: analise-de-binario
description: Analisa um executável sem o código-fonte. Use quando o usuário pedir para entender o que um binário faz.
---

# Análise de binário sem o código

1. Identifique o arquivo: `file <binario>`. Anote formato e arquitetura.
2. Procure texto: `strings -n 6 <binario>`. Liste só o que o programa imprime.
3. Desmonte: `objdump -d -M intel <binario>`. Ache a função que decide o resultado.
4. Cada afirmação sobre o binário precisa apontar para uma linha da saída real.
5. Confirme a hipótese reproduzindo a entrada. Não afirme o que não foi reproduzido.
