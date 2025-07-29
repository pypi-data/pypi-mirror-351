# Generate the first 100 Fibonacci numbers
fibonacci_numbers = [0, 1]

while len(fibonacci_numbers) < 100:
    next_fib = fibonacci_numbers[-1] + fibonacci_numbers[-2]
    fibonacci_numbers.append(next_fib)

# Print the first 100 Fibonacci numbers
for num in fibonacci_numbers:
    print(num)