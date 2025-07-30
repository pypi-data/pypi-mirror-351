def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

prime_numbers = []
number = 2
while len(prime_numbers) < 20:
    if is_prime(number):
        prime_numbers.append(number)
    number += 1

with open('prime_numbers.txt', 'w') as file:
    for prime in prime_numbers:
        file.write(f'{prime}\n')