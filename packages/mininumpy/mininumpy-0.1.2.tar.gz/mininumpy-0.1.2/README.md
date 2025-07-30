# MiniNumPy - Simplified Parallel Computing Library

A lightweight numpy-like library focusing on core array operations with threading and multiprocessing support.

## Features

- **Core Array Class**: Basic numpy-like array with indexing, reshaping, and data manipulation
- **Arithmetic Operations**: Element-wise add, subtract, multiply, divide
- **Statistical Functions**: Sum, mean, max, min with parallel versions
- **Parallel Computing**: Threading and multiprocessing support for performance
- **Easy to Use**: Simple API similar to NumPy

## Installation

```bash
# Clone or download the project
cd mininumpy/
python demo.py  # Run the demo
```

## Quick Start

```python
import mininumpy as mnp

# Create arrays
a = mnp.zeros((1000, 1000))
b = mnp.ones((1000, 1000))

# Basic operations
c = mnp.add(a, b)
total = mnp.sum(c)

# Parallel operations
c_parallel = mnp.add_parallel(a, b, n_threads=4)
total_parallel = mnp.sum_parallel(c, n_threads=4)
```

## Project Structure

```
mininumpy/
├── core/
│   ├── __init__.py
│   └── array.py          # MiniArray class
├── operations/
│   ├── __init__.py
│   ├── arithmetic.py     # Basic math operations
│   └── stats.py          # Statistical functions
├── parallel/
│   ├── __init__.py
│   └── parallel.py       # Threading/multiprocessing
├── tests/
│   └── test_basic.py     # Unit tests
├── examples/
│   └── demo.py          # Demonstration script
└── README.md
```

## Running Tests

```bash
cd tests/
python test_basic.py
```

## Performance

The library shows performance improvements with parallel operations on large arrays:

- Threading: Best for I/O bound and shared memory operations
- Multiprocessing: Best for CPU-intensive computations

See `demo.py` for detailed benchmarking results.

## API Reference

### Array Creation
- `MiniArray(data, shape=None, dtype='float64')` - Create array from data
- `zeros(shape)` - Create array filled with zeros
- `ones(shape)` - Create array filled with ones  
- `arange(start, stop, step=1)` - Create array with range of values

### Arithmetic Operations
- `add(a, b)` - Element-wise addition
- `subtract(a, b)` - Element-wise subtraction
- `multiply(a, b)` - Element-wise multiplication
- `divide(a, b)` - Element-wise division
- `add_parallel(a, b, n_threads=4)` - Parallel addition
- `multiply_parallel(a, b, n_processes=2)` - Parallel multiplication

### Statistical Operations
- `sum(array)` - Sum all elements
- `mean(array)` - Calculate mean
- `max(array)` - Find maximum value
- `min(array)` - Find minimum value
- `sum_parallel(array, n_threads=4)` - Parallel sum
- `mean_parallel(array, n_threads=4)` - Parallel mean

## Example Usage

```python
# Import the library
import mininumpy as mnp

# Create and manipulate arrays
arr = mnp.MiniArray([1, 2, 3, 4, 5, 6], shape=(2, 3))
print(f"Array shape: {arr.shape}")
print(f"Element at [1,1]: {arr[1, 1]}")

# Reshape operations
reshaped = arr.reshape((3, 2))
flattened = arr.flatten()

# Mathematical operations
a = mnp.ones((1000,))
b = mnp.arange(0, 1000)
result = mnp.add(a, b)

# Statistical analysis
total = mnp.sum(result)
average = mnp.mean(result)

# Parallel computing for large datasets
large_a = mnp.zeros((100000,))
large_b = mnp.ones((100000,))

# Compare performance
import time

# Sequential
start = time.time()
seq_result = mnp.add(large_a, large_b)
seq_time = time.time() - start

# Parallel
start = time.time()
par_result = mnp.add_parallel(large_a, large_b, n_threads=4)
par_time = time.time() - start

print(f"Sequential: {seq_time:.4f}s")
print(f"Parallel: {par_time:.4f}s") 
print(f"Speedup: {seq_time/par_time:.2f}x")
```

## Implementation Notes

- Arrays are stored as flat Python lists with shape metadata
- Parallel operations split work across threads/processes
- Thread-based parallelism for shared memory operations
- Process-based parallelism for CPU-intensive tasks
- Error handling for shape mismatches and invalid operations

## Limitations

- No broadcasting (arrays must have same shape)
- Limited to basic operations (no advanced linear algebra)
- Python lists instead of optimized C arrays
- No GPU acceleration

## Future Extensions

- Matrix multiplication
- Advanced slicing operations
- Broadcasting support
- GPU acceleration with numba
- More statistical functions
- Linear algebra operations

## Contributing

This is an educational project. Feel free to extend with additional features:

1. Add new mathematical operations
2. Implement advanced indexing
3. Add more statistical functions
4. Optimize performance
5. Add GPU support

## License

Educational/demonstration purposes. Feel free to modify and extend.