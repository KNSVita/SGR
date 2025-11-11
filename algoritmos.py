def merge_sort(lista: list, key: str, descending: bool = False):
    """
    Ordena uma lista de dicionarios com base em uma chave 
    usando o algoritmo de Merge Sort.

    Args:
        lista (list): Lista de dicionarios a ser ordenada.
        key (str): Chave com base na qual a lista sera ordenada.
        descending (bool): Indica se a ordena o sera descendente ou ascendente (padr o False).

    Returns:
        list: Lista ordenada.
    """
    if len(lista) <= 1:
        return lista

    meio = len(lista) // 2
    metade_esquerda = lista[:meio]
    metade_direita = lista[meio:]

    esquerda_ordenada = merge_sort(metade_esquerda, key, descending)
    direita_ordenada = merge_sort(metade_direita, key, descending)

    return merge(esquerda_ordenada, direita_ordenada, key, descending)


def merge(esquerda: list, direita: list, key: str, descending: bool):
    """
    Une as duas listas ordenadas em uma unica lista tambem ordenada.

    Args:
        esquerda (list): Primeira lista ordenada.
        direita (list): Segunda lista ordenada.
        key (str): Chave com base na qual a lista sera ordenada.
        descending (bool): Indica se a ordena o sera descendente ou ascendente (padr o False).

    Returns:
        list: Lista ordenada.
    """
    resultado = []
    idx_esq = idx_dir = 0

    while idx_esq < len(esquerda) and idx_dir < len(direita):
        valor_esq = esquerda[idx_esq][key]
        valor_dir = direita[idx_dir][key]

        if descending:
            if valor_esq >= valor_dir:
                resultado.append(esquerda[idx_esq])
                idx_esq += 1
            else:
                resultado.append(direita[idx_dir])
                idx_dir += 1
        else:
            if valor_esq <= valor_dir:
                resultado.append(esquerda[idx_esq])
                idx_esq += 1
            else:
                resultado.append(direita[idx_dir])
                idx_dir += 1

    resultado.extend(esquerda[idx_esq:])
    resultado.extend(direita[idx_dir:])
    
    return resultado