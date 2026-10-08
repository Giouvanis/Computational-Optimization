# Computational-Optimization
Sparse Matrix Representation (CSR &amp; CSC in Python) A lightweight, zero-dependency Python implementation for processing sparse matrices and converting them into Compressed Sparse Row (CSR) and Compressed Sparse Column (CSC) formats using 1-based indexing.

Features
Interactive Menu-Driven: Easily select between manual matrix creation or reading from external files.

File Parsing & Matrix: Robust file reading for space-separated 2D matrices from .txt files.

Dual Sparse Storage Formats:

CSR (Compressed Sparse Row): Compresses matrices row-by-row into Anz (values), JA (column indices), and IA (row start pointers).

CSC (Compressed Sparse Column): Compresses matrices column-by-column into Anz (values), JA (row indices), and IA (column start pointers).

Pure Python: Implemented without external scientific libraries (e.g., NumPy or SciPy) to showcase the underlying algorithmic mechanics.
