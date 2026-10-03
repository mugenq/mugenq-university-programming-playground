import sys

if __name__ == "__main__":

    P, T = map(int, input().split())
    opinion_lines = [line.strip() for line in sys.stdin if line.strip()]


    opinion_tables = [[0 for _ in range(T)] for _ in range(P)]
    opinion_dict = {}

    for line in opinion_lines:
        i, j = map(int, line.split())
        opinion_tables[i-1][j-1] = 1

    for person in opinion_tables:
        key = sum(person[k]*(2**i) for k in range(T-1))
        opinion_dict[key] = opinion_dict.get(key, 0) + 1

    print(len(opinion_dict))

"""python-seminar/test.py"""

"""
3 4
1 2
3 3
1 3
2 2
3 2
2 4
"""
