

import os

def rec_nonrec():
    _read_file('recursiveNonrecursive.txt')

def divideAndConquer():
    _read_file('divideAndConquer.txt')

def Greedy():
    _read_file('Greedy.txt')

def DP():
    _read_file('DP.txt')

def Backtracking():
    _read_file('Backtracking.txt')

def stringMatching():
    _read_file('stringMatching.txt')

def all():
    _read_file('all.txt')

def _read_file(filename):
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            print(text)  # Works in both Jupyter and terminal
    except FileNotFoundError:
        print(f"{filename} not found.")
    except UnicodeEncodeError as e:
        print("UnicodeEncodeError:", e)


