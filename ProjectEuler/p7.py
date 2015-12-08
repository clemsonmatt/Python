##
 # By listing the first six prime numbers: 2, 3, 5, 7, 11, and 13, we can see that the 6th prime is 13.
 # What is the 10,001st prime number?
 #
 # 12/8/15
 ##

import sys, os

def isPrime(number):
    if number >= 2:
        for n in range(2, number):
            if number % n == 0:
                return False
    else:
        return False

    return True


class Main:
    counter = 0;
    number  = 2;

    while counter != 10001:
        if isPrime(number):
            counter += 1

        number += 1

        # print to console
        if counter % 1000 == 0:
            os.system('clear')

            print '[',
            for i in range(1, counter / 1000):
                print '#',
            for i in range(counter / 1000, 10):
                print '.',
            print ']'

    print "10,001st number is: %d" % (number - 1)
