import sys
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QMessageBox,
    QComboBox, QLineEdit, QTabWidget
)
from PySide6.QtCore import Qt
from banco import conectar, criar_banco
from estilo import APP_STYLE

DIAS_PT = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]

class Totem(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cantina IFSP CJO - Totem")
        self.resize(1100, 700)
        self.carrinho = []
        self.nome_cliente = ""
        self.montar_tela()
        self.carregar_cardapio()

    def montar_tela(self):
        principal = QVBoxLayout(self)

        titulo = QLabel("🍔 CANTINA IFSP CJO")
        titulo.setObjectName("titulo")
        principal.addWidget(titulo)

        nome_layout = QHBoxLayout()
        nome_layout.addWidget(QLabel("Nome do aluno:"))
        self.nome = QLineEdit()
        self.nome.setPlaceholderText("Digite seu nome para começar o pedido")
        nome_layout.addWidget(self.nome)
        principal.addLayout(nome_layout)

        corpo = QHBoxLayout()
        esquerda = QVBoxLayout()

        self.abas = QTabWidget()
        esquerda.addWidget(self.abas)

        for categoria in ["Salgados", "Bebidas"]:
            lista = QListWidget()
            lista.itemDoubleClicked.connect(self.adicionar_item)
            self.abas.addTab(lista, categoria)

        self.almoco_lista = QListWidget()
        self.almoco_lista.itemDoubleClicked.connect(self.adicionar_almoco)
        self.abas.addTab(self.almoco_lista, "🍛 Almoço")

        esquerda.addWidget(QLabel("Clique duas vezes no item para adicionar ao pedido."))

        direita = QVBoxLayout()
        titulo_pedido = QLabel("🛒 SEU PEDIDO")
        titulo_pedido.setStyleSheet("font-size: 23px; font-weight: bold;")
        direita.addWidget(titulo_pedido)

        self.lista = QListWidget()
        direita.addWidget(self.lista)

        self.total = QLabel("TOTAL: R$ 0,00")
        self.total.setStyleSheet("font-size: 23px; font-weight: bold;")
        direita.addWidget(self.total)

        self.pagamento = QComboBox()
        self.pagamento.addItems(["Pix", "Cartão", "Dinheiro"])
        direita.addWidget(QLabel("Forma de pagamento:"))
        direita.addWidget(self.pagamento)

        remover = QPushButton("🗑 Remover item")
        remover.clicked.connect(self.remover_item)
        direita.addWidget(remover)

        finalizar = QPushButton("FINALIZAR PEDIDO")
        finalizar.setStyleSheet("font-size: 18px; font-weight: bold; padding: 14px;")
        finalizar.clicked.connect(self.finalizar)
        direita.addWidget(finalizar)

        corpo.addLayout(esquerda, 2)
        corpo.addLayout(direita, 1)
        principal.addLayout(corpo)

    def carregar_cardapio(self):
        for i in range(2):
            self.abas.widget(i).clear()
        self.almoco_lista.clear()

        conn = conectar()
        produtos = conn.execute("""
            SELECT id, nome, categoria, preco
            FROM produtos
            WHERE ativo = 1
            ORDER BY categoria, nome
        """).fetchall()

        hoje_num = datetime.now().weekday()
        dia = DIAS_PT[hoje_num] if hoje_num < 5 else None
        almoco = None
        if dia:
            almoco = conn.execute(
                "SELECT id, descricao, preco FROM almocos WHERE dia = ? AND ativo = 1",
                (dia,)
            ).fetchone()
        conn.close()

        for produto in produtos:
            produto_id, nome, categoria, preco = produto
            for i in range(2):
                if self.abas.tabText(i) == categoria:
                    item = QListWidgetItem(f"{nome}\nR$ {preco:.2f}")
                    item.setData(Qt.UserRole, ("produto", produto_id, nome, preco))
                    item.setSizeHint(item.sizeHint() * 1.25)
                    self.abas.widget(i).addItem(item)

        if dia and almoco and almoco[1] != "Não definido":
            item = QListWidgetItem(
                f"🍛 ALMOÇO DE HOJE ({dia.upper()})\n{almoco[1]}\nR$ {almoco[2]:.2f}"
            )
            item.setData(Qt.UserRole, ("almoco", almoco[0], "Almoço - " + almoco[1], almoco[2]))
            self.almoco_lista.addItem(item)
        else:
            self.almoco_lista.addItem("Almoço de hoje ainda não definido.")

    def adicionar_item(self, item):
        if not self.nome.text().strip():
            QMessageBox.warning(self, "Nome necessário", "Digite seu nome antes de fazer o pedido.")
            self.nome.setFocus()
            return
        self.carrinho.append(item.data(Qt.UserRole))
        self.atualizar_carrinho()

    def adicionar_almoco(self, item):
        dados = item.data(Qt.UserRole)
        if not dados:
            return
        if not self.nome.text().strip():
            QMessageBox.warning(self, "Nome necessário", "Digite seu nome antes de fazer o pedido.")
            self.nome.setFocus()
            return
        self.carrinho.append(dados)
        self.atualizar_carrinho()

    def atualizar_carrinho(self):
        self.lista.clear()
        total = 0
        for tipo, produto_id, nome, preco in self.carrinho:
            self.lista.addItem(f"{nome} - R$ {preco:.2f}")
            total += preco
        self.total.setText(f"TOTAL: R$ {total:.2f}")

    def remover_item(self):
        linha = self.lista.currentRow()
        if linha >= 0:
            self.carrinho.pop(linha)
            self.atualizar_carrinho()

    def finalizar(self):
        nome = self.nome.text().strip()
        if not nome:
            QMessageBox.warning(self, "Nome necessário", "Digite seu nome.")
            return
        if not self.carrinho:
            QMessageBox.warning(self, "Pedido vazio", "Adicione pelo menos um item.")
            return

        total = sum(item[3] for item in self.carrinho)
        pagamento = self.pagamento.currentText()

        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO pedidos (nome_cliente, total, pagamento, status)
            VALUES (?, ?, ?, 'Recebido')
        """, (nome, total, pagamento))
        pedido_id = cur.lastrowid

        contagem = {}
        for item in self.carrinho:
            chave = (item[1], item[2], item[3])
            contagem[chave] = contagem.get(chave, 0) + 1

        for (produto_id, nome_produto, preco), quantidade in contagem.items():
            cur.execute("""
                INSERT INTO itens_pedido
                (pedido_id, produto_id, nome_produto, preco, quantidade)
                VALUES (?, ?, ?, ?, ?)
            """, (pedido_id, produto_id, nome_produto, preco, quantidade))

        conn.commit()
        conn.close()

        QMessageBox.information(
            self, "Pedido realizado",
            f"PEDIDO #{pedido_id}\n\n"
            f"Nome: {nome}\n"
            f"Total: R$ {total:.2f}\n"
            f"Pagamento: {pagamento}\n\n"
            "Seu pedido foi enviado para a cozinha!"
        )

        self.carrinho.clear()
        self.nome.clear()
        self.atualizar_carrinho()

if __name__ == "__main__":
    criar_banco()
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QPushButton { padding: 10px; }
        QListWidget { font-size: 16px; }
        QLineEdit { padding: 8px; font-size: 15px; }
    """)
    janela = Totem()
    janela.show()
    sys.exit(app.exec())
