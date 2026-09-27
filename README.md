# PROJETO-CANTINA-POOS
Projeto Cantina do Pablo.

## 3 computadores/programas

- `totem.py` — totem dos clientes.
- `cozinha.py` — fila e preparo dos pedidos.
- `pablo.py` — administração da cantina.

`banco.py` é compartilhado pelos três programas.

## Regras

- O cliente informa o nome antes de pedir.
- O pedido recebe um número e fica associado ao nome.
- Produtos podem ser alterados, suspensos ou excluídos pelo Pablo.
- Produtos suspensos não aparecem no totem.
- O almoço é administrado separadamente por dia da semana.
- O Pablo pode alterar o almoço de cada dia.
- O preço do almoço começa em R$ 20,00.
- Caçula 200 ml começa em R$ 3,50.

## Instalação

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Executar

Abra três terminais na pasta do projeto:

```bash
python totem.py
python cozinha.py
python pablo.py
```

O banco `cantina.db` é criado automaticamente.
