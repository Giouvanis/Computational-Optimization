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
        return matrix
        print()

    elif option == 2:
        print("2. Read a 2D array (matrix) from a text file")
        filename = input("Enter the filename to save the sparse matrix: ")
        matrix = []
        # Read the sparse matrix from the file
        with open(filename, 'r') as file:
            for line in file:
                row = list(map(int, line.strip().split()))
                if row:  # Check if the row is not empty
                    matrix.append(row)
            print("Reading the sparse matrix from the file...")
            for row in matrix:
                print(*row)  # print(*row) prints the elements of the row without brackets and commas, making it more readable.
        return matrix

    elif option == 3:
        print("Exiting the program.")
        exit()
# https://www.geeksforgeeks.org/dsa/sparse-matrix-representations-set-3-csr/

def sparsify(Matrix):
    m = len(Matrix)
    n = (0 if len(Matrix) == 0 else len(Matrix[0]))
    A = []
    IA = [1]
    JA = []

    for i in range(m):
        for j in range(n):
            if Matrix[i][j] != 0:
                A.append(Matrix[i][j])
                JA.append(j + 1)
        IA.append(len(A) + 1)

    return A, IA, JA


def main():
    matrix = menu()
    if matrix is not None:
        A, IA, JA = sparsify(matrix)
        print("A =", A)
        print("JA =", JA)
        print("IA =", IA)


if __name__ == "__main__":
    main()        
       
    