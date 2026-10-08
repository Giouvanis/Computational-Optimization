
def menu():
    print("Menu:")
    print("1. Create a 2D array (matrix)")
    print("2. Read a 2D array (matrix) from a text file")
    print("3. Exit")

    option = int(input("Enter your option (1, 2 or 3): "))
    if option in [1, 2, 3]:
        pass
    else:
        print("Invalid option. Please try again.")
        return menu()

    
    if option == 1:
        print("1. Create a 2D array (matrix)")

        # Option 1: tell the user to enter the matrix manually
        # https://intellipaat.com/blog/how-to-take-2d-array-input-in-python/

        rows = int(input("give me a integer number of rows: "))
        cols = int(input("give me a integer number of columns: "))
        matrix_option1 = []
        for i in range(rows):
            row = []
            for j in range(cols):
                value = int(input(f"Enter element at position ({i},{j}): "))
                row.append(value)
            matrix_option1.append(row)
        print("2D Array (Matrix):")
        # for row in matrix:
            # print(*row)
        # return matrix
        for i in range(rows):                           
            for j in range(cols):
                print(matrix_option1[i][j], end=" ")
            print()
            return matrix_option1
    elif option == 2:
        print("2. Read a 2D array (matrix) from a text file")

        # Option 2: using read_txt_file.py
        # https://www.geeksforgeeks.org/python/how-to-read-text-file-into-list-in-python/
        # https://www.geeksforgeeks.org/python/python-read-text-file-into-list-or-array/
        # https://www.geeksforgeeks.org/python/how-to-print-a-list-without-brackets-in-python/

        filename = input("Enter the filename to save the sparse matrix: ")
        matrix_option2 = []
        # Read the sparse matrix from the file
        with open(filename, 'r') as file:
            for line in file:
                row = list(map(int, line.strip().split()))
                if row:  # Check if the row is not empty
                    matrix_option2.append(row)
            print("Reading the sparse matrix from the file...")
            for row in matrix_option2:
                print(*row)  # print(*row) prints the elements of the row without brackets and commas, making it more readable.
        return matrix_option2
    elif option == 3:
       print("Exiting the program.")
       exit()

# https://www.geeksforgeeks.org/dsa/sparse-matrix-representations-set-3-csr/

def sparsify(Matrix) :
        m = len(Matrix)
        n = (0 if len(Matrix) == 0 else len(Matrix[0])) 
        Anz =  [] # the number of non-zero elements in the matrix
        IA =  [1] # the number of elements in each row of the CSR. It has N+1 elements and it is initialized with 1 because the first element of A is at index 1.
        i= 0
        j= 0
        # IA matrix has N+1
        # rows
        JA =  []
        while (i < m) :
            j = 0
            while (j < n) :
                if (Matrix[i][j] != 0) :
                    Anz.append(Matrix[i][j])
                    JA.append(j + 1) # JA matrix has N column
                j += 1
            IA.append(len(Anz) + 1) # IA matrix has N+1 rows
            i += 1
        return Anz, IA, JA 
matrix = menu()
Anz, IA, JA = sparsify(matrix)

print("Anz =", Anz)
print("JA =", JA)
print("IA =", IA)

