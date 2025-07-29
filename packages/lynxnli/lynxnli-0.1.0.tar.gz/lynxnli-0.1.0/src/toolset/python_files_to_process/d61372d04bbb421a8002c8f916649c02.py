def fibonacci(n):
    sequence = [0, 1]
    for i in range(2, n):
        next_fib = sequence[-1] + sequence[-2]
        sequence.append(next_fib)
    return sequence

# Calculate the first 100 Fibonacci numbers
fibonacci_numbers = fibonacci(100)
print(fibonacci_numbers)