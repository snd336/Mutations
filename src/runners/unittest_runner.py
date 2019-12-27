import unittest


def suites():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite(loader.discover('./src/tests'))
    return suite


def debug_suit():
    suite_obj = suites()
    suite_obj.debug()


if __name__ == '__main__':
    debug_suit()
