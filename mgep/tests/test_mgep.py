#!/usr/bin/env python
from unittest import TestCase

from mgep import *

class TestMgep(TestCase):
    def test_world_is_dict(self):
        self.assertTrue(isinstance(world, dict))

    def test_to_normal_map(self):
        self.assertEqual(z_of_byte(128), 0.0)
        self.assertEqual(z_of_byte(255), -1.0)
        self.assertEqual(f_of_byte(128), 0.0)
        self.assertEqual(f_of_byte(0), -1.0)
        self.assertEqual(f_of_byte(255), 1.0)

    def test_from_normal_map(self):
        self.assertEqual(byte_of_z(0.0), 128)
        self.assertEqual(byte_of_z(-1.0), 255)
        self.assertEqual(byte_of_f(0.0), 128)
        self.assertEqual(byte_of_f(-1.0), 0)
        self.assertEqual(byte_of_f(1.0), 255)
