"""
Portions of this implementation are inspired by or adapted from cachetools:
https://github.com/tkem/cachetools/

License for the original code is below.

The MIT License (MIT)

Copyright (c) 2014-2024 Thomas Kemmer

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Iterator
from collections.abc import MutableMapping
from typing import Any
from typing import TypeVar
from typing import overload

from ._typing import override

_T = TypeVar("_T")
_TKey = TypeVar("_TKey")
_TValue = TypeVar("_TValue")


class LRUCache(MutableMapping[_TKey, _TValue]):
    """
    Least Recently Used (LRU) cache implementation.
    Discards least recently used items when cache reaches maxsize.
    """

    def __init__(self, maxsize: int):
        if maxsize <= 0:
            raise ValueError("maxsize must be positive")
        self._maxsize = maxsize
        self._data: OrderedDict[_TKey, _TValue] = OrderedDict()
        self._currsize = 0

    @override
    def __getitem__(self, key: _TKey) -> _TValue:
        try:
            value = self._data.pop(key)
            self._data[key] = value  # Move to end
            return value
        except KeyError:
            return self.__missing__(key)

    @override
    def __setitem__(self, key: _TKey, value: _TValue) -> None:
        if key in self._data:
            del self._data[key]
        elif len(self._data) >= self._maxsize:
            self.popitem()
        self._data[key] = value

    @override
    def __delitem__(self, key: _TKey) -> None:
        del self._data[key]

    @override
    def __iter__(self) -> Iterator[_TKey]:
        return iter(self._data)

    @override
    def __len__(self) -> int:
        return len(self._data)

    @override
    def __contains__(self, key: object) -> bool:
        return key in self._data

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(dict(self._data))}, maxsize={self._maxsize})"

    def __missing__(self, key: _TKey) -> _TValue:
        raise KeyError(key)

    @overload
    def get(self, key: _TKey) -> _TValue | None: ...

    @overload
    def get(self, key: _TKey, default: _T) -> _TValue | _T: ...

    @override
    def get(self, key: _TKey, default: Any = None) -> Any:
        """Return value for key if present, else default."""
        try:
            return self[key]
        except KeyError:
            return default

    @override
    def pop(self, key: _TKey, default: Any = ...) -> _TValue:
        """Remove specified key and return the corresponding value."""
        if default is ...:
            value = self[key]
            del self[key]
            return value
        try:
            value = self[key]
            del self[key]
            return value
        except KeyError:
            return default

    @override
    def setdefault(self, key: _TKey, default: _TValue = None) -> _TValue:
        """Return value for key if present, else set and return default."""
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    @override
    def popitem(self) -> tuple[_TKey, _TValue]:
        """Remove and return the `(key, value)` pair least recently used."""
        try:
            key = next(iter(self._data))
        except StopIteration as err:
            raise KeyError(f"{self.__class__.__name__} is empty") from err
        value = self._data[key]
        del self._data[key]
        return key, value

    @override
    def clear(self) -> None:
        """Remove all items from the cache."""
        self._data.clear()

    @property
    def maxsize(self) -> int:
        """The maximum size of the cache."""
        return self._maxsize
