#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import List
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

from soup_files import File
from convert_stream.imagelib import ImageObject, LibraryImage
from convert_stream.models.models_pdf import ABCConvertPdf, ABCImageConvertPdf, LibraryPDF

from convert_stream.pdf_page import (
    PageDocumentPdf, MODULE_PYPDF2, MODULE_FITZ
)

if MODULE_PYPDF2:
    from PyPDF2 import PdfReader, PdfWriter, PageObject
if MODULE_FITZ:
    try:
        import fitz
    except:
        try:
            import pymupdf
        except:
            pass


#======================================================================#
# Converter PDFs em Imagens
#======================================================================#

class ImplementPdfToImageFitz(ABCConvertPdf):
    """
        Implementação para converter PDFs em Imagens (ImageObject) com o fitz.
    """

    def __init__(self, library_image: LibraryImage = LibraryImage.OPENCV, *, dpi: int = 200):
        super().__init__()
        self.library_image: LibraryImage = library_image
        self.dpi: int = dpi
        
    def from_page_bytes(self, page_bytes: bytes) -> ImageObject:
        """
            Recebe uma página PDF e converte os bytes da página PDF em ImagemObject
        """
        if not isinstance(page_bytes, bytes):
            raise ValueError(f'{__class__.__name__}\nUse: bytes, não {type(page_bytes)}')
        
        page_pdf: PageDocumentPdf = PageDocumentPdf.create_from_page_bytes(page_bytes, library=LibraryPDF.FITZ)
        pix: fitz.Pixmap = page_pdf.page.page.get_pixmap()
        return ImageObject.create_from_bytes(pix.tobytes(), library=self.library_image)
        
    def from_page_pdf(self, page: PageDocumentPdf) -> ImageObject:
        if page.current_library == LibraryPDF.FITZ:
            return self.__from_page_fitz(page.page.page)
        return self.from_page_bytes(page.to_bytes())
    
    def __from_page_fitz(self, page_fitz: fitz.Page) -> ImageObject:
        """Converte uma página PDF em imagem."""
        if not isinstance(page_fitz, fitz.Page):
            raise ValueError(f'{__class__.__name__}Use: fitz.Page(), não {type(page_fitz)}')
        pix: fitz.Pixmap = page_fitz.get_pixmap()
        return ImageObject.create_from_bytes(pix.tobytes(), library=self.library_image)
        
    def inner_images(self, page_bytes) -> List[ImageObject]:
        images_obj: List[ImageObject] = []
        doc = fitz.Document(stream=page_bytes, filetype="pdf")
        page: fitz.Page = doc[0]
        # Extrair imagens embutidas na página
        images_list = page.get_images(full=True)
        for img in images_list:
            try:
                xref = img[0]  # Referência do objeto da imagem
                base_image = doc.extract_image(xref)  # Extrair imagem
                image_bytes = base_image["image"]  # Bytes da imagem
                image_ext = base_image["ext"]  # Extensão (jpg, png, etc.)
            except Exception as e:
                print(e)
            else:
                img = ImageObject.create_from_bytes(image_bytes, library=self.library_image)
                images_obj.append(img)
        return images_obj
    
    
class ConvertPdfToImage(ABCConvertPdf):
    def __init__(self, *, library_pdf=LibraryPDF.FITZ, library_image=LibraryImage.OPENCV, dpi:int=200):
        super().__init__()
        self.library_pdf: LibraryPDF = library_pdf
        if self.library_pdf == LibraryPDF.FITZ:
            self.convert_pdf_to_images = ImplementPdfToImageFitz(library_image, dpi=dpi)
        elif self.library_pdf == LibraryPDF.PYPDF:
            raise NotImplementedError(f'{__class__.__name__}\nFuncionalidade não implementada para PYPDF2')
        elif self.library_pdf == LibraryPDF.CANVAS:
            raise NotImplementedError(f'{__class__.__name__}\nFuncionalidade não implementada para CANVAS')
        else:
            raise NotImplementedError(f'{__class__.__name__}\nLibraryPDF inválida: {type(self.library_pdf)}')
        
    def from_page_bytes(self, page_bytes: bytes) -> ImageObject:
        print(f'[+] {__class__.__name__}() Convertendo bytes pdf em imagem, aguarde')
        return self.convert_pdf_to_images.from_page_bytes(page_bytes)
    
    def from_page_pdf(self, page: PageDocumentPdf) -> ImageObject:
        print(f'[+] {__class__.__name__}() Convertendo página pdf em imagem, aguarde')
        return self.convert_pdf_to_images.from_page_pdf(page)
    
    def inner_images(self, page_bytes) -> List[ImageObject]:
        print(f'[+] {__class__.__name__}() Extraindo imagem de página PDF, aguarde')
        return self.convert_pdf_to_images.inner_images(page_bytes)
   
         
#########################################################################
# Converter IMAGEM para Arquivo ou página PDF.
#########################################################################

class ImplementImageConvertPdfFitz(ABCImageConvertPdf):
    def __init__(self, library_image):
        super().__init__(library_image)
        self._library_pdf = LibraryPDF.FITZ
        
    def from_image_file(self, file:File) -> PageDocumentPdf:
        # https://pymupdf.readthedocs.io/en/latest/recipes-images.html

        doc = fitz.Document()
        img: fitz.Document = fitz.Document(file.absolute())  # open pic as document
        rect = img[0].rect  # pic dimension
        pdfbytes = img.convert_to_pdf()  # make a PDF stream
        img.close()  # no longer needed
        imgPDF = fitz.Document("pdf", pdfbytes)  # open stream as PDF
        
        page = doc.new_page(
                    width = rect.width,  # new page with ...
                    height = rect.height # pic dimension
            )  
        page.show_pdf_page(rect, imgPDF, 0)  # image fills the page
        return PageDocumentPdf.create_from_page_fitz(page)
        
    def from_image(self, img:ImageObject) -> PageDocumentPdf:
        return self.from_image_bytes(img.to_bytes())
    
    def from_image_bytes(self, image_bytes:bytes) -> PageDocumentPdf:
        doc: fitz.Document = fitz.Document()
        
        # Criar um Pixmap diretamente dos bytes da imagem
        pix = fitz.Pixmap(BytesIO(image_bytes))

        # Criar uma nova página do tamanho da imagem
        page = doc.new_page(width=pix.width, height=pix.height)

        # Inserir a imagem na página
        page.insert_image(page.rect, pixmap=pix)
        return PageDocumentPdf.create_from_page_fitz(page)

# Implementação para converter imagem em PDF usando CANVAS.
class ImplementImageConvertPdfCanvas(ABCImageConvertPdf):
    """
        Implementação para converter uma imagem em página PDF (canvas).
    """
    def __init__(self, library_image):
        super().__init__(library_image)
        self._library_pdf = LibraryPDF.FITZ
        
    def from_image(self, img:ImageObject) -> PageDocumentPdf:
        # Cria um buffer de memória para o PDF
        buffer_pdf = BytesIO()

        # Cria o canvas associado ao buffer
        c:Canvas = canvas.Canvas(buffer_pdf, pagesize=letter)
        # Adicionar a imagem.
        c.drawImage(
                ImageReader(img.to_image_pil()), 
                0, 
                0, 
                width=letter[0], 
                height=letter[1], 
                preserveAspectRatio=True, 
                anchor='c'
            )
        c.showPage()
    
        # Finaliza o PDF
        c.save()

        # Move o ponteiro do buffer para o início
        buffer_pdf.seek(0)

        # Obtém os bytes do PDF
        pdf_bytes = buffer_pdf.getvalue()

        # Fecha o buffer (opcional, mas recomendado)
        buffer_pdf.close()
        
        # Gerar a página PDF
        return PageDocumentPdf.create_from_page_bytes(pdf_bytes, library=self._library_pdf)
        
    def from_image_file(self, file:File) -> PageDocumentPdf:
        """
            Converter um arquivo de imagem em páginas PDF
        """
        img = ImageObject.create_from_file(file, library=self.library_image)
        return self.from_image(img)
    
    def from_image_bytes(self, img_bytes:bytes) -> PageDocumentPdf:
        return self.from_image(
                ImageObject.create_from_bytes(img_bytes, library=self.library_image)
            )
        
# Implementação para converter imagem em PDF usando PIL.
class ImplementImageConvertToPdfPIL(ABCImageConvertPdf):
    """
        Implementação para converter uma imagem em página PDF (PIL).
    """
    def __init__(self, library_image):
        super().__init__(library_image)
        self._library_pdf:LibraryPDF = LibraryPDF.FITZ
        
    def from_image(self, img:ImageObject) -> PageDocumentPdf:
        img_pil = img.to_image_pil()
        buff = BytesIO()
        # Converter e salvar como PDF
        img_pil.save(buff, "PDF")
        pdf_bytes:bytes = buff.getvalue()
        buff.close()
        return PageDocumentPdf.create_from_page_bytes(pdf_bytes, library=self._library_pdf)
        
    def from_image_file(self, file:File) -> PageDocumentPdf:
        """
            Converter um arquivo de imagem em páginas PDF
        """
        # Carregar a imagem
        imagem:Image.Image = Image.open(file.absolute())
        buff = BytesIO()
        # Converter e salvar como PDF
        imagem.save(buff, "PDF")
        pdf_bytes:bytes = buff.getvalue()
        buff.close()
        return PageDocumentPdf.create_from_page_bytes(pdf_bytes, library=self._library_pdf)
    
    def from_image_bytes(self, img_bytes:bytes) -> PageDocumentPdf:
        img_pil = Image.open(BytesIO(img_bytes))
        buff_pdf = BytesIO()
        
        # Converter e salvar como PDF
        img_pil.save(buff_pdf, "PDF")
        pdf_bytes:bytes = buff_pdf.getvalue()
        buff_pdf.close()
        return PageDocumentPdf.create_from_page_bytes(pdf_bytes, library=self._library_pdf)
         
         
class ImageConvertPdf(ABCImageConvertPdf):
    """
        Converter Imagem em páginas PDF.
    """
    def __init__(self, convert_image_to_pdf:ABCImageConvertPdf):
        super().__init__(convert_image_to_pdf.library_image)
        self.convertImageToPdf:ABCImageConvertPdf = convert_image_to_pdf
        self._count:int = 0
            
    def from_image_file(self, file:File) -> PageDocumentPdf:
        self._count += 1
        print(f'{__class__.__name__}() Criando página PDF com arquivo de imagem {self._count}')
        return self.convertImageToPdf.from_image_file(file)
    
    def from_image(self, img:ImageObject) -> PageDocumentPdf:
        if not isinstance(img, ImageObject):
            raise ValueError(f'{__class__.__name__}\nUser: ImageObject(), não {type(img)}')
        self._count += 1
        print(f'{__class__.__name__}() Criando página PDF com objeto imagem {self._count}')
        return self.convertImageToPdf.from_image(img)
    
    def from_image_bytes(self, img_bytes) -> PageDocumentPdf:
        self._count += 1
        print(f'{__class__.__name__}() Criando página PDF com bytes de imagem {self._count}')
        return self.convertImageToPdf.from_image_bytes(img_bytes)
    
    @classmethod
    def create_from_pil(cls, library_image:LibraryImage=LibraryImage.OPENCV) -> ImageConvertPdf:
        img_convert:ABCImageConvertPdf = ImplementImageConvertToPdfPIL(library_image)
        return cls(img_convert)
    
    @classmethod
    def create_from_canvas(cls, library_image:LibraryImage=LibraryImage.OPENCV) -> ImageConvertPdf:
        img_convert:ABCImageConvertPdf = ImplementImageConvertPdfCanvas(library_image)
        return cls(img_convert)
    
    @classmethod
    def create_from_fitz(cls, library_image:LibraryImage=LibraryImage.OPENCV) -> ImageConvertPdf:
        img_convert:ABCImageConvertPdf = ImplementImageConvertPdfFitz(library_image)
        return cls(img_convert)


