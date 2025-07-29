# fk7py
Conjunto de scripts python para leitura e interpretação de arquivos FK7 de acordo com a norma ABNT NBR 14522.

## 🎯 Objetivo

Este projeto tem como objetivo facilitar a leitura e interpretação de arquivos FK7.
Os scripts deste projeto interpretam o arquivo FK7 de acordo com o que é apresentado na norma ABNT NBR 14522.

## 🖥️ QuickStart

```python
pip install fk7py
```

```python

from fk7py import FK7

caminho_do_arquivo_FK7 = 'C:/caminho/do/arquivo'

arquivo = FK7(caminho_do_arquivo)

# Imprime o número do medidor
print(arquivo.serial_medidor)  # Saída: 00000000

```

## 🧩 Interpretação dos Dados

Veja o progresso da interpretação dos dados no arquivo:

👉 [Tabela de Dados Interpretados](https://github.com/bruno-so25/fk7py/blob/main/progresso.md)


## 🌟 Componentes Básicos

### Atributos

##### `caminho_arquivo -> string`
String com o caminho do arquivo.

##### `dado_bruto -> string`
Dados do arquivo FK7 sem nenhum tratamento.

##### `hex_blocos -> list`
Dados do arquivo FK7 já convertidos em hexadecimais e separados em blocos de 256 octetos.

##### `enum_blocos -> list`
Lista de blocosdo arquivo FK7 já convertidos em hexadecimais.
Cada bloco com sua posição enumerada de 1 até 256.

##### `qtd_blocos -> int`
Quantidade de blocos (de 256 octetos) encontrados no arquivo FK7.

##### `bloco_presente -> dict`
Verifica a presença de blocos específicos. O tipo do bloco é determinando pelo primeiro octeto, podendo ser uma das opções a seguir:

'20', '21', '22', '51', '23', '24', '41', '44', '42', '43', '45', '46', '25', '26', '27', '52', '28', '80', '14'

Este atributo vem em forma de dicionário, onde as chaves são os octetos e os valores são True/False, sendo True indicando que o bloco está presente no arquivo FK7.

```python
print(arquivo.bloco_presente['20']) # Saída: True
```

##### `serial_medidor -> int`
Número serial do medidor.


##### `data_hora_atual -> datetime`
Data e hora encontrada no arquivo FK7.

### Métodos

#### `Interpretação de bloco`

```python
lerBlocos(bloco)
```

Recebe o bloco em formato de dicionário. Este argumento deve ser um item do atributo 'enum_blocos'.

Exemplo de uso:
```python
arquivo = FK7('C:/caminho/do/arquivo')

dados = arquivo.lerBloco(arquivo.enum_blocos[0])
```

