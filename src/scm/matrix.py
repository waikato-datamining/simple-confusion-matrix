from enum import Enum


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


class ConfusionMatrix(object):
    """
    For generating a confusion matrix from actual and predicted labels.
    """

    def __init__(self, actual, predicted, prob=None, labels=None, actual_prefix="a: ", predicted_prefix="p: "):
        """
        Initializes the matrix.

        :param actual: the list of actual labels
        :type actual: list
        :param predicted: the list of predicted labels
        :type predicted: list
        :param prob: the list of probabilities (0-1, float) associated with the predictions
        :type prob: list
        :param labels: the predefined list of labels to use, rather than determining from the actual/predicted labels (sorted)
        :type labels: list
        :param actual_prefix: the prefix to use in the matrix to denote actual cells
        :type actual_prefix: str
        :param predicted_prefix: the prefix to use in the matrix to denote predicted cells
        :type predicted_prefix: str
        """
        if len(actual) != len(predicted):
            raise Exception("Actual and predicted labels differ in length: %d != %d" % (len(actual), len(predicted)))
        self.actual = actual[:]
        self.actual_prefix = actual_prefix
        self.predicted = predicted[:]
        self.predicted_prefix = predicted_prefix
        self.prob = None
        if prob is not None:
            if len(prob) != len(predicted):
                raise Exception("Probabilities and predicted labels differ in length: %d != %d" % (len(prob), len(predicted)))
            self.prob = prob[:]
        if labels is not None:
            self.labels = labels[:]
        else:
            all_labels = set()
            all_labels.update(actual)
            all_labels.update(predicted)
            self.labels = list(all_labels)
            self.labels.sort()

    def generate(self, matrix_type=MatrixType.COUNTS):
        """
        Generates the confusion matrix and returns it as list of list (row-based).

        :param matrix_type: the type of matrix to generate
        :type matrix_type: MatrixType
        :return: the generated matrix
        :rtype: list
        """
        result = []

        indices = dict()
        for i, l in enumerate(self.labels):
            indices[l] = i + 1

        # header
        row = ["x"]
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
            weight = 1 if self.prob is None else self.prob[i]
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

        return result
