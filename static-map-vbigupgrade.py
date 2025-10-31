import os
import sys
import math

import requests
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QCheckBox
from PyQt6.QtCore import Qt

SCREEN_SIZE = [800, 600]


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.ll = [37.530887, 55.703118]
        self.spn = [0.002, 0.002]
        self.mark = ""
        self.map_theme = "light"
        self.search_flag = False
        self.getImage()
        self.initUI()

    def getImage(self):
        server_address = 'https://static-maps.yandex.ru/v1?'
        api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
        ll_spn = '&'.join(['ll=' + ','.join(map(str, self.ll)), 'spn=' + ','.join(map(str, self.spn))])
        theme_param = f'&theme={self.map_theme}'
        mark_param = "&pt=" + self.mark if self.mark else ""
        map_request = f"{server_address}{ll_spn}{theme_param}{mark_param}&apikey={api_key}"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUI(self):
        self.setFixedSize(*SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        self.pixmap = QPixmap(self.map_file)
        self.image = QLabel(self)
        self.image.move(100, 100)
        self.image.resize(800, 400)
        self.image.setPixmap(self.pixmap)

        self.change_theme = QPushButton('Сменить тему карты', self)
        self.change_theme.move(0, 0)
        self.change_theme.resize(120, 40)
        self.change_theme.clicked.connect(self.change_map_theme)

        self.name_object = QLineEdit(self, placeholderText='Введите название объекта')
        self.name_object.move(160, 0)
        self.name_object.resize(240, 40)
        self.name_object.returnPressed.connect(self.find_object)

        self.select_object = QPushButton("Найти объект", self)
        self.select_object.move(400, 0)
        self.select_object.resize(120, 40)
        self.select_object.clicked.connect(self.find_object)

        self.btn_delete_mark = QPushButton("Сброс поискового запроса", self)
        self.btn_delete_mark.move(0, 40)
        self.btn_delete_mark.resize(160, 40)
        self.btn_delete_mark.clicked.connect(self.delete_mark)

        self.full_address = QLabel(self)
        self.full_address.move(160, 40)

        self.postal_code_checkbox = QCheckBox("Показать почтовый индекс", self)
        self.postal_code_checkbox.move(520, 0)
        self.postal_code_checkbox.resize(180, 40)
        self.postal_code_checkbox.setChecked(True)
        self.postal_code_checkbox.stateChanged.connect(self.change_full_address)
        self.setFocus()

    def geocode_get_info(self, query):
        server_address = 'http://geocode-maps.yandex.ru/1.x/?'
        api_key = '8013b162-6b42-4997-9691-77b7074026e0'
        geocode = query
        geocoder_request = f'{server_address}apikey={api_key}&geocode={geocode}&format=json'
        response = requests.get(geocoder_request)
        if response:
            try:
                json_response = response.json()
                toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
                toponym_coordinates = toponym["Point"]["pos"]
                federal_district, postal_code = None, None
            except:
                return None
            try:
                federal_district = toponym["metaDataProperty"]["GeocoderMetaData"]["AddressDetails"]["Country"]["AdministrativeArea"]["AdministrativeAreaName"]
            except KeyError:
                federal_district = "Неизвестно"
            try:
                postal_code = postal_code = toponym["metaDataProperty"]["GeocoderMetaData"]["AddressDetails"]["Country"]["AdministrativeArea"]["Locality"]["Thoroughfare"]["Premise"]["PostalCode"]["PostalCodeNumber"]
            except KeyError:
                postal_code = "Неизвестно"
            return (toponym_address, federal_district, postal_code, toponym_coordinates)
        else:
            return None

    def update_image(self):
        self.getImage()
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)
        self.setFocus()

    def delete_mark(self):
        if self.search_flag:
            self.mark = ""
            self.full_address.setText("")
            self.search_flag = False
            self.update_image()

    def change_full_address(self):
        if self.search_flag and self.search_flag != 2:
            self.full_address.setText(
                f"Полный адрес: {self.search_res[0]}\nПочтовый код: {self.search_res[2]}" 
                if self.postal_code_checkbox.isChecked() 
                else f"Полный адрес: {self.search_res[0]}")
            self.full_address.resize(self.full_address.sizeHint())
        elif self.search_flag == 2:
            self.full_address.setText(
                f"Организация: {self.search_res[0]}\nПолный адрес: {self.search_res[1]}\nПочтовый код: {self.search_res[3]}"
                if self.postal_code_checkbox.isChecked() 
                else f"Организация: {self.search_res[0]}\nПолный адрес: {self.search_res[1]}")
            self.full_address.resize(self.full_address.sizeHint())

    def find_object(self):
        if self.name_object.text() != "":
            search_res = self.geocode_get_info(self.name_object.text())
            if search_res is not None:
                self.search_res = search_res
                self.search_flag = True
                self.ll = list(map(float, search_res[3].split()))
                self.name_object.setText("")
                self.mark = f"{self.ll[0]},{self.ll[1]},pmrdl99"
                self.change_full_address()
                self.update_image()

    def change_map_theme(self):
        self.map_theme = "dark" if self.map_theme == "light" else "light"
        self.update_image()

    def closeEvent(self, event):
        os.remove(self.map_file)

    def screen_to_geo(self, x, y):
        map_width, map_height = self.pixmap.width(), self.pixmap.height()
        dx = (x / map_width - 0.5) * self.spn[0] * 2
        dy = (0.5 - y / map_height) * self.spn[1] * 2
        return self.ll[0] + dx, self.ll[1] + dy

    def find_mouse_object(self, l1, l2):
        coords = f"{l1},{l2}"
        search_res = self.geocode_get_info(coords)
        if search_res is not None:
            self.search_flag = True
            self.search_res = search_res
            self.mark = f"{l1},{l2},pmrdl52"
            self.change_full_address()
            self.update_image()

    def find_distance(self, l11, l21, l12, l22):
        dx = (l12 - l11) * 111000 * abs(math.cos(math.radians(l21)))
        dy = (l22 - l21) * 111000
        return (dx ** 2 + dy ** 2) ** 0.5

    def find_nearest_organization(self, l1, l2):
        coords = f"{l1},{l2}"
        api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
        search_params = {
            "apikey": api_key, 
            "text": "организация", 
            "lang": "ru_RU", 
            "ll": coords, 
            "type": "biz"}
        url = "https://search-maps.yandex.ru/v1/"
        response = requests.get(url, params=search_params)
        print(response)
        if response and response.status_code == 200:
            orgs = response.json()["features"]
            for org in orgs:
                org_coords = org["geometry"]["coordinates"]
                dist = self.find_distance(l1, l2, org_coords[0], org_coords[1])
                if dist <= 50:
                    name = org["properties"]["CompanyMetaData"]["name"]
                    self.search_flag = 2
                    search_res = self.geocode_get_info(f"{org_coords[0]},{org_coords[1]}")
                    self.mark = f"{org_coords[0]},{org_coords[1]},pmrdl52"
                    self.search_res = [name] + list(search_res)
                    self.change_full_address()
                    self.update_image()
                    return
            self.full_address.setText("")
            self.full_address.resize(self.full_address.sizeHint())
            self.mark = ""
            self.search_flag = False
            self.update_image()

    def mousePressEvent(self, event):
        x = event.position().x()
        y = event.position().y()
        if 100 <= x <= 700 and 100 <= y <= 500:
            map_x = x - 100
            map_y = y - 100
            l1, l2 = self.screen_to_geo(map_x, map_y)
            if event.button() == Qt.MouseButton.LeftButton:
                self.find_mouse_object(l1, l2)  
            if event.button() == Qt.MouseButton.RightButton:
                self.find_nearest_organization(l1, l2)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_PageUp:
            if self.spn[0] == 1.0 or self.spn[1] == 1.0:
                return
            self.spn = [el + 0.001 for el in self.spn]
        if event.key() == Qt.Key.Key_PageDown:
            if self.spn[0] == 0.001 or self.spn[1] == 0.001:
                return
            self.spn = [el - 0.001 for el in self.spn]
        if event.key() == Qt.Key.Key_Up:
            self.ll[1] += 0.005
            if self.ll[1] > 90:
                self.ll[1] = 90
        if event.key() == Qt.Key.Key_Down:
            self.ll[1] -= 0.005
            if self.ll[1] < -90:
                self.ll[1] = -90
        if event.key() == Qt.Key.Key_Left:
            self.ll[0] -= 0.005
            if self.ll[0] < -180:
                self.ll[0] = -180
        if event.key() == Qt.Key.Key_Right:
            self.ll[0] += 0.005
            if self.ll[0] > 180:
                self.ll[0] = 180
        self.update_image()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())