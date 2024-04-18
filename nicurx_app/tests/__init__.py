import unittest

def suite():  
    return unittest.TestLoader().discover("nicurx.tests", pattern="*.py")