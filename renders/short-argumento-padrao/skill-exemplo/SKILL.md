---
name: achar-argumento-mutavel
description: Procura em código Python um valor que vaza entre chamadas, como argumento padrão mutável. Use quando o usuário disser que uma função "guarda coisa de uma chamada para outra" ou o resultado muda sem motivo.
---

# Achar argumento padrão mutável

1. Reproduza o erro: chame a função duas vezes com entradas diferentes e compare com o resultado esperado. Se a segunda chamada traz dados da primeira, siga.
2. Rode o interpretador sem esperar aviso: `python3 <arquivo>`. Ele não avisa; anote que o erro é silencioso.
3. Procure o padrão com o ruff: `ruff check --isolated --select B006 <arquivo>`. Anote a linha `-->` do aviso.
4. Abra a linha citada e confirme que o padrão padrão é uma lista, dict ou set (`=[]`, `={}`, `=set()`).
5. Corrija com `None` e crie o objeto dentro da função. Rode as duas chamadas de novo e o ruff. Só afirme que está certo se a saída bate.
6. Cada afirmação sobre o código aponta para uma linha da saída real. Não afirme o que não foi reproduzido.
