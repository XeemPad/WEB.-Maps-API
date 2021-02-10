import os
import sys

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit


SCREEN_SIZE = [600, 450]


class MapWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def update_image(self):
        server = "http://static-maps.yandex.ru/1.x/"
        parameters = {'ll': ','.join(map(str, self.coordinates)),
                      'z': self.zoom,
                      'l': self.map_type}
        response = requests.get(server, params=parameters)
        if not response:
            print(response.reason)
        with open(self.map_file, "wb") as file:
            file.write(response.content)

        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        self.coordinates = [0, 0]
        self.zoom = 3
        self.map_type = 'map'

        self.map_file = "map.png"
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)

        self.update_image()

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)

    def keyPressEvent(self, event):
        print('Вход')
        if event.key() == Qt.LeftArrow:
            print('Левая стрелка')
            self.coordinates[0] -= 1
        elif event.key() == Qt.RightArrow:
            self.coordinates[0] += 1
        elif event.key() == Qt.UpArrow:
            self.coordinates[1] -= 1
        elif event.key() == Qt.DownArrow:
            self.coordinates[1] += 1
        else:
            return
        self.update_image()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapWindow()
    ex.show()
    sys.exit(app.exec())
