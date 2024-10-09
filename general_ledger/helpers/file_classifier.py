from django.db.models import TextChoices
from rich import inspect
from loguru import logger

class FileType(TextChoices):
    OFXV1 = "OFXV1", "OFX Version 1"
    OFXV2 = "OFXV2", "OFX Version 2"
    QFX = "QFX", "Quicken Financial Exchange"
    QIF = "QIF", "Quicken Interchange Format"
    CSV = "CSV", "Comma Separated Values"
    UNKNOWN_CSV = "UCSV", "Comma Separated Values"
    UNKNOWN = "UNKNOWN", "Unknown"

class FileClassifier:
    """
    Class to classify the file based on the file name and content
    """
    def __init__(self, file_path):
        self.file_path = file_path

    def get_mimetype(self):
        import magic
        file_type = magic.from_file(self.file_path, mime=True)
        #print(f'The file type is {file_type}')
        return file_type

    def classify(self):
        file_type = self.get_mimetype()

        if file_type == 'application/octet-stream':
            return FileType.UNKNOWN


        elif file_type == "text/xml":
            from ofxparse import OfxParser
            with open(self.file_path) as file:
                try:
                    ofx = OfxParser.parse(file)
                    #inspect(ofx)
                    return FileType.OFXV2
                except Exception as e:
                    # that didn't work. try somethig else
                    pass
        elif file_type == 'text/plain':

            with open(self.file_path) as file:
                from ofxparse import OfxParser
                try:
                    ofx = OfxParser.parse(file)
                    return FileType.OFXV1
                except Exception as e:
                    logger.trace("OFXV1 parse failed")
                    pass

            with open(self.file_path) as file:
                from qifparse.parser import QifParser
                try:
                    qif = QifParser.parse(file)
                    return FileType.QIF
                except Exception as e:
                    logger.trace("QIF parse failed {}", str(e))
                    pass

        elif file_type == 'text/csv':
            import pandas as pd

            try:
                df = pd.read_csv(self.file_path)
                logger.trace('File is a CSV.')
                return FileType.CSV
            except pd.errors.ParserError as e:
                logger.error('File is not a valid CSV. error: {}', str(e))
                raise Exception(f"File is not a valid CSV: {self.file_path} for reason {e}")




        return FileType.UNKNOWN
        #raise Exception(f"Unknown file type: {file_type} for file {self.file_path}")

