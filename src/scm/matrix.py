import csv
from io import StringIO
from enum import Enum


def load_csv(input_file, col_act, col_pred, col_weight=None, delimiter=",", quotechar="\"", header=True):
    """
    Loads the actual, predicted and weight (if present) values from the CSV file as column lists.

    :param input_file: the CSV file to load actual/predicted labels from
    :type input_file: str
    :param col_act: the 0-based index of the column that contains the actual/ground truth labels
    :type col_act: int
    :param col_pred: the 0-based index of the column that contains the predicted labels
    :type col_pred: int
    :param col_weight: the 0-based index of the (optional) column containing the weights (0-1) for the predictions, default is None (ie a weight 1 is assumed)
    :type col_weight: int
    :param delimiter: the delimiter to use for the CSV file
    :type delimiter: str
    :param quotechar: the quote character to use for the CSV file
    :type quotechar: str
    :param header: whether the CSV file has a header
    :type header: bool
    :return: the actual, predicted and weight (None if not present) columns as lists
    :rtype: tuple
    """
    actual = []
    predicted = []
    weight = None if col_weight is None else []
    with open(input_file, "r") as inputf:
        reader = csv.reader(inputf, delimiter=delimiter, quotechar=quotechar)
        first = True
        for row in reader:
            if first and header:
                first = False
                continue
            actual.append(row[col_act - 1])
            predicted.append(row[col_pred - 1])
            if col_weight is not None:
                weight.append(row[col_weight - 1])
    return actual, predicted, weight


class MatrixType(Enum):
    """
    The types of confusion matrices that can be generated.

    Argparse integration taken from here:
    https://stackoverflow.com/a/55500795/4698227
    """
    COUNTS = 1
    PERCENTAGES = 2
    PERCENTAGES_PER_ROW = 3

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)

    @staticmethod
    def argparse(s):
        try:
            return MatrixType[s.upper()]
        except KeyError:
            return s


class MatrixResult(object):
    """
    Encapsulates the matrix result.
    """

    def __init__(self, data, max_decimals=3):
        """
        Initializes the container.

        :param data: the data, list of lists (row-based)
        :type data: list
        :param max_decimals: the maximum decimals after the decimal point to use in case of float values, -1 for no restrictions
        :type max_decimals: int
        """
        self.data = data
        self.max_decimals = max_decimals
        self.separator = " "

    def _cell_to_string(self, c):
        """
        Turns the cell into a string, takes the maximum number of decimals into account.

        :param c: the cell value to convert
        :type c: object
        :return: the converted value
        :rtype: str
        """
        if (self.max_decimals > -1) and isinstance(c, float):
            cell_format = "%." + str(self.max_decimals) + "f"
            result = str(cell_format % c)
        else:
            result = str(c)
        return result

    def to_raw(self):
        """
        Returns the underlying data as list of list (row-based).

        :return: the underlying data
        :rtype: list
        """
        return self.data

    def to_list(self):
        """
        Returns the matrix result as list of list (row-based).

        :return: the result
        :rtype: list
        """
        result = []
        for r in self.data:
            r_new = []
            for c in r:
                r_new.append(self._cell_to_string(c))
            result.append(r_new)
        return result

    def to_csv(self, output_file=None, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL):
        """
        Writes the matrix to a CSV file.

        :param output_file: the CSV file to create
        :type output_file: str
        :param delimiter: the cell delimiter to use (default: ,)
        :type delimiter: str
        :param quotechar: the quoting character to use (default: ")
        :type quotechar: str
        :param quoting: the type of quoting to perform, default is csv.QUOTE_MINIMAL
        :type quoting: int
        :return: None if output file provided, otherwise the generated CSV output
        :rtype: str
        """
        rows = self.to_list()
        if output_file is None:
            outputf = StringIO()
            writer = csv.writer(outputf, delimiter=delimiter, quotechar=quotechar, quoting=quoting)
            for r in rows:
                writer.writerow(r)
            return outputf.getvalue()
        else:
            with open(output_file, "w") as outputf:
                writer = csv.writer(outputf, delimiter=delimiter, quotechar=quotechar, quoting=quoting)
                for r in rows:
                    writer.writerow(r)
            return None

    def to_plaintext(self, output_file=None):
        """
        Turns the matrix result into plain text.

        :param output_file: the CSV file to create
        :type output_file: str
        :return: None if output file provided, otherwise the generated plain text output
        :rtype: str
        """
        widths = []
        num_rows = len(self.data)
        num_cols = 0
        for r in self.data:
            if len(widths) == 0:
                num_cols = len(r)
                for i in range(num_cols):
                    widths.append(0)
            for x in range(num_cols):
                widths[x] = max(widths[x], len(self._cell_to_string(r[x])))

        result = ""
        for y in range(num_rows):
            r = self.data[y]
            for x in range(num_cols):
                value = self._cell_to_string(r[x])
                if (x == 0) or (y == 0):
                    result += value.ljust(widths[x])
                else:
                    result += value.rjust(widths[x])
                if x < num_cols - 1:
                    result += self.separator
            result += "\n"

        if output_file is not None:
            with open(output_file, "w") as outputf:
                outputf.write(result)
            return None
        else:
            return result

    def __str__(self):
        return self.to_plaintext()


class ConfusionMatrix(object):
    """
    For generating a confusion matrix from actual and predicted labels.
    """

    def __init__(self, actual, predicted, weight=None, labels=None,
                 actual_prefix="a: ", predicted_prefix="p: ", corner="x"):
        """
        Initializes the matrix.

        :param actual: the list of actual labels
        :type actual: list
        :param predicted: the list of predicted labels
        :type predicted: list
        :param weight: the list of weights (0-1, float) associated with the predictions
        :type weight: list
        :param labels: the predefined list of labels to use, rather than determining from the actual/predicted labels (sorted)
        :type labels: list
        :param actual_prefix: the prefix to use in the matrix to denote actual cells (left column)
        :type actual_prefix: str
        :param predicted_prefix: the prefix to use in the matrix to denote predicted cells (top row)
        :type predicted_prefix: str
        :param corner: the text to use for the top-left corner
        :type corner: str
        """
        if len(actual) != len(predicted):
            raise Exception("Actual and predicted labels differ in length: %d != %d" % (len(actual), len(predicted)))
        self.actual = actual[:]
        self.actual_prefix = actual_prefix
        self.predicted = predicted[:]
        self.predicted_prefix = predicted_prefix
        self.corner = corner
        self.weight = None
        if weight is not None:
            if len(weight) != len(predicted):
                raise Exception("Weights and predicted labels differ in length: %d != %d" % (len(weight), len(predicted)))
            self.weight = weight[:]
        if labels is not None:
            self.labels = labels[:]
        else:
            all_labels = set()
            all_labels.update(actual)
            all_labels.update(predicted)
            self.labels = list(all_labels)
            self.labels.sort()

    def generate(self, matrix_type=MatrixType.COUNTS, max_decimals=3):
        """
        Generates the confusion matrix and returns it as list of list (row-based).

        :param matrix_type: the type of matrix to generate
        :type matrix_type: MatrixType
        :param max_decimals: the maximum decimals after the decimal point to use for float values, -1 for no restrictions
        :type max_decimals: int
        :return: the generated matrix
        :rtype: MatrixResult
        """
        result = []

        indices = dict()
        for i, l in enumerate(self.labels):
            indices[l] = i + 1

        # header
        row = [self.corner]
        for l in self.labels:
            row.append(self.predicted_prefix + l)
        result.append(row)

        # data
        for l in self.labels:
            row = [self.actual_prefix + l]
            for i in range(len(self.labels)):
                row.append(0)
            result.append(row)

        # fill in counts
        for i in range(len(self.actual)):
            index_act = indices[self.actual[i]]
            index_pred = indices[self.predicted[i]]
            weight = 1 if self.weight is None else self.weight[i]
            result[index_act][index_pred] += weight

        # post-process cells?
        if matrix_type == MatrixType.PERCENTAGES:
            sum = 0.0
            for y in range(len(self.labels)):
                for x in range(len(self.labels)):
                    sum += result[y+1][x+1]
            if sum > 0:
                for y in range(len(self.labels)):
                    for x in range(len(self.labels)):
                        result[y + 1][x + 1] /= sum
        elif matrix_type == MatrixType.PERCENTAGES_PER_ROW:
            for y in range(len(self.labels)):
                sum = 0
                for x in range(len(self.labels)):
                    sum += result[y+1][x+1]
                for x in range(len(self.labels)):
                    result[y + 1][x + 1] /= sum

        return MatrixResult(result, max_decimals=max_decimals)
