import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from PyQt5.QtCore import Qt

class PrinterCostCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora Universal de Custo por Hora - Impressoras")
        self.setGeometry(100, 100, 500, 600)

        # Widget principal e layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Título
        title_label = QLabel("Calculadora de Custo por Hora de Impressora")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Campos de entrada para tinta
        layout.addWidget(QLabel("=== Consumo de Tinta ==="))
        self.black_ink_consumption = QLineEdit()
        self.black_ink_consumption.setPlaceholderText("Ex.: 15.0 (mL/hora)")
        layout.addWidget(QLabel("Consumo de tinta preta por hora (mL/hora):"))
        layout.addWidget(self.black_ink_consumption)

        self.color_ink_consumption = QLineEdit()
        self.color_ink_consumption.setPlaceholderText("Ex.: 27.0 (mL/hora)")
        layout.addWidget(QLabel("Consumo de tinta colorida por hora (mL/hora):"))
        layout.addWidget(self.color_ink_consumption)

        self.ink_kit_capacity = QLineEdit()
        self.ink_kit_capacity.setPlaceholderText("Ex.: 260.0 (mL)")
        layout.addWidget(QLabel("Capacidade total do kit de tinta (mL):"))
        layout.addWidget(self.ink_kit_capacity)

        self.ink_kit_cost = QLineEdit()
        self.ink_kit_cost.setPlaceholderText("Ex.: 60.00 (R$)")
        layout.addWidget(QLabel("Custo do kit de tinta (R$):"))
        layout.addWidget(self.ink_kit_cost)

        # Campos de entrada para energia
        layout.addWidget(QLabel("=== Consumo de Energia ==="))
        self.printer_wattage = QLineEdit()
        self.printer_wattage.setPlaceholderText("Ex.: 50.0 (watts)")
        layout.addWidget(QLabel("Potência da impressora em modo impressão (watts):"))
        layout.addWidget(self.printer_wattage)

        self.energy_cost_per_kwh = QLineEdit()
        self.energy_cost_per_kwh.setPlaceholderText("Ex.: 0.80 (R$/kWh)")
        layout.addWidget(QLabel("Custo da energia por kWh (R$/kWh):"))
        layout.addWidget(self.energy_cost_per_kwh)

        # Campo para outros custos
        layout.addWidget(QLabel("=== Outros Custos ==="))
        self.other_costs_per_hour = QLineEdit()
        self.other_costs_per_hour.setPlaceholderText("Ex.: 0.50 (R$/hora, opcional)")
        layout.addWidget(QLabel("Outros custos por hora (R$/hora, opcional):"))
        layout.addWidget(self.other_costs_per_hour)

        # Botão de cálculo
        self.calculate_button = QPushButton("Calcular Custo por Hora")
        self.calculate_button.clicked.connect(self.calculate_cost)
        layout.addWidget(self.calculate_button)

        # Área de resultados
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        layout.addWidget(QLabel("=== Resultados ==="))
        layout.addWidget(self.result_area)

        layout.addStretch()

    def calculate_cost(self):
        try:
            # Obter e validar entradas
            black_ink = float(self.black_ink_consumption.text().replace(',', '.')) if self.black_ink_consumption.text() else 0.0
            color_ink = float(self.color_ink_consumption.text().replace(',', '.')) if self.color_ink_consumption.text() else 0.0
            ink_kit_capacity = float(self.ink_kit_capacity.text().replace(',', '.'))
            ink_kit_cost = float(self.ink_kit_cost.text().replace(',', '.'))
            printer_wattage = float(self.printer_wattage.text().replace(',', '.'))
            energy_cost_per_kwh = float(self.energy_cost_per_kwh.text().replace(',', '.'))
            other_costs = float(self.other_costs_per_hour.text().replace(',', '.')) if self.other_costs_per_hour.text() else 0.0

            if any(x <= 0 for x in [ink_kit_capacity, ink_kit_cost, printer_wattage, energy_cost_per_kwh]):
                self.result_area.setText("Erro: Todos os valores obrigatórios devem ser maiores que zero.")
                return
            if black_ink < 0 or color_ink < 0 or other_costs < 0:
                self.result_area.setText("Erro: Consumos e custos não podem ser negativos.")
                return

            # Cálculo do custo de tinta
            ink_cost_per_ml = ink_kit_cost / ink_kit_capacity
            total_ink_consumption = black_ink + color_ink
            ink_cost_per_hour = total_ink_consumption * ink_cost_per_ml

            # Cálculo do custo de energia
            energy_consumption_kwh = printer_wattage / 1000  # kWh/hora
            energy_cost_per_hour = energy_consumption_kwh * energy_cost_per_kwh

            # Custo total por hora
            total_cost_per_hour = ink_cost_per_hour + energy_cost_per_hour + other_costs

            # Exibir resultados
            result_text = (
                "=== Resultados ===\n"
                f"Consumo de tinta preta por hora: {black_ink:.2f} mL\n"
                f"Consumo de tinta colorida por hora: {color_ink:.2f} mL\n"
                f"Custo por mL (kit de R$ {ink_kit_cost:.2f}): R$ {ink_cost_per_ml:.4f}\n"
                f"Custo de tinta por hora: R$ {ink_cost_per_hour:.2f}\n\n"
                f"Consumo de energia por hora: {energy_consumption_kwh:.3f} kWh\n"
                f"Custo de energia por hora: R$ {energy_cost_per_hour:.2f}\n\n"
                f"Outros custos por hora: R$ {other_costs:.2f}\n\n"
                f"Custo total por hora: R$ {total_cost_per_hour:.2f}"
            )
            self.result_area.setText(result_text)

        except ValueError:
            self.result_area.setText("Erro: Digite valores numéricos válidos (ex.: 60.00). Use ponto ou vírgula para decimais.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PrinterCostCalculator()
    window.show()
    sys.exit(app.exec_())