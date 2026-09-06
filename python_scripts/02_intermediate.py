# =============================================================================
# python_scripts/02_intermediate.py  --  LEVEL: INTERMEDIATE  (Django)
# =============================================================================
# Purpose: concepts that power Django's ORM / DRF under the hood.
# Run with:  .venv/bin/python python_scripts/02_intermediate.py
#
# Topics: classes & inheritance, magic methods, decorators, context managers,
#         argument passing (mutable default pitfalls), *typing basics, closures.

# --- Inheritance & super() ---------------------------------------------------
# Django ModelSerializer / views use inheritance + super() everywhere.
class SayHello:
    def hello(self):
        return "Hello"

class World(SayHello):
    def hello(self):
        base = super().hello()      # call parent's version
        return f"{base}, World"

print(World().hello())

# --- Decorators (used pervasively in Django/DRF) -----------------------------
# A decorator is a callable that takes a function and returns a (wrapped) one.
import functools

def logged(func):
    @functools.wraps(func)          # preserve __name__ / __doc__
    def wrapper(*args, **kwargs):
        print(f"CALL {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@logged
def add(a, b):
    return a + b

print(add(2, 3))

# Decorator WITH arguments (e.g. permission_classes in DRF is similar in spirit)
def repeat(times: int):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            results = []
            for _ in range(times):
                results.append(func(*args, **kwargs))
            return results
        return wrapper
    return decorator

@repeat(3)
def poke():
    return "poke"

print(poke())

# --- Context managers ---------------------------------------------------------
# `with open(...) as f:` uses __enter__/__exit__. That's what guarantees the
# file closes. You can build your own for consistency (like transaction.atomic).
class AtomicTag:
    def __enter__(self):
        print("BEGIN")
        return self                       # value bound by `as`
    def __exit__(self, exc_type, exc, tb):
        print("COMMIT" if exc_type is None else "ROLLBACK")
        return False                      # False => propagate exceptions

with AtomicTag() as txn:
    print("doing work...")

# --- Mutable default arg gotcha (famous interview question) -------------------
def append_to(element, target=[]):      # BAD: shared mutable default
    target.append(element)
    return target

a1 = append_to(1)
a2 = append_to(2)
print(a1, a2)        # both [1, 2] — the SAME list was mutated!

def append_ok(element, target=None):    # GOOD: immutable default + create per call
    if target is None:
        target = []
    target.append(element)
    return target

print(append_ok(1), append_ok(2))     # [1] [2]

# --- Closures ----------------------------------------------------------------
# Inner functions remember their enclosing scope even after outer has returned.
def make_multiplier(factor: int):
    def multiply(x: int) -> int:
        return x * factor
    return multiply

double = make_multiplier(2)
print(double(21))          # 42

# --- Typing 101 ---------------------------------------------------------------
from typing import Optional, List, Dict, Callable
def get_or_default(d: Dict[str, int], key: str, default: Optional[int] = None) -> Optional[int]:
    return d.get(key, default)

print(get_or_default({"a": 1}, "b", 0))

if __name__ == "__main__":
    print("02_intermediate.py ran OK")
