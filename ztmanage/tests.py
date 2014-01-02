"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

# from django.test import TestCase
#
# class SimpleTest(TestCase):
#     def test_basic_addition(self):
#         """
#         Tests that 1 + 1 always equals 2.
#         """
#         self.failUnlessEqual(1 + 1, 2)
#
# __test__ = {"doctest": """
# Another way to test that 1 + 1 is equal to 2.
#
# >>> 1 + 1 == 2
# True
# """}

html = {u"\x00\x03\x00\x00\x00\x01\x00\x04null\x00\x02/2\x00\x00\x01\ufffd\n\x00\x00\x00\x01\x11\n\ufffd\x13Oflex.messaging.messages.RemotingMessage\rsource\x13operation\tbody\x11clientId\x13messageId\x13timestamp\x0fheaders\x15timeToLive\x17destination\x01\x06\x11saveUser\t\x03\x01\n\x0b\x01\x13last_name\x06\x13\u50a8\u5de7\u9759\x05id\x04\x05\x11username\x06\x07CQJ\x13is_active\x02\x17permissions\t\x05\x01\x06\x19user_manager\x06\x17scx_manager\x01\x06I0227ac89-3761-4212-872a-a30f94b2755b\x06I6E9F3EE8-654B-BB70-4C2C-524A6561C37F\x04\x00\n\x05\x15DSEndpoint\x06\x1bpyamf-channel'DSRemoteCredentials\x06\x01\tDSId\x06\x07nil5DSRemoteCredentialsCharset\x01\x01\x04\x00\x06\x0fservice": [u'']}
print html.keys()[0]