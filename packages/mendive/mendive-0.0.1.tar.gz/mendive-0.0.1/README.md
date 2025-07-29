# Mendive: Claw-Free Solver

![Honoring the Memory of Rafael Maria de Mendive (a notable Cuban educator and poet)](docs/mendive.jpg)

This work builds upon [Claw Finding Algorithm Using Aegypti](https://dev.to/frank_vega_987689489099bf/claw-finding-algorithm-using-aegypti-2p0k).

---

# Claw-Free Graph Problem

The Claw-Free Graph Problem is a fundamental decision problem in graph theory. Given an undirected graph, the problem asks whether the graph is **claw-free** – meaning it contains no induced subgraph isomorphic to a _claw_ (the complete bipartite graph $K_{1,3}$). A claw consists of:

- A central vertex connected to three independent vertices (leaves)
- No edges between the leaves (forming a star with three rays)

This problem is important for various reasons:

- **Graph Analysis:** Serves as a foundation for complex graph algorithms with applications in network analysis, combinatorial optimization, and scheduling.
- **Computational Complexity:** A benchmark for efficient graph property verification. The brute-force approach checks all vertex quadruplets ($O(n^4)$), while optimized algorithms:
  - Achieve $O(n^{3})$ via neighbor independence checks
  - Reach subcubic time ($O(n^{ω})$) using matrix multiplication (where $ω < 2.373$)
- **Structural Implications:** Claw-free graphs exhibit special properties (e.g., perfect graph connections, polyhedral characterization).

Understanding this problem is essential for graph algorithm design and complexity theory.

## Problem Statement

Input: A Boolean Adjacency Matrix $M$.

Question: Does $M$ contain no claws?

Answer: True / False

### Example Instance: 5 x 5 matrix

|        | c1    | c2  | c3  | c4  | c5  |
| ------ | ----- | --- | --- | --- | --- |
| **r1** | 0     | 0   | 1   | 1   | 1   |
| **r2** | 0     | 0   | 0   | 0   | 0   |
| **r3** | **1** | 0   | 0   | 0   | 1   |
| **r4** | **1** | 0   | 0   | 0   | 0   |
| **r5** | **1** | 0   | 1   | 0   | 0   |

The input for undirected graph is typically provided in [DIMACS](http://dimacs.rutgers.edu/Challenges) format. In this way, the previous adjacency matrix is represented in a text file using the following string representation:

```
p edge 5 4
e 1 3
e 1 5
e 1 4
e 2 5
```

This represents a 5x5 matrix in DIMACS format such that each edge $(v,w)$ appears exactly once in the input file and is not repeated as $(w,v)$. In this format, every edge appears in the form of

```
e W V
```

where the fields W and V specify the endpoints of the edge while the lower-case character `e` signifies that this is an edge descriptor line.

_Example Solution:_

Claw Found `(1, 3, 4, 5)`: In Column `1` and Rows `3` & `4` & `5`

# Claw Detection Algorithm Overview

## Algorithm Description

This algorithm, implemented as `find_claw_coordinates`, detects claws (a $K\_{1,3}$ subgraph with one central vertex connected to three non-adjacent leaf vertices) in an undirected graph. It leverages the [aegypti](https://pypi.org/project/aegypti/) package (developed by the same author), which provides a **linear-time triangle detection algorithm** claimed to run in $O(n + m)$ time, where $n$ is the number of nodes and $m$ is the number of edges. The claw detection process adapts this by applying triangle finding to the complement of each node’s neighbor-induced subgraph.

### Key Steps:

1. **Neighbor Subgraph and Complement**:

   - For each node $i$ with degree at least 3, extract the induced subgraph of its neighbors.
   - Compute the complement of this subgraph, where edges represent the absence of connections in the original graph.

2. **Triangle Finding with Aegypti**:

   - Use the `aegypti` package’s `find_triangle_coordinates` function to detect triangles in the complement subgraph.
   - A triangle in the complement indicates three neighbors of $i$ that form an independent set, which, combined with $i$, forms a claw.
   - The `aegypti` algorithm employs Depth-First Search (DFS) tailored for this subgraph, achieving efficiency based on its claimed $O(n' + m')$ complexity, where $n'$ and $m'$ are the nodes and edges in the complement subgraph.

3. **Claw Storage**:
   - Store detected claws as frozensets, each containing the center $i$ and the three leaf vertices.
   - The storage time is $O(c)$, where $c$ is the number of claws found.

---

## Runtime Analysis

The runtime of the `find_claw_coordinates` algorithm depends on the graph’s structure, particularly the maximum degree $\Delta$, and varies based on the `first_claw` parameter.

### Notation:

- $n = |V|$: Number of vertices.
- $m = |E|$: Number of edges.
- $\text{deg}(i)$: Degree of vertex $i$.
- $\Delta$: Maximum degree in the graph.
- $c$: Number of claws detected.
- For each node $i$, the complement subgraph has $n' = \text{deg}(i)$ vertices and up to $m' \leq {\text{deg}(i) \choose 2}$ edges.

### Case 1: `first_claw=True` (Find One Claw)

- **Process**: Iterates over nodes until a claw is found, checking each node’s neighbor complement for a triangle.
- **Per Node $i$**:
  - Subgraph and complement construction: $O(\text{deg}(i)^2)$.
  - `aegypti` triangle detection: $O(\text{deg}(i)^2)$ for the complement subgraph.
  - Total per node: $O(\text{deg}(i)^2)$.
- **Total**:
  - Worst case (no claws): $\sum_i O(\text{deg}(i)^2) \leq \Delta \cdot \sum_i \text{deg}(i) = \Delta \cdot 2m = O(m \cdot \Delta)$.
  - Best case (claw found early): $O(\text{deg}(i)^2)$ for the first node with a claw.
- **Conclusion**: $O(m \cdot \Delta)$, efficient for sparse graphs ($\Delta = O(1)$), but not linear in $n + m$ for dense graphs.

### Case 2: `first_claw=False` (List All Claws)

- **Process**: Iterates over all nodes, finding all triangles in each complement subgraph.
- **Per Node $i$**:
  - Same construction cost: $O(\text{deg}(i)^2)$.
  - `aegypti` lists all triangles: $O(\text{deg}(i)^2)$ plus output time for each triangle.
  - Claw formation: $O(1)$ per triangle, up to ${\text{deg}(i) \choose 3}$ triangles.
- **Total**:
  - Base cost: $\sum_i O(\text{deg}(i)^2) = O(m \cdot \Delta)$.
  - Output cost: $O(c)$, where $c$ is the number of claws (up to $\sum_i {\text{deg}(i) \choose 3}$, potentially $O(n^3)$ in dense graphs).
- **Conclusion**: $O(m \cdot \Delta + c)$, output-sensitive, with runtime dominated by $c$ in graphs with many claws.

### Special Case: Claw-Free Graphs

- If no claws exist ($c = 0$), the runtime simplifies to $O(m \cdot \Delta)$ for both cases, as no additional output processing is needed.
- This matches the efficiency of triangle detection in the absence of claws.

---

## Impact of the Algorithm

This claw detection algorithm, built on the `aegypti` package, has significant implications:

1. **Leveraging Aegypti’s Innovation**:

   - The `aegypti` algorithm’s claimed $O(n + m)$ triangle detection (potentially challenging the sparse triangle hypothesis, $O(m^{4/3})$) enables efficient claw finding per node.
   - Its availability via `pip install aegypti` makes it accessible for practical use.

2. **Practical Applications**:

   - Useful in network analysis (e.g., social networks, bioinformatics) to identify claw-like structures.
   - Integrates seamlessly with NetworkX, enhancing graph processing workflows.

3. **Theoretical Significance**:

   - If `aegypti`’s linear-time claim holds against 3SUM-hard instances, this algorithm could contribute to breakthroughs in graph theory, influencing related problems like independent set detection.
   - The degree-dependent runtime ($O(m \cdot \Delta)$) suggests it’s optimized for sparse graphs, aligning with real-world networks.

4. **Limitations**:
   - Not strictly linear-time ($O(n + m)$) due to $\Delta$-dependence, limiting scalability in dense graphs.
   - Listing all claws can be slow if $c$ is large, reflecting the output-sensitive nature.

In summary, this algorithm extends the `aegypti` breakthrough to claw detection, offering a practical tool with theoretical promise. Further testing on diverse graphs could solidify its impact, especially if `aegypti`’s claims are validated.

---

# Compile and Environment

## Install Python >=3.10.

## Install Mendive's Library and its Dependencies with:

```bash
pip install mendive
```

# Execute

1. Go to the package directory to use the benchmarks:

```bash
git clone https://github.com/frankvegadelgado/mendive.git
cd mendive
```

2. Execute the script:

```bash
claw -i .\benchmarks\testMatrix1
```

utilizing the `claw` command provided by Mendive's Library to execute the Boolean adjacency matrix `mendive\benchmarks\testMatrix1`. The file `testMatrix1` represents the example described herein. We also support .xz, .lzma, .bz2, and .bzip2 compressed text files.

## The console output will display:

```
testMatrix1: Claw Found (1, 3, 4, 5)
```

which implies that the Boolean adjacency matrix `mendive\benchmarks\testMatrix1` contains a claw combining the nodes `(1, 3, 4, 5)`.

---

## Find and Count All Claws

The `-a` flag enables the discovery of all claws within the graph.

**Example:**

```bash
claw -i .\benchmarks\testMatrix2 -a
```

**Output:**

```
testMatrix2: Claws Found (1, 4, 8, 12); (1, 6, 9, 11); (2, 6, 8, 11); (1, 6, 9, 12); (1, 3, 8, 12); (2, 3, 4, 5); (2, 6, 9, 11); (1, 9, 11, 12); (1, 6, 11, 12); (1, 3, 6, 12); (1, 6, 8, 11); (1, 8, 9, 12); (2, 6, 8, 9); (1, 8, 11, 12); (1, 2, 3, 12); (1, 3, 6, 8); (2, 8, 9, 11); (1, 6, 8, 12); (2, 4, 6, 8); (1, 8, 9, 11); (5, 8, 9, 11); (1, 6, 8, 9); (2, 3, 5, 9); (2, 3, 5, 11); (1, 4, 6, 12); (1, 4, 6, 8)
```

When multiple claws exist, the output provides a list of their vertices.

Similarly, the `-c` flag counts all claws in the graph.

**Example:**

```bash
claw -i .\benchmarks\testMatrix2 -c
```

**Output:**

```
testMatrix2: Claws Count 26
```

## Runtime Analysis:

We employ the same algorithm used to solve the claw-free problem.

---

# Command Options

To display the help message and available options, run the following command in your terminal:

```bash
claw -h
```

This will output:

```
usage: claw [-h] -i INPUTFILE [-a] [-b] [-c] [-v] [-l] [--version]

Solve the Claw-Free Problem for an undirected graph encoded in DIMACS format.

options:
  -h, --help            show this help message and exit
  -i INPUTFILE, --inputFile INPUTFILE
                        input file path
  -a, --all             identify all claws
  -b, --bruteForce      compare with a brute-force approach using matrix multiplication
  -c, --count           count the total amount of claws
  -v, --verbose         anable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
```

This output describes all available options.

## The Mendive Testing Application

A command-line tool, `test_claw`, has been developed for testing algorithms on randomly generated, large sparse matrices. It accepts the following options:

```
usage: test_claw [-h] -d DIMENSION [-n NUM_TESTS] [-s SPARSITY] [-a] [-b] [-c] [-w] [-v] [-l] [--version]

The Mendive Testing Application using randomly generated, large sparse matrices.

options:
  -h, --help            show this help message and exit
  -d DIMENSION, --dimension DIMENSION
                        an integer specifying the dimensions of the square matrices
  -n NUM_TESTS, --num_tests NUM_TESTS
                        an integer specifying the number of tests to run
  -s SPARSITY, --sparsity SPARSITY
                        sparsity of the matrices (0.0 for dense, close to 1.0 for very sparse)
  -a, --all             identify all claws
  -b, --bruteForce      compare with a brute-force approach using matrix multiplication
  -c, --count           count the total amount of claws
  -w, --write           write the generated random matrix to a file in the current directory
  -v, --verbose         anable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
```

**This tool is designed to benchmark algorithms for sparse matrix operations.**

It generates random square matrices with configurable dimensions (`-d`), sparsity levels (`-s`), and number of tests (`-n`). While a comparison with a brute-force matrix multiplication approach is available, it's recommended to avoid this for large datasets due to performance limitations. Additionally, the generated matrix can be written to the current directory (`-w`), and verbose output or file logging can be enabled with the (`-v`) or (`-l`) flag, respectively, to record test results.

---

# Code

- Python code by **Frank Vega**.

---

# Complexity

```diff
+ This algorithm provides multiple of applications to other computational problems in combinatorial optimization and computational geometry.
```

---

# License

- MIT.
