import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout
)
from banco import conectar, criar_banco, itens_do_pedido
from estilo import APP_STYLE

class Cozinha(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cantina IFSP CJO - Cozinha")
        self.resize(1000, 650)

        layout = QVBoxLayout(self)

        titulo = QLabel("👨‍🍳 COZINHA - FILA DE PEDIDOS")
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(
            ["Pedido", "Cliente", "Itens", "Pagamento", "Status"]
        )
        self.tabela.setAlternatingRowColors(True)
        self.tabela.verticalHeader().setDefaultSectionSize(44)
        self.tabela.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.tabela)

        botoes = QHBoxLayout()
        for texto, status in [("▶ Preparar", "Em preparo"), ("✅ Pronto", "Pronto"), ("📦 Entregar", "Entregue")]:
            b = QPushButton(texto); b.clicked.connect(lambda _, s=status: self.mudar_status(s)); botoes.addWidget(b)
        atualizar = QPushButton("🔄 Atualizar"); atualizar.clicked.connect(self.carregar); botoes.addWidget(atualizar)
        layout.addLayout(botoes)

        self.carregar()

    def carregar(self):
        self.tabela.setRowCount(0)
        conn = conectar()
        pedidos = conn.execute("""
            SELECT id, nome_cliente, pagamento, status
            FROM pedidos
            WHERE status != 'Entregue'
            ORDER BY id
        """).fetchall()
        conn.close()

        for pedido_id, cliente, pagamento, status in pedidos:
            itens = itens_do_pedido(pedido_id)
            texto = ", ".join(f"{qtd}x {nome}" for nome, qtd, preco in itens)

            linha = self.tabela.rowCount()
            self.tabela.insertRow(linha)
            valores = [f"#{pedido_id}", cliente, texto, pagamento, status]
            for col, valor in enumerate(valores):
                self.tabela.setItem(linha, col, QTableWidgetItem(str(valor)))

    def mudar_status(self, status):
        linha = self.tabela.currentRow()
        if linha < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um pedido.")
            return

        pedido_id = self.tabela.item(linha, 0).text().replace("#", "")
        conn = conectar()
        conn.execute("UPDATE pedidos SET status = ? WHERE id = ?", (status, pedido_id))
        conn.commit()
        conn.close()
        self.carregar()

if __name__ == "__main__":
    criar_banco()
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    janela = Cozinha()
    janela.show()
    sys.exit(app.exec())
