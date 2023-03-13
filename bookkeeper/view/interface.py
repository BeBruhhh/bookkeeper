"""
Описание главного окна.
"""
from PySide6 import QtWidgets

from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.view.expense import ExpenseTab
from bookkeeper.view.budget import BudgetTab
from bookkeeper.view.categories import CategoriesTab
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget
from bookkeeper.models.category import Category


class MainWindow(QtWidgets.QMainWindow):
    """
    Главное окно приложения.
    Создаются виджеты, содержащиеся в окне.
    Описывается передача сигналов от одних виджетов к другим.
    """
    def __init__(self, exp_repo: AbstractRepository[Expense],
                 cat_repo: AbstractRepository[Category],
                 bud_repo: AbstractRepository[Budget]) -> None:
        super().__init__()
        self.exp_repo = exp_repo
        self.cat_repo = cat_repo
        self.bud_repo = bud_repo

        self.setWindowTitle('Home bookkeeper')
        self.resize(1280, 760)

        self.expense = ExpenseTab(self.exp_repo, self.cat_repo)
        self.budget = BudgetTab(self.exp_repo, self.bud_repo)
        self.category = CategoriesTab(self.cat_repo, self.exp_repo)

        self.expense.setMinimumWidth(600)
        self.expense.setMaximumWidth(1000)
        self.budget.setMinimumWidth(350)
        self.category.setMinimumWidth(330)

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addWidget(self.expense)
        self.layout.addWidget(self.budget)
        self.layout.addWidget(self.category)

        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.category.new_cat.button_clicked.connect(self.expense.new_exp.set_cat_list)
        self.category.act_cat.table.cellChanged.connect(self.expense.new_exp.set_cat_list)
        self.expense.new_exp.button_clicked.connect(self.budget.act_bud.set_data)
