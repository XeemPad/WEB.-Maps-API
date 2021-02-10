import os
import sys

import requests
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit


SCREEN_SIZE = [600, 450]


class MapWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.getImage()

    def getImage(self):
        server = "http://static-maps.yandex.ru/1.x/"
        parameters = {'ll': ','.join(map(str, self.coordinates)),
                      'z': self.zoom,
                      'l': self.map_type}
        response = requests.get(server, params=parameters)
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        self.coordinates = [37.530887, 55.703118]
        self.zoom = 1.0
        self.map_type = 'map'

        self.map_file = "map.png"

        self.pixmap = QPixmap(self.map_file)
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.LeftArrow:
            self.coordinates
        if event.key() == QtCore.Qt.RightArrow:
            self.created.setText('enter')
        if event.key() == QtCore.Qt.UpArrow:
            self.created.setText('enter')
        if event.key() == QtCore.Qt.DownArrow:
            self.created.setText('enter')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapWindow()
    ex.show()
    sys.exit(app.exec())
