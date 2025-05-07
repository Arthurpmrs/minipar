class ReturnInterruption(Exception):
    def __init__(self, objectValue=None, *args):
        self.objectValue = objectValue
        super().__init__(*args)

class ContinueInterruption(Exception):
    pass

class BreakInterruption(Exception):
    pass