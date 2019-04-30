#!/usr/bin/env python3
##############################################################################
# The MIT License (MIT)
#
# Copyright (c) 2016-2019 Hajime Nakagami<nakagami@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
##############################################################################
"""Tests for db2"""
import unittest
import os
import decimal
import datetime
import decimal
import drda


class TestBasic(unittest.TestCase):
    host = os.environ['DB2_HOST']
    database = os.environ['DB2_DATABASE']
    user = os.environ['DB2_USER']
    password = os.environ['DB2_PASSWORD']
    port = int(os.environ['DB2_PORT'])

    def setUp(self):
        self.connection = drda.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password,
            port=self.port,
        )
        cur = self.connection.cursor()
        try:
            cur.execute("DROP TABLE test_basic")
        except drda.OperationalError:
            pass
        cur.execute("""
            CREATE TABLE test_basic (
                s VARCHAR(20),
                i int,
                d1 decimal(2, 1),
                d2 decimal(11, 2)
            )
            """)
        self.connection.commit()

    def tearDown(self):
        self.connection.close()

    def test_basic(self):
        cur = self.connection.cursor()
        cur.execute("""
            INSERT INTO test_basic (s, i, d1, d2) VALUES
                ('abcdefghijklmnopq', 1, 1.1, 123456789.12),
                ('B', 2, 1.2, -2),
                ('C', 3, null, null)
        """)
        cur.execute("SELECT * FROM test_basic")
        self.assertEqual(cur.description, [
            ('S', 449, 20, 20, 0, 0, None),
            ('I', 497, 4, 4, 0, 0, None),
            ('D1', 485, 0, 0, 2, 1, None),
            ('D2', 485, 0, 0, 11, 2, None)
        ])
        self.assertEqual(cur.fetchall(), [
            ('abcdefghijklmnopq', 1, decimal.Decimal('1.1'), decimal.Decimal('123456789.12')),
            ('B', 2, decimal.Decimal('1.2'), decimal.Decimal('-2.00')),
            ('C', 3, None, None)
        ])

    def test_error(self):
        cur = self.connection.cursor()
        with self.assertRaises(drda.OperationalError):
            cur.execute("invalid query"),


class TestDataType(unittest.TestCase):
    host = os.environ['DB2_HOST']
    database = os.environ['DB2_DATABASE']
    user = os.environ['DB2_USER']
    password = os.environ['DB2_PASSWORD']
    port = int(os.environ['DB2_PORT'])

    def setUp(self):
        self.connection = drda.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password,
            port=self.port,
        )

    def test_datetime(self):
        cur = self.connection.cursor()
        try:
            cur.execute("DROP TABLE test_datetime")
        except drda.OperationalError:
            pass
        cur.execute("""
            CREATE TABLE test_datetime (
                d date,
                t time,
                dt timestamp
            )
        """)
        cur.execute("""
            INSERT INTO test_datetime (d, t, dt) VALUES
                ('2019-04-30', '12:34:56', '2019-04-30 12:34:56.123456789')
        """)
        cur.execute("SELECT * FROM test_datetime")
        self.assertEqual(cur.fetchall(), [(
            datetime.date(2019, 4, 30),
            datetime.time(12, 34, 56),
            datetime.datetime(2019, 4, 30, 12, 34, 56, 123456)
        )])

    def test_double(self):
        cur = self.connection.cursor()
        try:
            cur.execute("""
                CREATE TABLE test_double (
                    bi bigint,
                    si smallint,
                    r real,
                    d double
                )
            """)
        except drda.OperationalError:
            pass
        cur.execute("DELETE FROM test_double")
        cur.execute("""
            INSERT INTO test_double (bi, si, r, d) VALUES
                (-1, -1, -1, -1)
        """)
        cur.execute("SELECT * FROM test_double")
        self.assertEqual(cur.fetchall(), [(-1, -1, -1.0, -1.0)])

    def tearDown(self):
        self.connection.close()


if __name__ == "__main__":
    import unittest
    unittest.main()
