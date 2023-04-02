#!/usr/bin/env python3
import time
import unittest

from opendbc.can.parser import CANParser
from opendbc.can.packer import CANPacker
from opendbc.can.tests.test_packer_parser import can_list_to_can_capnp



class TestParser(unittest.TestCase):
  def _benchmark(self, signals, checks, thresholds, n):
    parser = CANParser('toyota_new_mc_pt_generated', signals, checks, 0, False)
    packer = CANPacker('toyota_new_mc_pt_generated')
    can_msgs = []
    for i in range(50000):
      values = {"ACC_CONTROL": {"ACC_TYPE": 1, "ALLOW_LONG_PRESS": 3}}
      msgs = [packer.make_can_msg(k, 0, v) for k, v in values.items()]
      bts = can_list_to_can_capnp(msgs, logMonoTime=int(0.01 * i * 1e9))
      can_msgs.append(bts)

    strings = []
    for i in range(0, len(can_msgs), n):
      strings.append(can_msgs[i:i + n])
    t1 = time.process_time_ns()
    for m in strings:
      parser.update_strings(m)
    t2 = time.process_time_ns()

    et = t2 - t1
    avg_nanos = et / len(can_msgs)
    print('%s: [n=%d] %.1fms to parse %s, avg: %dns' % (self._testMethodName, n, et/1e6, len(can_msgs), avg_nanos))

    minn, maxx = thresholds
    self.assertLess(avg_nanos, maxx)
    self.assertGreater(avg_nanos, minn, "Performance seems to have improved, update test thresholds.")

  def test_performance_all_signals(self):
    self._benchmark([], [('ACC_CONTROL', 10)], (11000, 18000), 1)
    self._benchmark([], [('ACC_CONTROL', 10)], (1700, 2500), 10)


if __name__ == "__main__":
  unittest.main()
