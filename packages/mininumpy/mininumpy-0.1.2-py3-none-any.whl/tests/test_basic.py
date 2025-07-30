# tests/test_basic.py
import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.array import MiniArray, zeros, ones, arange
from operations.arithmetic import add, subtract, multiply, divide, add_parallel, multiply_parallel
from operations.stats import sum_array, mean, max_array, min_array, sum_parallel, mean_parallel

class TestMiniArray(unittest.TestCase):
    """Test cases for MiniArray class"""
    
    def test_array_creation(self):
        """Test basic array creation"""
        # Test with list
        arr = MiniArray([1, 2, 3, 4])
        self.assertEqual(arr.shape, (4,))
        self.assertEqual(arr.size, 4)
        self.assertEqual(arr.ndim, 1)
        
        # Test with 2D shape
        arr = MiniArray([1, 2, 3, 4], shape=(2, 2))
        self.assertEqual(arr.shape, (2, 2))
        self.assertEqual(arr.size, 4)
        self.assertEqual(arr.ndim, 2)
    
    def test_indexing(self):
        """Test array indexing"""
        arr = MiniArray([1, 2, 3, 4], shape=(2, 2))
        
        # Test single index
        self.assertEqual(arr[0], 1)
        self.assertEqual(arr[3], 4)
        
        # Test 2D indexing
        self.assertEqual(arr[0, 0], 1)
        self.assertEqual(arr[0, 1], 2)
        self.assertEqual(arr[1, 0], 3)
        self.assertEqual(arr[1, 1], 4)
    
    def test_setting_values(self):
        """Test setting array values"""
        arr = MiniArray([1, 2, 3, 4])
        arr[0] = 10
        self.assertEqual(arr[0], 10)
        
        arr = MiniArray([1, 2, 3, 4], shape=(2, 2))
        arr[0, 1] = 20
        self.assertEqual(arr[0, 1], 20)
    
    def test_reshape(self):
        """Test array reshaping"""
        arr = MiniArray([1, 2, 3, 4, 5, 6])
        reshaped = arr.reshape((2, 3))
        self.assertEqual(reshaped.shape, (2, 3))
        self.assertEqual(reshaped[1, 2], 6)
    
    def test_flatten(self):
        """Test array flattening"""
        arr = MiniArray([1, 2, 3, 4], shape=(2, 2))
        flattened = arr.flatten()
        self.assertEqual(flattened.shape, (4,))
        self.assertEqual(flattened.data, [1, 2, 3, 4])

class TestArrayCreation(unittest.TestCase):
    """Test cases for array creation functions"""
    
    def test_zeros(self):
        """Test zeros function"""
        arr = zeros((3, 2))
        self.assertEqual(arr.shape, (3, 2))
        self.assertEqual(arr.data, [0.0] * 6)
    
    def test_ones(self):
        """Test ones function"""
        arr = ones((2, 3))
        self.assertEqual(arr.shape, (2, 3))
        self.assertEqual(arr.data, [1.0] * 6)
    
    def test_arange(self):
        """Test arange function"""
        arr = arange(0, 5)
        self.assertEqual(arr.data, [0, 1, 2, 3, 4])
        
        arr = arange(1, 10, 2)
        self.assertEqual(arr.data, [1, 3, 5, 7, 9])

class TestArithmetic(unittest.TestCase):
    """Test cases for arithmetic operations"""
    
    def setUp(self):
        self.arr1 = MiniArray([1, 2, 3, 4])
        self.arr2 = MiniArray([5, 6, 7, 8])
    
    def test_add(self):
        """Test addition"""
        result = add(self.arr1, self.arr2)
        expected = [6, 8, 10, 12]
        self.assertEqual(result.data, expected)
    
    def test_subtract(self):
        """Test subtraction"""
        result = subtract(self.arr2, self.arr1)
        expected = [4, 4, 4, 4]
        self.assertEqual(result.data, expected)
    
    def test_multiply(self):
        """Test multiplication"""
        result = multiply(self.arr1, self.arr2)
        expected = [5, 12, 21, 32]
        self.assertEqual(result.data, expected)
    
    def test_divide(self):
        """Test division"""
        result = divide(self.arr2, self.arr1)
        expected = [5.0, 3.0, 7/3, 2.0]
        self.assertEqual(result.data, expected)
    
    def test_parallel_add(self):
        """Test parallel addition"""
        result = add_parallel(self.arr1, self.arr2, n_threads=2)
        expected = [6, 8, 10, 12]
        self.assertEqual(result.data, expected)
    
    def test_parallel_multiply(self):
        """Test parallel multiplication"""
        result = multiply_parallel(self.arr1, self.arr2, n_threads=2)
        expected = [5, 12, 21, 32]
        self.assertEqual(result.data, expected)

class TestStatistics(unittest.TestCase):
    """Test cases for statistical operations"""
    
    def setUp(self):
        self.arr = MiniArray([1, 2, 3, 4, 5])
    
    def test_sum(self):
        """Test sum function"""
        result = sum_array(self.arr)
        self.assertEqual(result, 15)
    
    def test_mean(self):
        """Test mean function"""
        result = mean(self.arr)
        self.assertEqual(result, 3.0)
    
    def test_max(self):
        """Test max function"""
        result = max_array(self.arr)
        self.assertEqual(result, 5)
    
    def test_min(self):
        """Test min function"""
        result = min_array(self.arr)
        self.assertEqual(result, 1)
    
    def test_parallel_sum(self):
        """Test parallel sum"""
        result = sum_parallel(self.arr, n_threads=2)
        self.assertEqual(result, 15)
    
    def test_parallel_mean(self):
        """Test parallel mean"""
        result = mean_parallel(self.arr, n_threads=2)
        self.assertEqual(result, 3.0)

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def test_empty_array(self):
        """Test empty array handling"""
        arr = MiniArray([])
        self.assertEqual(arr.size, 0)
        self.assertEqual(arr.shape, (0,))
    
    def test_single_element(self):
        """Test single element array"""
        arr = MiniArray([42])
        self.assertEqual(arr.size, 1)
        self.assertEqual(arr[0], 42)
        
        # Test operations on single element
        arr2 = MiniArray([10])
        result = add(arr, arr2)
        self.assertEqual(result.data, [52])
    
    def test_shape_mismatch(self):
        """Test operations with mismatched shapes"""
        arr1 = MiniArray([1, 2, 3])
        arr2 = MiniArray([1, 2])
        
        with self.assertRaises(ValueError):
            add(arr1, arr2)
    
    def test_invalid_reshape(self):
        """Test invalid reshape operations"""
        arr = MiniArray([1, 2, 3, 4])
        
        with self.assertRaises(ValueError):
            arr.reshape((2, 3))  # Size mismatch
    
    def test_invalid_indexing(self):
        """Test invalid indexing"""
        arr = MiniArray([1, 2, 3])
        
        with self.assertRaises(IndexError):
            _ = arr[5]

class TestPerformance(unittest.TestCase):
    """Test performance improvements with parallelization"""
    
    def test_large_array_operations(self):
        """Test operations on larger arrays"""
        size = 1000
        arr1 = ones((size,))
        arr2 = ones((size,))
        
        # Sequential operation
        result_seq = add(arr1, arr2)
        
        # Parallel operation
        result_par = add_parallel(arr1, arr2, n_threads=4)
        
        # Results should be the same
        self.assertEqual(result_seq.data, result_par.data)
        
        # Test statistical operations
        sum_seq = sum_array(arr1)
        sum_par = sum_parallel(arr1, n_threads=4)
        
        self.assertEqual(sum_seq, sum_par)

if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)