from datetime import datetime, timedelta

import pytest

from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.models.budget import Budget


@pytest.fixture
def repo():
    return MemoryRepository()


def test_create_with_full_args_list():
    bud = Budget(amount=100, category=1, length=7, start_date=datetime.now(),
               end_date=(datetime.now()+timedelta(days=7)), pk=1)
    assert bud.amount == 100
    assert bud.category == 1
    assert bud.length == 7


def test_create_brief():
    bud = Budget(100, 1, 7)
    assert bud.amount == 100
    assert bud.category == 1
    assert bud.length == 7
    assert bud.end_date - bud.start_date == timedelta(days=bud.length)


def test_can_add_to_repo(repo):
    bud = Budget(100, 1, 7)
    pk = repo.add(bud)
    assert bud.pk == pk
