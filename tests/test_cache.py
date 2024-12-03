from __future__ import annotations

import pytest

from django_bird.cache import LRUCache


class TestLRUCache:
    def test_init_positive_maxsize(self):
        cache = LRUCache(maxsize=2)
        assert cache.maxsize == 2

    def test_init_invalid_maxsize(self):
        with pytest.raises(ValueError, match="maxsize must be positive"):
            LRUCache(maxsize=0)
        with pytest.raises(ValueError, match="maxsize must be positive"):
            LRUCache(maxsize=-1)

    def test_basic_operations(self):
        cache = LRUCache(maxsize=2)

        cache["a"] = 1
        assert cache["a"] == 1
        assert len(cache) == 1

        assert cache.get("a") == 1
        assert cache.get("missing") is None
        assert cache.get("missing", "default") == "default"

    def test_lru_eviction(self):
        cache = LRUCache(maxsize=2)

        cache["a"] = 1
        cache["b"] = 2
        cache["c"] = 3

        assert "a" not in cache
        assert cache["b"] == 2
        assert cache["c"] == 3

    def test_access_updates_order(self):
        cache = LRUCache(maxsize=2)

        cache["a"] = 1
        cache["b"] = 2

        _ = cache["a"]
        cache["c"] = 3

        assert "b" not in cache
        assert cache["a"] == 1
        assert cache["c"] == 3

    def test_setdefault(self):
        cache = LRUCache(maxsize=2)

        assert cache.setdefault("a", 1) == 1
        assert cache["a"] == 1

        assert cache.setdefault("a", 2) == 1
        assert cache["a"] == 1

    def test_pop(self):
        cache = LRUCache(maxsize=2)
        cache["a"] = 1

        assert cache.pop("a") == 1
        assert "a" not in cache

        assert cache.pop("missing", "default") == "default"

        with pytest.raises(KeyError):
            cache.pop("missing")

    def test_popitem(self):
        cache = LRUCache(maxsize=2)
        cache["a"] = 1
        cache["b"] = 2

        key, value = cache.popitem()
        assert key == "a"
        assert value == 1
        assert "a" not in cache

        cache.clear()
        with pytest.raises(KeyError, match="LRUCache is empty"):
            cache.popitem()

    def test_clear(self):
        cache = LRUCache(maxsize=2)
        cache["a"] = 1
        cache["b"] = 2

        cache.clear()
        assert len(cache) == 0
        assert "a" not in cache
        assert "b" not in cache

    def test_iteration(self):
        cache = LRUCache(maxsize=3)
        items = [("a", 1), ("b", 2), ("c", 3)]

        for k, v in items:
            cache[k] = v

        cached_items = [(k, cache._data[k]) for k in cache._data]
        assert len(cached_items) == len(items)
        assert set(cached_items) == set(items)

    def test_maintains_insertion_order(self):
        cache = LRUCache(maxsize=3)

        cache["a"] = 1
        cache["b"] = 2
        cache["c"] = 3

        keys = list(cache._data.keys())
        assert keys == ["a", "b", "c"]

        _ = cache["b"]

        keys = list(cache._data.keys())
        assert keys == ["a", "c", "b"]

    def test_repr(self):
        cache = LRUCache(maxsize=2)
        cache["a"] = 1

        expected = "LRUCache({'a': 1}, maxsize=2)"
        assert repr(cache) == expected

    def test_setitem_existing_updates_order(self):
        cache = LRUCache(maxsize=2)
        cache["a"] = 1
        cache["b"] = 2
        cache["a"] = 3

        assert list(cache) == ["b", "a"]
        assert cache["a"] == 3

    def test_iter_reflects_access_order(self):
        cache = LRUCache(maxsize=2)
        cache["a"] = 1
        cache["b"] = 2
        _ = cache["a"]

        assert list(cache) == ["b", "a"]

    def test_missing_key_raises(self):
        cache = LRUCache(maxsize=2)
        with pytest.raises(KeyError):
            cache["missing"]

    def test_pop_with_default_missing(self):
        cache = LRUCache(maxsize=2)
        cache["a"] = 1

        value = cache.pop("a")
        assert value == 1
        assert "a" not in cache

        with pytest.raises(KeyError):
            cache.pop("missing")

        assert cache.pop("missing", "default") == "default"

    def test_missing_dunder(self):
        cache = LRUCache(maxsize=2)
        with pytest.raises(KeyError, match="test_key"):
            cache.__missing__("test_key")

    def test_pop_existing_deletes(self):
        cache = LRUCache(maxsize=2)
        cache["a"] = 1
        cache["b"] = 2

        value = cache.pop("a")
        assert value == 1
        assert "a" not in cache
        assert len(cache) == 1

        with pytest.raises(KeyError):
            cache["a"]

    def test_pop_with_default_success(self):
        cache = LRUCache(maxsize=2)
        cache["a"] = 1

        value = cache.pop("a", "default")
        assert value == 1
        assert "a" not in cache
