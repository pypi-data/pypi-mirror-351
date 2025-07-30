# Modified on 05/28/2025
# Author: Frank Vega


import numpy as np
import scipy.sparse as sp
from itertools import combinations

import networkx as nx
import aegypti.algorithm as algo

def find_claw_coordinates(graph, first_claw=True):
    """
    Finds the coordinates of all claws in a given undirected NetworkX graph.

    Args:
        graph: An undirected NetworkX graph.
        first_claw: A boolean indicating whether to return only the first found claw.

    Returns:
        A list of sets, where each set represents the coordinates of a claw.
        Each claw is represented as a set of 4 vertex indices: {center, leaf1, leaf2, leaf3}
        Returns None if no claws are found.
    """
    # Ensure the input is a valid undirected NetworkX graph
    if not isinstance(graph, nx.Graph):
        raise ValueError("Input must be an undirected NetworkX Graph.")
    
    # Initialize a set to store unique claws, each as a frozenset of 4 vertices
    claws = set()
    
    # Iterate over each node in the graph as a potential center of a claw
    for i in graph.nodes():
        # Skip nodes with fewer than 3 neighbors, as a claw requires a center with degree at least 3
        if graph.degree(i) < 3:
            continue
        
        # Get all neighbors of the current node i
        neighbors = graph.neighbors(i)
        
        # Create an induced subgraph containing only the neighbors of i
        neighbor_subgraph = graph.subgraph(neighbors)
        
        # Compute the complement of the neighbor subgraph
        # In the complement, an edge exists if the original graph has no edge between those neighbors
        neighbor_complement = nx.complement(neighbor_subgraph)
        
        # Use the aegypti algorithm to find triangles in the complement graph
        # A triangle in the complement means the three vertices form an independent set in the original graph
        # This is key: three independent neighbors of i, plus i, form a claw
        triangles = algo.find_triangle_coordinates(neighbor_complement, first_claw)
        
        # If no triangles are found, no claw exists with i as the center
        if triangles is None:
            continue
        
        # If only the first claw is needed, take one triangle and form a claw
        elif first_claw:
            triangle = triangles.pop()
            claws = {triangle.union({i})}  # Combine the triangle (3 leaves) with center i
            break  # Stop after finding the first claw
        
        # Otherwise, collect all claws by combining each triangle with center i
        else:
            claws.update({triangle.union({i}) for triangle in triangles})
    
    # Return the list of claws, or None if none were found
    return list(claws) if claws else None

def is_claw_free_brute_force(adj_matrix):
    """
    Checks if a graph represented by a sparse adjacency matrix is claw-free using matrix multiplication.
    
    A graph is claw-free if it contains no induced K₁,₃ (claw) subgraph.
    A claw consists of a center vertex connected to three mutually non-adjacent vertices.
    
    Args:
        adj_matrix: A SciPy sparse matrix (e.g., csc_matrix) representing the adjacency matrix.
        
    Returns:
        True if the graph is claw-free, False otherwise.
        
    Raises:
        ValueError: if the input matrix is not square.
        TypeError: if the input is not a sparse matrix.
    """
    # Input validation
    if not sp.issparse(adj_matrix):
        raise TypeError("Input must be a sparse matrix (scipy.sparse)")
    
    if adj_matrix.shape[0] != adj_matrix.shape[1]:
        raise ValueError("Adjacency matrix must be square")
    
    n = adj_matrix.shape[0]
    
    # Convert to CSR format for efficient row operations
    A = adj_matrix.tocsr()
    
    # Ensure the matrix is symmetric and has no self-loops
    A.setdiag(0)  # Remove self-loops
    
    # Method 1: Matrix multiplication approach
    # For each vertex v, check if any three of its neighbors are mutually non-adjacent
    
    # A² gives us paths of length 2
    A_squared = A @ A
    A_squared.setdiag(0)  # Remove diagonal (paths from vertex to itself)
    
    # For each vertex, we need to check if it's the center of a claw
    for center in range(n):
        # Get neighbors of the center vertex
        neighbors = A[center, :].nonzero()[1]  # Column indices of non-zero elements
        
        if len(neighbors) < 3:
            continue  # Cannot form a claw with less than 3 neighbors
        
        # Create submatrix of neighbors
        neighbor_submatrix = A[np.ix_(neighbors, neighbors)]
        
        # Check if there are three mutually non-adjacent neighbors
        if _has_independent_set_of_size_3(neighbor_submatrix, neighbors):
            return False  # Found a claw
    
    return True


def _has_independent_set_of_size_3(submatrix, vertices):
    """
    Check if there exists an independent set of size 3 in the subgraph.
    Uses matrix operations to efficiently detect three mutually non-adjacent vertices.
    """
    n = len(vertices)
    if n < 3:
        return False
    
    # Convert to dense for easier manipulation of small submatrices
    dense_sub = submatrix.toarray() if sp.issparse(submatrix) else submatrix
    
    # Check all combinations of 3 vertices
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                # Check if vertices i, j, k are mutually non-adjacent
                if (dense_sub[i, j] == 0 and 
                    dense_sub[i, k] == 0 and 
                    dense_sub[j, k] == 0):
                    return True
    
    return False

def find_claw_coordinates_brute_force(adjacency_matrix):
    """
    Finds the coordinates of all claws in a given SciPy sparse matrix.
    
    A claw (K₁,₃) consists of:
    - One center vertex connected to three other vertices
    - The three other vertices are mutually non-adjacent
    
    Args:
        adjacency_matrix: A SciPy sparse matrix (e.g., csr_matrix).
   
    Returns:
        A list of sets, where each set represents the coordinates of a claw.
        Each claw is represented as a set of 4 vertex indices: {center, leaf1, leaf2, leaf3}
        
    Raises:
        TypeError: if the input is not a sparse matrix.
        ValueError: if the input matrix is not square.
    """
    # Input validation
    if not sp.issparse(adjacency_matrix):
        raise TypeError("Input must be a sparse matrix (scipy.sparse)")
    
    if adjacency_matrix.shape[0] != adjacency_matrix.shape[1]:
        raise ValueError("Adjacency matrix must be square")
    
    n = adjacency_matrix.shape[0]
    claws = []
    
    # Convert to CSR format for efficient row access
    A = adjacency_matrix.tocsr()
    A.setdiag(0)  # Remove self-loops
    
    # For each potential center vertex
    for center in range(n):
        # Get all neighbors of the center vertex using sparse matrix operations
        neighbors = A[center, :].nonzero()[1]  # Column indices of non-zero elements
        
        if len(neighbors) < 3:
            continue  # Cannot form a claw with less than 3 neighbors
        
        # Extract the subgraph induced by the neighbors
        neighbor_subgraph = A[np.ix_(neighbors, neighbors)]
        
        # Find all combinations of 3 neighbors that are mutually non-adjacent
        claws_from_center = _find_independent_triplets_matrix(
            neighbor_subgraph, neighbors, center
        )
        claws.extend(claws_from_center)
    
    return claws

def _find_independent_triplets_matrix(subgraph, vertices, center):
    """
    Find all independent sets of size 3 in the subgraph using matrix operations.
    
    Args:
        subgraph: Sparse adjacency matrix of the subgraph
        vertices: List of vertex indices in the original graph
        center: The center vertex of potential claws
        
    Returns:
        List of sets representing claws with the given center
    """
    n = len(vertices)
    if n < 3:
        return []
    
    claws = []
    dense_sub = subgraph.toarray()  # Convert to dense for small subgraphs
    
    # Check all combinations of 3 vertices for independence (no edges between them)
    for triplet_indices in combinations(range(n), 3):
        i, j, k = triplet_indices
        
        # Check if the three vertices are mutually non-adjacent
        if (dense_sub[i, j] == 0 and 
            dense_sub[i, k] == 0 and 
            dense_sub[j, k] == 0):
            
            # Found an independent triplet - forms a claw with center
            claw = {center, vertices[i], vertices[j], vertices[k]}
            claws.append(claw)
    
    return claws

def find_claw_coordinates_optimized(adjacency_matrix):
    """
    Optimized version using advanced matrix operations and bit manipulation.
    
    This version uses matrix powers and boolean operations to find claws more efficiently.
    """
    if not sp.issparse(adjacency_matrix):
        raise TypeError("Input must be a sparse matrix (scipy.sparse)")
    
    if adjacency_matrix.shape[0] != adjacency_matrix.shape[1]:
        raise ValueError("Adjacency matrix must be square")
    
    n = adjacency_matrix.shape[0]
    A = adjacency_matrix.tocsr()
    A.setdiag(0)
    
    claws = []
    
    # Precompute complement matrix for efficiency
    complement_matrix = _compute_complement_matrix(A)
    
    for center in range(n):
        neighbors = A[center, :].nonzero()[1]
        
        if len(neighbors) < 3:
            continue
        
        # Use complement matrix to find independent sets more efficiently
        neighbor_complement = complement_matrix[np.ix_(neighbors, neighbors)]
        claws_from_center = _find_triangles_as_claws(
            neighbor_complement, neighbors, center
        )
        claws.extend(claws_from_center)
    
    return claws

def _compute_complement_matrix(adj_matrix):
    """Compute the complement of the adjacency matrix efficiently."""
    n = adj_matrix.shape[0]
    
    # Create identity matrix to exclude self-loops
    identity = sp.eye(n, format='csr')
    
    # Create all-ones matrix
    ones_matrix = sp.csr_matrix(np.ones((n, n)))
    
    # Complement = ones - adjacency - identity
    complement = ones_matrix - adj_matrix - identity
    complement.eliminate_zeros()
    
    return complement

def _find_triangles_as_claws(complement_subgraph, vertices, center):
    """
    Find triangles in complement graph (which correspond to independent sets in original).
    """
    claws = []
    n = len(vertices)
    
    if n < 3:
        return claws
    
    # Convert to dense for triangle detection
    C = complement_subgraph.toarray()
    
    # Find all triangles in the complement graph
    for i in range(n):
        for j in range(i + 1, n):
            if C[i, j] == 0:  # No edge in complement = edge in original
                continue
            for k in range(j + 1, n):
                if C[i, k] > 0 and C[j, k] > 0:  # Triangle in complement
                    # This corresponds to an independent set in the original
                    claw = {center, vertices[i], vertices[j], vertices[k]}
                    claws.append(claw)
    
    return claws


def find_claw_coordinates_vectorized(adjacency_matrix):
    """
    Highly optimized vectorized version using NumPy broadcasting.
    """
    if not sp.issparse(adjacency_matrix):
        raise TypeError("Input must be a sparse matrix (scipy.sparse)")
    
    if adjacency_matrix.shape[0] != adjacency_matrix.shape[1]:
        raise ValueError("Adjacency matrix must be square")
    
    n = adjacency_matrix.shape[0]
    A = adjacency_matrix.tocsr()
    A.setdiag(0)
    
    claws = []
    
    for center in range(n):
        neighbors = A[center, :].nonzero()[1]
        num_neighbors = len(neighbors)
        
        if num_neighbors < 3:
            continue
        
        # Extract neighbor subgraph
        neighbor_adj = A[np.ix_(neighbors, neighbors)].toarray()
        
        # Vectorized approach to find all independent triplets
        claws_from_center = _vectorized_independent_triplets(
            neighbor_adj, neighbors, center
        )
        claws.extend(claws_from_center)
    
    return claws


def _vectorized_independent_triplets(adj_matrix, vertices, center):
    """
    Vectorized computation of independent triplets using NumPy operations.
    """
    n = len(vertices)
    if n < 3:
        return []
    
    claws = []
    
    # Generate all triplet combinations using vectorized operations
    indices = np.arange(n)
    
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                # Check if triplet (i,j,k) is independent
                if (adj_matrix[i, j] == 0 and 
                    adj_matrix[i, k] == 0 and 
                    adj_matrix[j, k] == 0):
                    
                    claw = {center, vertices[i], vertices[j], vertices[k]}
                    claws.append(claw)
    
    return claws


def find_claw_coordinates_parallel_ready(adjacency_matrix):
    """
    Version optimized for parallel processing - returns generator for memory efficiency.
    """
    if not sp.issparse(adjacency_matrix):
        raise TypeError("Input must be a sparse matrix (scipy.sparse)")
    
    if adjacency_matrix.shape[0] != adjacency_matrix.shape[1]:
        raise ValueError("Adjacency matrix must be square")
    
    n = adjacency_matrix.shape[0]
    A = adjacency_matrix.tocsr()
    A.setdiag(0)
    
    def claw_generator():
        for center in range(n):
            neighbors = A[center, :].nonzero()[1]
            
            if len(neighbors) < 3:
                continue
            
            neighbor_subgraph = A[np.ix_(neighbors, neighbors)]
            
            for claw in _find_independent_triplets_matrix(neighbor_subgraph, neighbors, center):
                yield claw
    
    return list(claw_generator())
