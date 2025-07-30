# operations/arithmetic.py

import threading
import multiprocessing as mp
from multiprocessing import shared_memory
import math


def _check_compatible_shapes(a, b):
    """Check if two arrays can be used in element-wise operations."""
    if a.shape != b.shape:
        # Basic broadcasting: allow if one is scalar (size 1)
        if a.size == 1 or b.size == 1:
            return True
        else:
            raise ValueError(f"Shape mismatch: {a.shape} vs {b.shape}")
    return True


def _broadcast_arrays(a, b):
    """Handle basic broadcasting for scalar operations."""
    if a.size == 1 and b.size > 1:
        # Broadcast a to match b's size
        broadcasted_data = [a._data[0]] * b.size
        from core.array import MiniArray
        a_broadcast = MiniArray(broadcasted_data, shape=b.shape, dtype=a.dtype)
        return a_broadcast, b
    elif b.size == 1 and a.size > 1:
        # Broadcast b to match a's size
        broadcasted_data = [b._data[0]] * a.size
        from core.array import MiniArray
        b_broadcast = MiniArray(broadcasted_data, shape=a.shape, dtype=b.dtype)
        return a, b_broadcast
    else:
        return a, b


# Sequential arithmetic operations
def add(a, b):
    """Element-wise addition of two arrays."""
    from core.array import MiniArray
    
    _check_compatible_shapes(a, b)
    a_broadcast, b_broadcast = _broadcast_arrays(a, b)
    
    result_data = []
    for i in range(len(a_broadcast._data)):
        result_data.append(a_broadcast._data[i] + b_broadcast._data[i])
    
    # Determine output dtype (promote to higher precision if needed)
    output_dtype = _promote_dtype(a.dtype, b.dtype)
    
    return MiniArray(result_data, shape=a_broadcast.shape, dtype=output_dtype)


def subtract(a, b):
    """Element-wise subtraction of two arrays."""
    from core.array import MiniArray
    
    _check_compatible_shapes(a, b)
    a_broadcast, b_broadcast = _broadcast_arrays(a, b)
    
    result_data = []
    for i in range(len(a_broadcast._data)):
        result_data.append(a_broadcast._data[i] - b_broadcast._data[i])
    
    output_dtype = _promote_dtype(a.dtype, b.dtype)
    return MiniArray(result_data, shape=a_broadcast.shape, dtype=output_dtype)


def multiply(a, b):
    """Element-wise multiplication of two arrays."""
    from core.array import MiniArray
    
    _check_compatible_shapes(a, b)
    a_broadcast, b_broadcast = _broadcast_arrays(a, b)
    
    result_data = []
    for i in range(len(a_broadcast._data)):
        result_data.append(a_broadcast._data[i] * b_broadcast._data[i])
    
    output_dtype = _promote_dtype(a.dtype, b.dtype)
    return MiniArray(result_data, shape=a_broadcast.shape, dtype=output_dtype)


def divide(a, b):
    """Element-wise division of two arrays."""
    from core.array import MiniArray
    
    _check_compatible_shapes(a, b)
    a_broadcast, b_broadcast = _broadcast_arrays(a, b)
    
    result_data = []
    for i in range(len(a_broadcast._data)):
        if b_broadcast._data[i] == 0:
            raise ZeroDivisionError("Division by zero encountered")
        result_data.append(a_broadcast._data[i] / b_broadcast._data[i])
    
    # Division always promotes to float
    return MiniArray(result_data, shape=a_broadcast.shape, dtype='float64')


def power(a, b):
    """Element-wise power operation."""
    from core.array import MiniArray
    
    _check_compatible_shapes(a, b)
    a_broadcast, b_broadcast = _broadcast_arrays(a, b)
    
    result_data = []
    for i in range(len(a_broadcast._data)):
        result_data.append(a_broadcast._data[i] ** b_broadcast._data[i])
    
    output_dtype = _promote_dtype(a.dtype, b.dtype)
    return MiniArray(result_data, shape=a_broadcast.shape, dtype=output_dtype)


def _promote_dtype(dtype1, dtype2):
    """Determine the appropriate output dtype for operations."""
    type_hierarchy = ['bool', 'int32', 'int64', 'float32', 'float64']
    
    try:
        idx1 = type_hierarchy.index(dtype1)
        idx2 = type_hierarchy.index(dtype2)
        return type_hierarchy[max(idx1, idx2)]
    except ValueError:
        return 'float64'  # Default fallback


# Parallel arithmetic operations using threading
def _thread_worker_arithmetic(func, a_data, b_data, start_idx, end_idx, result_data):
    """Worker function for threaded arithmetic operations."""
    for i in range(start_idx, end_idx):
        result_data[i] = func(a_data[i], b_data[i])


def add_parallel(a, b, n_threads=4):
    """Parallel element-wise addition using threading."""
    from core.array import MiniArray
    
    _check_compatible_shapes(a, b)
    a_broadcast, b_broadcast = _broadcast_arrays(a, b)
    
    # Prepare result array
    result_data = [0] * len(a_broadcast._data)
    
    # Calculate chunk size for each thread
    chunk_size = len(a_broadcast._data) // n_threads
    threads = []
    
    # Create and start threads
    for i in range(n_threads):
        start_idx = i * chunk_size
        end_idx = len(a_broadcast._data) if i == n_threads - 1 else (i + 1) * chunk_size
        
        thread = threading.Thread(
            target=_thread_worker_arithmetic,
            args=(lambda x, y: x + y, a_broadcast._data, b_broadcast._data, 
                  start_idx, end_idx, result_data)
        )
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    output_dtype = _promote_dtype(a.dtype, b.dtype)
    return MiniArray(result_data, shape=a_broadcast.shape, dtype=output_dtype)


def multiply_parallel(a, b, n_threads=4):
    """Parallel element-wise multiplication using threading."""
    from core.array import MiniArray
    
    _check_compatible_shapes(a, b)
    a_broadcast, b_broadcast = _broadcast_arrays(a, b)
    
    result_data = [0] * len(a_broadcast._data)
    chunk_size = len(a_broadcast._data) // n_threads
    threads = []
    
    for i in range(n_threads):
        start_idx = i * chunk_size
        end_idx = len(a_broadcast._data) if i == n_threads - 1 else (i + 1) * chunk_size
        
        thread = threading.Thread(
            target=_thread_worker_arithmetic,
            args=(lambda x, y: x * y, a_broadcast._data, b_broadcast._data, 
                  start_idx, end_idx, result_data)
        )
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    output_dtype = _promote_dtype(a.dtype, b.dtype)
    return MiniArray(result_data, shape=a_broadcast.shape, dtype=output_dtype)


# Parallel operations using multiprocessing
def _process_worker_arithmetic(func_name, a_data, b_data, start_idx, end_idx, result_queue):
    """Worker function for multiprocessing arithmetic operations."""
    result_chunk = []
    
    for i in range(start_idx, end_idx):
        if func_name == 'add':
            result_chunk.append(a_data[i] + b_data[i])
        elif func_name == 'multiply':
            result_chunk.append(a_data[i] * b_data[i])
        elif func_name == 'subtract':
            result_chunk.append(a_data[i] - b_data[i])
        elif func_name == 'divide':
            if b_data[i] == 0:
                result_chunk.append(float('inf'))  # Handle division by zero
            else:
                result_chunk.append(a_data[i] / b_data[i])
    
    result_queue.put((start_idx, result_chunk))


def add_multiprocess(a, b, n_processes=2):
    """Parallel element-wise addition using multiprocessing."""
    from core.array import MiniArray
    
    _check_compatible_shapes(a, b)
    a_broadcast, b_broadcast = _broadcast_arrays(a, b)
    
    # Create result array
    result_data = [0] * len(a_broadcast._data)
    
    # Setup multiprocessing
    chunk_size = len(a_broadcast._data) // n_processes
    processes = []
    result_queue = mp.Queue()
    
    # Create and start processes
    for i in range(n_processes):
        start_idx = i * chunk_size
        end_idx = len(a_broadcast._data) if i == n_processes - 1 else (i + 1) * chunk_size
        
        process = mp.Process(
            target=_process_worker_arithmetic,
            args=('add', a_broadcast._data, b_broadcast._data, 
                  start_idx, end_idx, result_queue)
        )
        processes.append(process)
        process.start()
    
    # Collect results
    for _ in range(n_processes):
        start_idx, result_chunk = result_queue.get()
        for j, value in enumerate(result_chunk):
            result_data[start_idx + j] = value
    
    # Wait for all processes to complete
    for process in processes:
        process.join()
    
    output_dtype = _promote_dtype(a.dtype, b.dtype)
    return MiniArray(result_data, shape=a_broadcast.shape, dtype=output_dtype)


def multiply_multiprocess(a, b, n_processes=2):
    """Parallel element-wise multiplication using multiprocessing."""
    from core.array import MiniArray
    
    _check_compatible_shapes(a, b)
    a_broadcast, b_broadcast = _broadcast_arrays(a, b)
    
    result_data = [0] * len(a_broadcast._data)
    chunk_size = len(a_broadcast._data) // n_processes
    processes = []
    result_queue = mp.Queue()
    
    for i in range(n_processes):
        start_idx = i * chunk_size
        end_idx = len(a_broadcast._data) if i == n_processes - 1 else (i + 1) * chunk_size
        
        process = mp.Process(
            target=_process_worker_arithmetic,
            args=('multiply', a_broadcast._data, b_broadcast._data, 
                  start_idx, end_idx, result_queue)
        )
        processes.append(process)
        process.start()
    
    for _ in range(n_processes):
        start_idx, result_chunk = result_queue.get()
        for j, value in enumerate(result_chunk):
            result_data[start_idx + j] = value
    
    for process in processes:
        process.join()
    
    output_dtype = _promote_dtype(a.dtype, b.dtype)
    return MiniArray(result_data, shape=a_broadcast.shape, dtype=output_dtype)


# # Example usage and testing
# if __name__ == "__main__":
#     # Import the array class
#     import sys
#     import os
#     sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#     from core.array import MiniArray, ones, zeros, arange
    
#     print("=== Testing Sequential Arithmetic ===")
    
#     # Create test arrays
#     a = MiniArray([1, 2, 3, 4, 5])
#     b = MiniArray([10, 20, 30, 40, 50])
    
#     print(f"a = {a}")
#     print(f"b = {b}")
    
#     # Test sequential operations
#     print(f"add(a, b) = {add(a, b)}")
#     print(f"subtract(a, b) = {subtract(a, b)}")
#     print(f"multiply(a, b) = {multiply(a, b)}")
#     print(f"divide(a, b) = {divide(a, b)}")
    
#     # Test broadcasting
#     print("\n=== Testing Broadcasting ===")
#     scalar = MiniArray([5])
#     print(f"a = {a}")
#     print(f"scalar = {scalar}")
#     print(f"add(a, scalar) = {add(a, scalar)}")
#     print(f"multiply(a, scalar) = {multiply(a, scalar)}")
    
#     # Test parallel operations
#     print("\n=== Testing Parallel Operations ===")
    
#     # Create larger arrays for better parallel demonstration
#     large_a = arange(0, 1000)
#     large_b = arange(1000, 2000)
    
#     print("Testing with large arrays (1000 elements each)")
    
#     # Time comparison
#     import time
    
#     # Sequential timing
#     start_time = time.time()
#     result_seq = add(large_a, large_b)
#     seq_time = time.time() - start_time
    
#     # Parallel timing (threading)
#     start_time = time.time()
#     result_par = add_parallel(large_a, large_b, n_threads=4)
#     par_time = time.time() - start_time
    
#     print(f"Sequential time: {seq_time:.6f} seconds")
#     print(f"Parallel time: {par_time:.6f} seconds")
#     print(f"Speedup: {seq_time/par_time:.2f}x")
    
#     # Verify results are the same
#     same_results = all(result_seq._data[i] == result_par._data[i] 
#                       for i in range(len(result_seq._data)))
#     print(f"Results match: {same_results}")
    
#     # Test multiprocessing (if not on Windows or in interactive mode)
#     try:
#         print("\n=== Testing Multiprocessing ===")
#         start_time = time.time()
#         result_mp = add_multiprocess(large_a, large_b, n_processes=2)
#         mp_time = time.time() - start_time
        
#         print(f"Multiprocessing time: {mp_time:.6f} seconds")
        
#         same_mp_results = all(result_seq._data[i] == result_mp._data[i] 
#                              for i in range(len(result_seq._data)))
#         print(f"Multiprocessing results match: {same_mp_results}")
        
#     except Exception as e:
#         print(f"Multiprocessing test failed: {e}")
#         print("This might be due to environment limitations")