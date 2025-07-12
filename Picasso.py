import sys
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QAction, QColor, QPixmap
from PyQt6.QtWidgets import (
  QApplication, QMainWindow, QLabel,
  QGraphicsColorizeEffect, QToolBar, QSlider, QPushButton
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Picasso")
        self.setFixedSize(QSize(600, 400))

        # Меню
        main_menu = self.menuBar()
        file_menu = main_menu.addMenu("Файл")
        new_img_action = QAction(QIcon("icons/new-image.png"), "Создать", self)
        open_action = QAction(QIcon("icons/open-image.png"), "Открыть", self)
        save_action = QAction(QIcon("icons/save-image.png"), "Сохранить", self)
        file_menu.addAction(new_img_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)

        # Центральный текст
        self.label = QLabel("ДЕЙСТВИЕ")
        font = self.label.font()
        font.setPointSize(25)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.setCentralWidget(self.label)

        # Подключение действий
        new_img_action.triggered.connect(self.new_img_text)
        open_action.triggered.connect(self.open_img_text)
        save_action.triggered.connect(self.save_img_text)

        # Создаем тулбары
        self.create_toolbars()

    def create_toolbars(self):
        # --- FILE TOOLBAR ---
        self.fileToolbar = QToolBar(self)
        self.fileToolbar.setIconSize(QSize(16, 16))
        self.fileToolbar.setObjectName("fileToolbar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.fileToolbar)

        # Кнопка "Создать"
        new_img_button = QPushButton()
        new_img_button.setIcon(QIcon("icons/new-image.png"))
        self.fileToolbar.addWidget(new_img_button)

        # Кнопка "Открыть"
        open_img_button = QPushButton()
        open_img_button.setIcon(QIcon("icons/open-image.png"))
        self.fileToolbar.addWidget(open_img_button)

        # Кнопка "Сохранить"
        save_img_button = QPushButton()
        save_img_button.setIcon(QIcon("icons/save-image.png"))
        self.fileToolbar.addWidget(save_img_button)

        # --- SLIDER TOOLBAR ---
        self.sliderToolbar = QToolBar(self)
        self.sliderToolbar.setIconSize(QSize(16, 16))
        self.sliderToolbar.setObjectName("sliderToolbar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.sliderToolbar)

        # Иконка border-weight
        sizeicon = QLabel()
        sizeicon.setPixmap(QPixmap("icons/border-weight.png").scaled(
            16, 16,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        self.sliderToolbar.addWidget(sizeicon)

        # Слайдер размера
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(10, 30)
        self.slider.setValue(25)
        self.slider.valueChanged.connect(self.change_text)
        self.sliderToolbar.addWidget(self.slider)

        # --- DRAWING TOOLBAR ---
        self.drawingToolbar = QToolBar(self)
        self.drawingToolbar.setIconSize(QSize(16, 16))
        self.drawingToolbar.setObjectName("drawingToolbar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.drawingToolbar)

        # Кнопка "Карандаш"
        brush_button = QPushButton()
        brush_button.setIcon(QIcon("icons/paint-brush.png"))
        brush_button.setCheckable(True)
        self.drawingToolbar.addWidget(brush_button)

        # Кнопка "Заливка"
        can_button = QPushButton()
        can_button.setIcon(QIcon("icons/paint-can.png"))
        can_button.setCheckable(True)
        self.drawingToolbar.addWidget(can_button)

        # Кнопка "Ластик"
        eraser_button = QPushButton()
        eraser_button.setIcon(QIcon("icons/eraser.png"))
        eraser_button.setCheckable(True)
        self.drawingToolbar.addWidget(eraser_button)

        # Кнопка "Ластик"
        picker_button = QPushButton()
        picker_button.setIcon(QIcon("icons/pipette.png"))
        picker_button.setCheckable(True)
        self.drawingToolbar.addWidget(picker_button)

    def add_toolbar_button(self, toolbar, icon_path):
        button = QPushButton()
        button.setIcon(QIcon(icon_path))
        toolbar.addWidget(button)

    def change_text(self, value):
        font = self.label.font()
        font.setPointSize(value)
        self.label.setFont(font)

    def change_color(self, color_name):
        color_effect = QGraphicsColorizeEffect()
        color_effect.setColor(QColor(color_name))
        self.label.setGraphicsEffect(color_effect)

    def new_img_text(self):
        self.label.setText("НОВОЕ ИЗОБРАЖЕНИЕ")
        self.change_color("green")

    def open_img_text(self):
        self.label.setText("ОТКРЫТЬ ИЗОБРАЖЕНИЕ")
        self.change_color("blue")

    def save_img_text(self):
        self.label.setText("СОХРАНИТЬ ИЗОБРАЖЕНИЕ")
        self.change_color("red")


# Запуск приложения
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
