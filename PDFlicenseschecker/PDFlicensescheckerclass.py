from PyPDF2 import PdfReader
from PIL import Image, ExifTags
import io
import xml.etree.cElementTree as ET
import os
# for printing the table
from tabulate import tabulate
# HTML Report
from xml.dom.minidom import getDOMImplementation, Document
# CSV Report
import csv

class PDFLC():
    def __init__(self,filename,saveimages=False):
        """Instantiate a PDFlicenseschecker object.

        Args:
            filename (str): The name of the PDF file or its path.
            saveimages (bool, optional): If True the images of the PDF file will
            be exported into a folder in the same directory of the file. Defaults to False.

        Returns:
            Tuple: A list with all the metadata of the images and a dict with the metadata of the PDF.
        """
        super().__init__()
        self.filename = filename
        self.PDFmetadata = None
        self.imagesmetadata = None 
        self.foldername = filename.split(".")[0]
        self.header = ["pagenumber", "image.name", "width", "height", "xmp",
                    "iptcrights", "creatorstxt", "exif", "exifrights", "exifartist"]
        self.saveimages = saveimages
        self.readPDF(filename=filename)


    def readPDF(self,filename=None,saveimages=False):
        """Read the PDF and generate a list of the metadata.

        Args:
            filename (str): The path of the PDF file.

        Returns:
            list : a list of list with the image matadata
            meta : the PDF document metadata
        """
        if filename is None:
            if self.filename is None:
                raise ValueError("Provide a valid filename.")
            filename = self.filename
        # in case the images were not saved before
        self.saveimages = True if saveimages else self.saveimages
        if self.saveimages and not os.path.exists(self.foldername):
            os.mkdir(self.foldername)
        reader = PdfReader(filename)
        # read the metadata of the PDF file.
        meta = reader.metadata
        table = []
        for pagenum, page in enumerate(reader.pages, 1):
            for image in page.images:
                xmp = False
                exif = False
                iptcrights = None
                exifrights = None
                creators_txt = None
                exifartist = None
                creators_joined = None
                # find the begining and the end of the xpacket.
                begin = image.data.find(b"<?xpacket begin")
                end = image.data.find(b"<?xpacket end")
                if begin != -1 and end != -1:
                    xmp = True
                    # exctract the metadata
                    metadata = image.data[begin:end]
                    # create a DOM from the metadata string
                    doc = ET.fromstring(metadata)
                    # find the creator
                    creators = doc.findall(
                        './/{http://purl.org/dc/elements/1.1/}creator')
                    creators_txt = []
                    for i in creators:
                        for k in i:
                            # this in the case we have multiple creators
                            if k.tag == "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Seq":
                                for j in k:
                                    creators_txt.append(j.text)
                        else:
                            creators_txt.append(i.text)
                    creators_joined = ";".join(filter(None, creators_txt))
                    rights = doc.findall(
                        './/{http://purl.org/dc/elements/1.1/}rights')
                    rights_txt = []
                    for i in rights:
                        for k in i:
                            # in case we have multiple rights
                            if k.tag == '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Alt':
                                for j in k:
                                    rights_txt.append(j.text)
                        else:
                            rights_txt.append(i.text)
                    iptcrights = "".join(filter(None, rights_txt))

                # the exif metadata is retrieved using PIL.
                imagex = Image.open(io.BytesIO(image.data))
                if self.saveimages:
                    imagex.save(os.path.join(self.foldername,
                                "-".join(map(str, (pagenum, image.name)))))
                img_exif = imagex.getexif()

                if img_exif is not None:
                    exif = True
                    for key, val in img_exif.items():
                        if key == 33432:  # rights
                            exifrights = val
                        if key == 315:  # artist
                            exifartist = val

                table.append([pagenum, image.name, imagex.width, imagex.height,
                            xmp, iptcrights, creators_joined, exif, exifrights, exifartist])
            self.imagesmetadata = table
            self.PDFmetadata = meta
            return table, meta

    def printImagesMetadata(self,**kwargs):
        """Print the relevant images metadata.
        """         
        print("***************")
        print("IMAGES METADATA:")
        print("***************")
        print(tabulate(self.imagesmetadata, headers=self.header,**kwargs))
    
    def printPDFMetadata(self,**kwargs):
        """Print the PDF document metadata.
        """     
        print("**********************")
        print("PDF DOCUMENT METADATA:")
        print("**********************")
        print(tabulate(self.PDFmetadata.items(),**kwargs))

    def printMetadata(self,**kwargs):
        """Print the relevant metadata of the PDF document and the images inside 
        the PDF.
        """
        self.printPDFMetadata(**kwargs)
        self.printImagesMetadata(**kwargs) 

    def generateHTMLDOM(self):
        """Generate an HTML DOM containing all the metadata information.

        Returns:
            _type_: A DOM of the HTML in XML.
        """
        impl = getDOMImplementation()
        dt = impl.createDocumentType(
            "html",
            "-//W3C//DTD XHTML 1.0 Strict//EN",
            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd",
        )
        dom = impl.createDocument("http://www.w3.org/1999/xhtml", "html", dt)
        html = dom.documentElement
        h1 = dom.createElement("h1")
        h1.appendChild(dom.createTextNode("Report copyright"))
        html.appendChild(h1)
        h2 = dom.createElement("h2")
        h2.appendChild(dom.createTextNode("Informazioni file PDF"))
        html.appendChild(h2)
        # HTML metadata table
        mtable = dom.createElement("table")
        mbody = dom.createElement("tbody")
        for i in self.PDFmetadata:
            trg = dom.createElement("tr")
            mbody.appendChild(trg)
            tdk = dom.createElement("td")
            trg.appendChild(tdk)
            tdk.appendChild(dom.createTextNode(str(i)))
        
            tdv = dom.createElement("td")
            trg.appendChild(tdv) 
            trg.appendChild(dom.createTextNode(str(self.PDFmetadata[i])))
            mbody.appendChild(trg) 

        mtable.appendChild(mbody)
        html.appendChild(mtable)

        htable = dom.createElement("table")
        tbody = dom.createElement("tbody")

        h2i = dom.createElement("h2")
        h2i.appendChild(dom.createTextNode("Informazioni immagini nel PDF"))
        html.appendChild(h2i)
        for row in self.imagesmetadata:
            ##
            ## Elemento
            ##
            tr = dom.createElement("tr")
            tr.setAttribute("align","right")
            tbody.appendChild(tr)
            # image td
            tdimg = dom.createElement("td")
            #tr.setAttribute("align","right")
            tr.appendChild(tdimg)
            # <img style="display: inline;" id="imgPreview" width=300 src="/Users/univr/Documents/PDFimagelicencechecker/testimmagini/Im1.jpg"
            img = dom.createElement("img")
            img.setAttribute("stype","dislpay: inline;")
            #img.setAttribute("src","/Users/univr/Documents/PDFimagelicencechecker/%s/%s"%(foldern,"-".join(map(str,row[:2]))))
            img.setAttribute("src","-".join(map(str,row[:2])))
            img.setAttribute("height","200")
            tdimg.appendChild(img)

            # subtable td
            tdt = dom.createElement("td")
            #tr.setAttribute("align","right")
            tr.appendChild(tdt)
            stable = dom.createElement("table")
            stbody = dom.createElement("tbody")
            ## METADATO
            for ind,i in enumerate(self.header):
                trs = dom.createElement("tr")
                trs.setAttribute("align","right")
                stbody.appendChild(trs)
                # label
                mtd  = dom.createElement("td")
                mtd.appendChild(dom.createTextNode(i))
                trs.appendChild(mtd)
                # value
                mtdx  = dom.createElement("td")
                mtdx.appendChild(dom.createTextNode(str(row[ind])))
                trs.appendChild(mtdx)
                stbody.appendChild(trs)    
            stable.appendChild(stbody)
            tr.appendChild(stable)

        htable.appendChild(tbody)
        html.appendChild(htable)
        dom.toxml()
        return dom

    def saveHTMLreport(self):
        """Save a report in an HTML file inside a folder with the same name of
        the PDF file.
        """
        if not self.saveimages:
            self.readPDF(self.filename,saveimages=True)
        with open(os.path.join(self.foldername,'report.html'),'w') as f: 
            dom = self.generateHTMLDOM()
            dom.writexml(f)

    def saveCSVreport(self):
        """Save a CSV file containing all the relevant image metadata inside a
        folder with the same name of the PDF file.
        """
        if not os.path.exists(self.foldername):
            os.mkdir(self.foldername)
        with open(os.path.join(self.foldername,'report.csv'),'w') as f: 
            cw = csv.writer(f)
            cw.writerow(self.header)
            cw.writerows(self.imagesmetadata)
