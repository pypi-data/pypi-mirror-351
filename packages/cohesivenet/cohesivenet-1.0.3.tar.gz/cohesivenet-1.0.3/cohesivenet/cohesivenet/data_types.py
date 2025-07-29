from typing import Tuple, List
from collections import namedtuple

ExceptionResult = namedtuple("ExceptionResult", "exception client")
OperationResult = namedtuple("OperationResult", "result client")
BulkOperationResult = Tuple[List[OperationResult], List[ExceptionResult]]
