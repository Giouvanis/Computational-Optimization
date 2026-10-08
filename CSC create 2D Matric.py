# Option 1: tell the user to enter the matrix manually

# https://intellipaat.com/blog/how-to-take-2d-array-input-in-python/

rows = int(input("give me a integer number of rows: "))     
cols = int(input("give me a integer number of columns: "))

matrix = []

for i in range(rows):  
    row = [] 
    for j in range(cols):  
        value = int(input(f"Enter element at position ({i},{j}): ")) 
        row.append(value) 
    matrix.append(row)  


print("2D Array (Matrix):") 
for i in range(rows):  
    for j in range(cols):  
        print(matrix[i][j], end=" ")  
    print()

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
        while (j < n) :
            i = 0
            while (i < m) :
                if (matrix[i][j] != 0) :
                    A.append(matrix[i][j])
                    JA.append(i + 1) # JA matrix has N column
                i += 1
            IA.append(len(A) + 1) # IA matrix has N+1 rows
            j += 1
        return A, IA, JA
A, IA, JA = sparsify(matrix)

print("A =", A)
print("JA =", JA)
print("IA =", IA)