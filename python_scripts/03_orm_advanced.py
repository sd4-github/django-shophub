# =============================================================================
# python_scripts/03_orm_advanced.py  --  LEVEL: ADVANCED  (Django)
# =============================================================================
# Purpose: the Django ORM topics interviewers probe at ~5 YoE.
# Run with:  .venv/bin/python python_scripts/03_orm_advanced.py
#
# Topics: queryset laziness, F() expressions, select_related vs prefetch_related
#         (N+1), aggregation/annotate, defer/only, bulk_create, transactions.

# -----------------------------------------------------------------------------
# 1) QUERYSET LAZINESS  (one of the first "deep" Django questions)
# -----------------------------------------------------------------------------
# A queryset is LAZY: building it does NOT hit the DB. It runs only when
# EVALUATED (iterated, len(), list(), .first(), boolean(), etc.).
#
#   qs = Product.objects.filter(price__gt=10)   # NO SQL yet
#   for p in qs:                                 # <- SQL runs HERE
#       ...
#
# This lets you CHAIN filters without paying for each one:
#
#   qs = Product.objects.all()
#   qs = qs.filter(category=cat)      # still no query
#   qs = qs.order_by("-price")         # still no query
#   results = list(qs)                 # exactly ONE query here

# -----------------------------------------------------------------------------
# 2) F() EXPRESSIONS  (atomic in-database updates — avoids races)
# -----------------------------------------------------------------------------
# Instead of read-in-Python-then-write (racy), ask the DB to do the math:
#
#   Product.objects.filter(pk=1).update(stock=F("stock") - 1)
#
# The SQL becomes:  UPDATE product SET stock = stock - 1 WHERE id = 1
# Two concurrent requests can no longer both read the same stale `stock`.
# (Our orders app uses F() to decrement stock atomically — see orders/views.py.)

# -----------------------------------------------------------------------------
# 3) N+1 PROBLEM and select_related / prefetch_related
# -----------------------------------------------------------------------------
# N+1: fetching a list of rows, then hitting the DB once PER related row.
#
#   BAD  --  for each order, a NEW query for its user (N+1 queries total)
#     orders = Order.objects.all()
#     for o in orders:
#         print(o.user.email)        # triggers a query EVERY iteration
#
#   GOOD -- select_related for FOREIGN KEY / OneToOne (a JOIN, ONE query):
#     orders = Order.objects.select_related("user").all()
#
#   GOOD -- prefetch_related for ManyToMany / reverse FK (TWO extra queries):
#     orders = Order.objects.prefetch_related("items__product").all()
#       -> 1 query for orders, 1 for items (with order_id IN ...), 1 for products
#
# Rule of thumb:
#   * forward FK / O2O  (Order.user)              -> select_related
#   * reverse FK / M2M  (Order.items -> Product)  -> prefetch_related
#
# You can combine:  Order.objects.select_related("user").prefetch_related("items__product")

# -----------------------------------------------------------------------------
# 4) AGGREGATION & ANNOTATION  (math done in the DB, not Python)
# -----------------------------------------------------------------------------
#   from django.db.models import Count, Sum, Avg, F, Q, Max, Min
#
#   # Aggregate over the WHOLE table -> a single dict/scalar
#   Order.objects.aggregate(total=Sum("total"), average=Avg("total"))
#
#   # Annotate adds a computed column to EACH row (GROUP BY semantics)
#   Product.objects.annotate(order_count=Count("orderitem"))
#
# These push heavy math into SQL so you do NOT ship rows to Python just to sum.

# -----------------------------------------------------------------------------
# 5) defer() / only()  (slim queries for expensive columns)
# -----------------------------------------------------------------------------
# Big text/blob columns you rarely need? Skip loading them:
#
#   Product.objects.defer("description")   # load everything except description
#   Product.objects.only("name", "price")  # load ONLY name & price
#
# Accessing a deferred field triggers a follow-up query, so use only where it
# clearly helps (e.g. list endpoints needing just a title).

# -----------------------------------------------------------------------------
# 6) bulk_create  (one INSERT for many rows instead of N)
# -----------------------------------------------------------------------------
#   Product.objects.bulk_create([
#       Product(name="A", price=1),
#       Product(name="B", price=2),
#   ])
# Our OrderCreateSerializer uses bulk_create for OrderItems (see serializers.py).

# -----------------------------------------------------------------------------
# 7) TRANSACTIONS  (atomic, select_for_update)
# -----------------------------------------------------------------------------
#   from django.db import transaction
#   with transaction.atomic():
#       order = Order.objects.create(user=user)          # all-or-nothing
#       OrderItem.objects.bulk_create(items)            # rolled back on error
#
#   # Lock a row for update so concurrent requests serialize (prevents double
#   # spending): inside the atomic block:
#   product = Product.objects.select_for_update().get(id=1)
#
# With ATOMIC_REQUESTS you can wrap entire requests, but explicit blocks are
# clearer and only lock what you need.

# -----------------------------------------------------------------------------
# Run-time check (only if run inside the project, with DB reachable)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("03_orm_advanced.py — conceptual guide, comment-out sections and run")
    print("inside Django shell for a live demo:")
    print("  .venv/bin/python manage.py shell -c")
