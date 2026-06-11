# DAA Lab Programs

This repository contains implementations of Design and Analysis of Algorithms (DAA) lab programs based on the official lab manual.

## Programs Structure

### Program 1: Kruskal's Algorithm (Minimum Spanning Tree)
- **File:** `Program1_Kruskals.c`
- **Algorithm:** Greedy approach using Union-Find
- **Time Complexity:** O(E log E)
- **Space Complexity:** O(V + E)

### Program 2: Prim's Algorithm (Minimum Spanning Tree)
- **File:** `Program2_Prims.c`
- **Algorithm:** Greedy approach selecting vertices
- **Time Complexity:** O(V²)
- **Space Complexity:** O(V²)

### Program 3(a): Floyd's Algorithm (All-Pairs Shortest Path)
- **File:** `Program3a_Floyd.c`
- **Algorithm:** Dynamic Programming approach
- **Time Complexity:** O(V³)
- **Space Complexity:** O(V²)

### Program 3(b): Warshall's Algorithm (Transitive Closure)
- **File:** `Program3b_Warshall.c`
- **Algorithm:** Computes transitive closure of a graph
- **Time Complexity:** O(V³)
- **Space Complexity:** O(V²)

### Program 4: Dijkstra's Algorithm (Single Source Shortest Path)
- **File:** `Program4_Dijkstra.c`
- **Algorithm:** Greedy approach for non-negative weights
- **Time Complexity:** O(V²)
- **Space Complexity:** O(V²)

### Program 5: Topological Sorting
- **File:** `Program5_TopologicalSort.c`
- **Algorithm:** Kahn's algorithm using indegree
- **Time Complexity:** O(V + E)
- **Space Complexity:** O(V)

### Program 6: 0/1 Knapsack Problem (Dynamic Programming)
- **File:** `Program6_Knapsack_01.c`
- **Algorithm:** Dynamic Programming
- **Time Complexity:** O(n × W)
- **Space Complexity:** O(n × W)

### Program 7: Greedy Knapsack (Fractional/Continuous Knapsack)
- **File:** `Program7_Knapsack_Greedy.c`
- **Algorithm:** Greedy approach based on profit/weight ratio
- **Time Complexity:** O(n log n)
- **Space Complexity:** O(n)

### Program 8: Sum of Subsets (Backtracking)
- **File:** `Program8_SumOfSubsets.c`
- **Algorithm:** Backtracking to find subsets with given sum
- **Time Complexity:** O(2^n)
- **Space Complexity:** O(n)

### Program 9: Selection Sort
- **File:** `Program9_SelectionSort.c`
- **Algorithm:** Selection-based sorting
- **Time Complexity:** O(n²)
- **Space Complexity:** O(1)

### Program 10: Quick Sort
- **File:** `Program10_QuickSort.c`
- **Algorithm:** Divide and conquer with partitioning
- **Average Time Complexity:** O(n log n)
- **Worst Case:** O(n²)
- **Space Complexity:** O(log n)

### Program 11: Merge Sort
- **File:** `Program11_MergeSort.c`
- **Algorithm:** Divide and conquer with merging
- **Time Complexity:** O(n log n)
- **Space Complexity:** O(n)

### Program 12: N-Queens Problem (Backtracking)
- **File:** `Program12_NQueens.c`
- **Algorithm:** Backtracking to place N queens
- **Time Complexity:** O(N!)
- **Space Complexity:** O(N)

## Compilation and Execution

### Compile a program:
```bash
gcc -o Program1_Kruskals Program1_Kruskals.c
```

### Run the program:
```bash
./Program1_Kruskals
```

### Compile all programs:
```bash
gcc -o Program1_Kruskals Program1_Kruskals.c
gcc -o Program2_Prims Program2_Prims.c
gcc -o Program3a_Floyd Program3a_Floyd.c
gcc -o Program3b_Warshall Program3b_Warshall.c
gcc -o Program4_Dijkstra Program4_Dijkstra.c
gcc -o Program5_TopologicalSort Program5_TopologicalSort.c
gcc -o Program6_Knapsack_01 Program6_Knapsack_01.c
gcc -o Program7_Knapsack_Greedy Program7_Knapsack_Greedy.c
gcc -o Program8_SumOfSubsets Program8_SumOfSubsets.c
gcc -o Program9_SelectionSort Program9_SelectionSort.c
gcc -o Program10_QuickSort Program10_QuickSort.c
gcc -o Program11_MergeSort Program11_MergeSort.c
gcc -o Program12_NQueens Program12_NQueens.c
```

## Requirements

- GCC compiler or compatible C compiler
- Linux/Unix environment or Windows with WSL
- Basic understanding of Data Structures and Algorithms

## Algorithm Categories

### Graph Algorithms (Programs 1-5)
- Minimum Spanning Tree: Kruskal's and Prim's
- Shortest Path: Floyd's and Dijkstra's
- Graph Properties: Warshall's (Transitive Closure)
- Graph Traversal: Topological Sort

### Dynamic Programming & Optimization (Programs 6-8)
- Knapsack Problem (0/1 and Greedy variants)
- Subset Problems

### Sorting Algorithms (Programs 9-11)
- Elementary Sort: Selection Sort
- Advanced Sorts: Quick Sort, Merge Sort

### Backtracking (Programs 12, and 8)
- N-Queens Problem
- Sum of Subsets

## Lab Manual Reference

These programs follow the official DAA lab manual structure with 12 main programs covering:
- Graph Algorithms
- Dynamic Programming
- Backtracking
- Sorting Algorithms

## Author
DAA Lab - Design and Analysis of Algorithms

## License
Educational Use Only

---

**Note:** Each program is self-contained and can be compiled independently. Follow the on-screen prompts for input when running each program.
