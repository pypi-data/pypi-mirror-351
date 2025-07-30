#!/usr/bin/env python
# Test script for compatibility with Python 3.11

import os
import sys
from pathlib import Path

# Add src to the Python path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Test basic imports
from orca_parse.xyz import xyz
from orca_studio.molecule import Molecule, Geometry, Atom, Element

print(f"Python version: {sys.version}")

# Test basic functionality that uses fixed f-strings
def test_xyz_string_gen():
    lines = ["Header line", "Comment line", "H 0.0 0.0 0.0", "O 1.0 0.0 0.0"]
    # Mock find_section_starts and extract_table_lines results
    class MockFinder:
        def __call__(self, *args, **kwargs):
            return [3]  # line index
    
    # Monkey patch functions for testing
    import orca_parse.xyz as xyz_module
    original_find = xyz_module.find_section_starts
    original_extract = xyz_module.extract_table_lines
    
    try:
        xyz_module.find_section_starts = MockFinder()
        xyz_module.extract_table_lines = lambda *args, **kwargs: ["H 0.0 0.0 0.0", "O 1.0 0.0 0.0"]
        
        result = xyz_module.xyz(lines)
        print("XYZ generation test:", "PASSED" if "2\n\nH 0.0 0.0 0.0\nO 1.0 0.0 0.0" == result else "FAILED")
    finally:
        # Restore original functions
        xyz_module.find_section_starts = original_find
        xyz_module.extract_table_lines = original_extract


def test_molecule_repr():
    # Create a simple molecule
    h_element = Element.from_symbol("H")
    o_element = Element.from_symbol("O")
    
    h_atom = Atom(h_element, np.array([0.0, 0.0, 0.0]))
    o_atom = Atom(o_element, np.array([1.0, 0.0, 0.0]))
    
    geom = Geometry(atoms=[h_atom, o_atom], comment="Water")
    mol = Molecule(charge=0, mult=1, geometry=geom)
    
    repr_str = repr(mol)
    print("Molecule __repr__ test:", "PASSED" if repr_str.startswith("2\n{") else "FAILED")
    print(f"Repr content: {repr_str!r}")


if __name__ == "__main__":
    try:
        import numpy as np
        test_xyz_string_gen()
        test_molecule_repr()
        print("All tests completed")
    except Exception as e:
        print(f"Error in tests: {e}")