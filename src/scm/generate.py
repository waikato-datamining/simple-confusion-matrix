import argparse
import csv
import traceback
from scm.matrix import ConfusionMatrix, MatrixType


def generate(input_file, output_file, col_act, col_pred, col_prob=None, matrix_type=MatrixType.COUNTS,
             delimiter=",", quotechar="\"", header=True, labels=None):
    """
    Generates the confusion matrix from the CSV file. Outputs the result on stdout if no output file provided.

    :param input_file: the CSV file to load actual/predicted labels from
    :type input_file: str
    :param output_file: the (optional) CSV file to write the matrix to
    :type output_file: str
    :param col_act: the 1-based index of the column that contains the actual/ground truth labels
    :type col_act: int
    :param col_pred: the 1-based index of the column that contains the predicted labels
    :type col_pred: int
    :param col_prob: the 1-based index of the (optional) column containing the probability (0-1) for the predictions, default is None
    :type col_prob: int
    :param matrix_type: the type of matrix to generate
    :type matrix_type: MatrixType
    :param delimiter: the delimiter to use for the CSV file
    :type delimiter: str
    :param quotechar: the quote character to use for the CSV file
    :type quotechar: str
    :param header: whether the CSV file has a header
    :type header: bool
    :param labels: the (optional) list of predefined labels to use
    :type labels: list
    """

    # read data
    act = []
    pred = []
    prob = None if col_prob is None else []
    with open(input_file, "r") as inputf:
        reader = csv.reader(inputf, delimiter=delimiter, quotechar=quotechar)
        first = True
        for row in reader:
            if first and header:
                first = False
                continue
            act.append(row[col_act - 1])
            pred.append(row[col_pred - 1])
            if col_prob is not None:
                prob.append(row[col_prob - 1])

    matrix = ConfusionMatrix(act, pred, prob=prob, labels=labels)
    result = matrix.generate(matrix_type=matrix_type)

    if output_file is None:
        for r in result:
            print(r)
    else:
        with open(output_file, "w") as outputf:
            writer = csv.writer(outputf, delimiter=delimiter, quotechar=quotechar, quoting=csv.QUOTE_MINIMAL)
            for r in result:
                writer.writerow(r)


def main(args=None):
    """
    Performs the matrix generation.
    Use -h to see all options.

    :param args: the command-line arguments to use, uses sys.argv if None
    :type args: list
    """
    parser = argparse.ArgumentParser(
        description='Generates a confusion matrix from a CSV file with actual/predicted label columns.',
        prog="scm-generate",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input", dest="input_file", metavar="FILE", required=True, help="the CSV file to load the actual/predicted labels from")
    parser.add_argument("-d", "--delimiter", dest="delimiter", metavar="DELIMITER", required=False, default=",", help="the column delimited in the CSV file")
    parser.add_argument("-q", "--quotechar", dest="quotechar", metavar="CHAR", required=False, default="\"", help="the quote character to use in the CSV file")
    parser.add_argument("-H", "--no_header", action="store_false", dest="header", help="whether the CSV file has no header row")
    parser.add_argument("-o", "--output", dest="output_file", metavar="FILE", required=False, help="the optional CSV file to write the generated matrix to")
    parser.add_argument("-a", "--actual", dest="col_act", metavar="COL", required=False, default=1, type=int, help="the 1-based column index for the actual/ground truth labels")
    parser.add_argument("-p", "--predicted", dest="col_pred", metavar="COL", required=False, default=2, type=int, help="the 1-based column index for the predicted labels")
    parser.add_argument("-P", "--probability", dest="col_prob", metavar="COL", required=False, default=None, type=int, help="the 1-based column index for probability (0-1) of the predicted label")
    parser.add_argument("-l", "--labels", dest="labels", metavar="LABELS", required=False, default=None, type=str, help="comma-separated list of predefined labels to use (eg if not all labels present in CSV file)")
    parser.add_argument("-t", "--matrix_type", dest="matrix_type", metavar="TYPE", required=False, default=MatrixType.COUNTS, choices=list(MatrixType), type=MatrixType.argparse, help="the type of matrix to generate")
    # TODO: actual/predicted prefix
    parsed = parser.parse_args(args=args)
    labels = None if parsed.labels is None else parsed.labels.split(",")
    generate(parsed.input_file, parsed.output_file, parsed.col_act, parsed.col_pred,
             col_prob=parsed.col_prob, matrix_type=parsed.matrix_type,
             delimiter=parsed.delimiter, quotechar=parsed.quotechar, header=parsed.header, labels=labels)


def sys_main():
    """
    Runs the main function using the system cli arguments, and
    returns a system error code.

    :return: 0 for success, 1 for failure.
    :rtype: int
    """

    try:
        main()
        return 0
    except Exception:
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc())

