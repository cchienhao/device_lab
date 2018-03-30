import unittest

from utils.misc import on_exception_return


class TestOnExceptionReturn(unittest.TestCase):
    def test_on_error_exception_return_value(self):
        @on_exception_return(None)
        def raise_exception(msg):
            raise Exception(msg)
        self.assertIsNone(raise_exception('bad things happen'))

    def test_on_error_exception_return_callable(self):
        @on_exception_return(str)
        def raise_exception(msg):
            raise Exception(msg)
        msg = 'bad things happen'
        self.assertEqual(msg, raise_exception(msg))
