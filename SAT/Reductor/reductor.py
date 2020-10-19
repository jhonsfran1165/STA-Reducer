import lzma
import logging
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

    with lzma.open(file_location, mode='rt') as file:
        for line in file:
            if len(line) > 0 and not line.startswith('p') and not line.startswith('c'):
                clauses.append(line.replace('\n', '').replace(' 0', ''))

            if len(line) > 0 and line.startswith('p') or line.startswith('c'):
                comments.append(line.replace('\n', ''))


    print(clauses)
    print(comments)