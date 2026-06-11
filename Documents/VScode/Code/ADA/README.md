# DAA Lab Programs

This repository contains implementations of fundamental Design and Analysis of Algorithms (DAA) programs for educational purposes.

## Programs Included

### Sorting Algorithms
1. **Program1_SelectionSort.c** - Selection Sort
   - Time Complexity: O(n²)
   - Space Complexity: O(1)
   - Selects the minimum element and places it at the beginning

2. **Program3_MergeSort.c** - Merge Sort
   - Time Complexity: O(n log n)
   - Space Complexity: O(n)
   - Divide and conquer sorting algorithm

3. **Program4_QuickSort.c** - Quick Sort
   - Average Time Complexity: O(n log n)
   - Worst Case: O(n²)
   - Space Complexity: O(log n)
   - Efficient in-place sorting using pivot partitioning

### Searching Algorithms

5. **Program5_BinarySearch.c** - Binary Search
   - Time Complexity: O(log n)
   - Space Complexity: O(1)
   - Efficient search on sorted arrays

### Dynamic Programming
6. **Program6_Knapsack.c** - 0/1 Knapsack Problem
   - Time Complexity: O(n*W)
   - Space Complexity: O(n*W)
   - Solves optimization problems using dynamic programming

### Graph Algorithms

7. **Program7_Prims.c** - Prim's Algorithm (Minimum Spanning Tree)
   - Time Complexity: O(n²)
   - Greedy algorithm for finding MST

8. **Program8_Kruskals.c** - Kruskal's Algorithm (Minimum Spanning Tree)
   - Time Complexity: O(E log E)
   - Uses Union-Find data structure

9. **Program9_Dijkstra.c** - Dijkstra's Algorithm (Shortest Path)
   - Time Complexity: O(n²)
   - Finds shortest paths from a source vertex

10. **Program10_FloydWarshall.c** - Floyd-Warshall Algorithm (All-Pairs Shortest Path)
    - Time Complexity: O(n³)
    - Finds shortest paths between all pairs of vertices

### Backtracking Algorithms

11. **Program11_NQueens.c** - N-Queens Problem
    - Solves the classic N-Queens problem
    - Uses backtracking to find valid placements

### Miscellaneous

12. **Program12_TSP.c** - Traveling Salesman Problem
    - Optimization problem using dynamic programming
    - Finds shortest route visiting all cities

## How to Compile and Run

### Compile a single program:
```bash
gcc -o Program1_SelectionSort Program1_SelectionSort.c
```

### Run the program:
```bash
./Program1_SelectionSort
```

## Requirements

- GCC compiler or any C compiler
- Basic understanding of algorithms
- Linux/Unix environment or WSL on Windows

## Author
Lab Programs for Design and Analysis of Algorithms

## License
Educational Use Only

---

**Note:** Each program is self-contained and can be compiled and executed independently. Follow the on-screen prompts for input.
