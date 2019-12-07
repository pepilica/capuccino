import sys
import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QMainWindow, QWidget, QMessageBox


class Coffee(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.con = sqlite3.connect("coffee.db")
        cur = self.con.cursor()
        result = list(cur.execute("Select * from Coffee").fetchall())
        for i in range(len(result)):
            result[i] = list(result[i])
            result[i][2] = cur.execute(f'select degree from roasting_degrees '
                                       f'where id = {result[i][2]}').fetchone()[0]
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(7)
        self.titles = 'ID', 'Название сорта', 'Степень обжарки', \
                      'Молотый/В зёрнах', 'Описание вкуса', 'Цена', 'Объём упаковки'
        self.tableWidget.setHorizontalHeaderLabels(self.titles)
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.tableWidget.resizeColumnsToContents()
        self.pushButton.clicked.connect(self.edit_show)

    def edit_show(self):
        self.xx = AddEdit(self.con)
        self.xx.show()
        ex.hide()


class AddEdit(QWidget):
    def __init__(self, con):
        super().__init__()
        self.con = con
        self.cur = con.cursor()
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.btn_create.clicked.connect(self.create_n)
        self.btn_load.clicked.connect(self.load)
        self.btn_edit.clicked.connect(self.edit)
        self.names = [i[0] for i in self.cur.execute('select name from Coffee').fetchall()]
        self.tableWidgetEdit.setRowCount(1)
        self.tableWidgetCreate.setRowCount(1)
        self.tableWidgetEdit.setColumnCount(7)
        self.tableWidgetCreate.setColumnCount(7)
        self.nodes = 'name', 'degree', 'grind', 'taste', 'price', 'size'
        self.titles = 'Название сорта', 'Степень обжарки', \
                      'Молотый/В зёрнах', 'Описание вкуса', 'Цена', 'Объём упаковки'
        self.tableWidgetEdit.setHorizontalHeaderLabels(self.titles)
        self.tableWidgetCreate.setHorizontalHeaderLabels(self.titles)
        for name in self.names:
            self.comboBox.addItem(name)

    def load(self):
        self.name = self.comboBox.currentText()
        if self.comboBox.currentText():
            table = self.cur.execute(f'select * from Coffee where name = "{self.name}"').fetchone()
            self.id = table[0]
            for j, val in enumerate(table[1::]):
                self.tableWidgetEdit.setItem(0, j, QTableWidgetItem(str(val)))
            self.tableWidgetEdit.resizeColumnsToContents()

    def is_completed(self, table):
        return all(list(map(lambda a: a != '', table)))

    def warn(self):
        return QMessageBox.critical(self, 'Ошибка', 'Не все поля заполнены. Повторите попытку.',
                                    buttons=QMessageBox.Ok)

    def edit(self):
        row = []
        for j in range(6):
            item = self.tableWidgetEdit.item(0, j).text()
            row.append(item)
        if self.is_completed(row):
            row = list(map(lambda a: "'" + a + "'", row))
            for i in range(len(row)):
                self.cur.execute(f'update Coffee \n'
                                 f'SET {self.nodes[i]} = {row[i]} where id = "{self.id}"')
            self.con.commit()
            self.comboBox.addItem(row[0][1:-1])
            self.comboBox.removeItem(self.comboBox.findText(self.name))
            self.comboBox.setCurrentIndex(len(self.comboBox) - 1)
        else:
            self.warn()

    def create_n(self):
        row = []
        for j in range(6):
            item = self.tableWidgetEdit.item(0, j).text()
            row.append(item)
        if self.is_completed(row):
            row = list(map(lambda a: "'" + a + "'", row))
            self.cur.execute(f'insert into Coffee({self.nodes}) values({", ".join(row)})')
            self.comboBox.addItem(row[0][1:-1])
            self.con.commit()
        else:
            self.warn()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Coffee()
    ex.show()
    sys.exit(app.exec())