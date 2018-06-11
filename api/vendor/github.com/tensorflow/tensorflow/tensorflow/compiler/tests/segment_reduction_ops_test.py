# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Test cases for segment reduction ops."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import functools
import numpy as np

from tensorflow.compiler.tests.xla_test import XLATestCase
from tensorflow.python.ops import array_ops
from tensorflow.python.ops import math_ops
from tensorflow.python.platform import googletest


class SegmentReductionOpsTest(XLATestCase):
  """Test cases for segment reduction ops."""

  def UnsortedSegmentSum(self, data, indices, num_segments):
    with self.test_session() as sess, self.test_scope():
      d = array_ops.placeholder(data.dtype, shape=data.shape)
      if isinstance(indices, int):
        i = array_ops.placeholder(np.int32, shape=[])
      else:
        i = array_ops.placeholder(indices.dtype, shape=indices.shape)
      return sess.run(
          math_ops.unsorted_segment_sum(d, i, num_segments),
          {d: data,
           i: indices})

  def testUnsortedSegmentSum0DIndices1DData(self):
    for dtype in self.numeric_types:
      self.assertAllClose(
          np.array(
              [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 1, 2, 3, 4, 5],
               [0, 0, 0, 0, 0, 0]],
              dtype=dtype),
          self.UnsortedSegmentSum(
              np.array([0, 1, 2, 3, 4, 5], dtype=dtype), 2, 4))

  def testUnsortedSegmentSum1DIndices1DData(self):
    for dtype in self.numeric_types:
      self.assertAllClose(
          np.array([1, 3, 2, 9], dtype=dtype),
          self.UnsortedSegmentSum(
              np.array([0, 1, 2, 3, 4, 5], dtype=dtype),
              np.array([3, 0, 2, 1, 3, 3], dtype=np.int32), 4))

  def testUnsortedSegmentSum1DIndices1DDataNegativeIndices(self):
    for dtype in self.numeric_types:
      self.assertAllClose(
          np.array([6, 3, 0, 6], dtype=dtype),
          self.UnsortedSegmentSum(
              np.array([0, 1, 2, 3, 4, 5, 6], dtype=dtype),
              np.array([3, -1, 0, 1, 0, -1, 3], dtype=np.int32), 4))

  def testUnsortedSegmentSum1DIndices2DDataDisjoint(self):
    for dtype in self.numeric_types:
      data = np.array(
          [[0, 1, 2, 3], [20, 21, 22, 23], [30, 31, 32, 33], [40, 41, 42, 43],
           [50, 51, 52, 53]],
          dtype=dtype)
      indices = np.array([8, 1, 0, 3, 7], dtype=np.int32)
      num_segments = 10
      y = self.UnsortedSegmentSum(data, indices, num_segments)
      self.assertAllClose(
          np.array(
              [[30, 31, 32, 33], [20, 21, 22, 23], [0, 0, 0, 0],
               [40, 41, 42, 43], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0],
               [50, 51, 52, 53], [0, 1, 2, 3], [0, 0, 0, 0]],
              dtype=dtype), y)

  def testUnsortedSegmentSum1DIndices2DDataNonDisjoint(self):
    for dtype in self.numeric_types:
      data = np.array(
          [[0, 1, 2, 3], [20, 21, 22, 23], [30, 31, 32, 33], [40, 41, 42, 43],
           [50, 51, 52, 53]],
          dtype=dtype)
      indices = np.array([0, 1, 2, 0, 1], dtype=np.int32)
      num_segments = 4
      y = self.UnsortedSegmentSum(data, indices, num_segments)
      self.assertAllClose(
          np.array(
              [[40, 42, 44, 46], [70, 72, 74, 76], [30, 31, 32, 33],
               [0, 0, 0, 0]],
              dtype=dtype), y)

  def testUnsortedSegmentSum2DIndices3DData(self):
    for dtype in self.numeric_types:
      data = np.array(
          [[[0, 1, 2], [10, 11, 12]], [[100, 101, 102], [110, 111, 112]],
           [[200, 201, 202], [210, 211, 212]], [[300, 301, 302],
                                                [310, 311, 312]]],
          dtype=dtype)
      indices = np.array([[3, 5], [3, 1], [5, 0], [6, 2]], dtype=np.int32)
      num_segments = 8
      y = self.UnsortedSegmentSum(data, indices, num_segments)
      self.assertAllClose(
          np.array(
              [[210, 211, 212], [110, 111, 112], [310, 311, 312],
               [100, 102, 104], [0, 0, 0.], [210, 212, 214], [300, 301,
                                                              302], [0, 0, 0]],
              dtype=dtype), y)

  def testUnsortedSegmentSum1DIndices3DData(self):
    for dtype in self.numeric_types:
      data = np.array(
          [[[0, 1, 2], [10, 11, 12]], [[100, 101, 102], [110, 111, 112]],
           [[200, 201, 202], [210, 211, 212]], [[300, 301, 302],
                                                [310, 311, 312]]],
          dtype=dtype)
      indices = np.array([3, 0, 2, 5], dtype=np.int32)
      num_segments = 6
      y = self.UnsortedSegmentSum(data, indices, num_segments)
      self.assertAllClose(
          np.array(
              [[[100, 101, 102.], [110, 111, 112]], [[0, 0, 0], [0, 0, 0]],
               [[200, 201, 202], [210, 211, 212]], [[0, 1, 2.], [10, 11, 12]],
               [[0, 0, 0], [0, 0, 0]], [[300, 301, 302], [310, 311, 312]]],
              dtype=dtype), y)

  def testUnsortedSegmentSumShapeError(self):
    for dtype in self.numeric_types:
      data = np.ones((4, 8, 7), dtype=dtype)
      indices = np.ones((3, 2), dtype=np.int32)
      num_segments = 4
      self.assertRaises(ValueError,
                        functools.partial(self.UnsortedSegmentSum, data,
                                          indices, num_segments))


if __name__ == '__main__':
  googletest.main()
