class InsufficientFundsException(Exception):
    def __init__(self, *args: object) -> None:
        if args:
            self.message = args[0]
            self.missing_funds = args[1]
        else:
            self.message = None
            self.missing_funds = None

    def __str__(self) -> str:
        if self.message:
            return f'InsufficientFundsException, {self.message}'
        else:
            return 'InsufficientFundsException raised'