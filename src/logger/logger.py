class Logger:
    def __init__(self, verbose):
        self.verbose = verbose

    def log(self, message, override_verbose=False):
        if self.verbose or override_verbose:
            print(message)
