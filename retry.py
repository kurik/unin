#!/usr/bin/env python

import time

# Retry decorator with exponential backoff
def retry(tries, delay=3, backoff=2):
    '''Retries a function or method until it returns True.

    delay sets the initial delay in seconds, and backoff sets the factor by which
    the delay should lengthen after each failure. backoff must be greater than 1,
    or else it isn't really a backoff. tries must be at least 0, and delay
    greater than 0.'''

    if backoff <= 1:
        raise ValueError("backoff must be greater than 1")

    tries = int(tries)
    if tries < 0:
        raise ValueError("tries must be 0 or greater")

    if delay <= 0:
        raise ValueError("delay must be greater than 0")

    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay # make mutable

            try:
                result = f(*args, **kwargs) # first attempt
                rv = True
            except:
                rv = False
            while mtries > 0:
                if rv is True: # Done on success
                    return result

                mtries -= 1      # consume an attempt
                time.sleep(mdelay) # wait...
                mdelay *= backoff  # make future wait longer

                try:
                    result = f(*args, **kwargs) # Try again
                    rv = True
                except:
                    rv = False

            # Ran out of tries :-(
            raise Exception('Ran out of tries')

        return f_retry # true decorator -> decorated function
    return deco_retry  # @retry(arg[, ...]) -> true decorator

# Module test
if __name__ == "__main__":
    @retry(3)
    def __test1():
        print('Test #1 - failing')
        raise Exception('Function #1')
        return False

    @retry(3)
    def __test2():
        print('Test #2 - working')
        return 'Some useful result'

    try:
        print(__test1())
    except:
        print('The test function has been constantly failing')
    print(__test2())
