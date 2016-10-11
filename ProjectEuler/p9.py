##
 # A Pythagorean triplet is a set of three natural numbers,
 # a < b < c, for which,
 #
 #     a2 + b2 = c2
 #
 # For example, 3^2 + 4^2 = 9 + 16 = 25 = 5^2.
 #
 # There exists exactly one Pythagorean triplet for which a + b + c = 1000.
 # Find the product abc.
 #
 # 1/6/16
 ##

class Main:
    for a in xrange(1, 997):
        for b in xrange(a + 1, 998):
            for c in xrange(b + 1, 999):
                if a + b + c == 1000:
                    if a*a + b*b == (c*c):
                        print "a = %d, b = %d, c = %d" % (a, b, c)
                        print "a * b * c = %d" % (a * b * c)
                        break
