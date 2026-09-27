import sys
from PySide6.QtWidgets import (
    QHeaderView,
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QLineEdit,
    QDoubleSpinBox, QFormLayout, QGroupBox, QMessageBox,
    QTabWidget, QComboBox
)
from banco import conectar, criar_banco, DIAS
from estilo import APP_STYLE

class Pablo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cantina IFSP CJO - Painel do Pablo")
        self.resize(1100, 750)

        layout = QVBoxLayout(self)
        titulo = QLabel("👨‍💼 PAINEL DO PABLO - CANTINA")
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)

        resumo = QHBoxLayout()
        self.receitas = QLabel()
        self.despesas = QLabel()
        self.saldo = QLabel()
        self.caixa = QLabel()
        for label in [self.receitas, self.despesas, self.saldo, self.caixa]:
            label.setProperty("class", "card")
            resumo.addWidget(label)
        layout.addLayout(resumo)

        self.abas = QTabWidget()
        layout.addWidget(self.abas)

        self.criar_aba_pedidos()
        self.criar_aba_produtos()
        self.criar_aba_almoco()
        self.criar_aba_despesas()
        self.criar_aba_caixa()

        self.carregar()

    def criar_aba_pedidos(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        self.tabela_pedidos = QTableWidget()
        self.tabela_pedidos.setColumnCount(5)
        self.tabela_pedidos.setHorizontalHeaderLabels(
            ["Pedido", "Cliente", "Total", "Pagamento", "Status"]
        )
        self.configurar_tabela(self.tabela_pedidos)
        layout.addWidget(self.tabela_pedidos)
        botao = QPushButton("🔄 Atualizar")
        botao.clicked.connect(self.carregar)
        layout.addWidget(botao)
        self.abas.addTab(pagina, "📋 Pedidos")

    def criar_aba_produtos(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)

        self.tabela_produtos = QTableWidget()
        self.tabela_produtos.setColumnCount(5)
        self.tabela_produtos.setHorizontalHeaderLabels(
            ["ID", "Produto", "Categoria", "Preço", "Situação"]
        )
        self.configurar_tabela(self.tabela_produtos)
        layout.addWidget(self.tabela_produtos)

        form = QFormLayout()
        self.produto_id = QLineEdit()
        self.produto_nome = QLineEdit()
        self.produto_categoria = QComboBox()
        self.produto_categoria.addItems(["Salgados", "Bebidas"])
        self.produto_preco = QDoubleSpinBox()
        self.produto_preco.setMaximum(100000)
        self.produto_preco.setDecimals(2)
        self.produto_preco.setPrefix("R$ ")

        form.addRow("ID para editar:", self.produto_id)
        form.addRow("Nome:", self.produto_nome)
        form.addRow("Categoria:", self.produto_categoria)
        form.addRow("Preço:", self.produto_preco)
        layout.addLayout(form)

        botoes = QHBoxLayout()
        adicionar = QPushButton("➕ Adicionar")
        adicionar.clicked.connect(self.adicionar_produto)
        editar = QPushButton("✏️ Alterar")
        editar.clicked.connect(self.editar_produto)
        suspender = QPushButton("⛔ Suspender/Ativar")
        suspender.clicked.connect(self.alternar_produto)
        excluir = QPushButton("🗑️ Excluir")
        excluir.clicked.connect(self.excluir_produto)
        for b in [adicionar, editar, suspender, excluir]:
            botoes.addWidget(b)
        layout.addLayout(botoes)

        self.abas.addTab(pagina, "🍔 Produtos")

    def criar_aba_almoco(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)

        info = QLabel("🍛 ALMOÇO DA SEMANA — somente o Pablo pode editar")
        info.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(info)

        self.tabela_almoco = QTableWidget()
        self.tabela_almoco.setColumnCount(4)
        self.tabela_almoco.setHorizontalHeaderLabels(
            ["Dia", "Almoço", "Preço", "Ativo"]
        )
        self.configurar_tabela(self.tabela_almoco)
        layout.addWidget(self.tabela_almoco)

        form = QFormLayout()
        self.dia_almoco = QComboBox()
        self.dia_almoco.addItems(DIAS)
        self.descricao_almoco = QLineEdit()
        self.descricao_almoco.setPlaceholderText("Ex.: Strogonoff de frango")
        self.preco_almoco = QDoubleSpinBox()
        self.preco_almoco.setMaximum(100000)
        self.preco_almoco.setDecimals(2)
        self.preco_almoco.setValue(20.00)
        self.preco_almoco.setPrefix("R$ ")

        form.addRow("Dia:", self.dia_almoco)
        form.addRow("Almoço:", self.descricao_almoco)
        form.addRow("Preço:", self.preco_almoco)
        layout.addLayout(form)

        salvar = QPushButton("💾 Salvar almoço do dia")
        salvar.clicked.connect(self.salvar_almoco)
        layout.addWidget(salvar)

        self.abas.addTab(pagina, "🍛 Almoço")

    def criar_aba_despesas(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)

        form = QFormLayout()
        self.descricao_despesa = QLineEdit()
        self.valor_despesa = QDoubleSpinBox()
        self.valor_despesa.setMaximum(1000000)
        self.valor_despesa.setDecimals(2)
        self.valor_despesa.setPrefix("R$ ")
        form.addRow("Descrição:", self.descricao_despesa)
        form.addRow("Valor:", self.valor_despesa)
        layout.addLayout(form)

        botao = QPushButton("➕ Adicionar despesa")
        botao.clicked.connect(self.adicionar_despesa)
        layout.addWidget(botao)

        self.tabela_despesas = QTableWidget()
        self.tabela_despesas.setColumnCount(4)
        self.tabela_despesas.setHorizontalHeaderLabels(["ID", "Descrição", "Valor", "Ação"])
        self.configurar_tabela(self.tabela_despesas)
        layout.addWidget(self.tabela_despesas)

        self.abas.addTab(pagina, "💸 Despesas")

    def criar_aba_caixa(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.addWidget(QLabel("💵 CAIXA FÍSICO — dinheiro em espécie"))

        form = QFormLayout()
        self.caixa_descricao = QLineEdit()
        self.caixa_descricao.setPlaceholderText("Ex.: Abertura, sangria, troco...")
        self.caixa_valor = QDoubleSpinBox()
        self.caixa_valor.setMaximum(1000000)
        self.caixa_valor.setDecimals(2)
        self.caixa_valor.setPrefix("R$ ")
        self.caixa_tipo = QComboBox()
        self.caixa_tipo.addItems(["Entrada", "Saída"])
        form.addRow("Descrição:", self.caixa_descricao)
        form.addRow("Tipo:", self.caixa_tipo)
        form.addRow("Valor:", self.caixa_valor)
        layout.addLayout(form)

        botao = QPushButton("💾 Registrar movimento")
        botao.clicked.connect(self.adicionar_movimento_caixa)
        layout.addWidget(botao)

        self.tabela_caixa = QTableWidget()
        self.tabela_caixa.setColumnCount(4)
        self.tabela_caixa.setHorizontalHeaderLabels(["ID", "Descrição", "Tipo", "Valor"])
        self.configurar_tabela(self.tabela_caixa)
        layout.addWidget(self.tabela_caixa)
        self.abas.addTab(pagina, "💵 Caixa")

    def configurar_tabela(self, tabela):
        tabela.setAlternatingRowColors(True)
        tabela.verticalHeader().setDefaultSectionSize(36)
        tabela.horizontalHeader().setStretchLastSection(True)
        tabela.horizontalHeader().setSectionResizeMode(tabela.horizontalHeader().Stretch if False else QHeaderView.Stretch)

    def carregar(self):
        conn = conectar()

        receitas = conn.execute(
            "SELECT COALESCE(SUM(total), 0) FROM pedidos WHERE status = 'Entregue'"
        ).fetchone()[0]
        despesas = conn.execute(
            "SELECT COALESCE(SUM(valor), 0) FROM despesas"
        ).fetchone()[0]
        caixa_mov = conn.execute(
            "SELECT COALESCE(SUM(CASE WHEN tipo='Entrada' THEN valor ELSE -valor END), 0) FROM caixa_movimentos"
        ).fetchone()[0]
        dinheiro = conn.execute(
            "SELECT COALESCE(SUM(total), 0) FROM pedidos WHERE status='Entregue' AND pagamento='Dinheiro'"
        ).fetchone()[0]
        caixa_saldo = caixa_mov + dinheiro

        pedidos = conn.execute(
            "SELECT id, nome_cliente, total, pagamento, status FROM pedidos ORDER BY id DESC"
        ).fetchall()
        produtos = conn.execute(
            "SELECT id, nome, categoria, preco, ativo FROM produtos ORDER BY categoria, nome"
        ).fetchall()
        almocos = conn.execute(
            "SELECT dia, descricao, preco, ativo FROM almocos ORDER BY id"
        ).fetchall()
        despesas_lista = conn.execute(
            "SELECT id, descricao, valor FROM despesas ORDER BY id DESC"
        ).fetchall()
        caixa_lista = conn.execute(
            "SELECT id, descricao, tipo, valor FROM caixa_movimentos ORDER BY id DESC"
        ).fetchall()
        conn.close()

        self.receitas.setText(f"💰 Receitas: R$ {receitas:.2f}")
        self.despesas.setText(f"💸 Despesas: R$ {despesas:.2f}")
        self.saldo.setText(f"💵 Saldo: R$ {receitas - despesas:.2f}")
        self.caixa.setText(f"💵 Caixa físico: R$ {caixa_saldo:.2f}")

        self.tabela_pedidos.setRowCount(0)
        for pedido in pedidos:
            linha = self.tabela_pedidos.rowCount()
            self.tabela_pedidos.insertRow(linha)
            valores = [f"#{pedido[0]}", pedido[1], f"R$ {pedido[2]:.2f}", pedido[3], pedido[4]]
            for col, valor in enumerate(valores):
                self.tabela_pedidos.setItem(linha, col, QTableWidgetItem(str(valor)))

        self.tabela_produtos.setRowCount(0)
        for produto in produtos:
            linha = self.tabela_produtos.rowCount()
            self.tabela_produtos.insertRow(linha)
            situacao = "Ativo" if produto[4] else "Suspenso"
            valores = [produto[0], produto[1], produto[2], f"R$ {produto[3]:.2f}", situacao]
            for col, valor in enumerate(valores):
                self.tabela_produtos.setItem(linha, col, QTableWidgetItem(str(valor)))

        self.tabela_almoco.setRowCount(0)
        for almoco in almocos:
            linha = self.tabela_almoco.rowCount()
            self.tabela_almoco.insertRow(linha)
            valores = [almoco[0], almoco[1], f"R$ {almoco[2]:.2f}", "Sim" if almoco[3] else "Não"]
            for col, valor in enumerate(valores):
                self.tabela_almoco.setItem(linha, col, QTableWidgetItem(str(valor)))

        self.tabela_despesas.setRowCount(0)
        for item in despesas_lista:
            linha = self.tabela_despesas.rowCount()
            self.tabela_despesas.insertRow(linha)
            valores = [item[0], item[1], f"R$ {item[2]:.2f}"]
            for col, valor in enumerate(valores):
                self.tabela_despesas.setItem(linha, col, QTableWidgetItem(str(valor)))

            botao_excluir = QPushButton("🗑️ Excluir despesa")
            botao_excluir.clicked.connect(
                lambda checked=False, despesa_id=item[0]: self.excluir_despesa(despesa_id)
            )
            self.tabela_despesas.setCellWidget(linha, 3, botao_excluir)

        self.tabela_caixa.setRowCount(0)
        for item in caixa_lista:
            linha = self.tabela_caixa.rowCount()
            self.tabela_caixa.insertRow(linha)
            valores = [item[0], item[1], item[2], f"R$ {item[3]:.2f}"]
            for col, valor in enumerate(valores):
                self.tabela_caixa.setItem(linha, col, QTableWidgetItem(str(valor)))

    def adicionar_movimento_caixa(self):
        descricao = self.caixa_descricao.text().strip()
        valor = self.caixa_valor.value()
        tipo = self.caixa_tipo.currentText()
        if not descricao or valor <= 0:
            QMessageBox.warning(self, "Atenção", "Informe descrição e valor.")
            return
        conn = conectar()
        conn.execute("INSERT INTO caixa_movimentos (descricao, tipo, valor) VALUES (?, ?, ?)",
                     (descricao, tipo, valor))
        conn.commit()
        conn.close()
        self.caixa_descricao.clear()
        self.caixa_valor.setValue(0)
        self.carregar()

    def adicionar_produto(self):
        nome = self.produto_nome.text().strip()
        categoria = self.produto_categoria.currentText()
        preco = self.produto_preco.value()
        if not nome or preco <= 0:
            QMessageBox.warning(self, "Atenção", "Informe nome e preço.")
            return
        conn = conectar()
        conn.execute(
            "INSERT INTO produtos (nome, categoria, preco, ativo) VALUES (?, ?, ?, 1)",
            (nome, categoria, preco)
        )
        conn.commit()
        conn.close()
        self.limpar_produto()
        self.carregar()

    def editar_produto(self):
        try:
            pid = int(self.produto_id.text())
        except ValueError:
            QMessageBox.warning(self, "Atenção", "Informe um ID válido.")
            return
        nome = self.produto_nome.text().strip()
        preco = self.produto_preco.value()
        categoria = self.produto_categoria.currentText()
        if not nome or preco <= 0:
            QMessageBox.warning(self, "Atenção", "Informe nome e preço.")
            return
        conn = conectar()
        cur = conn.cursor()
        cur.execute(
            "UPDATE produtos SET nome=?, categoria=?, preco=? WHERE id=?",
            (nome, categoria, preco, pid)
        )
        conn.commit()
        alterados = cur.rowcount
        conn.close()
        if not alterados:
            QMessageBox.warning(self, "Atenção", "Produto não encontrado.")
        else:
            self.limpar_produto()
            self.carregar()

    def alternar_produto(self):
        try:
            pid = int(self.produto_id.text())
        except ValueError:
            QMessageBox.warning(self, "Atenção", "Informe o ID do produto.")
            return
        conn = conectar()
        conn.execute(
            "UPDATE produtos SET ativo = CASE WHEN ativo=1 THEN 0 ELSE 1 END WHERE id=?",
            (pid,)
        )
        conn.commit()
        conn.close()
        self.carregar()

    def excluir_produto(self):
        try:
            pid = int(self.produto_id.text())
        except ValueError:
            QMessageBox.warning(self, "Atenção", "Informe o ID do produto.")
            return
        resposta = QMessageBox.question(
            self, "Excluir", "Tem certeza que deseja excluir este produto?"
        )
        if resposta != QMessageBox.Yes:
            return
        conn = conectar()
        conn.execute("DELETE FROM produtos WHERE id=?", (pid,))
        conn.commit()
        conn.close()
        self.limpar_produto()
        self.carregar()

    def limpar_produto(self):
        self.produto_id.clear()
        self.produto_nome.clear()
        self.produto_preco.setValue(0)

    def salvar_almoco(self):
        dia = self.dia_almoco.currentText()
        descricao = self.descricao_almoco.text().strip()
        preco = self.preco_almoco.value()
        if not descricao or preco <= 0:
            QMessageBox.warning(self, "Atenção", "Informe o almoço e o preço.")
            return
        conn = conectar()
        conn.execute(
            "UPDATE almocos SET descricao=?, preco=?, ativo=1 WHERE dia=?",
            (descricao, preco, dia)
        )
        conn.commit()
        conn.close()
        self.descricao_almoco.clear()
        self.preco_almoco.setValue(20.00)
        self.carregar()

    def excluir_despesa(self, despesa_id):
        resposta = QMessageBox.question(
            self,
            "Confirmar exclusão",
            "Tem certeza que deseja excluir esta despesa?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if resposta != QMessageBox.Yes:
            return

        conn = conectar()
        conn.execute("DELETE FROM despesas WHERE id=?", (despesa_id,))
        conn.commit()
        conn.close()
        self.carregar()

    def adicionar_despesa(self):
        descricao = self.descricao_despesa.text().strip()
        valor = self.valor_despesa.value()
        if not descricao or valor <= 0:
            QMessageBox.warning(self, "Atenção", "Informe descrição e valor.")
            return
        conn = conectar()
        conn.execute(
            "INSERT INTO despesas (descricao, valor) VALUES (?, ?)",
            (descricao, valor)
        )
        conn.commit()
        conn.close()
        self.descricao_despesa.clear()
        self.valor_despesa.setValue(0)
        self.carregar()

if __name__ == "__main__":
    criar_banco()
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    janela = Pablo()
    janela.show()
    sys.exit(app.exec())
