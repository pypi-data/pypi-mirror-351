import re

def mediana(x):
    if x == []: raise ValueError("lista invalida")
    x = sorted(x)
    comprimento = len(x)
    meio = comprimento // 2
    
    if comprimento % 2 == 0:
        return (x[meio] + x[meio -1])/2
    return x[meio]

def quartis(x, largura=50, raw=False):
    if x == []: raise ValueError("lista invalida")
    comprimento = len(x)
    meio = comprimento // 2
    
    q2 = mediana(x)
    q1 = mediana(x[:meio])
    q3 = mediana(x[meio:])
    
    if comprimento % 2 != 0:
        q3 = mediana(x[meio+1:])
    
    print(f"lista{x}")

    minimo = q1 - 1.5*(q3-q1)
    maximo = q3 + 1.5*(q3-q1)

    if raw:
        return f"min: {minimo:.2f}, q1: {q1:.2f}, q2: {q2:.2f}, q3: {q3:.2f}, max: {maximo:.2f}"

    # mapeia valores para posições numa linha de largura
    def escala(valor):
        return int((valor - minimo) / (maximo - minimo) * (largura - 1)) if maximo != minimo else largura // 2

    pos = {
        'min': escala(minimo),
        'q1': escala(q1),
        'q2': escala(q2),
        'q3': escala(q3),
        'max': escala(maximo)
    }

    linha = [' '] * largura
    linha[pos['min']] = '['
    linha[pos['q1']] = '|'
    linha[pos['q2']] = '|'
    linha[pos['q3']] = '|'
    linha[pos['max']] = ']'

    print("".join(linha))

    valores = [' '] * largura
    valores[pos['min']] = f"{minimo:.2f}"
    valores[pos['q1']] = f"{q1:.2f}"
    valores[pos['q2']] = f"{q2:.2f}"
    valores[pos['q3']] = f"{q3:.2f}"
    valores[pos['max']] = f"{maximo:.2f}"

    linha_valores = [' '] * largura
    for i in sorted(pos.values()):
        v = valores[i]
        for j, ch in enumerate(v):
            if i + j < largura:
                linha_valores[i + j] = ch

    return "".join(linha_valores)

def atipicos(x):
    atipicos = []
    match = re.search(r"min: (-?\d+\.?\d*),.*max: (-?\d+\.?\d*)", quartis(x, raw=True))

    if not match:
        return []

    minimo = float(match.group(1))
    maximo = float(match.group(2))

    for num in x:
        if num > maximo or num < minimo:
            atipicos.append(num)

    return atipicos