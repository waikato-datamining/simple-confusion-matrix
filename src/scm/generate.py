import argparse
import csv
import traceback
from enum import Enum
from scm.matrix import ConfusionMatrix, MatrixType, load_csv


class OutputFormat(Enum):
    """
    The types of output formats.

    Argparse integration taken from here:
    https://stackoverflow.com/a/55500795/4698227
    """
    CSV = 1
    PLAINTEXT = 2

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)

    @staticmethod
    def argparse(s):
        try:
            return OutputFormat[s.upper()]
        except KeyError:
            return s


def generate(input_file, output_file, col_act, col_pred, col_weight=None, matrix_type=MatrixType.COUNTS,
             delimiter=",", quotechar="\"", header=True, labels=None, prefix_act="a: ", prefix_pred="p: ", corner="x",
             output_format=OutputFormat.CSV, max_decimals=3):
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
    :param col_weight: the 1-based index of the (optional) column containing the weight (0-1) for the predictions, default is None
    :type col_weight: int
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
    :param prefix_act: the prefix to use for the the actual cells (left column)
    :type prefix_act: str
    :param prefix_pred: the prefix to use for the the predicted cells (top row)
    :type prefix_pred: str
    :param corner: the text to print in the top-left corner
    :type corner: str
    :param output_format: the format to use when writing to a file (csv|plaintext)
    :type output_format: OutputFormat
    :param max_decimals: the maximum decimals after the decimal point to use in case of float values, -1 for no restrictions
    :type max_decimals: int
    """

    actual, predicted, weight = load_csv(input_file, col_act, col_pred, col_weight=col_weight,
                                         delimiter=delimiter, quotechar=quotechar, header=header)
    matrix = ConfusionMatrix(actual, predicted, weight=weight, labels=labels,
                             actual_prefix=prefix_act, predicted_prefix=prefix_pred, corner=corner)
    result = matrix.generate(matrix_type=matrix_type, max_decimals=max_decimals)

    if output_file is None:
        print(result.to_plaintext())
    else:
        with open(output_file, "w") as outputf:
            if output_format == OutputFormat.CSV:
                result.to_csv(output_file, delimiter=delimiter, quotechar=quotechar, quoting=csv.QUOTE_MINIMAL)
            elif output_format == OutputFormat.PLAINTEXT:
                outputf.write(result.to_plaintext())
            else:
                raise Exception("Unhandled output format: " + str(output_format))


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
    parser.add_argument("-O", "--output_format", dest="output_format", metavar="FORMAT", required=False, default=OutputFormat.CSV, choices=list(OutputFormat), type=OutputFormat.argparse, help="the output format to use when writing to the output file")
    parser.add_argument("-a", "--actual", dest="col_act", metavar="COL", required=False, default=1, type=int, help="the 1-based column index for the actual/ground truth labels")
    parser.add_argument("-A", "--actual_prefix", dest="prefix_act", metavar="PREFIX", required=False, default="a: ", type=str, help="the prefix to use for the labels depicted in the 'actual' labels column")
    parser.add_argument("-p", "--predicted", dest="col_pred", metavar="COL", required=False, default=2, type=int, help="the 1-based column index for the predicted labels")
    parser.add_argument("-P", "--predicted_prefix", dest="prefix_pred", metavar="PREFIX", required=False, default="p: ", type=str, help="the prefix to use for the labels depicted in the 'predicted' labels row")
    parser.add_argument("-w", "--weight", dest="col_weight", metavar="COL", required=False, default=None, type=int, help="the 1-based column index for the weight (0-1) of the predicted label")
    parser.add_argument("-l", "--labels", dest="labels", metavar="LABELS", required=False, default=None, type=str, help="comma-separated list of predefined labels to use (eg if not all labels present in CSV file)")
    parser.add_argument("-C", "--corner", dest="corner", metavar="CORNER", required=False, default="x", type=str, help="the text to print in the top-left corner")
    parser.add_argument("-D", "--max_decimals", dest="max_decimals", metavar="NUM", required=False, default=3, type=int, help="the maximum number of decimals after the decimal point to use in case of float values like percentages")
    parser.add_argument("-t", "--matrix_type", dest="matrix_type", metavar="TYPE", required=False, default=MatrixType.COUNTS, choices=list(MatrixType), type=MatrixType.argparse, help="the type of matrix to generate")
    parsed = parser.parse_args(args=args)
    labels = None if parsed.labels is None else parsed.labels.split(",")
    generate(parsed.input_file, parsed.output_file, parsed.col_act, parsed.col_pred,
             col_weight=parsed.col_weight, matrix_type=parsed.matrix_type,
             delimiter=parsed.delimiter, quotechar=parsed.quotechar, header=parsed.header, labels=labels,
             prefix_act=parsed.prefix_act, prefix_pred=parsed.prefix_pred, corner=parsed.corner,
             output_format=parsed.output_format, max_decimals=parsed.max_decimals)


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

