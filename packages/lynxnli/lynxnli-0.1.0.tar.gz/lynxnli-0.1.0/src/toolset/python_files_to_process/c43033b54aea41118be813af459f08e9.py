def fibonacci_sequence(n):
    fib_sequence = [0, 1]
    for i in range(2, n):
        next_fib = fib_sequence[-1] + fib_sequence[-2]
        fib_sequence.append(next_fib)
    return fib_sequence

# Calculate the first 100 Fibonacci numbers
first_100_fib = fibonacci_sequence(100)
print(first_100_fib)