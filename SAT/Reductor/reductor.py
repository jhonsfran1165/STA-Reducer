import lzma
import logging
import argparse
import numpy as np
# from pysat.solvers import Glucose3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

clauses = []
comments = []
cnf_num_variables = 0
cnf_num_clauses = 0


def sat_from_file(file_location):
    with lzma.open(file_location, mode='rt') as file:
        for line in file:
            # clean each line
            line = line.replace('\n', '').replace(' 0', '')

            # get clauses
            if len(line) > 0 and not line.startswith('p') and not line.startswith('c'):
                global clauses
                clauses.append(line)
                # g.add_clause((line.replace('\n', '').replace(' 0', '')))

            # get comments
            if len(line) > 0 and line.startswith('p') or line.startswith('c'):
                if line.startswith('p'):
                    data = line.split(' ')
                    global cnf_num_variables
                    cnf_num_variables = int(data[2])
                    global cnf_num_clauses
                    cnf_num_clauses = int(data[3])

                global comments
                comments.append(line)


def find_max_variable(clauses):
    """
    find the last id of the variables used in the clauses.
    We are looking for it because we need to add new variables to the clauses
    """
    all_clauses = []

    for clause in clauses:
        for literal in clause.split(' '):
            if literal.startswith('-') == True:
                all_clauses.append(int(literal[1:]))
            else:
                all_clauses.append(int(literal))

    print(max(all_clauses))


def reduce_to_3sat():
    """
    reduce all SAT instances to 3 SAT
    """

    reduced_clauses = []
    # we use this to keep the amount of all variables added
    total_num_variables = cnf_num_variables

    # reduce SAT to 3-SAT
    for clause in clauses:
        # we got four scenarios
        # docs: https://opendsa-server.cs.vt.edu/ODSA/Books/Everything/html/SAT_to_threeSAT.html
        literals = clause.split(' ')
        count_literals = len(literals)

        # 1. clause have 1 literal
        if count_literals == 1:
            # introduce new variables and new clauses
            num_variables = 2
            num_clauses = 4

            # create an array with the variables we'll use later
            new_variables = [
                (total_num_variables+i+1)
                for i in range(num_variables)
            ]

            # add those new variables to the total
            total_num_variables = total_num_variables + num_variables

            # create each sentence
            i = 0
            init = [
                str(new_variables[i])
                for i in range(2)
            ]

            finish = [
                str(-new_variables[num_variables-i-1])
                for i in range(2)
            ]

            while i < num_clauses:
                tmp = []

                if i == 0:
                    reduced_clauses.append(' '.join(literals + init))
                elif i == num_clauses-1:
                    reduced_clauses.append(' '.join(literals + finish))
                else:
                    # create the proper combination of literals
                    for j in range(num_variables):
                        if i-1 == j:
                            tmp.append(str(-new_variables[j-1]))
                        else:
                            tmp.append(str(new_variables[j-1]))
                    reduced_clauses.append(' '.join(literals + tmp))

                i = i+1

        # # 2. clause have 2 literals
        if count_literals == 2:
            # introduce new variables and new clauses
            num_variables = 1
            num_clauses = 2

            new_variables = [
                (total_num_variables+i+1)
                for i in range(num_variables)
            ]

            # add those new variables to the total
            total_num_variables = total_num_variables + num_variables

            # create each sentence
            i = 0
            init = [
                str(new_variables[i])
                for i in range(1)
            ]

            finish = [
                str(-new_variables[num_variables-i-1])
                for i in range(1)
            ]

            while i < num_clauses:
                if i == 0:
                    reduced_clauses.append(' '.join(literals + init))
                else:
                    reduced_clauses.append(' '.join(literals + finish))
                i = i+1

        # # 3. clause have 3 literals
        if count_literals == 3:
            reduced_clauses.append(' '.join(literals))

        # 4. clause have more than 3 literals
        if count_literals > 3:
            # introduce k-3 new variables
            # introduce k-2 new clauses
            num_variables = count_literals-3
            num_clauses = count_literals-2

            new_variables = [
                (total_num_variables+i+1)
                for i in range(num_variables)
            ]

            # add those new variables to the total
            total_num_variables = total_num_variables + num_variables

            init = [
                (literals[i])
                for i in range(2)
            ]

            finish = [
                (literals[count_literals-i-1])
                for i in range(2)
            ]

            # create each sentence
            i = 0
            while i < num_clauses:
                tmp = []

                if i == 0:
                    reduced_clauses.append(
                        ' '.join(init+[str(new_variables[0])]))
                elif i == num_clauses-1:
                    reduced_clauses.append(
                        ' '.join([str(-new_variables[i-1])]+finish))
                else:
                    # create the proper combination of literals
                    tmp.append(str(-new_variables[i-1]))
                    for j in range(1):
                        tmp.append(literals[j+2])
                    tmp.append(str(new_variables[i]))
                    reduced_clauses.append(' '.join(tmp))
                i = i+1

    return reduced_clauses


def three_sat_to_xsat(x_sat, sat_clauses):
    """
    Transform 3 SAT instances to X SAT
    """
    transform_clauses = []
    # we use this to keep the amount of all variables added
    total_num_variables = cnf_num_variables

    # reduce 3-SAT to X-SAT
    for clause in sat_clauses:
        # we got four scenarios
        # docs: https://opendsa-server.cs.vt.edu/ODSA/Books/Everything/html/SAT_to_threeSAT.html
        literals = clause.split(' ')
        count_literals = len(literals)

        # introduce new variables and new clauses
        num_variables = x_sat - 3
        num_clauses = x_sat - 1

        # create an array with the variables we'll use later
        new_variables = [
            (total_num_variables+i+1)
            for i in range(num_variables)
        ]

        # add those new variables to the total
        total_num_variables = total_num_variables + num_variables

        # create each sentence
        i = 0
        init = [
            str(new_variables[i])
            for i in range(num_variables)
        ]

        finish = [
            str(-new_variables[num_variables-i-1])
            for i in range(num_variables)
        ]

        while i < num_clauses:
            tmp = []

            if i == 0:
                transform_clauses.append(', '.join(literals + init))
            elif i == num_clauses-1:
                transform_clauses.append(', '.join(literals + finish))
            else:
                # create the proper combination of literals
                for j in range(num_variables):
                    if i-1 == j:
                        tmp.append(str(-new_variables[j-1]))
                    else:
                        tmp.append(str(new_variables[j-1]))
                transform_clauses.append(', '.join(literals + tmp))

            i = i+1

    return transform_clauses


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'x_sat',
        help='Please type a number mayor than 3 (X-SAT) ej. 5',
        type=int
    )

    parser.add_argument(
        'file_location',
        help='Please type the file location that you want to process',
        type=str
    )

    args = parser.parse_args()
    x_sat = args.x_sat
    file_location = args.file_location

    # 5 SAT
    # file_location = "../InstanciasSAT/sc14-crafted/sgen6-840-5-1.cnf.lzma"

    # 4 SAT
    # file_location = "../InstanciasSAT/sc14-crafted/sgen4-sat-160-8.cnf.lzma"

    # 3 SAT
    # file_location = "../InstanciasSAT/sc14-crafted/edges-070-3-10062999-36.cnf.lzma"

    # 2 SAT
    # file_location = "../InstanciasSAT/sc14-crafted/sgen6-1440-5-1.cnf.lzma"

    # 1 SAT
    # file_location = "../InstanciasSAT/sc14-crafted/hid-uns-enc-6-1-0-0-0-0-2907.cnf.lzma"

    sat_from_file(file_location)
    reduced_clauses = reduce_to_3sat()

    if x_sat < 3:
        logger.info('x_sat parameter has to be > 3. Error x_sat {} invalid'.format(x_sat))

    if x_sat == 3:
        result = reduced_clauses
    else:
        result = three_sat_to_xsat(x_sat, reduced_clauses)

    # print(g.solve())
    # print(g.get_model())

    # print(clauses)
    # find_max_variable(clauses)
    print(result)
    # print(cnf_num_clauses)
