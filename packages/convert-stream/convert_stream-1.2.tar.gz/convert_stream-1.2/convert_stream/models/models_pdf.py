#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
from __future__ import annotations
from abc import  abstractmethod, ABC
from io import BytesIO
from typing import List
from enum import Enum

from pandas import DataFrame
from soup_files import File, Directory
from convert_stream.models.models_image import ABCImageObject, LibraryImage
from convert_stream.models.progress_bar import ProgressBarAdapter, ProgressBarSimple

class LibraryPDF(Enum):
    """Enumerar as libs para manipulação de PDF"""
    PYPDF = 'pypdf2'
    FITZ = 'fitz'
    CANVAS = 'canvas'
    PILPDF = 'pil'


# Representação de uma página PDF.
class ABCPagePdf(ABC):
    """Abstração de uma página PDF"""

    def __init__(self):
        super().__init__()
        self.page: object = None
        self.page_number: int = 0
        self.current_library: LibraryPDF = None

    @abstractmethod
    def to_string(self) -> str:
        pass
    
    @abstractmethod
    def to_list(self, separator:str='\n') -> List[str]:
        pass
    
    @abstractmethod
    def to_table(self, separator:str='\n') -> DataFrame:
        pass

    @abstractmethod
    def to_bytes(self) -> bytes:
        pass
    
    @abstractmethod
    def is_paisagem(self) -> bool:
        pass

    @abstractmethod
    def set_paisagem(self):
        pass
    
    @abstractmethod
    def set_page_pypdf2(self):
        pass
    
    @abstractmethod
    def set_page_fitz(self):
        pass

    @abstractmethod
    def rotate(self, degrees: int):
        pass 
    
    @classmethod
    def create_from_page_bytes(cls, page_bytes:bytes) -> ABCPagePdf:
        pass
    
    @classmethod
    def create_from_page_fitz(cls, page:object) -> ABCPagePdf:
        pass
    
    @classmethod
    def create_from_page_pypdf2(cls, page:object) -> ABCPagePdf:
        pass
    

class ABCDocumentPdf(ABC):
    def __init__(
                self,
                library: LibraryPDF = LibraryPDF.FITZ,
                *,
                progress_bar: ProgressBarAdapter = ProgressBarAdapter(ProgressBarSimple())
            ):
        self.__pages: List[ABCPagePdf] = []
        self.__num_pages: int = 0
        self.library: LibraryPDF = library
        self.__max_num_pages: int= 4000
        self.progress_bar: ProgressBarAdapter = progress_bar

    @property
    def max_num_pages(self) -> int:
        return self.__max_num_pages

    @max_num_pages.setter
    def max_num_pages(self, new:int):
        if isinstance(new, int):
            self.__max_num_pages = new
         
    @property
    def num_pages(self) -> int:
        return self.__num_pages
    
    @num_pages.setter
    def num_pages(self, new: int):
        if not isinstance(new, int):
            print(f'Número inválido...')
            return
        self.__num_pages = new

    @property
    def pages(self) -> List[ABCPagePdf]:
        return self.__pages

    @pages.setter
    def pages(self, new: List[ABCPagePdf]):
        if not isinstance(new, list):
            raise ValueError(f'{__class__.__name__}Erro: Use List[PagePdf], não {type(new)}')
        self.__pages = new
        
    @abstractmethod
    def is_null(self) -> bool:
        pass

    @abstractmethod
    def add_file_pdf(self, file:File):
        pass

    @abstractmethod
    def add_page(self, page:ABCPagePdf) -> bool:
        pass

    @abstractmethod
    def add_pages(self, pages:List[ABCPagePdf]):
        pass

    @abstractmethod
    def add_bytes_page(self, page_bytes:bytes):
        pass
    
    @abstractmethod
    def add_bytes_file_pdf(self, file_bytes:BytesIO):
        pass
    
    @abstractmethod
    def add_file_url(self, url:str):
        pass
        
    @abstractmethod
    def remove_page(self, page_number:int) -> None:
        pass
    
    @abstractmethod
    def remove_pages(self, num_pages:List[int]):
        pass
        
    @abstractmethod
    def rotate_page(self, page_number: int, degrees: int):
        pass
    
    @abstractmethod
    def set_paisagem(self):
        pass
        
    @abstractmethod
    def to_file_pdf(self, file:File):
        pass
    
    @abstractmethod
    def to_data(self, separator='\n') -> DataFrame:
        pass
    
    @abstractmethod
    def to_list(self, separator='\n') -> List[str]:
        pass
    
    @abstractmethod
    def to_excel(self, file:File, *, separator:str='\n'):
        pass
    
    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def get_page_number(self, num:int) -> ABCPagePdf:
        pass
    
    @abstractmethod
    def get_pages_numbers(self, numbers:List[int]) -> List[ABCPagePdf]:
        pass

    @abstractmethod
    def get_document_with_text(self, text:str) -> ABCDocumentPdf:
        pass


class ABCConvertPdf(ABC):
    """
        Converte um documento PDF ou Página PDF em imagem(s).
    """
    def __init__(self):
        super().__init__()
        
    @abstractmethod
    def from_page_bytes(self, page_bytes:bytes, dpi:int=200) -> ABCImageObject:
        """
            Converte os bytes de uma página PDF em objeto Imagem.
        """
        pass
    
    @abstractmethod
    def from_page_pdf(self, page: ABCPagePdf, dpi: int = 200) -> ABCImageObject:
        """
            Converte o um objeto PageDocumentPdf() em objeto Imagem.
        """
        pass
    
    @abstractmethod
    def inner_images(self, page_bytes: bytes) -> List[ABCImageObject]:
        """
            Converte todas as imagens embutidas em uma página PDF para uma lista de objetos Imagem.
        """
        pass
                    
        
class ABCImageConvertPdf(ABC):
    """Convete uma imagem em uma página PDF."""

    def __init__(self, library_image: LibraryImage = LibraryImage.OPENCV):
        super().__init__()
        self.library_image: LibraryImage = library_image
        
    @abstractmethod
    def from_image_file(self, file: File) -> ABCPagePdf:
        """
            Converte um arquivo de imagem em página PDF.
        """
        pass
    
    @abstractmethod
    def from_image(self, img: ABCImageObject) -> ABCDocumentPdf:
        """Converte um objeto imagem em uma página PDF."""
        pass
    
    @abstractmethod
    def from_image_bytes(self, img_bytes: bytes) -> ABCPagePdf:
        """Converte os bytes de uma imagem e uma página PDF."""
        pass
    
    
class ABCDocumentStream(ABC):
    """
        Objeto para manipular a exportação de dados PDF    
    """
    def __init__(
            self, *, 
            library_pdf: LibraryPDF = LibraryPDF.FITZ,
            library_image: LibraryImage = LibraryImage.OPENCV,
            progress_bar: ProgressBarAdapter = ProgressBarAdapter(ProgressBarSimple())
            ):
        self.library_pdf: LibraryPDF = library_pdf
        self.liabrary_image: LibraryImage = library_image
        self.progress_bar: ProgressBarAdapter = progress_bar
        
    @abstractmethod
    def is_null(self) -> bool:
        pass
    
    @abstractmethod
    def clear(self):
        pass
        
    @abstractmethod
    def to_file_pdf(self, f: File):
        """
            Exporta os dados para um arquivo PDF no disco.
        """
        pass
        
    @abstractmethod
    def to_files_pdf(self, outdir: Directory, *, prefix='pag'):
        """Exporta cada página para um novo arquivo PDF no disco"""
        pass
         
    @abstractmethod   
    def to_files_image(self, d: Directory, *, prefix:str='página-para-imagem'):
        """
            Exporta cada página PDF como um arquivo de imagem.
        """
        pass
            
    @abstractmethod
    def to_images(self) -> List[ABCImageObject]:
        """Retorna uma lista de imagens, dos documentos adicionados."""
        pass
    
    @abstractmethod
    def to_document(self) -> ABCDocumentPdf:
        """Converte os itens adicionados em documento"""
        pass
    
    def inner_images(self) -> List[ABCImageObject]:
        """
            Retorna uma lista com todas as imagens presentes em todas as páginas
        """
        pass
    
    @abstractmethod
    def inner_images_to_files(self, d: Directory, prefix: str = 'página-para-imagens') -> None:
        """
            Salva todas as imagens presentes nas páginas em arquivos de imagem.
        """
        pass
    
    @abstractmethod
    def add_page(self, p:ABCPagePdf):
        """Adiciona uma página PDF"""
        pass
    
    @abstractmethod
    def add_pages(self, pages: List[ABCPagePdf]):
        pass
       
    @abstractmethod     
    def add_page_pdf_bytes(self, bt: bytes):
        """Adicona os bytes de uma página PDF."""
        pass
          
    @abstractmethod  
    def add_file_pdf(self, f: File):
        pass
        
    @abstractmethod
    def add_files_pdf(self, files: List[File]):
        pass
    
    @abstractmethod
    def add_document(self, doc: ABCDocumentPdf):
        pass
    
    @abstractmethod
    def add_image(self, image: ABCImageObject):
        pass
    
    @abstractmethod
    def set_paisagem(self):
        """Define todas as páginas como paisagem."""
        pass

        
 
    
    








