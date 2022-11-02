import argparse
from .PDFlicensescheckerclass import PDFLC

def RunCLI():
    description = """
    'This is the command line interface of PDFlicenseschecker.
    This software helps you to identify the licenses and the creators of a PDF
    document and the images inside the document. 

    PDFlicenseschecker mypdf.pdf

    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('filename',
                        help="The filename or path of the PDF.")
    parser.add_argument('--html',
                        action='store_true',
                        required=False,
                        help="saves an HTML report of the results.")
    parser.add_argument('--csv',
                        action='store_true',
                        required=False,
                        help="saves a CSV file containing the results of the images analysis.")

    parser.add_argument('--exportimages',
                        action='store_true',
                        required=False,
                        help="saves all the images of the document to a folder.")

    parser.add_argument('--silent',
                        action='store_true',
                        required=False,
                        help="avoids printing to terminal the metadata.")

    args = parser.parse_args()
    myAnalysis = PDFLC(filename=args.filename,saveimages=args.exportimages)
    if not args.silent:
        myAnalysis.printMetadata()
    if args.csv:
        myAnalysis.saveCSVreport()
    if args.html:
        myAnalysis.saveHTMLreport()
        
if __name__ == '__main__':
    RunCLI()
