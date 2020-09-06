"""
Exceptions which match errors raised by the Vuforia Cloud Recognition Web APIs.
"""


from vws.exceptions.base_exceptions import CloudRecoException


class MatchProcessing(CloudRecoException):
    """
    Exception raised when a query is made with an image which matches a target
    which is processing or has recently been deleted.
    """


class MaxNumResultsOutOfRange(CloudRecoException):
    """
    Exception raised when the ``max_num_results`` given to the Cloud
    Recognition Web API query endpoint is out of range.
    """
