def adiciona(item, lista=None):
    if lista is None:
        lista = []
    lista.append(item)
    return lista


print(adiciona("pão"))
print(adiciona("leite"))
