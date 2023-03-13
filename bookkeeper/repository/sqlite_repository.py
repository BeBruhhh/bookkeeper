from typing import Any
from inspect import get_annotations
from datetime import datetime

import sqlite3

from bookkeeper.repository.abstract_repository import AbstractRepository, T


class SQLiteRepository(AbstractRepository[T]):
    def __init__(self, db_file: str, cls: type):
        self.cls: type = cls
        self.db_file: str = db_file
        self.table_name: str = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')

    def add(self, obj: T) -> int:
        if getattr(obj, 'pk', None) != 0:
            raise ValueError(f'trying to add object {obj} with filled `pk` attribute')
        names = ', '.join(self.fields.keys())
        placeholders = ', '.join('?' * len(self.fields))
        values = [getattr(obj, i) for i in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(f'INSERT INTO {self.table_name} ({names}) '
                        f'VALUES ({placeholders})', values)
            con.commit()
            obj.pk = cur.lastrowid
        con.close()
        return obj.pk

    def convert_object_datetime(self, temp: list[T] | tuple[T]) -> tuple[T]:
        obj = self.cls(*temp)
        converted_temp: tuple = tuple()
        for i, element in enumerate(temp):
            try:
                converted_temp += (list(obj.__annotations__.values())[i](elememt),)
            except TypeError:
                if isinstance(temp[i], datetime):
                    converted_temp += (list(obj.__annotations__.values(
                    ))[i].strptime(element, '%Y-%m-%d %H:%M:%S'),)
                elif temp[i] is None:
                    converted_temp += (temp[i],)
                else:
                    converted_temp += (type(temp[i])(temp[i]),)
        return converted_temp

    def get(self, pk: int) -> T | None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            res = cur.execute(f'SELECT * FROM {self.table_name} WHERE pk = {pk}')
            temp = res.fetchone()
        con.close()
        if temp is None:
            return None
        return self.cls(*self.convert_object_datetime(temp))

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            res = cur.execute(f'SELECT * FROM {self.table_name}')
        if where is None:
            return [self.cls(*self.convert_object_datetime(temp))
                    for temp in res.fetchall()]
        objects = []
        for temp in res.fetchall():
            obj = self.cls(*self.convert_object_datetime(temp))
            if all([getattr(obj, attr) == value for attr, value in where.items()]):
                objects.append(obj)
        con.close()
        return objects

    def update(self, obj: T) -> None:
        if obj.pk == 0:
            raise ValueError('attempt to update object with unknown primary key')
        names = list(self.fields.keys())
        values = [getattr(obj, i) for i in self.fields]
        pk = obj.pk
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            for i, element in enumerate(names):
                try:
                    cur.execute(f'UPDATE {self.table_name} SET {element}'
                                f' = {repr(values[i])} WHERE pk = {pk}')
                except sqlite3.OperationalError:
                    cur.execute(f'UPDATE {self.table_name} SET {element}'
                                f' = {repr(str(values[i]))} WHERE pk = {pk}')
            con.commit()
        con.close()

    def delete(self, pk: int) -> None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(f'DELETE FROM {self.table_name} WHERE pk = {pk}')
            row_count = cur.rowcount
            if row_count == 0:
                raise KeyError
            con.commit()
        con.close()
