#!/usr/bin/env python
#coding: utf-8

import unittest
import breakreminder
import time

class TestBreakReminder(unittest.TestCase):
    def setup(self):
        pass

    def test_workmanager(self):
        """
        We are going to test this workmanager: w_3_r_2_w_7_r_9_w
        """
        workmanager = breakreminder.WorkManager()
        self.assertTrue(workmanager.isWorking())

        time.sleep(3)
        workmanager.rest()

        self.assertFalse(workmanager.isWorking())

        time.sleep(2)
        workmanager.work()

        self.assertTrue(workmanager.isWorking())
        self.assertEqual(workmanager.getPrevWorkingAndRestTime(), (3, 2))

        time.sleep(7)
        workmanager.rest()

        time.sleep(9)
        workmanager.work()
        self.assertTrue(workmanager.isWorking())
        self.assertEqual(workmanager.getPrevWorkingAndRestTime(), (7, 9))

        self.assertEqual(workmanager.getTotalTime(), 3 + 2 + 7 + 9)

        self.assertEqual(workmanager.getTotalWorkTime(), 3 + 7)

        self.assertEqual(workmanager.getTotalRestTime(), 2 + 9)


if __name__ == '__main__':
    unittest.main()