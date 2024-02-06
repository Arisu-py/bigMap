import os
import sys

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import Qt

SCREEN_SIZE = [600, 450]


class Example(QWidget):
    def __init__(self):
        self.coords = [46.034077, 51.529814]
        self.spn = [0.00419, 0.00419]
        self.redraw = True
        super().__init__()
        self.getImage()
        self.initUI()

    def get_coords(self, text):
        geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={text}&format=json"

        # Выполняем запрос.
        response = requests.get(geocoder_request)
        if response:
            # Преобразуем ответ в json-объект
            json_response = response.json()

            # Получаем первый топоним из ответа геокодера.
            # Согласно описанию ответа, он находится по следующему пути:
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0][
                "GeoObject"]
            # Полный адрес топонима:
            # Координаты центра топонима:
            toponym_coodrinates = toponym["Point"]["pos"]
            return ','.join(toponym_coodrinates.split())
            # Печатаем извлечённые из ответа поля:
        else:
            print("Ошибка выполнения запроса:")
            print(geocoder_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")

    def getImage(self):
        map_request = f"https://static-maps.yandex.ru/1.x/?ll={self.coords[0]},{self.coords[1]}&spn={self.spn[0]},{self.spn[1]}&l=map"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        ## Изображение
        self.pixmap = QPixmap(self.map_file)
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_U:
            if self.spn[0] - 0.001 > 0 and self.spn[1] - 0.001 > 0:
                self.spn = [self.spn[0] - 0.001, self.spn[1] - 0.001]
                self.redraw = True
        if event.key() == Qt.Key_D:
            self.spn = [self.spn[0] + 0.001, self.spn[1] + 0.001]
            self.redraw = True
        if event.key() == Qt.Key_Up:
            self.coords = [self.coords[0], self.coords[1] + 0.0028]
            self.redraw = True
        if event.key() == Qt.Key_Down:
            self.coords = [self.coords[0], self.coords[1] - 0.0028]
            self.redraw = True
        if event.key() == Qt.Key_Left:
            self.coords = [self.coords[0]  + 0.006, self.coords[1]]
            self.redraw = True
        if event.key() == Qt.Key_Right:
            self.coords = [self.coords[0] - 0.006, self.coords[1]]
            self.redraw = True

    def paintEvent(self, event):
        if self.redraw:
            self.getImage()
            self.pixmap = QPixmap(self.map_file)
            self.image.setPixmap(self.pixmap)
            self.needs_reload = False

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())