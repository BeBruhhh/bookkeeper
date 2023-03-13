"""
Класс ограничения бюджета
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, date


@dataclass
class Budget:
    """
.   Установка ограниченного бюджета на определенный срок
    amount - сумма ограничения
    category - id категории расходов
    length - срок в днях
    pk - id записи в базе данных
    """
    amount: int
    category: int = 0
    length: int = 7
    start_date: date = date.today() - timedelta(days=datetime.weekday(date.today()))
    end_date: date = start_date + timedelta(days=length)
    pk: int = 0
