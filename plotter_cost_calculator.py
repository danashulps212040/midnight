import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from PyQt5.QtCore import Qt

class PlotterCostCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora Universal de Custo por Hora - Plotters de Recorte")
        self.setGeometry(100, 100, 500, 700)

        # Widget principal e layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Título
        title_label = QLabel("Calculadora de Custo por Hora de Plotter de Recorte")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Campo para cortes por hora
        layout.addWidget(QLabel("=== Produtividade ==="))
        self.cuts_per_hour = QLineEdit()
        self.cuts_per_hour.setPlaceholderText("Ex.: 80.0 (cortes/hora)")
        layout.addWidget(QLabel("Número de cortes por hora (cortes/hora):"))
        layout.addWidget(self.cuts_per_hour)

        # Campos para energia
        layout.addWidget(QLabel("=== Consumo de Energia ==="))
        self.plotter_wattage = QLineEdit()
        self.plotter_wattage.setPlaceholderText("Ex.: 40.0 (watts)")
        layout.addWidget(QLabel("Potência da plotter em modo corte (watts):"))
        layout.addWidget(self.plotter_wattage)

        self.energy_cost_per_kwh = QLineEdit()
        self.energy_cost_per_kwh.setPlaceholderText("Ex.: 0.80 (R$/kWh)")
        layout.addWidget(QLabel("Custo da energia por kWh (R$/kWh):"))
        layout.addWidget(self.energy_cost_per_kwh)

        # Campos para lâminas
        layout.addWidget(QLabel("=== Desgaste de Lâminas ==="))
        self.blade_cost = QLineEdit()
        self.blade_cost.setPlaceholderText("Ex.: 50.00 (R$)")
        layout.addWidget(QLabel("Custo de uma lâmina (R$):"))
        layout.addWidget(self.blade_cost)

        self.blade_cuts = QLineEdit()
        self.blade_cuts.setPlaceholderText("Ex.: 5000 (cortes)")
        layout.addWidget(QLabel("Número de cortes por lâmina (cortes):"))
        layout.addWidget(self.blade_cuts)

        # Campos para tapetes
        layout.addWidget(QLabel("=== Desgaste de Tapetes ==="))
        self.mat_cost = QLineEdit()
        self.mat_cost.setPlaceholderText("Ex.: 50.00 (R$)")
        layout.addWidget(QLabel("Custo de um tapete de corte (R$):"))
        layout.addWidget(self.mat_cost)

        self.mat_uses = QLineEdit()
        self.mat_uses.setPlaceholderText("Ex.: 100 (usos)")
        layout.addWidget(QLabel("Número de usos por tapete (usos):"))
        layout.addWidget(self.mat_uses)

        # Campo para outros custos
        layout.addWidget(QLabel("=== Outros Custos ==="))
        self.other_costs_per_hour = QLineEdit()
        self.other_costs_per_hour.setPlaceholderText("Ex.: 10.00 (R$/hora, opcional)")
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
            cuts_per_hour = float(self.cuts_per_hour.text().replace(',', '.'))
            plotter_wattage = float(self.plotter_wattage.text().replace(',', '.'))
            energy_cost_per_kwh = float(self.energy_cost_per_kwh.text().replace(',', '.'))
            blade_cost = float(self.blade_cost.text().replace(',', '.'))
            blade_cuts = float(self.blade_cuts.text().replace(',', '.'))
            mat_cost = float(self.mat_cost.text().replace(',', '.'))
            mat_uses = float(self.mat_uses.text().replace(',', '.'))
            other_costs = float(self.other_costs_per_hour.text().replace(',', '.')) if self.other_costs_per_hour.text() else 0.0

            if any(x <= 0 for x in [cuts_per_hour, plotter_wattage, energy_cost_per_kwh, blade_cost, blade_cuts, mat_cost, mat_uses]):
                self.result_area.setText("Erro: Todos os valores obrigatórios devem ser maiores que zero.")
                return
            if other_costs < 0:
                self.result_area.setText("Erro: Outros custos não podem ser negativos.")
                return

            # Cálculo do custo de energia
            energy_consumption_kwh = plotter_wattage / 1000  # kWh/hora
            energy_cost_per_hour = energy_consumption_kwh * energy_cost_per_kwh

            # Cálculo do custo de lâminas
            blade_cost_per_cut = blade_cost / blade_cuts
            blade_cost_per_hour = blade_cost_per_cut * cuts_per_hour

            # Cálculo do custo de tapetes
            mat_cost_per_use = mat_cost / mat_uses
            mat_cost_per_hour = mat_cost_per_use * cuts_per_hour

            # Custo total por hora
            total_cost_per_hour = energy_cost_per_hour + blade_cost_per_hour + mat_cost_per_hour + other_costs

            # Exibir resultados
            result_text = (
                "=== Resultados ===\n"
                f"Número de cortes por hora: {cuts_per_hour:.2f} cortes\n\n"
                f"Consumo de energia por hora: {energy_consumption_kwh:.3f} kWh\n"
                f"Custo de energia por hora: R$ {energy_cost_per_hour:.2f}\n\n"
                f"Custo por corte (lâmina): R$ {blade_cost_per_cut:.4f}\n"
                f"Custo de lâminas por hora: R$ {blade_cost_per_hour:.2f}\n\n"
                f"Custo por uso (tapete): R$ {mat_cost_per_use:.4f}\n"
                f"Custo de tapetes por hora: R$ {mat_cost_per_hour:.2f}\n\n"
                f"Outros custos por hora: R$ {other_costs:.2f}\n\n"
                f"Custo total por hora: R$ {total_cost_per_hour:.2f}"
            )
            self.result_area.setText(result_text)

        except ValueError:
            self.result_area.setText("Erro: Digite valores numéricos válidos (ex.: 80.00). Use ponto ou vírgula para decimais.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlotterCostCalculator()
    window.show()
    sys.exit(app.exec_())