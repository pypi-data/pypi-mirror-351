# operations/stats.py

import threading
import multiprocessing as mp
import math
from functools import reduce


# Sequential statistical operations
def sum_array(arr):
    """Calculate sum of all elements in array."""
    if arr.size == 0:
        return 0
    
    total = 0
    for value in arr._data:
        total += value
    return total


def mean(arr):
    """Calculate mean (average) of all elements in array."""
    if arr.size == 0:
        raise ValueError("Cannot calculate mean of empty array")
    
    return sum_array(arr) / arr.size


def max_array(arr):
    """Find maximum value in array."""
    if arr.size == 0:
        raise ValueError("Cannot find max of empty array")
    
    max_val = arr._data[0]
    for value in arr._data[1:]:
        if value > max_val:
            max_val = value
    return max_val


def min_array(arr):
    """Find minimum value in array."""
    if arr.size == 0:
        raise ValueError("Cannot find min of empty array")
    
    min_val = arr._data[0]
    for value in arr._data[1:]:
        if value < min_val:
            min_val = value
    return min_val


def std(arr, ddof=0):
    """Calculate standard deviation of array elements."""
    if arr.size == 0:
        raise ValueError("Cannot calculate std of empty array")
    if arr.size == 1:
        return 0.0
    
    array_mean = mean(arr)
    variance_sum = 0
    
    for value in arr._data:
        variance_sum += (value - array_mean) ** 2
    
    # ddof = delta degrees of freedom (0 for population, 1 for sample)
    variance = variance_sum / (arr.size - ddof)
    return math.sqrt(variance)


def var(arr, ddof=0):
    """Calculate variance of array elements."""
    if arr.size == 0:
        raise ValueError("Cannot calculate variance of empty array")
    if arr.size == 1:
        return 0.0
    
    array_mean = mean(arr)
    variance_sum = 0
    
    for value in arr._data:
        variance_sum += (value - array_mean) ** 2
    
    return variance_sum / (arr.size - ddof)


def median(arr):
    """Calculate median of array elements."""
    if arr.size == 0:
        raise ValueError("Cannot calculate median of empty array")
    
    # Sort the data
    sorted_data = sorted(arr._data)
    n = len(sorted_data)
    
    if n % 2 == 0:
        # Even number of elements - average of middle two
        return (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
    else:
        # Odd number of elements - middle element
        return sorted_data[n//2]


# Parallel statistical operations using threading
def _thread_worker_sum(data, start_idx, end_idx, result_list, thread_id):
    """Worker function for parallel sum calculation."""
    partial_sum = 0
    for i in range(start_idx, end_idx):
        partial_sum += data[i]
    result_list[thread_id] = partial_sum


def sum_parallel(arr, n_threads=4):
    """Calculate sum using multiple threads."""
    if arr.size == 0:
        return 0
    
    if arr.size < n_threads:
        # Array too small for threading
        return sum_array(arr)
    
    # Prepare shared result storage
    result_list = [0] * n_threads
    chunk_size = arr.size // n_threads
    threads = []
    
    # Create and start threads
    for i in range(n_threads):
        start_idx = i * chunk_size
        end_idx = arr.size if i == n_threads - 1 else (i + 1) * chunk_size
        
        thread = threading.Thread(
            target=_thread_worker_sum,
            args=(arr._data, start_idx, end_idx, result_list, i)
        )
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Combine results
    return sum(result_list)


def _thread_worker_minmax(data, start_idx, end_idx, result_list, thread_id, operation):
    """Worker function for parallel min/max calculation."""
    if operation == 'min':
        result = data[start_idx]
        for i in range(start_idx + 1, end_idx):
            if data[i] < result:
                result = data[i]
    else:  # max
        result = data[start_idx]
        for i in range(start_idx + 1, end_idx):
            if data[i] > result:
                result = data[i]
    
    result_list[thread_id] = result


def max_parallel(arr, n_threads=4):
    """Find maximum value using multiple threads."""
    if arr.size == 0:
        raise ValueError("Cannot find max of empty array")
    
    if arr.size < n_threads:
        return max_array(arr)
    
    result_list = [None] * n_threads
    chunk_size = arr.size // n_threads
    threads = []
    
    for i in range(n_threads):
        start_idx = i * chunk_size
        end_idx = arr.size if i == n_threads - 1 else (i + 1) * chunk_size
        
        thread = threading.Thread(
            target=_thread_worker_minmax,
            args=(arr._data, start_idx, end_idx, result_list, i, 'max')
        )
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # Find maximum among thread results
    return max(result_list)


def min_parallel(arr, n_threads=4):
    """Find minimum value using multiple threads."""
    if arr.size == 0:
        raise ValueError("Cannot find min of empty array")
    
    if arr.size < n_threads:
        return min_array(arr)
    
    result_list = [None] * n_threads
    chunk_size = arr.size // n_threads
    threads = []
    
    for i in range(n_threads):
        start_idx = i * chunk_size
        end_idx = arr.size if i == n_threads - 1 else (i + 1) * chunk_size
        
        thread = threading.Thread(
            target=_thread_worker_minmax,
            args=(arr._data, start_idx, end_idx, result_list, i, 'min')
        )
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    return min(result_list)


def mean_parallel(arr, n_threads=4):
    """Calculate mean using parallel sum."""
    if arr.size == 0:
        raise ValueError("Cannot calculate mean of empty array")
    
    return sum_parallel(arr, n_threads) / arr.size


def _thread_worker_variance(data, array_mean, start_idx, end_idx, result_list, thread_id):
    """Worker function for parallel variance calculation."""
    partial_sum = 0
    for i in range(start_idx, end_idx):
        partial_sum += (data[i] - array_mean) ** 2
    result_list[thread_id] = partial_sum


def std_parallel(arr, n_threads=4, ddof=0):
    """Calculate standard deviation using multiple threads."""
    if arr.size == 0:
        raise ValueError("Cannot calculate std of empty array")
    if arr.size == 1:
        return 0.0
    
    # First calculate mean (can be done in parallel too)
    array_mean = mean_parallel(arr, n_threads)
    
    if arr.size < n_threads:
        # Fall back to sequential for small arrays
        return std(arr, ddof)
    
    # Parallel variance calculation
    result_list = [0] * n_threads
    chunk_size = arr.size // n_threads
    threads = []
    
    for i in range(n_threads):
        start_idx = i * chunk_size
        end_idx = arr.size if i == n_threads - 1 else (i + 1) * chunk_size
        
        thread = threading.Thread(
            target=_thread_worker_variance,
            args=(arr._data, array_mean, start_idx, end_idx, result_list, i)
        )
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # Combine results and calculate standard deviation
    variance_sum = sum(result_list)
    variance = variance_sum / (arr.size - ddof)
    return math.sqrt(variance)


# Multiprocessing implementations
def _process_worker_sum(data, start_idx, end_idx, result_queue):
    """Process worker for sum calculation."""
    partial_sum = 0
    for i in range(start_idx, end_idx):
        partial_sum += data[i]
    result_queue.put(partial_sum)


def sum_multiprocess(arr, n_processes=2):
    """Calculate sum using multiple processes."""
    if arr.size == 0:
        return 0
    
    if arr.size < n_processes * 100:  # Minimum chunk size for efficiency
        return sum_array(arr)
    
    chunk_size = arr.size // n_processes
    processes = []
    result_queue = mp.Queue()
    
    for i in range(n_processes):
        start_idx = i * chunk_size
        end_idx = arr.size if i == n_processes - 1 else (i + 1) * chunk_size
        
        process = mp.Process(
            target=_process_worker_sum,
            args=(arr._data, start_idx, end_idx, result_queue)
        )
        processes.append(process)
        process.start()
    
    # Collect results
    partial_sums = []
    for _ in range(n_processes):
        partial_sums.append(result_queue.get())
    
    # Wait for all processes to complete
    for process in processes:
        process.join()
    
    return sum(partial_sums)


def mean_multiprocess(arr, n_processes=2):
    """Calculate mean using multiple processes."""
    if arr.size == 0:
        raise ValueError("Cannot calculate mean of empty array")
    
    return sum_multiprocess(arr, n_processes) / arr.size


# Utility functions for statistical analysis
def describe(arr):
    """Generate descriptive statistics for the array."""
    if arr.size == 0:
        return "Empty array - no statistics available"
    
    stats = {
        'count': arr.size,
        'mean': mean(arr),
        'std': std(arr),
        'min': min_array(arr),
        'max': max_array(arr),
        'median': median(arr)
    }
    
    return stats


def percentile(arr, p):
    """Calculate the p-th percentile of array elements."""
    if arr.size == 0:
        raise ValueError("Cannot calculate percentile of empty array")
    
    if not (0 <= p <= 100):
        raise ValueError("Percentile must be between 0 and 100")
    
    sorted_data = sorted(arr._data)
    if p == 0:
        return sorted_data[0]
    if p == 100:
        return sorted_data[-1]
    
    # Linear interpolation method
    index = (p / 100) * (len(sorted_data) - 1)
    lower_index = int(index)
    upper_index = min(lower_index + 1, len(sorted_data) - 1)
    
    if lower_index == upper_index:
        return sorted_data[lower_index]
    
    # Interpolate
    weight = index - lower_index
    return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight


# # Example usage and testing
# if __name__ == "__main__":
#     # Import required modules
#     import sys
#     import os
#     sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#     from core.array import MiniArray, arange
#     import time
    
#     print("=== Testing Sequential Statistical Operations ===")
    
#     # Create test array
#     test_arr = MiniArray([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
#     print(f"Test array: {test_arr}")
    
#     # Test basic statistics
#     print(f"Sum: {sum_array(test_arr)}")
#     print(f"Mean: {mean(test_arr)}")
#     print(f"Min: {min_array(test_arr)}")
#     print(f"Max: {max_array(test_arr)}")
#     print(f"Std: {std(test_arr):.4f}")
#     print(f"Variance: {var(test_arr):.4f}")
#     print(f"Median: {median(test_arr)}")
    
#     # Test percentiles
#     print(f"25th percentile: {percentile(test_arr, 25)}")
#     print(f"75th percentile: {percentile(test_arr, 75)}")
    
#     # Test describe function
#     print("\nDescriptive Statistics:")
#     stats = describe(test_arr)
#     for key, value in stats.items():
#         if isinstance(value, float):
#             print(f"{key}: {value:.4f}")
#         else:
#             print(f"{key}: {value}")
    
#     print("\n=== Testing Parallel Operations ===")
    
#     # Create larger array for performance testing
#     large_arr = arange(0, 10000)
#     print(f"Testing with array of {large_arr.size} elements")
    
#     # Test parallel sum
#     print("\nTesting Parallel Sum:")
    
#     # Sequential
#     start_time = time.time()
#     seq_sum = sum_array(large_arr)
#     seq_time = time.time() - start_time
    
#     # Parallel (threading)
#     start_time = time.time()
#     par_sum = sum_parallel(large_arr, n_threads=4)
#     par_time = time.time() - start_time
    
#     print(f"Sequential sum: {seq_sum} (time: {seq_time:.6f}s)")
#     print(f"Parallel sum: {par_sum} (time: {par_time:.6f}s)")
#     print(f"Results match: {seq_sum == par_sum}")
#     if par_time > 0:
#         print(f"Speedup: {seq_time/par_time:.2f}x")
    
#     # Test parallel min/max
#     print("\nTesting Parallel Min/Max:")
    
#     start_time = time.time()
#     seq_max = max_array(large_arr)
#     seq_time = time.time() - start_time
    
#     start_time = time.time()
#     par_max = max_parallel(large_arr, n_threads=4)
#     par_time = time.time() - start_time
    
#     print(f"Sequential max: {seq_max} (time: {seq_time:.6f}s)")
#     print(f"Parallel max: {par_max} (time: {par_time:.6f}s)")
#     print(f"Results match: {seq_max == par_max}")
    
#     # Test parallel standard deviation
#     print("\nTesting Parallel Standard Deviation:")
    
#     start_time = time.time()
#     seq_std = std(large_arr)
#     seq_time = time.time() - start_time
    
#     start_time = time.time()
#     par_std = std_parallel(large_arr, n_threads=4)
#     par_time = time.time() - start_time
    
#     print(f"Sequential std: {seq_std:.6f} (time: {seq_time:.6f}s)")
#     print(f"Parallel std: {par_std:.6f} (time: {par_time:.6f}s)")
#     print(f"Results close: {abs(seq_std - par_std) < 1e-10}")
    
#     # Test multiprocessing (if available)
#     try:
#         print("\n=== Testing Multiprocessing ===")
        
#         start_time = time.time()
#         mp_sum = sum_multiprocess(large_arr, n_processes=2)
#         mp_time = time.time() - start_time
        
#         print(f"Multiprocess sum: {mp_sum} (time: {mp_time:.6f}s)")
#         print(f"Results match: {seq_sum == mp_sum}")
        
#     except Exception as e:
#         print(f"Multiprocessing test failed: {e}")
#         print("This might be due to environment limitations")