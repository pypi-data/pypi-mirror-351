from typing import Dict, Set, Optional
from collections import defaultdict

# Inverted Index Approach (Best for Repeated Queries)
class InvertedIndexFirstElementCollection:
    """
    Maintains inverted index for very fast repeated queries.
    Best for: When you do many first-element queries on the same sets.
    """
    
    def __init__(self):
        self.sets: Dict[int, Set[int]] = {}
        self.inverted_index: Dict[int, Set[int]] = defaultdict(set)
        self.sizes: Dict[int, int] = {}
        # Cache for repeated queries
        self._intersection_cache: Dict[tuple, Optional[int]] = {}
    
    def add_set(self, i: int, S_i: Set[int]):
        """Add a set and update inverted index."""
        # Clear cache when data changes
        self._intersection_cache.clear()
        
        # Remove old entries if updating
        if i in self.sets:
            for element in self.sets[i]:
                self.inverted_index[element].discard(i)
                if not self.inverted_index[element]:
                    del self.inverted_index[element]
        
        self.sets[i] = S_i.copy()
        self.sizes[i] = len(S_i)
        
        # Build inverted index
        for element in S_i:
            self.inverted_index[element].add(i)
    
    def first_intersection_element(self, i: int, j: int, k: int) -> Optional[int]:
        """Find first element using inverted index with caching."""
        # Check cache first
        cache_key = tuple(sorted([i, j, k]))
        if cache_key in self._intersection_cache:
            return self._intersection_cache[cache_key]
        
        if not all(key in self.sets for key in [i, j, k]):
            missing = [key for key in [i, j, k] if key not in self.sets]
            raise KeyError(f"Keys not found: {missing}")
        
        target_sets = {i, j, k}
        
        # Early termination for empty sets
        if any(self.sizes[idx] == 0 for idx in [i, j, k]):
            self._intersection_cache[cache_key] = None
            return None
        
        # Find first element that appears in all three sets
        # Use smallest set to minimize iterations
        smallest_id = min([i, j, k], key=lambda x: self.sizes[x])
        
        for element in self.sets[smallest_id]:
            if target_sets.issubset(self.inverted_index[element]):
                self._intersection_cache[cache_key] = element
                return element
        
        self._intersection_cache[cache_key] = None
        return None

# Example usage and testing
def example():
    # Simple example
    collection = InvertedIndexFirstElementCollection()
    
    # Add test sets
    collection.add_set(1, {1, 2, 3, 4, 5})
    collection.add_set(2, {3, 4, 5, 6, 7})
    collection.add_set(3, {4, 5, 6, 7, 8})
    
    # Find first intersection element
    first_element = collection.first_intersection_element(1, 2, 3)
    print(f"First intersection element: {first_element}")  # Should be 4 or 5
    
    # Test with no intersection
    collection.add_set(4, {10, 11, 12})
    no_intersection = collection.first_intersection_element(1, 2, 4)
    print(f"No intersection case: {no_intersection}")  # Should be None
    