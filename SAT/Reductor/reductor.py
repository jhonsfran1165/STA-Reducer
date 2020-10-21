import lzma
import logging
import argparse
import numpy as np
# from pysat.solvers import Glucose3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # news_domains_choices = list(config()['environments'].keys())

    # parser.add_argument(
    #     'environments',
    #     help='The new environtment that you want deploy',
    #     type=str,
    #     choices=news_domains_choices
    # )

    # parser.add_argument(
    #     'option',
    #     help='do you want destroy the infrastructure?',
    #     type=str,
    #     choices=["create", "destroy"]
    # )

    args = parser.parse_args()
    file_location = "../InstanciasSAT/sc14-crafted/edges-072-3-7923777-13.cnf.lzma"

    clauses = []
    comments = []
    cnf_num_variables = 0
    cnf_num_clauses = 0
    cnf_max_variable = 0
    # g = Glucose3()

    with lzma.open(file_location, mode='rt') as file:
        for line in file:
            # clean each line
            line = line.replace('\n', '').replace(' 0', '')

            # get clauses
            if len(line) > 0 and not line.startswith('p') and not line.startswith('c'):
                clauses.append(line)
                # g.add_clause((line.replace('\n', '').replace(' 0', '')))

            # get comments
            if len(line) > 0 and line.startswith('p') or line.startswith('c'):
                if line.startswith('p'):
                    data = line.split(' ')
                    cnf_num_variables = int(data[2])
                    cnf_num_clauses = int(data[3])
                comments.append(line)

    # TODO: Maybe we can use numpy
    # TODO: delete INT
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
            # introduce 2 new variables
            total_num_variables = total_num_variables + 2
            # replace Ci with a conjunction of those two new variables
            literal = int(literals[0])
            var1 = total_num_variables-1
            var2 = total_num_variables

            reduced_clauses.append('{} {} {}'.format(literal, var1, var2))
            reduced_clauses.append([literal, -var1, var2])
            reduced_clauses.append([literal, var1, -var2])
            reduced_clauses.append([literal, -var1, -var2])

        # 2. clause have 2 literals
        if count_literals == 2:
            # introduce 1 new variables
            total_num_variables = total_num_variables + 1
            # replace Ci with a conjunction of those two new variables
            literal1 = int(literals[0])
            literal2 = int(literals[1])
            var1 = total_num_variables

            reduced_clauses.append('{} {} {}'.format(literal1, literal2, var1))
            reduced_clauses.append(
                '{} {} {}'.format(literal1, literal2, -var1))

        # 3. clause have 3 literals
        if count_literals == 3:
            literal1 = int(literals[0])
            literal2 = int(literals[1])
            literal3 = int(literals[2])
            reduced_clauses.append('{} {} {}'.format(
                literal1, literal2, literal3))

        # 3. clause have more than 4 literals
        if count_literals > 3:
            # introduce k-3 new variables
            # introduce k-2 new clauses
            new_variables = count_literals-3
            new_clauses = count_literals-2
            total_num_variables = total_num_variables + new_variables

            # replace Ci with a conjunction of those new_variables
            literal1 = int(literals[0])
            literal2 = int(literals[1])
            literal_k_1 = int(literals[count_literals-1])
            literal_k = int(literals[count_literals])

            i = 0
            while i < new_clauses:
                if i == 0:
                    reduced_clauses.append(
                        '{} {} {}'.format(literals[i], literals[i+1], total_num_variables-new_variables+1))
                elif i == new_clauses-1:
                    reduced_clauses.append(
                        '{} {} {}'.format(-total_num_variables, literals[i+1], literals[i+2]))
                elif i % 2 == 0:
                    reduced_clauses.append(
                        '{} {} {}'.format(total_num_variables-new_variables+1, literals[i+1], -(total_num_variables-new_variables+2)))
                else:
                    reduced_clauses.append(
                        '{} {} {}'.format(-total_num_variables-new_variables+1, literals[i+1], total_num_variables-new_variables+2))

                i += 1

    # print(g.solve())
    # print(g.get_model())

    print(clauses)
    # find_max_variable(clauses)
    print(reduced_clauses)
    # print(cnf_num_variables)
    # print(cnf_num_clauses)
