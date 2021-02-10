import os
import sys

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit


SCREEN_SIZE = [600, 450]


class MapWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.getImage()
        self.initUI()

        self.map_request = ''

    def getImage(self):
        server = "http://static-maps.yandex.ru/1.x/"
        parameters = {'ll': ','.join(map(str, self.coordinates)),
                      'z': self.zoom,
                      'l': self.map_type}
        response = requests.get(server, params=parameters)

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        self.coordinates = [37.530887, 55.703118]
        self.zoom = 1.0
        self.map_type = 'map'

        self.pixmap = QPixmap(self.map_file)
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapWindow()
    ex.show()
    sys.exit(app.exec())
