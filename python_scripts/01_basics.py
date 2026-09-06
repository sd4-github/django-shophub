# =============================================================================
# python_scripts/01_basics.py  --  LEVEL: BASIC  (Django)
# =============================================================================
# Purpose: pure-Python warm-up before touching Django. Read top-to-bottom.
# Run with:  .venv/bin/python python_scripts/01_basics.py
#
# Topics: data types, f-strings, control flow, functions, comprehensions,
#         iterators/generators, *args/**kwargs, maps, OOP basics.
# These fundamentals underpin Django models, querysets and DRF serializers.

# --- Data types -----------------------------------------------------------
name: str = "ShopHub"
price: float = 49.99
in_stock: bool = True
tags: list[str] = ["django", "drf", "postgres"]
meta: dict[str, int] = {"orders": 12}
unique_ids: set[int] = {1, 2, 3}
point: tuple[int, int] = (10, 20)

print(f"{name} — base price ${price:.2f}, in stock: {in_stock}")

# --- Control flow ----------------------------------------------------------
if price > 50 and in_stock:
    status = "premium"
elif price > 20:
    status = "standard"
else:
    status = "budget"
print(status)

for i in range(3):
    print(f"loop {i}")

n = 0
while n < 4:
    n += 1
    if n == 2:
        continue
    if n == 3:
        break

# --- Functions --------------------------------------------------------------
def discount(price: float, *, percent: float = 10) -> float:
    """Default arg + keyword-only arg. Note how a model method looks similar."""
    return round(price * (1 - percent / 100), 2)

print(discount(100), discount(100, percent=50))

def log_all(*args, **kwargs):
    """*args = positional extras; **kwargs = named extras."""
    print("args:", args, "kwargs:", kwargs)

log_all(1, 2, user="alice")

# --- Comprehensions ---------------------------------------------------------
prices = [19.99, 29.99, 9.99]
discounted = [p * 0.9 for p in prices]            # list comp
big_ones = {p for p in prices if p > 15}          # set comp
by_id = {i: p for i, p in enumerate(prices)}      # dict comp (id -> price)
print(discounted, big_ones, by_id)

# --- Iterators & generators (memory-efficient, used by querysets) -----------
def counter(n: int):
    i = 0
    while i < n:
        yield i        # `yield` makes this a GENERATOR — lazy, not a list
        i += 1

for value in counter(3):
    print("gen:", value)

# --- Useful built-ins --------------------------------------------------------
nums = [3, 1, 2]
print(sorted(nums), max(nums), sum(nums))
pairs = list(zip(["a", "b"], [1, 2]))             # combine iterables

# --- OOP basics (models are classes) ----------------------------------------
class Product:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price                        # attribute assignment

    def __repr__(self) -> str:
        return f"Product({self.name})"

    def final_price(self, tax: float = 0.2) -> float:
        return self.price * (1 + tax)

p = Product("Keyboard", 40)
print(p, p.final_price())

if __name__ == "__main__":
    print("01_basics.py ran OK")
