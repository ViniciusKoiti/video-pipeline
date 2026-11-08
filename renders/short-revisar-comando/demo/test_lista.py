from lista import adiciona


def test_lista_nova_a_cada_chamada():
    adiciona("pão")
    assert adiciona("leite") == ["leite"]
