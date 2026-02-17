from controller.conrtoller import Rouge
from domain.generator import Generator

def main():

    # Generator()
    Rouge().run()
    

if __name__ == '__main__':
    main()



# from time import perf_counter
# n = 10000000
# t1 = perf_counter()
# for step in range(n):
#     s = set()
#     s.add(1)
#     # работа с s
# t1 = perf_counter() - t1
# t2 = perf_counter()
# s = set()
# for step in range(n):
#     s.add(1)
#     s.clear()
# t2 = perf_counter() - t2

# print(f'new set = {t1}, clear set = {t2}, t1 - t2={t1-t2}')

# from time import perf_counter
# n = 1000000
# t1 = perf_counter()
# for step in range(n):
#     s = set()
#     s.add(1)

# t1 = perf_counter() - t1
# t2 = perf_counter()

# for step in range(n):
#     s = list()
#     s.append(1)

# t2 = perf_counter() - t2

# print(f'set = {t1}, list = {t2}, t1 - t2={t1-t2}')