##
 # The sum of the primes below 10 is 2 + 3 + 5 + 7 = 17.
 #
 # Find the sum of all the primes below two million.
 #
 # --- I think this is working, but it currently takes too long.
 ##

import sys, os

MAX = 2000000;

def checkPrime(n):
    range = n;
    for i in xrange(2, range):
        if n % i == 0:
            return False

        range = n / i

    return True;


class Main:
    s = 0;

    for i in xrange(2, MAX):
        if checkPrime(i):
            s += i

    print "Sum = %d" % s



# def isPrime(number):
#     if number >= 2:
#         for n in range(2, number):
#             if n > number / 2:
#                 break

#             if n % 2 != 0 and n % 3 != 0:
#                 if number % n == 0:
#                     return False
#     else:
#         return False

#     return True


# class Main:
#     # add 2 + 3 already. start the range at 5 so we bypass 4
#     #  -- this will help improve effeciency
#     s = 5;

#     print '[..........]'

#     for num in xrange(5, 2000000):
#         if num % 2 != 0 and num % 3 != 0:
#             if isPrime(num):
#                 s += num

#         if num % 10000 == 0:
#             print num

#         # print to console
#         if num % 200000 == 0:
#             os.system('clear')

#             print '[',
#             for i in range(1, num / 200000):
#                 print '#',
#             for i in range(num / 200000, 10):
#                 print '.',
#             print ']'

#     print "Sum = %d" % s
