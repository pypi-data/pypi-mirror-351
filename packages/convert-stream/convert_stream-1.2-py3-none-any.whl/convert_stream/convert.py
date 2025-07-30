#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import List
import pandas

from convert_stream.models import ABCDocumentStream, LibraryImage, LibraryPDF
from convert_stream.imagelib import ImageObject
from convert_stream.models.progress_bar import ProgressBarAdapter, ProgressBarSimple
from convert_stream.pdf_page import PageDocumentPdf
from convert_stream.pdf_document import DocumentPdf
from convert_stream.pdf_convert import ConvertPdfToImage, ImageConvertPdf
from soup_files import File, Directory
 
#==================================================================#
# PDF
#==================================================================#

class PdfStream(ABCDocumentStream):
    """
        Objeto para manipular a exportação de dados PDF    
    """

    def __init__(
                    self, *,
                    library_pdf: LibraryPDF = LibraryPDF.FITZ,
                    library_image: LibraryImage = LibraryImage.OPENCV,
                    progress_bar: ProgressBarAdapter = ProgressBarAdapter(ProgressBarSimple())
            ):
        super().__init__(library_pdf=library_pdf, library_image=library_image, progress_bar=progress_bar)
        self.num_pages: int = 0
        self.library_pdf: LibraryPDF = library_pdf
        self.library_image: LibraryImage = library_image
        self.document: DocumentPdf = DocumentPdf(self.library_pdf, progress_bar=progress_bar)
        self.convertPdfToImages: ConvertPdfToImage = ConvertPdfToImage(library_image=library_image)
        
        if self.library_pdf == LibraryPDF.CANVAS:
            self.imagesToPdf:ImageConvertPdf = ImageConvertPdf.create_from_canvas(self.library_image)
        elif self.library_pdf == LibraryPDF.PILPDF:
            self.imagesToPdf:ImageConvertPdf = ImageConvertPdf.create_from_pil(LibraryImage.PIL)
        else:
            self.imagesToPdf:ImageConvertPdf = ImageConvertPdf.create_from_fitz(self.library_image)
        
    @property
    def num_pages(self) -> int:
        return self.document.num_pages
    
    @num_pages.setter
    def num_pages(self, num:int):
        pass
        
    @property
    def pages(self) -> List[PageDocumentPdf]:
        return self.document.pages
    
    @pages.setter
    def pages(self, new:List[PageDocumentPdf]):
        if not isinstance(new, list):
            return
        self.document.clear()
        for pg in new:
            self.add_page(pg)
        
    def is_null(self) -> bool:
        return self.document.is_null()
    
    def clear(self):
        self.document.clear()
        
    def add_page(self, p:PageDocumentPdf):
        if not isinstance(p, PageDocumentPdf):
            return
        self.document.add_page(p)
            
    def add_pages(self, pages: List[PageDocumentPdf]):
        if not isinstance(pages, list):
            print(f'{__class__.__name__} Erro: Use lista de PageDocumentPdf, não {type(pages)}')
            return
        max_num: int = len(pages)
        for num, p in enumerate(pages):
            self.progress_bar.update(
                ((num+1)/max_num) * 100,
                f'Adicionando página: [{num+1} de {max_num}]'
            )
            self.add_page(p)

    def add_page_pdf_bytes(self, bt: bytes):
        _page = PageDocumentPdf.create_from_page_bytes(bt, library=self.library_pdf)
        self.add_page(_page)
            
    def add_file_pdf(self, f: File):
        doc: DocumentPdf = DocumentPdf(self.library_pdf)
        doc.add_file_pdf(f)
        self.add_pages(doc.pages)
        
    def add_files_pdf(self, files: List[File]):
        for f in files:
            self.add_file_pdf(f)
            
    def add_document(self, doc:DocumentPdf):
        self.add_pages(doc.pages)
        
    def add_image(self, image: ImageObject):
        pg: PageDocumentPdf = self.imagesToPdf.from_image(image)
        self.add_page(pg)
        
    def to_file_pdf(self, f: File):
        if self.is_null():
            print(
                f'{__class__.__name__} Nenhuma página foi adiconada, adicione páginas ao documento para prosseguir!'
            )
        docpdf: DocumentPdf = DocumentPdf(self.library_pdf, progress_bar=self.progress_bar)
        docpdf.add_pages(self.pages)
        docpdf.to_file_pdf(f)
        
    def to_files_pdf(self, outdir: Directory, *, prefix='pag'):
        if self.is_null():
            print(
                f'{__class__.__name__} Nenhuma página foi adiconada, adicione páginas ao documento para prosseguir!'
            )
            
        outdir.mkdir()
        _document:DocumentPdf = DocumentPdf(self.library_pdf)
        for num, p in enumerate(self.pages):
            filename:str = f'{prefix}-{num+1}.pdf'
            print(f'Exportando página: {p.page_number} de {self.num_pages} | [{filename}]')
            _document.add_page(p)
            _document.to_file_pdf(outdir.join_file(filename))
            _document.clear()
            
    def to_files_image(self, d:Directory, *, prefix:str='página-para-imagem'):
        """
            Exporta cada página PDF como um arquivo de imagem.
        """
        d.mkdir()
        for num, page in enumerate(self.pages):
            filename = f'{prefix}-{page.page_number}.png'
            img = self.convertPdfToImages.from_page_pdf(page)
            print(f'Exportando página PDF para imagem: [{num+1} de {self.num_pages}] {filename}')
            img.to_file(d.join_file(filename))
            
    def to_images(self) -> List[ImageObject]:
        images_obj:List[ImageObject] = []
        for page in self.pages:
            images_obj.append(self.convertPdfToImages.from_page_pdf(page))
        return images_obj
    
    def to_document(self) -> DocumentPdf:
        doc = DocumentPdf(self.library_pdf)
        doc.add_pages(self.pages)
        return doc
    
    def inner_images(self) -> List[ImageObject]:
        inner_images:List[ImageObject] = []
        for p in self.pages:
            inner_images.extend(
                self.convertPdfToImages.inner_images(p.to_bytes())
            )
        return inner_images
    
    def inner_images_to_files(self, d:Directory, prefix:str='página-para-imagens') -> None:
        """
            Salva todas as imagens presentes nas páginas em arquivos de imagem.
        """
        outdir = d #.concat(f'{num+1}')
        outdir.mkdir()
        for num, page in enumerate(self.pages):
            images = self.convertPdfToImages.inner_images(page.to_bytes())
            if len(images) < 1:
                continue
            for n, img in enumerate(images):
                filename = f'{prefix}-{page.page_number}-img-{n+1}.png' 
                img.to_file(outdir.join_file(filename))
    
    def set_paisagem(self):
        for page in self.pages:
            page.set_paisagem()
             
#==================================================================#
# Imagens
#==================================================================#

class ImageStream(object):
    def __init__(self, *, library_image=LibraryImage.OPENCV, library_pdf=LibraryPDF.PILPDF):
        self.__images:List[ImageObject] = []
        self.num_images:int = len(self.__images)
        self.library_image:LibraryImage = library_image
        self.library_pdf:LibraryPDF = library_pdf
        # Objeto para converter IMAGEM em pdf.
        if library_pdf == LibraryPDF.FITZ:
            self.convertImagesToPdf:ImageConvertPdf = ImageConvertPdf.create_from_fitz(library_image)
        elif library_pdf == LibraryPDF.CANVAS:
            self.convertImagesToPdf:ImageConvertPdf = ImageConvertPdf.create_from_canvas(library_image)
        elif library_pdf == LibraryPDF.PILPDF:
            self.convertImagesToPdf:ImageConvertPdf = ImageConvertPdf.create_from_pil(library_image)
            
        # Objeto para converter PDF em imagem
        self.convertPdfToImages:ConvertPdfToImage = ConvertPdfToImage(
                library_pdf=LibraryPDF.FITZ, library_image=library_image, dpi=200,
            )
        
    @property
    def images(self) -> List[ImageObject]:
        return self.__images
    
    @images.setter
    def images(self, imgs:List[ImageObject]) -> None:
        if not isinstance(imgs, list):
            print(f'Erro: Use: list() não {type(imgs)}')
            return
        self.num_images = 0
        for img in imgs:
            self.add_image(img)
        
    def add_image(self, img:ImageObject) -> None:
        if not isinstance(img, ImageObject):
            return
        print(f'{__class__.__name__} Adicionando imagem {self.num_images+1}')
        self.__images.append(img)
        self.num_images += 1
        
    def add_images(self, images:List[ImageObject]):
        for i in images:
            self.add_image(i)
    
    def add_file_image(self, f:File):
        img = ImageObject.create_from_file(f, library=self.library_image)
        self.add_image(img)
        
    def add_files_image(self, files:List[File]):
        for f in files:
            self.add_file_image(f)
            
    def is_null(self) -> bool:
        if self.num_images < 1:
            return True
        return False
        
    def clear(self):
        self.__images.clear()
        self.num_images = 0
        
    def to_files_image(self, d:Directory, prefix:str='imagem'):
        d.mkdir()
        for num, image in enumerate(self.images):
            filename = f'{prefix}-{num+1}.png'
            print(f'Exportando imagem: {num+1} de {self.num_images} [{filename}]')
            image.to_file(d.join_file(filename))
                
    def to_pages_pdf(self) -> List[PageDocumentPdf]:
        if self.is_null():
            print(f'{__class__.__name__} Adicione imagens para prosseguir!')
            return []
        new_pages = []
        for image in self.images:
            new_pages.append(self.convertImagesToPdf.from_image(image))
        return new_pages
    
    def set_paisagem(self):
        for num, img in enumerate(self.images):
            self.images[num].set_paisagem()
            
    def set_gaussian_blur(self):
        for num, img in enumerate(self.images):
            print(f'Removendo ruido de imagem: [{num+1} de {self.num_images}]')
            self.images[num].set_gaussian()
            
    def set_backgroud_black(self):
        for num, img in enumerate(self.images):
            print(f'Escurecendo imagem: [{num+1} de {self.num_images}]')
            self.images[num].set_background_black()
            
    def set_background_gray(self):
        for num, img in enumerate(self.images):
            print(f'Escurecendo imagem: [{num+1} de {self.num_images}]')
            self.images[num].set_background_gray()
    
    def set_optimize(self):
        for num, img in enumerate(self.images):
            print(f'Otimizando imagem: [{num+1} de {self.num_images}]')
            self.images[num].set_optimize()
    

def get_data_from_pdfs(*, files_pdf:List[File]) -> pandas.DataFrame:
    """
        Recebe uma lista de arquivos PDF e retorna um DataFrame com os dados das cartas.
    """
    if not isinstance(files_pdf, list):
        raise ValueError(f'Erro: Use: list() não {type(files_pdf)}')
    
    data:List[pandas.DataFrame] = []
    values:List[str] = []
    doc = DocumentPdf()
    for file in files_pdf:
        doc.add_file_pdf(file)
        for page in doc.pages:
            text =  page.to_string()
            if (text is not None) and (text != ''):
                values.extend(text.split('\n'))
                data.append(
                    pandas.DataFrame(
                        {
                            'TEXT': values,
                            'ARQUIVO': [file.absolute()] * len(values)
                        }
                    )
                )

        values.clear()
        doc.clear()
    if len(data) < 1:
        return pandas.DataFrame()
    return pandas.concat(data).astype('str')
    