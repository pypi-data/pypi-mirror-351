from ..engine import R

# 0 is a natural number.
t1 = R("""
-------------
(零 是自然数)
""")

# For every natural number x, x = x. That is, equality is reflexive.
t2 = R("""
('x 是自然数)
-------------
('x = 'x)
""")

# For all natural numbers x and y, if x = y, then y = x. That is, equality is symmetric.
t3 = R("""
('x 是自然数)
('y 是自然数)
('x = 'y)
-------------
('y = 'x)
""")

# For all natural numbers x, y and z, if x = y and y = z, then x = z. That is, equality is transitive.
t4 = R("""
('x 是自然数)
('y 是自然数)
('z 是自然数)
('x = 'y)
('y = 'z)
-------------
('x = 'z)
""")

# For all a and b, if b is a natural number and a = b, then a is also a natural number. That is, the natural numbers are closed under equality.
t5 = R("""
('b 是自然数)
('a = 'b)
-------------
('a 是自然数)
""")

# For every natural number n, S(n) is a natural number. That is, the natural numbers are closed under S.
t6 = R("""
('n 是自然数)
----------------------
(('n 的后继) 是自然数)
""")

# For all natural numbers m and n, if S(m) = S(n), then m = n. That is, S is an injection.
t7 = R("""
('m 是自然数)
('n 是自然数)
(('m 的后继) = ('n 的后继))
-----------
('m = 'n)
""")

# For every natural number n, S(n) = 0 is false. That is, there is no natural number whose successor is 0.
t8 = R("""
('n 是自然数)
-----------
(! (('n 的后继) = 零))
""")

# If K is a set such that:
# - 0 is in K, and
# - for every natural number n, n being in K implies that S(n) is in K,
# then K contains every natural number.
