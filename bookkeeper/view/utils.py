"""
Часто использующиеся вспомогательные
функции и виджеты
"""
from PySide6 import QtWidgets


def add_del_buttons_widget(cls: QtWidgets.QWidget) -> QtWidgets.QWidget:
    """
    Создает виджет, содержащий кнопки 'Add' и 'Delete'.
    
    Параметры
    cls - виджет, в который необходимо добавить кнопки,
    они должны быть определены в нем.
    
    Возвращаемые значения
    Виджет с двумя кнопками.
    """
    buttons_widget = QtWidgets.QWidget()
    buttons_layout = QtWidgets.QHBoxLayout()
    buttons_layout.addWidget(cls.add_button)
    buttons_layout.addWidget(cls.delete_button)
    buttons_widget.setLayout(buttons_layout)
    return buttons_widget


class LabeledInput(QtWidgets.QWidget):
    """
    Создание поля ввода текста с названием text
    и значением по умолчанию placeholder.
    """
    def __init__(self, text: str, placeholder: int | str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel(text)
        self.input = QtWidgets.QLineEdit(placeholder)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input)
        self.setLayout(self.layout)


class LabeledBox(QtWidgets.QWidget):
    """
    Выпадающий список с названием text
    и вариантами выбора из списка data.
    """
    def __init__(self, text: str, data: list[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel(text)
        self.box = QtWidgets.QComboBox()
        self.box.addItems(data)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.box)
        self.setLayout(self.layout)


class HistoryTable(QtWidgets.QTableWidget):
    """
    Отрисовка таблицы.
    Получает кортежи названий строк и столбцов и количество строк.
    Если столбцов больше 2, все столбцы, кроме последнего, растягиваются
    по размеру контента; последний растягивается максимально.
    Если столбцов 2 - сторятся равные стобцы.
    Если строк больше трех, их названия не указываются на таблице.
    Ячейки активируются по двойному щелчку, измененные данные
    по умолчанию не сохраняются.
    """
    def __init__(self, rows: tuple = tuple(), columns: tuple = tuple(),
                 n_rows: int = 10, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setColumnCount(len(columns))
        if len(rows) == 0:
            rows = ('',) * n_rows

        self.setRowCount(len(rows))

        header = self.horizontalHeader()

        if len(columns) > 2:
            counter = 0
            for i in range(len(columns) - 1):
                counter = i
                header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(counter+1, QtWidgets.QHeaderView.Stretch)
        else:
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
            header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

        self.setEditTriggers(QtWidgets.QTableWidget.DoubleClicked)
        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Preferred)

        if len(rows) > 3:
            self.verticalHeader().hide()
        else:
            self.setVerticalHeaderLabels(rows)
        self.setHorizontalHeaderLabels(columns)

    def set_data(self, data: list[list[int | str]]) -> None:
        """
        Заполнение таблицы.
        
        Параметры
        data - данные, которыми заполняется таблица.
        
        Возвращаемые значения
        None
        """
        for i, row in enumerate(data):
            for number, x in enumerate(row):
                self.setItem(i, number, QtWidgets.QTableWidgetItem(str(x).capitalize()))
