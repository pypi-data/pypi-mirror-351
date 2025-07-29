def fibonacci(n):
    sequence = [0, 1]
    while len(sequence) < n:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence

# Calculate the first 100 Fibonacci numbers
fib_numbers = fibonacci(100)
print(fib_numbers)