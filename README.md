# pyPDFlicenseschecker
`PDFlinenceschecker` is a Python module for checking the license and the credits of PDF documents and images within them.

The software try to extract the metadata from each image in the document from exif and XMP metadata. These are some of the information that you can check: 

|   pagenumber | image.name   |   width |   height | xmp   | iptcrights     | creatorstxt   | exif   | exifrights     | exifartist      |
|-------------:|:-------------|--------:|---------:|:------|:---------------|:--------------|:-------|:---------------|:----------------|
|            1 | Im15.jpg     |    3026 |     2016 | False |                |               | True   | CC BY NC SA    | Andrea Brugnoli |
|            1 | Im17.jpg     |    3026 |     2016 | True  | CC BY NC SA 72 |               | True   | CC BY NC SA 72 |                 |


## Installation 

The development branch can be installed using git: 

```
pip install git+https://github.com/giacomomarchioro/pyPDFlicenseschecker
```

#### Building the software

## Using the command line interface (CLI)

If the package has been install the `PDFlicenseschecker` can be used using the command: `PDFlicenseschecker`followed by the name (or the path if not in the current directory) of the the PDF file.  For instance : `PDFlicenseschecker mypdf.pdf`.

Otherwise you can use `python -m PDFlicenseschecker.CLI ` instead. 

The command line interface offers some options to export the data in a readable format.

```bash
usage: CLI.py [-h] [--html] [--csv] [--exportimages] [--silent] filename

'This is the command line interface of PDFlicenseschecker. This software helps you to identify the licenses and the creators
of a PDF document and the images inside the document. PDFlicenseschecker mypdf.pdf

positional arguments:
  filename        The filename or path of the PDF.

optional arguments:
  -h, --help      shows this help message and exit
  --html          saves an HTML report of the results.
  --csv           saves a CSV file containing the results of the images analysis.
  --exportimages  saves all the images of the document to a folder.
  --silent        avoids printing to terminal the metadata.
```

## Using the application programming interface (API)

You can also import the package as a module: 
 
```python
import PDFlicenseschecker
# load the ProvaLibreOffice.pdf file
myanalysis =  PDFlicenseschecker.PDFLC('ProvaLibreOffice.pdf') 
# prints all the metadata
myanalysis.printMetadata()
# prints only the metadata of the PDF document 
myanalysis.printPDFMetadata()
# prints only the images metadataformatting the table using pipes
myanalysis.printImagesMetadata(tablefmt="pipe")
# variable were the images metadata are stored
myanalysis.imagesmetadata
# variable were the PDF document metadata are stored
myanalysis.PDFmetadata
# export the PDF images into a folder
myanalysis.readPDF(saveimages=True)
# the output foldername or path
myanalysis.foldername
# export the images  metadata into a csv file
 myanalysis.saveCSVreport()
# export all the metadata in a easy to read HTML document
 myanalysis.saveHTMLreport()

```


