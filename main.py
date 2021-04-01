import os
from io import BytesIO
import sys
from PIL import Image

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QColor, QPalette, QFont, QImage
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QButtonGroup


SCREEN_SIZE = [600, 600]
GEOCODER_APIKEY = "40d1649f-0493-4b70-98ba-98533de7710b"


class MapWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def log_error(self, error_message):
        print(error_message)
        self.info_label.setText(str(error_message))

    def update_image(self, pillow_image=None):
        if not pillow_image:
            server = "http://static-maps.yandex.ru/1.x/"
            parameters = {'ll': ','.join(map(str, self.coordinates)),
                          'z': self.zoom,
                          'l': self.map_type,
                          'pt': self.point_parameter,
                          }
            response = requests.get(server, params=parameters)
            if not response:
                self.log_error(f'Поиск не удался: HTTP-статус: {response.status_code} '
                               f'({response.reason})')
            pillow_image = Image.open(BytesIO(response.content))
        pillow_image.save(self.map_file, format='PNG')
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        self.main_font = QFont('Tahoma')
        self.main_font.setPointSize(12)

        self.coordinates = [0.0, 0.0]
        self.zoom = 5
        self.map_type = 'map'
        self.point_parameter = None

        self.search_input = QLineEdit(self)
        self.search_input.setGeometry(5, 5, SCREEN_SIZE[0] - 105, 30)
        self.search_input.setFont(self.main_font)

        self.search_btn = QPushButton('Поиск', self)
        self.search_btn.setGeometry(SCREEN_SIZE[0] - 100, 5, 100, 30)
        pal = self.search_btn.palette()
        pal.setColor(QPalette.Button, QColor(120, 170, 230))
        self.search_btn.setPalette(pal)
        self.search_btn.setFont(self.main_font)
        self.search_btn.clicked.connect(self.search_object)

        self.clear_btn = QPushButton('Очистить', self)
        self.clear_btn.setGeometry(SCREEN_SIZE[0] - 100, 40, 100, 30)
        pal.setColor(QPalette.Button, QColor(255, 100, 100))
        self.clear_btn.setPalette(pal)
        self.clear_btn.setFont(self.main_font)
        self.clear_btn.clicked.connect(self.clear_object)

        self.standard_mode_btn = QPushButton('Схема', self)
        self.standard_mode_btn.setGeometry(5, 40, 70, 30)
        self.standard_mode_btn.setFlat(True)
        self.satellite_mode_btn = QPushButton('Спутник', self)
        self.satellite_mode_btn.setGeometry(80, 40, 70, 30)
        self.hybrid_mode_btn = QPushButton('Гибрид', self)
        self.hybrid_mode_btn.setGeometry(155, 40, 70, 30)

        self.map_mode_btngroup = QButtonGroup(self)
        self.map_mode_btngroup.addButton(self.standard_mode_btn)
        self.map_mode_btngroup.addButton(self.satellite_mode_btn)
        self.map_mode_btngroup.addButton(self.hybrid_mode_btn)
        pal.setColor(QPalette.Button, QColor(250, 210, 120))
        for button in self.map_mode_btngroup.buttons():
            button.setPalette(pal)
            button.setFont(self.main_font)
            button.clicked.connect(self.switch_mode)

        self.map_file = "map.png"
        self.image = QLabel(self)
        self.image.setGeometry(0, 80, 600, 450)

        self.info_label = QLabel(self)
        self.info_label.setGeometry(5, SCREEN_SIZE[1] - 30, SCREEN_SIZE[0] - 100, 30)
        self.info_label.setFont(self.main_font)

        self.update_image()

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)

    def keyPressEvent(self, event):
        d_x = 0
        d_y = 0
        if event.key() == Qt.Key_Left:
            d_x = -(2 ** -self.zoom * 360)
        elif event.key() == Qt.Key_Right:
            d_x = 2 ** -self.zoom * 360
        elif event.key() == Qt.Key_Up:
            d_y = 2 ** -self.zoom * 180
        elif event.key() == Qt.Key_Down:
            d_y = -(2 ** -self.zoom * 180)
        elif event.key() == Qt.Key_Return:
            self.search_object()
            return
        else:
            return
        self.setFocus()
        if self.coordinates[0] + d_x > 180:
            self.coordinates[0] = -180 + d_x
        elif self.coordinates[0] + d_x < -180:
            self.coordinates[0] = (self.coordinates[0] + d_x) % 180
        else:
            self.coordinates[0] += d_x
        if abs(self.coordinates[1] + d_y) <= 90:
            self.coordinates[1] += d_y
        elif d_y:
            self.log_error('Перемещение невозможно')
        self.info_label.setText(f'Текущие координаты: {self.coordinates[0]}, {self.coordinates[1]}')
        self.update_image()

    def search_object(self):
        self.search_input.clearFocus()
        object_to_search = self.search_input.text().strip()
        if not object_to_search:
            self.log_error('Поиск не удался: запрос пуст')
            return
        self.info_label.setText('')

        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocoder_params = {"apikey": GEOCODER_APIKEY,
                           "geocode": object_to_search,
                           "format": "json"}
        response = requests.get(geocoder_api_server, params=geocoder_params)

        if not response:
            self.log_error(f'Поиск не удался: HTTP-статус: {response.status_code} '
                           f'({response.reason})')
            return
        json_response = response.json()
        try:
            objects_found = json_response["response"]["GeoObjectCollection"]["featureMember"]
        except Exception as error:
            print('JSON:', json_response)
            self.log_error(error)
            return

        if not objects_found:
            print('JSON:', json_response)
            self.log_error('По данному запросу не найдено ни одного объекта')
            return
        toponym = objects_found[0]["GeoObject"]
        # Координаты центра топонима:
        toponym_coordinates = list(map(float, toponym["Point"]["pos"].split(" ")))

        self.point_parameter = f'{toponym_coordinates[0]},{toponym_coordinates[1]},pm2rdl'
        self.coordinates = toponym_coordinates
        self.update_image()

    def clear_object(self):
        self.point_parameter = None
        self.setFocus()
        self.update_image()

    def switch_mode(self):
        if self.sender().isFlat():
            self.log_error('Данный режим уже выбран')
        else:
            self.info_label.setText('')
            for button in self.map_mode_btngroup.buttons():
                button.setFlat(False)
            self.sender().setFlat(True)
            if self.sender().text() == 'Схема':
                self.map_type = 'map'
            elif self.sender().text() == 'Спутник':
                self.map_type = 'sat'
            elif self.sender().text() == 'Гибрид':
                self.map_type = 'sat,skl'
            else:
                self.log_error('Where tf you got another mode?')
            self.update_image()
        for button in self.map_mode_btngroup.buttons():
            button.clearFocus()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapWindow()
    ex.show()
    sys.exit(app.exec())
