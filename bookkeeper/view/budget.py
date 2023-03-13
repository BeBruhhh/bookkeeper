"""
Виджет для работы с бюджетом.
"""
from datetime import datetime, timedelta, date
from PySide6 import QtWidgets, QtCore

from bookkeeper.view.utils import LabeledInput, HistoryTable, LabeledBox
from bookkeeper.repository.sqlite_repository import AbstractRepository
from bookkeeper.models.budget import Budget


def start_date(dayss: int) -> datetime:
    """
    Получение даты, с которой необходимо начать отсчет.
    
    Параметры
    dayss - количество дней в нужном периоде: неделя - 7,
    месяц - [28; 31],
    в ином случае - сегодняшнее число.
    
    Возвращаемое значение
    Дата начала данного периода в формате YYYY-MM-DD.
    """
    if dayss == 7:
        return datetime.strptime(str(date.today() -
                                     timedelta(days=datetime.weekday(
                                         date.today()))), '%Y-%m-%d')
    if dayss in [28, 29, 30, 31]:
        return datetime.strptime(str(date.today() -
                                     timedelta(days=int(datetime.strftime(
                                         datetime.now(), '%d'))-1)),
                                 '%Y-%m-%d')
    return datetime.strptime(str(datetime.today().date()), '%Y-%m-%d')


class ActiveBudgets(QtWidgets.QWidget):
    """
    Виджет, показывающий текущие траты и ограничения,
    дату и день недели.
    В случае превышения ограничения
    выдается окно с соответствующей информацией.
    Обновление каждые 0.5 секунды для обработки трат и новых бюджетов.
    """
    def __init__(self, exp_repo: AbstractRepository,
                 bud_repo: AbstractRepository[Budget], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exp_repo = exp_repo
        self.bud_repo = bud_repo
        self.rows_columns = (('Day', 'Week', 'Month'), ('Paid', 'Limit'))

        self.data: list[list[int]] = []
        self.table = HistoryTable(self.rows_columns[0], self.rows_columns[1])
        self.set_data()
        if self.data[0][0] > self.data[0][1] or \
                self.data[1][0] > self.data[1][1] or \
                self.data[2][0] > self.data[2][1]:
            QtWidgets.QMessageBox.critical(self, "You'll be poor!",
                                           'You shouldn\'t spend that much!!!')

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(QtWidgets.QLabel('Budgets'))
        self.layout.addWidget(QtWidgets.QLabel('Today:\n' +
                                               str(date.today()) + ', ' +
                                               str(datetime.weekday(
                                                   datetime.now())) +
                                               'th day of week'))
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
        self.timer = QtCore.QBasicTimer()
        self.timer.start(500, self)

    def timerEvent(self, event) -> None:
        """
        Работа таймера.
        
        Параметры
        event - необходимый параметр.
        
        Возвращаемое значение
        None
        """
        self.set_data()

    @QtCore.Slot()
    def set_data(self) -> None:
        """
        Подсчет трат за нужные периоды. Отрисовка таблицы бюджетов и трат.
        Вызывается по таймеру. 
        
        Возвращаемое значение
        None
        """
        data_bud = []
        for i in [1, 7, 30]:
            data_bud.append(self.bud_repo.get_all({'length': i})[::-1][0].amount)
        got_exp = self.exp_repo.get_all()[::-1]
        day_amount, week_amount, month_amount = 0, 0, 0
        for exp in got_exp:
            exp_date = datetime.strptime(exp.expense_date, '%Y-%m-%d %H:%M:%S')
            if exp_date >= start_date(1):
                month_amount += exp.amount
                day_amount += exp.amount
                week_amount += exp.amount
            elif exp_date >= start_date(7):
                month_amount += exp.amount
                week_amount += exp.amount
            elif exp_date >= start_date(30):
                month_amount += exp.amount
        self.data = [[day_amount, data_bud[0]],
                     [week_amount, data_bud[1]],
                     [month_amount, data_bud[2]]]

        self.table.set_data(self.data)


class BudgetManager(QtWidgets.QWidget):
    """
    Изменение бюджетов.
    """
    def __init__(self, bud_repo: AbstractRepository[Budget], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bud_repo = bud_repo
        self.length_choice = LabeledBox('Category', ['day', 'week', 'month'])
        self.limit_input = LabeledInput('New budget', '1000')
        self.submit_button = QtWidgets.QPushButton('Update')
        self.submit_button.clicked.connect(self.submit)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(QtWidgets.QLabel('Budget manager'))
        self.layout.addWidget(self.length_choice)
        self.layout.addWidget(self.limit_input)
        self.layout.addWidget(self.submit_button)
        self.setLayout(self.layout)

    def submit(self) -> None:
        """
        Срабатывает от нажатия кнопки. 
        Пытается вызвать функцию new_budget.
        В случае неудачи выдается ошибка.
        
        Возвращаемое значение
        None
        """
        try:
            self.new_budget(str(self.length_choice.box.currentText()),
                            int(self.limit_input.input.text()))
        except ValueError:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Incorrect input!')

    def new_budget(self, period: str, limit: int) -> None:
        """
        Добавление нового объект в БД с бюджетами.
        
        Параметры
        ----------
        period - продолжительность нового ограничения: 
        день, неделя или месяц.
        limit - органичение на данный промежуток времени.
        
        Возващаемое значение
        -------
        None
        """
        per = 7
        if period == 'day':
            per = 1
        elif period == 'week':
            per = 7
        elif period == 'month':
            per = 30
        bud = Budget(limit, length=per, start_date=start_date(per))
        self.bud_repo.add(bud)


class BudgetTab(QtWidgets.QWidget):
    """
    Создание виджета, который объединяет виджеты с текущими
    ограничениями и виджета для редактирования ограничений.
    """
    def __init__(self, exp_repo: AbstractRepository,
                 bud_repo: AbstractRepository[Budget], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exp_repo = exp_repo
        self.bud_repo = bud_repo
        self.layout = QtWidgets.QVBoxLayout()
        self.act_bud = ActiveBudgets(self.exp_repo, self.bud_repo)
        self.edit_bud = BudgetManager(self.bud_repo)
        self.layout.addWidget(self.act_bud)
        self.layout.addWidget(self.edit_bud)
        self.setLayout(self.layout)
