"""
Файл для соединения всех элементов в одно приложение
"""
import sys
from PySide6 import QtWidgets

from bookkeeper.view.interface import MainWindow
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.models.expense import Expense
from bookkeeper.models.category import Category
from bookkeeper.models.budget import Budget


class Presenter:
    """
    Создание репозиториев для расходов, категорий и бюджетов;
    Создание основного окна приложения.
    """
    def __init__(self, database: str) -> None:
        self.database: str = database
        self.exp_repo = SQLiteRepository[Expense](self.database, Expense)
        self.cat_repo = SQLiteRepository[Category](self.database, Category)
        self.bud_repo = SQLiteRepository[Budget](self.database, Budget)
        self.view: QtWidgets.QMainWindow = MainWindow(self.exp_repo,
                                                      self.cat_repo,
                                                      self.bud_repo)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = Presenter('main_db.db')
    window.view.show()

    sys.exit(app.exec())
