class UnhandledValueError(ValueError):
    def __init__(self, value):
        self.message = f'Unhandled value: {value} ({type(value).__name__})'
        super().__init__(self.message)
