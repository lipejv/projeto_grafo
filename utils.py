"""
Nesse módulo contém algumas funções úteis para o projeto.
"""


def formata_numero(num: str) -> str:
    """
    Formata um valor em string.
    """

    return num.replace('.', '').replace(',', '.').replace(' ', '')
