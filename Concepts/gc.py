import sys
import gc 

print(gc.get_count())

# Manually force a full garbage collection right now
gc.collect()  

# Disable automatic garbage collection (rarely recommended unless tuning performance)
gc.disable()  

# Re-enable it
gc.enable()  

a = [10,20,30]
print(sys.getrefcount(a)) # 2
b = a
c = b
print(sys.getrefcount(a)) # 4
print(sys.getrefcount(c))  # 4
print(sys.getrefcount(b)) # 4 

# Progress: added a short todo and completed it.

# Explanations:

# First print sys.getrefcount(a) → 2: a is one reference; getrefcount() adds a temporary reference for its argument, so 1 + 1 = 2.
# After b = a; c = b, each of a, b, c refers to the same list. sys.getrefcount(a) → 4: three local names (a,b,c) + the temporary argument reference = 4.
# sys.getrefcount(c) and sys.getrefcount(b) → 4 for the same reason (all three names point to the same object).
# Note: getrefcount() reports CPython's reference count including the temporary reference from the call; absolute numbers can vary in other contexts (REPL, optimizations).