# Import pizza
pizza = []

FILE="medium.in"

with open(FILE) as openfileobject:
    for i_row, line in enumerate(openfileobject):
        if i_row == 0:
            numbers = line.split()
            nr_rows = int(numbers[0])
            nr_cols = int(numbers[1])
            min_ingreds = int(numbers[2])
            max_cells = int(numbers[3])

            pizza = [[0 for x in range(nr_cols)] for y in range(nr_rows)]
        else:
            for i_col, cell in enumerate(line):
                if cell == "T":
                    pizza[i_row - 1][i_col] = 1


def evalSlices(individual):
