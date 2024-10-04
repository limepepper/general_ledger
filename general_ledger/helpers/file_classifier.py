

class FileClassifier:
    """
    Class to classify the file based on the file name and content
    """
    def __init__(self, file_name):
        self.file_name = file_name

    def is_general_ledger(self):
        return self.file_name == "general_ledger.csv"