def fibonacci(n):
    fib_sequence = []
    a, b = 0, 1
    for _ in range(n):
        fib_sequence.append(a)
        a, b = b, a + b
    return fib_sequence

# Calculate and print the first 100 Fibonacci numbers
fib_numbers = fibonacci(100)
print(fib_numbers)