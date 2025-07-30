# examples/demo.py
"""
Demo script showcasing MiniNumPy functionality and performance comparison
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import time
from core.array import MiniArray, zeros, ones, arange
from operations.arithmetic import add, multiply, add_parallel, multiply_parallel
from operations.stats import sum_array, mean, sum_parallel, mean_parallel


def print_separator(title):
    """Print a nice separator for demo sections"""
    print("\n" + "="*50)
    print(f" {title}")
    print("="*50)


def demo_basic_operations():
    """Demonstrate basic array operations"""
    print_separator("BASIC ARRAY OPERATIONS")
    
    # Create arrays
    print("Creating arrays...")
    arr1 = MiniArray([1, 2, 3, 4, 5, 6], shape=(2, 3))
    arr2 = ones((2, 3))
    
    print(f"Array 1: {arr1}")
    print(f"Array 2: {arr2}")
    print(f"Array 1 shape: {arr1.shape}, size: {arr1.size}")
    
    # Indexing
    print(f"\nIndexing examples:")
    print(f"arr1[0] = {arr1[0]}")
    print(f"arr1[1, 2] = {arr1[1, 2]}")
    
    # Reshaping
    reshaped = arr1.reshape((3, 2))
    print(f"\nReshaped to (3, 2): {reshaped}")
    
    # Basic arithmetic
    sum_result = add(arr1, arr2)
    print(f"\nAddition result: {sum_result}")
    
    mult_result = multiply(arr1, arr2)  
    print(f"Multiplication result: {mult_result}")


def demo_array_creation():
    """Demonstrate array creation functions"""
    print_separator("ARRAY CREATION FUNCTIONS")
    
    # Zeros and ones
    zeros_arr = zeros((3, 4))
    ones_arr = ones((2, 5))
    
    print(f"Zeros (3, 4): {zeros_arr}")
    print(f"Ones (2, 5): {ones_arr}")
    
    # Arange
    range_arr = arange(0, 10, 2)
    print(f"Arange(0, 10, 2): {range_arr}")
    
    # Large array for performance testing
    large_arr = ones((1000,))
    print(f"\nLarge array created with shape: {large_arr.shape}")


def demo_statistics():
    """Demonstrate statistical operations"""
    print_separator("STATISTICAL OPERATIONS")
    
    arr = MiniArray([1, 5, 3, 9, 2, 7, 4, 8, 6])
    print(f"Array: {arr}")
    
    print(f"Sum: {sum_array(arr)}")
    print(f"Mean: {mean(arr):.2f}")
    print(f"Max: {max(arr.data)}")
    print(f"Min: {min(arr.data)}")


def benchmark_operations():
    """Benchmark sequential vs parallel operations"""
    print_separator("PERFORMANCE BENCHMARKING")
    
    # Create large arrays for meaningful comparison
    size = 100000
    print(f"Creating arrays of size {size:,}...")
    
    arr1 = ones((size,))
    arr2 = arange(0, size)
    
    # Warm up
    _ = add(arr1, arr2)
    
    print("\nBenchmarking Addition:")
    print("-" * 30)
    
    # Sequential addition
    start_time = time.time()
    result_seq = add(arr1, arr2)
    seq_time = time.time() - start_time
    print(f"Sequential time: {seq_time:.4f} seconds")
    
    # Parallel addition with different thread counts
    for n_threads in [2, 4, 8]:
        start_time = time.time()
        result_par = add_parallel(arr1, arr2, n_threads=n_threads)
        par_time = time.time() - start_time
        speedup = seq_time / par_time if par_time > 0 else 0
        print(f"Parallel ({n_threads} threads): {par_time:.4f} seconds (speedup: {speedup:.2f}x)")
    
    # Verify results are the same
    print(f"Results match: {result_seq.data == result_par.data}")
    
    print("\nBenchmarking Statistical Operations:")
    print("-" * 40)
    
    # Sequential sum
    start_time = time.time()
    sum_seq = sum_array(arr1)
    seq_time = time.time() - start_time
    print(f"Sequential sum: {seq_time:.4f} seconds (result: {sum_seq})")
    
    # Parallel sum
    for n_threads in [2, 4, 8]:
        start_time = time.time()
        sum_par = sum_parallel(arr1, n_threads=n_threads)
        par_time = time.time() - start_time
        speedup = seq_time / par_time if par_time > 0 else 0
        print(f"Parallel sum ({n_threads} threads): {par_time:.4f} seconds (speedup: {speedup:.2f}x)")
    
    print(f"Sum results match: {sum_seq == sum_par}")


def demo_memory_usage():
    """Demonstrate memory considerations"""
    print_separator("MEMORY USAGE DEMONSTRATION")
    
    sizes = [1000, 10000, 100000]
    
    for size in sizes:
        arr = zeros((size,))
        # Rough memory estimation (each float64 is 8 bytes, plus Python overhead)
        estimated_mb = (size * 8) / (1024 * 1024)
        print(f"Array size {size:,}: ~{estimated_mb:.2f} MB")


def demo_advanced_indexing():
    """Demonstrate advanced indexing and operations"""
    print_separator("ADVANCED OPERATIONS")
    
    # 2D array operations
    matrix = MiniArray([1, 2, 3, 4, 5, 6, 7, 8, 9], shape=(3, 3))
    print(f"3x3 Matrix:\n{matrix}")
    
    # Element access
    print(f"\nMatrix[1, 1] = {matrix[1, 1]}")
    print(f"Matrix[2, 0] = {matrix[2, 0]}")
    
    # Modify elements
    matrix[0, 0] = 10
    print(f"\nAfter setting [0,0] = 10:\n{matrix}")
    
    # Create another matrix for operations
    matrix2 = ones((3, 3))
    print(f"\nOnes matrix:\n{matrix2}")
    
    # Matrix addition
    result = add(matrix, matrix2)
    print(f"\nMatrix addition result:\n{result}")


def run_all_demos():
    """Run all demonstration functions"""
    print("MINI NUMPY LIBRARY DEMONSTRATION")
    print("=" * 60)
    print("A simplified numpy-like library with parallel computing support")
    
    try:
        demo_basic_operations()
        demo_array_creation()
        demo_statistics()
        demo_advanced_indexing()
        demo_memory_usage()
        benchmark_operations()
        
        print_separator("DEMO COMPLETED SUCCESSFULLY")
        print("All operations completed without errors!")
        print("Check the performance results above to see parallel speedups.")
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_demos()