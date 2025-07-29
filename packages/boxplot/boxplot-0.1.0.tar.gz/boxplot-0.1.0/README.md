# boxplot
este é um programa que visa calcular os quartis em um boxplot baseado em uma lista X de números. boxplot é uma maneira de construir medias mais precisas, eliminando valores absurdos em relação ao demais, criando uma "média mais realista".

# fórmula de calculo
para dizer que um valor é "absurdo" ele deve ser menor que o minimo ou maior que o máximo, estes são definidos com fórmulas arbitrarias
```
minimo = q1 - 1.5*(q3-q1)
maximo = q3 + 1.5*(q3-q1)
```
