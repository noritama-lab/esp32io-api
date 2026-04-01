import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QSlider, QComboBox,
    QStatusBar, QMessageBox, QFrame,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from pyside6stylekit import (
    Theme, IndusAlternateButton, IndusLamp,
    StyledButton, StyledLabel
)

from esp32io import ESP32IO
import serial

class ESP32IOTestUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.esp = None
        
        # テーマ設定
        self.lbl_theme = Theme(primary="green", mode="dark", size="small", text_color="white")
        self.btn_theme = Theme(primary="blue", mode="dark", size="small", text_color="black")
        self.indus_btn_theme = Theme(primary="green", mode="dark", size="small", text_color="white")
        self.indus_lamp_theme = Theme(primary="green", mode="dark", size="small", text_color="white")
        
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self.refresh_di_adc)
        
        self.setWindowTitle("ESP32IO Test UI")
        self.setGeometry(100, 100, 300, 400)
        
        # UI コンポーネントの辞書
        self.dio_buttons = {}  # pin_id: IndusAlternateButton
        self.di_lamps = {}     # pin_id: IndusLamp
        self.adc_labels = {}   # pin_id: StyledLabel
        self.pwm_sliders = {}  # pin_id: QSlider
        
        self.setup_ui()
        
    def setup_ui(self):
        """UI コンポーネントを設定"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # ===== 接続設定 =====
        connection_group = QGroupBox("接続設定")
        conn_layout = QHBoxLayout()
        
        conn_layout.addWidget(StyledLabel("COM ポート:", theme=self.lbl_theme))
        self.port_combo = QComboBox()
        self.port_combo.addItems(self.get_available_ports())
        conn_layout.addWidget(self.port_combo)
        
        self.connect_btn = StyledButton("接続", theme=self.btn_theme)
        self.connect_btn.clicked.connect(self.connect_esp32)
        conn_layout.addWidget(self.connect_btn)
        
        self.disconnect_btn = StyledButton("切断", theme=self.btn_theme)
        self.disconnect_btn.clicked.connect(self.disconnect_esp32)
        self.disconnect_btn.setEnabled(False)
        conn_layout.addWidget(self.disconnect_btn)
        
        self.auto_refresh_btn = StyledButton("自動更新: OFF", theme=self.btn_theme)
        self.auto_refresh_btn.setCheckable(True)
        self.auto_refresh_btn.toggled.connect(self.toggle_auto_refresh)
        self.auto_refresh_btn.setEnabled(False)
        conn_layout.addWidget(self.auto_refresh_btn)
        
        connection_group.setLayout(conn_layout)
        main_layout.addWidget(connection_group)
        
        # ===== DIO 出力（ボタン6個）=====
        do_group = QGroupBox("DIO 出力 - set_do (PIN 0~5)")
        do_layout = QHBoxLayout()
        for i in range(6):
            btn = IndusAlternateButton(f"PIN{i}", self.indus_btn_theme, diameter=48)
            btn.toggled.connect(lambda checked, pin_id=i: self.on_do_toggle(pin_id, checked))
            self.dio_buttons[i] = btn
            do_layout.addWidget(btn)
        do_group.setLayout(do_layout)
        main_layout.addWidget(do_group)
        
        # ===== DIO 入力（ランプ6個）=====
        di_group = QGroupBox("DIO 入力 - read_di (PIN 0~5)")
        di_layout = QHBoxLayout()
        for i in range(6):
            lamp = IndusLamp(f"PIN{i}", self.indus_lamp_theme, diameter=48, state=False)
            self.di_lamps[i] = lamp
            di_layout.addWidget(lamp)
        di_group.setLayout(di_layout)
        main_layout.addWidget(di_group)
        
        # ===== ADC 読み取り（表示2個）=====
        adc_group = QGroupBox("ADC 読み取り - read_adc (PIN 0~1)")
        adc_layout = QHBoxLayout()
        for i in range(2):
            frame = QFrame()
            frame.setFrameStyle(QFrame.Box | QFrame.Raised)
            frame.setLineWidth(2)
            layout = QVBoxLayout()
            
            label = StyledLabel(f"PIN{i}", theme=self.lbl_theme)
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont("Arial", 10, QFont.Bold))
            
            value = StyledLabel("0", theme=self.lbl_theme)
            value.setAlignment(Qt.AlignCenter)
            value.setFont(QFont("Arial", 14, QFont.Bold))
            
            layout.addWidget(label)
            layout.addWidget(value)
            frame.setLayout(layout)
            
            self.adc_labels[i] = value
            adc_layout.addWidget(frame)
        adc_group.setLayout(adc_layout)
        main_layout.addWidget(adc_group)
        
        # ===== PWM 出力（スライダー2個）=====
        pwm_group = QGroupBox("PWM 出力 - set_pwm (PIN 0~1)")
        pwm_layout = QHBoxLayout()
        for i in range(2):
            frame = QFrame()
            frame.setFrameStyle(QFrame.Box | QFrame.Raised)
            frame.setLineWidth(2)
            layout = QVBoxLayout()
            
            label = StyledLabel(f"PIN{i}", theme=self.lbl_theme)
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont("Arial", 10, QFont.Bold))
            
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 255)
            slider.setValue(0)
            slider.sliderMoved.connect(lambda value, pin_id=i: self.on_pwm_change(pin_id, value))
            
            value_label = StyledLabel("0", theme=self.lbl_theme)
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setFont(QFont("Arial", 12, QFont.Bold))
            value_label.setMinimumWidth(40)
            
            slider.sliderMoved.connect(lambda value, label=value_label: label.setText(str(value)))
            
            layout.addWidget(label)
            layout.addWidget(slider)
            layout.addWidget(value_label)
            frame.setLayout(layout)
            
            self.pwm_sliders[i] = (slider, value_label)
            pwm_layout.addWidget(frame)
        pwm_group.setLayout(pwm_layout)
        main_layout.addWidget(pwm_group)
        
        # ステータスバー
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("切断状態")
        
        # 初期状態：ボタン無効化
        self.set_buttons_enabled(False)
    
    def get_available_ports(self):
        """利用可能な COM ポートを取得"""
        ports = []
        for i in range(1, 16):
            port = f"COM{i}"
            try:
                s = serial.Serial(port)
                s.close()
                ports.append(port)
            except serial.SerialException:
                pass
        return ports if ports else ["COM1"]
    
    def connect_esp32(self):
        """ESP32 に接続"""
        port = self.port_combo.currentText()
        try:
            self.esp = ESP32IO(port, debug=False)
            self.statusBar.showMessage(f"接続完了: {port}")
            self.set_buttons_enabled(True)
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.port_combo.setEnabled(False)
            self.refresh_di_adc()
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"接続失敗: {str(e)}")
    
    def disconnect_esp32(self):
        """ESP32 から切断"""
        try:
            if self.esp:
                self.esp.close()
            self.esp = None
            self.statusBar.showMessage("切断状態")
            self.set_buttons_enabled(False)
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(True)
            self.port_combo.setEnabled(True)
            self.auto_refresh_timer.stop()
            self.auto_refresh_btn.setChecked(False)
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"切断エラー: {str(e)}")
    
    def set_buttons_enabled(self, enabled: bool):
        """操作ボタンの有効/無効を設定"""
        for btn in self.dio_buttons.values():
            btn.setEnabled(enabled)
        for slider, _ in self.pwm_sliders.values():
            slider.setEnabled(enabled)
        self.auto_refresh_btn.setEnabled(enabled)
    
    def on_do_toggle(self, pin_id: int, checked: bool = None):
        """DIO 出力ボタンがトグルされた"""
        if not self.esp:
            return
        try:
            if checked is None:
                checked = self.dio_buttons[pin_id].isChecked()
            value = 1 if checked else 0
            self.esp.set_do(pin_id, value)
        except Exception as e:
            QMessageBox.warning(self, "エラー", f"set_do 失敗: {str(e)}")
            # ボタンの状態を戻す
            self.dio_buttons[pin_id].blockSignals(True)
            self.dio_buttons[pin_id].setChecked(not self.dio_buttons[pin_id].isChecked())
            self.dio_buttons[pin_id].blockSignals(False)
    
    def on_pwm_change(self, pin_id: int, value: int):
        """PWM スライダーが変更された"""
        if not self.esp:
            return
        try:
            self.esp.set_pwm(pin_id, value)
        except Exception as e:
            QMessageBox.warning(self, "エラー", f"set_pwm 失敗: {str(e)}")
    
    def toggle_auto_refresh(self, checked: bool):
        """自動更新をトグル"""
        if checked:
            self.auto_refresh_btn.setText("自動更新: ON")
            self.auto_refresh_timer.start(500)  # 500ms ごと
        else:
            self.auto_refresh_btn.setText("自動更新: OFF")
            self.auto_refresh_timer.stop()
    
    def refresh_di_adc(self):
        """DIO入力と ADC を更新"""
        if not self.esp:
            return
        try:
            # DIO 入力を読む
            for pin_id in range(6):
                value = self.esp.read_di(pin_id)
                self.di_lamps[pin_id].set_state(value)
            
            # ADC を読む
            for pin_id in range(2):
                value = self.esp.read_adc(pin_id)
                self.adc_labels[pin_id].setText(str(value))
        except Exception as e:
            QMessageBox.warning(self, "エラー", f"更新失敗: {str(e)}")


def main():
    app = QApplication(sys.argv)
    ui = ESP32IOTestUI()
    ui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
