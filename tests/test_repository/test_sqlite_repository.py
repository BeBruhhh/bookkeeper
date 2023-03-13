import datetime

from bookkeeper.repository.sqlite_repository import SQLiteRepository  # CustomClass
from dataclasses import dataclass
import pytest


@pytest.fixture
def custom_class():
    @dataclass
    class Custom:
        pk: int = 0
        name: str = 'bebra'
        date: str = str(datetime.datetime(2023, 3, 10))
        test_float: float = 1.2345

    return Custom


@pytest.fixture
def repo(custom_class):
    return SQLiteRepository('tests/test_repository/new_db.db', custom_class)


def test_crud(repo, custom_class):
    obj = custom_class()
    pk = repo.add(obj)
    assert obj.pk == pk
    assert repo.get(pk) == obj
    obj2 = custom_class()
    obj2.pk = pk
    repo.update(obj2)
    assert repo.get(pk) == obj2
    repo.delete(pk)
    assert repo.get(pk) is None


def test_cannot_add_with_pk(repo, custom_class):
    obj = custom_class()
    obj.pk = 1
    with pytest.raises(ValueError):
        pk = repo.add(obj)
        assert repo.get(pk)
        repo.delete(pk)


def test_cannot_add_without_pk(repo, custom_class):
    obj = custom_class()
    obj.pk = None
    with pytest.raises(ValueError):
        pk = repo.add(obj)
        assert repo.get(pk)
        repo.delete(pk)


def test_cannot_delete_unexistent(repo, custom_class):
    obj = custom_class()
    pk = repo.add(obj)
    with pytest.raises(KeyError):
        assert repo.delete(pk + 10)
        repo.delete(pk)


def test_cannot_update_without_pk(repo, custom_class):
    obj = custom_class()
    with pytest.raises(ValueError):
        repo.update(obj)


def test_get_all(repo, custom_class):
    for obj in repo.get_all():
        repo.delete(obj.pk)
    objects = [custom_class() for i in range(5)]
    for o in objects:
        repo.add(o)
    assert repo.get_all() == objects, repo.get_all()


def test_get_all_with_condition(repo, custom_class):
    objects = []
    for i in range(5):
        o = custom_class()
        o.test_float = i + 1.4352
        o.name = 'bruhhh'
        repo.add(o)
        objects.append(o)
    assert repo.get_all({'test_float': 1.4352}) == [objects[0]]
    assert repo.get_all({'name': 'bruhhh'}) == objects
