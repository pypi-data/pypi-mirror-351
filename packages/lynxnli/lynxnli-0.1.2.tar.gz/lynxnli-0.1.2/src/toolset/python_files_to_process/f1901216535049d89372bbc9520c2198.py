def is_prime(num):
    if num <= 1:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

def first_n_primes(n):
    primes = []
    candidate = 2
    while len(primes) < n:
        if is_prime(candidate):
            primes.append(candidate)
        candidate += 1
    return primes

if __name__ == '__main__':
    primes = first_n_primes(100)
    with open('primes.txt', 'w') as f:
        for prime in primes:
            f.write(f'{prime}\n')