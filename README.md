# simple-confusion-matrix
Python library for generating a confusion matrix from actual and predicted label.

## Functionality:

* load actual, predicted and weight columns from a CSV
* if no weight list (values: 0-1) is provided, a value of 1 is assumed;
  this value is used as weight for the counting then
* can generate three types of matrices:
  
  * counts 
  * percentages (all cells sum up to 1)
  * percentages per row (all cells of a row sum up to 1)
  
* can generate plain text or CSV output
* can write generated matrix back to a CSV file


## Installation

* create virtual environment

  ```commandline
  python3 -m venv venv
  ./venv/bin/pip install simple-confusion-matrix
  ```

## Command-line usage

You don't have to write code for using the library, you can just use the
`scm-generate` command-line utility:

```
usage: scm-generate [-h] -i FILE [-d DELIMITER] [-q CHAR] [-H] [-o FILE]
                    [-O FORMAT] [-a COL] [-A PREFIX] [-p COL] [-P PREFIX]
                    [-w COL] [-l LABELS] [-C CORNER] [-D NUM] [-t TYPE]

Generates a confusion matrix from a CSV file with actual/predicted label
columns.

optional arguments:
  -h, --help            show this help message and exit
  -i FILE, --input FILE
                        the CSV file to load the actual/predicted labels from
                        (default: None)
  -d DELIMITER, --delimiter DELIMITER
                        the column delimited in the CSV file (default: ,)
  -q CHAR, --quotechar CHAR
                        the quote character to use in the CSV file (default:
                        ")
  -H, --no_header       whether the CSV file has no header row (default: True)
  -o FILE, --output FILE
                        the optional CSV file to write the generated matrix to
                        (default: None)
  -O FORMAT, --output_format FORMAT
                        the output format to use when writing to the output
                        file (default: csv)
  -a COL, --actual COL  the 1-based column index for the actual/ground truth
                        labels (default: 1)
  -A PREFIX, --actual_prefix PREFIX
                        the prefix to use for the labels depicted in the
                        'actual' labels column (default: a: )
  -p COL, --predicted COL
                        the 1-based column index for the predicted labels
                        (default: 2)
  -P PREFIX, --predicted_prefix PREFIX
                        the prefix to use for the labels depicted in the
                        'predicted' labels row (default: p: )
  -w COL, --weight COL  the 1-based column index for the weight (0-1) of the
                        predicted label (default: None)
  -l LABELS, --labels LABELS
                        comma-separated list of predefined labels to use (eg
                        if not all labels present in CSV file) (default: None)
  -C CORNER, --corner CORNER
                        the text to print in the top-left corner (default: x)
  -D NUM, --max_decimals NUM
                        the maximum number of decimals after the decimal point
                        to use in case of float values like percentages
                        (default: 3)
  -t TYPE, --matrix_type TYPE
                        the type of matrix to generate (default: counts)
```

## Code examples

* Generating counts:

  ```python
  from scm.matrix import ConfusionMatrix, MatrixType
  
  actual = ["a", "a", "b", "b", "a", "b", "c", "c", "c", "c"]
  predicted = ["a", "c", "b", "a", "a", "b", "a", "b", "c", "c"]
  matrix = ConfusionMatrix(actual=actual, predicted=predicted)
  result = matrix.generate(matrix_type=MatrixType.COUNTS)
  print(result)
  ```
  Generates the following output:
  ```
  x    p: a p: b p: c
  a: a    2    0    1
  a: b    1    2    0
  a: c    1    1    2
  ```

* Using predefined label order:

  ```python
  from scm.matrix import ConfusionMatrix, MatrixType
  
  actual = ["a", "a", "b", "b", "a", "b", "c", "c", "c", "c"]
  predicted = ["a", "c", "b", "a", "a", "b", "a", "b", "c", "c"]
  labels = ["c", "b", "a"]
  matrix = ConfusionMatrix(actual=actual, predicted=predicted, labels=labels)
  result = matrix.generate(matrix_type=MatrixType.COUNTS)
  print(result)
  ```
  Generates the following output:
  ```
  x    p: c p: b p: a
  a: c    2    1    1
  a: b    0    2    1
  a: a    1    0    2
  ```

* Using global percentages:

  ```python
  from scm.matrix import ConfusionMatrix, MatrixType
  
  actual = ["a", "a", "b", "b", "a", "b", "c", "c", "c", "c"]
  predicted = ["a", "c", "b", "a", "a", "b", "a", "b", "c", "c"]
  matrix = ConfusionMatrix(actual=actual, predicted=predicted, labels=labels)
  result = matrix.generate(matrix_type=MatrixType.PERCENTAGES)
  print(result)
  ```
  Generates the following output:
  ```
  x    p: a  p: b  p: c 
  a: a 0.200 0.000 0.100
  a: b 0.100 0.200 0.000
  a: c 0.100 0.100 0.200
  ```

* Using row percentages (and only two decimals after decimal point):

  ```python
  from scm.matrix import ConfusionMatrix, MatrixType
  
  actual = ["a", "a", "b", "b", "a", "b", "c", "c", "c", "c"]
  predicted = ["a", "c", "b", "a", "a", "b", "a", "b", "c", "c"]
  matrix = ConfusionMatrix(actual=actual, predicted=predicted, labels=labels)
  result = matrix.generate(matrix_type=MatrixType.PERCENTAGES_PER_ROW, max_decimals=2)
  print(result)
  ```
  Generates the following output:
  ```
  x    p: a p: b p: c
  a: a 0.67 0.00 0.33
  a: b 0.33 0.67 0.00
  a: c 0.25 0.25 0.50
  ```

* Saving the matrix as CSV file:

  ```python
  from scm.matrix import ConfusionMatrix, MatrixType
  
  actual = ["a", "a", "b", "b", "a", "b", "c", "c", "c", "c"]
  predicted = ["a", "c", "b", "a", "a", "b", "a", "b", "c", "c"]
  matrix = ConfusionMatrix(actual=actual, predicted=predicted, labels=labels)
  result = matrix.generate(matrix_type=MatrixType.PERCENTAGES_PER_ROW, max_decimals=2)
  result.to_csv(output_file="/some/where/out.csv")
  ```

* Loading the actual and predicted values from a CSV file and writing the result back to a CSV:

  ```python
  from scm.matrix import ConfusionMatrix, MatrixType, load_csv
  
  actual, predicted, _ = load_csv("/some/where/in.csv", 1, 2)
  matrix = ConfusionMatrix(actual=actual, predicted=predicted)
  result = matrix.generate(matrix_type=MatrixType.PERCENTAGES_PER_ROW)
  result.to_csv(output_file="/some/where/out.csv")
  ```
