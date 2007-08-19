# browsershots.org - Test your web design in different browsers
# Copyright (C) 2007 Johann C. Rocholl <johann@browsershots.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston,
# MA 02111-1307, USA.

"""
Test suite for nonces app.
"""

__revision__ = "$Rev$"
__date__ = "$Date$"
__author__ = "$Author$"

from unittest import TestCase
from psycopg import IntegrityError, ProgrammingError, DatabaseError
from django.db import transaction
from django.contrib.auth.models import User
from shotserver04.nonces.models import Nonce
from shotserver04.platforms.models import Architecture
from shotserver04.platforms.models import Platform, OperatingSystem
from shotserver04.factories.models import Factory


class NonceTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create()
        self.factory = Factory.objects.create(
            name='factory',
            admin=self.user,
            architecture=Architecture.objects.get(pk=1),
            operating_system=OperatingSystem.objects.get(pk=1))

    def tearDown(self):
        self.factory.delete()
        self.user.delete()

    def assertNonceValid(self, hashkey):
        try:
            try:
                nonce = Nonce.objects.create(factory=self.factory,
                    hashkey=hashkey, ip='127.0.0.1')
                nonce.delete()
            except (IntegrityError, ProgrammingError):
                self.fail(u"could not create nonce with valid hashkey '%s'" %
                          hashkey)
        finally:
            transaction.rollback()

    def assertNonceInvalid(self, hashkey):
        try:
            try:
                nonce = Nonce.objects.create(factory=self.factory,
                    hashkey=hashkey, ip='127.0.0.1')
                nonce.save()
                nonce.delete()
                self.fail(u"created nonce with invalid hashkey '%s'" % hashkey)
            except (IntegrityError, ProgrammingError):
                pass
        finally:
            transaction.rollback()

    def testValidNonces(self):
        for nonce in [
            '12345678901234567890123456789012',
            'a234b6789012c4567d90123e56789f12',
            '0a234b6789012c4567d90123e56789ff',
            ]:
            self.assertNonceValid(nonce)

    def testInvalidNonces(self):
        for nonce in [
            '1234567890123456789012345678901',
            'a234b6789012c4567d90123e56789f123',
            '0a234b6789012c4567d90123e56789fg',
            ]:
            self.assertNonceInvalid(nonce)

    def testNonceDuplicate(self):
        try:
            hashkey = '0123456789abcdef' * 2
            nonce = Nonce.objects.create(hashkey=hashkey,
                factory=self.factory, ip='127.0.0.1')
            self.assertRaises(IntegrityError, Nonce.objects.create,
                hashkey=hashkey, factory=self.factory, ip='127.0.0.1')
        finally:
            transaction.rollback()

    def testInvalidFactoryForNonce(self):
        try:
            self.assertRaises(DatabaseError, Nonce.objects.create,
                              factory_id=-1)
        finally:
            transaction.rollback()