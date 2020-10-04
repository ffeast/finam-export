__all__ = ['FinamExportError',
           'FinamDownloadError',
           'FinamThrottlingError',
           'FinamParsingError',
           'FinamObjectNotFoundError',
           'FinamTooLongTimeframeError',
           'FinamAlreadyInProgressError'
           ]


class FinamExportError(Exception):
    pass


class FinamDownloadError(FinamExportError):
    pass


class FinamThrottlingError(FinamExportError):
    pass


class FinamParsingError(FinamExportError):
    pass


class FinamObjectNotFoundError(FinamExportError):
    pass


class FinamTooLongTimeframeError(FinamExportError):
    pass


class FinamAlreadyInProgressError(FinamExportError):
    pass
