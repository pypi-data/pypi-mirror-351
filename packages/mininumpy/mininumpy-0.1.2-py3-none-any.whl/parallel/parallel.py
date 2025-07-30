# parallel/parallel.py
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import math
from typing import List, Callable, Any

class ParallelCompute:
    """Utilities for parallel computing with threading and multiprocessing"""
    
    @staticmethod
    def split_array_threads(array, n_threads):
        """Split array data into chunks for threading"""
        if n_threads <= 0:
            n_threads = 1
        
        data_size = len(array.data)
        chunk_size = max(1, data_size // n_threads)
        chunks = []
        
        for i in range(0, data_size, chunk_size):
            end_idx = min(i + chunk_size, data_size)
            chunks.append((i, end_idx, array.data[i:end_idx]))
        
        return chunks
    
    @staticmethod
    def split_array_processes(array, n_processes):
        """Split array data into chunks for multiprocessing"""
        if n_processes <= 0:
            n_processes = 1
            
        data_size = len(array.data)
        chunk_size = max(1, data_size // n_processes)
        chunks = []
        
        for i in range(0, data_size, chunk_size):
            end_idx = min(i + chunk_size, data_size)
            chunks.append(array.data[i:end_idx])
        
        return chunks
    
    @staticmethod
    def thread_worker_binary(func, chunk1, chunk2):
        """Worker function for binary operations with threading"""
        return [func(a, b) for a, b in zip(chunk1, chunk2)]
    
    @staticmethod
    def thread_worker_unary(func, chunk):
        """Worker function for unary operations with threading"""
        return func(chunk)
    
    @staticmethod
    def process_worker_binary(args):
        """Worker function for binary operations with multiprocessing"""
        func, chunk1, chunk2 = args
        return [func(a, b) for a, b in zip(chunk1, chunk2)]
    
    @staticmethod
    def process_worker_unary(args):
        """Worker function for unary operations with multiprocessing"""
        func, chunk = args
        return func(chunk)

def parallel_binary_op_threads(array1, array2, operation, n_threads=4):
    """Execute binary operation in parallel using threads"""
    from ..core.array import MiniArray
    
    if array1.shape != array2.shape:
        raise ValueError("Arrays must have the same shape")
    
    n_threads = min(n_threads, len(array1.data))
    if n_threads <= 1:
        # Fall back to sequential
        result_data = [operation(a, b) for a, b in zip(array1.data, array2.data)]
        return MiniArray(result_data, array1.shape, array1.dtype)
    
    # Split arrays into chunks
    chunk_size = max(1, len(array1.data) // n_threads)
    chunks1 = [array1.data[i:i+chunk_size] for i in range(0, len(array1.data), chunk_size)]
    chunks2 = [array2.data[i:i+chunk_size] for i in range(0, len(array2.data), chunk_size)]
    
    # Process chunks in parallel
    with ThreadPoolExecutor(max_workers=n_threads) as executor:
        futures = []
        for chunk1, chunk2 in zip(chunks1, chunks2):
            future = executor.submit(ParallelCompute.thread_worker_binary, operation, chunk1, chunk2)
            futures.append(future)
        
        # Collect results
        result_data = []
        for future in futures:
            result_data.extend(future.result())
    
    return MiniArray(result_data, array1.shape, array1.dtype)

def parallel_binary_op_processes(array1, array2, operation, n_processes=2):
    """Execute binary operation in parallel using processes"""
    from ..core.array import MiniArray
    
    if array1.shape != array2.shape:
        raise ValueError("Arrays must have the same shape")
    
    n_processes = min(n_processes, len(array1.data))
    if n_processes <= 1:
        # Fall back to sequential
        result_data = [operation(a, b) for a, b in zip(array1.data, array2.data)]
        return MiniArray(result_data, array1.shape, array1.dtype)
    
    # Split arrays into chunks
    chunk_size = max(1, len(array1.data) // n_processes)
    chunks1 = [array1.data[i:i+chunk_size] for i in range(0, len(array1.data), chunk_size)]
    chunks2 = [array2.data[i:i+chunk_size] for i in range(0, len(array2.data), chunk_size)]
    
    # Prepare arguments for processes
    args = [(operation, chunk1, chunk2) for chunk1, chunk2 in zip(chunks1, chunks2)]
    
    # Process chunks in parallel
    with ProcessPoolExecutor(max_workers=n_processes) as executor:
        results = list(executor.map(ParallelCompute.process_worker_binary, args))
    
    # Flatten results
    result_data = []
    for result in results:
        result_data.extend(result)
    
    return MiniArray(result_data, array1.shape, array1.dtype)

def parallel_reduction_threads(array, operation, n_threads=4):
    """Execute reduction operation in parallel using threads"""
    n_threads = min(n_threads, len(array.data))
    if n_threads <= 1:
        return operation(array.data)
    
    # Split array into chunks
    chunk_size = max(1, len(array.data) // n_threads)
    chunks = [array.data[i:i+chunk_size] for i in range(0, len(array.data), chunk_size)]
    
    # Process chunks in parallel
    with ThreadPoolExecutor(max_workers=n_threads) as executor:
        futures = [executor.submit(operation, chunk) for chunk in chunks]
        partial_results = [future.result() for future in futures]
    
    # Combine partial results
    if hasattr(operation, '__name__'):
        if 'sum' in operation.__name__:
            return sum(partial_results)
        elif 'max' in operation.__name__:
            return max(partial_results)
        elif 'min' in operation.__name__:
            return min(partial_results)
    
    # Default: assume it's summable
    return sum(partial_results)

def parallel_reduction_processes(array, operation, n_processes=2):
    """Execute reduction operation in parallel using processes"""
    n_processes = min(n_processes, len(array.data))
    if n_processes <= 1:
        return operation(array.data)
    
    # Split array into chunks  
    chunk_size = max(1, len(array.data) // n_processes)
    chunks = [array.data[i:i+chunk_size] for i in range(0, len(array.data), chunk_size)]
    
    # Prepare arguments for processes
    args = [(operation, chunk) for chunk in chunks]
    
    # Process chunks in parallel
    with ProcessPoolExecutor(max_workers=n_processes) as executor:
        partial_results = list(executor.map(ParallelCompute.process_worker_unary, args))
    
    # Combine partial results
    if hasattr(operation, '__name__'):
        if 'sum' in operation.__name__:
            return sum(partial_results)
        elif 'max' in operation.__name__:
            return max(partial_results)
        elif 'min' in operation.__name__:
            return min(partial_results)
    
    # Default: assume it's summable  
    return sum(partial_results)