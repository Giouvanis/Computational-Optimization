# https://www.geeksforgeeks.org/python/python-read-text-file-into-list-or-array/
# https://www.geeksforgeeks.org/python/how-to-print-a-list-without-brackets-in-python/
filename = input("Enter the filename to save the sparse matrix: ")
matrix = []
    # Read the sparse matrix from the file
with open(filename, 'r', ) as file: 
        for line in file:
            row = list(map(int, line.strip().split()))
            if row:  # Check if the row is not empty
                matrix.append(row)
        print("Reading the sparse matrix from the file...")
        for row in matrix:
            print(*row) # print(*row) prints the elements of the row without brackets and commas, making it more readable.

def sparsify( matrix) :
        m = len(matrix)
        n = (0 if len(matrix) == 0 else len(matrix[0])) # 
        i = 0
        j = 0
        A =  [] # the number of non-zero elements in the matrix
        IA =  [1] # the number of elements in each row of the CSR. It has N+1 elements and it is initialized with 1 because the first element of A is at index 1.
        # IA matrix has N+1
        # rows
        JA =  []
        i = 0
        while (i < m) :
            j = 0
            while (j < n) :
                if (matrix[i][j] != 0) :
                    A.append(matrix[i][j])
                    JA.append(j + 1) # JA matrix has N column
                j += 1
            IA.append(len(A) + 1) # IA matrix has N+1 rows
            i += 1
        return A, IA, JA  
A, IA, JA = sparsify(matrix)

print("A =", A)
print("JA =", JA)
print("IA =", IA)