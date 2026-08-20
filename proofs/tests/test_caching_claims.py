"""Proofs for python-best-practices caching rule claims (perf-lru-cache-pure-fns, simplify-cached-property)."""

import functools
import gc
import sys
import weakref


def test_cached_property_lock_removed_in_312():
    """simplify-cached-property: "On 3.8–3.11, a class-wide lock serialized first access ...
    On 3.12+, the lock is gone."
    """
    prop = functools.cached_property(lambda self: 1)
    if sys.version_info < (3, 12):
        assert hasattr(prop, "lock")  # the class-wide RLock the rule describes
    else:
        assert not hasattr(prop, "lock")


def test_lru_cache_on_method_pins_instances_until_clear():
    """perf-lru-cache-pure-fns: "the cache holds a strong reference to every instance it has
    seen — released only on eviction or cache_clear()."
    """

    class Thing:
        @functools.lru_cache(maxsize=8)  # noqa: B019 — the claim under test
        def compute(self) -> int:
            return 1

    thing = Thing()
    thing.compute()
    ref = weakref.ref(thing)
    del thing
    gc.collect()
    assert ref() is not None  # pinned by the cache entry

    Thing.compute.cache_clear()
    gc.collect()
    assert ref() is None  # released after cache_clear()


def test_lru_cache_bounded_eviction_releases_instances():
    """perf-lru-cache-pure-fns: "A bounded LRU retains up to maxsize instances." """

    class Thing:
        @functools.lru_cache(maxsize=1)  # noqa: B019 — the claim under test
        def compute(self) -> int:
            return 1

    first = Thing()
    first.compute()
    first_ref = weakref.ref(first)
    del first
    gc.collect()
    assert first_ref() is not None  # still the sole cache entry

    second = Thing()
    second.compute()  # evicts the entry pinning `first`
    gc.collect()
    assert first_ref() is None  # eviction released it
    assert second is not None
