#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import List
from io import BytesIO

from pandas import DataFrame, concat
from soup_files import File
from convert_stream.models.models_pdf import (
    LibraryPDF, ABCPagePdf, ABCDocumentPdf
)
from convert_stream.models.progress_bar import ProgressBarAdapter, ProgressBarSimple
from convert_stream.pdf_page import (
    PageDocumentPdf, PagePdfFitz, PagePyPdf2, MODULE_PYPDF2, MODULE_FITZ
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


#=======================================================================#
# Documento PDF
#=======================================================================#

class DocumentPyPdf2(ABCDocumentPdf):

    def __init__(
                self, library: LibraryPDF = LibraryPDF.FITZ,
                *,
                progress_bar: ProgressBarAdapter = ProgressBarAdapter(ProgressBarSimple())
            ):
        super().__init__(library, progress_bar=progress_bar)

    def is_null(self):
        if len(self.pages) < 1:
            return True
        return False
        
    def add_page(self, page: PageDocumentPdf) -> bool:
        if not isinstance(page, PageDocumentPdf):
            raise ValueError(f'Use: PageDocumentPdf(), não {type(page)}')
        if self.num_pages >= self.max_num_pages:
            print(f'Número máximo de páginas está definido em: {self.max_num_pages}')
            return False
        self.num_pages += 1
        page.page_number = self.num_pages
        self.pages.append(page)
        return True
        
    def add_pages(self, pages: List[PageDocumentPdf]):
        max_num: int = len(pages)
        for n, p in enumerate(pages):
            self.progress_bar.update(
                ((n+1)/max_num) * 100,
                f'Adicionando página: [{p.page_number} de {max_num}]'
            )
            self.add_page(p)
            
    def add_file_pdf(self, file: File):
        self.progress_bar.update_text(f'Adicionando arquivo: {file.basename()}')
        pdf_reader = PdfReader(file.absolute())
        num: int = len(pdf_reader.pages)
        for n, page in enumerate(pdf_reader.pages):
            self.progress_bar.update(
                ((n+1)/num) * 100,
                f'Adicionando página: [{n+1} de {num}] arquivo: {file.basename()}'
            )
            self.add_page(PageDocumentPdf.create_from_page_pypdf2(page))
        print()
        
    def add_files_pdf(self, files:List[File]):
        for f in files:
            self.add_file_pdf(f)

    def add_bytes_page(self, page_bytes: bytes):
        self.add_page(PageDocumentPdf.create_from_page_bytes(page_bytes))
        
    def add_bytes_file_pdf(self, bytes_file_pdf:BytesIO):
        try:
            # Cria um objeto PdfReader a partir dos bytes
            pdf_reader = PdfReader(bytes_file_pdf)
        except Exception as e:
            print(f"Erro ao adicionar PDF a partir de bytes: {e}")
        else:
            # Itera pelas páginas do documento e adiciona ao objeto atual
            page: PageObject = None
            for num, page in enumerate(pdf_reader.pages):
                self.add_page(
                        PageDocumentPdf(PagePyPdf2(page, num+1))
                    )
        finally:
            pass
        
    def add_file_url(self, url):
        try:
            import requests
        except Exception as e:
            print(e)
            return
        
        try:
            response:requests.Response = requests.get(url)
        except Exception as e:
            print(e)
            return
        
        if not response.status_code == 200:
            return
        bt:BytesIO = BytesIO(response.content)
        self.add_bytes_file_pdf(bt)
        
    def remove_page(self, page_number:int) -> None:
        if (page_number > self.num_pages) or (page_number < 1):
            return
        del self.pages[page_number - 1]
        for num, page in enumerate(self.pages):
            page.page_number = num + 1
        self.num_pages = len(self.pages)
        
    def remove_pages(self, num_pages:List[int]):
        new:List[PageDocumentPdf] = []
        for idx, page in enumerate(self.pages):
            if (idx + 1) in num_pages:
                continue
            new.append(page)
        self.clear()
        self.add_pages(new)
        #self.pages = new
        
    def rotate_page(self, page_number: int, degrees:int):
        if page_number > self.num_pages:
            return
        if page_number < 1:
            return
        self.pages[page_number - 1].rotate(degrees)
        
    def set_paisagem(self):
        for page in self.pages:
            page.set_paisagem()
    
    def to_file_pdf(self, fp: File):
        """
            Salva o documento no disco, usando PyPDF2.
        """
        writer = PdfWriter()
        for page in self.pages:
            if not isinstance(page.page, PagePyPdf2):  # Verifica se a página é do tipo PyPdf2
                raise TypeError("Todas as páginas devem ser do tipo PyPdf2PagePdf para salvar com PyPDF2.")
            writer.add_page(page.page.page)  # Adiciona a página ao writer
        with open(fp.absolute(), "wb+") as f:
            writer.write(f)
        
    def to_data(self, separator:str='\n') -> DataFrame:
        data: List[DataFrame] = []
        for page in self.pages:
            current_df = page.to_table(separator)
            if current_df.empty:
                continue
            current_num = len(current_df)
            current_df['NUM_PÁGINA'] = [page.page_number] * current_num
            data.append(current_df)
        return concat(data)
    
    def to_excel(self, file, *, separator:str='\n'):
        try:
            self.to_data(separator).to_excel(file.absolute(), index=False)
        except Exception as e:
            print(e)
    
    def to_list(self, separator='\n') -> List[str]:
        values: List[str] = []
        for p in self.pages:
            text = p.to_string()
            if text is not None:
                values.append(text)
        return values
    
    def clear(self):
        self.num_pages = 0
        self.pages.clear()

    def get_page_number(self, num) -> PageDocumentPdf:
        """
            Retorna a página correspondente ao número fornecido.
            Se o número estiver fora do intervalo, retorna None.
        """
        if not isinstance(num, int):
            raise ValueError(f'{__class__.__name__} Use um número inteiro para referência de páginas, não {type(num)}')
        if (num > self.num_pages) or (num < 1):
            return None
        if self.is_null():
            return None
        return self.pages[num - 1]
    
    def get_pages_numbers(self, numbers: List[int]) -> List[PageDocumentPdf]:
        """
            Retorna uma lista de páginas correspondentes aos números fornecidos.
            Se algum número estiver fora do intervalo, ele será ignorado.
        """
        if not isinstance(numbers, list):
            raise ValueError(
                f'{__class__.__name__} Use uma List[int], não {type(numbers)}'
            )
        if self.is_null():
            return []
        
        new_pages:List[PageDocumentPdf] = []
        for num in numbers:
            pg = self.get_page_number(num)
            if pg is not None:
                new_pages.append(pg)
        return new_pages
    
    def get_document_with_text(self, text) -> DocumentPdf:
        """
            Retorna uma lista de páginas que contêm o texto especificado.
            Se o texto não for encontrado, retorna uma lista vazia.
        """
        doc = DocumentPdf(self.library)
        for page in self.pages:
            current_text:str = page.to_string()
            if (current_text is not None) and (text in current_text):
                doc.add_page(page)
        return doc


class DocumentFitz(ABCDocumentPdf):

    def __init__(
                self,
                library: LibraryPDF = LibraryPDF.FITZ,
                *,
                progress_bar: ProgressBarAdapter = ProgressBarAdapter(ProgressBarSimple())
            ):
        super().__init__(library, progress_bar=progress_bar)

    def is_null(self):
        if len(self.pages) < 1:
            return True
        return False
        
    def add_page(self, page:PageDocumentPdf):
        if not isinstance(page, PageDocumentPdf):
            raise ValueError(f'Use: PageDocumentPdf(), não {type(page)}')
        if self.num_pages >= self.max_num_pages:
            print(f'Número máximo de páginas está definido em: {self.max_num_pages}')
            return False
        self.num_pages += 1
        page.page_number = self.num_pages
        self.pages.append(page)
        return True
        
    def add_pages(self, pages: List[ABCPagePdf]):
        max_num: int = len(pages)
        for n, p in enumerate(pages):
            self.progress_bar.update(
                ((n + 1) / max_num) * 100,
                f'Adicionando página: [{p.page_number} de {max_num}]'
            )
            self.add_page(p)
            
    def add_file_pdf(self, file: File):
        doc: fitz.Document = fitz.Document(file.absolute())

        self.progress_bar.update_text(f'Adicionando arquivo: {file.basename()}')
        num: int = len(doc)
        for n, page in enumerate(doc):
            self.progress_bar.update(
                ((n + 1) / num) * 100,
                f'Adicionando página: [{n + 1} de {num}] arquivo: {file.basename()}'
            )
            self.add_page(PageDocumentPdf.create_from_page_fitz(page))
        print()
        
    def add_files_pdf(self, files: List[File]):
        for f in files:
            self.add_file_pdf(f)

    def add_bytes_page(self, page_bytes:bytes):
        self.add_page(PageDocumentPdf.create_from_page_bytes(page_bytes, library=LibraryPDF.FITZ))
        
    def add_bytes_file_pdf(self, bytes_file_pdf:BytesIO):
        try:
            # Cria um objeto fitz.Document a partir dos bytes
            pdf_document: fitz.Document = fitz.Document(stream=bytes_file_pdf, filetype="pdf")
            # Itera pelas páginas do documento e adiciona ao objeto atual
            for page in pdf_document:
                self.add_page(
                        PageDocumentPdf(PagePdfFitz(page, page.number))
                    )
        except Exception as e:
            print(f"Erro ao adicionar PDF a partir de bytes: {e}")
        finally:
            pass
            #pdf_document.close()  # Fecha o documento após o uso
            
    def add_file_url(self, url):
        try:
            import requests
        except Exception as e:
            print(e)
            return
        
        try:
            response: requests.Response = requests.get(url)
        except Exception as e:
            print(e)
            return
        
        if not response.status_code == 200:
            return
        bt:BytesIO = BytesIO(response.content)
        self.add_bytes_file_pdf(bt)
        
    def remove_page(self, page_number:int) -> None:
        if not isinstance(page_number, int):
            raise ValueError(f'{__class__.__name__} Use um número inteiro para referência de páginas, não {type(page_number)}')
            
        if (page_number > self.num_pages) or (page_number < 1):
            return
        del self.pages[page_number - 1]
        for num, page in enumerate(self.pages):
            page.page_number = num + 1
        self.num_pages = len(self.pages)
        
    def remove_pages(self, num_pages: List[int]):
        new: List[PageDocumentPdf] = []
        for idx, page in enumerate(self.pages):
            if (idx + 1) in num_pages:
                continue
            new.append(page)
        self.clear()
        self.add_pages(new)
        #self.pages = new
        
    def rotate_page(self, page_number: int, degrees:int):
        if (page_number > self.num_pages) or (page_number < 1):
            return
        self.pages[page_number - 1].rotate(degrees)
        
    def set_paisagem(self):
        for page in self.pages:
            page.set_paisagem()
    
    def to_file_pdf(self, fp: File):
        """
            Salva o documento no disco, incluíndo todas as páginas (atuais e adicionadas)
        com a lib fitz.
        """
        pdf_document = fitz.Document()  # Cria um novo documento PDF
        for page in self.pages:
            if not isinstance(page.page.page, fitz.Page):  # Verifica se a página é do tipo fitz.Page
                raise TypeError(f"Todas as páginas devem ser do tipo [fitz.Page], não {type(page.page.page)}.")
            # Insere as páginas no novo documento
            pdf_document.insert_pdf(
                page.page.page.parent,
                from_page=page.page.page.number,
                to_page=page.page.page.number
            )
        
        # Salva o documento final no disco
        pdf_document.save(fp.absolute())
        pdf_document.close()

    def to_data(self, separator:str='\n') -> DataFrame:
        data: List[DataFrame] = []
        for page in self.pages:
            current_df = page.to_table()
            if current_df.empty:
                continue
            current_num = len(current_df)
            current_df['NUM_PÁGINA'] = [page.page_number] * current_num
            data.append(current_df)
        return concat(data)
    
    def to_excel(self, file, *, separator:str='\n'):
        try:
            self.to_data(separator).to_excel(file.absolute(), index=False)
        except Exception as e:
            print(e)
    
    def to_list(self, separator='\n') -> List[str]:
        values: List[str] = []
        for p in self.pages:
            text = p.to_string()
            if text is not None:
                values.append(text)
        return values
    
    def clear(self):
        self.num_pages = 0
        self.pages.clear()

    def get_page_number(self, num) -> PageDocumentPdf:
        """
            Retorna a página correspondente ao número fornecido.
            Se o número estiver fora do intervalo, retorna None.
        """
        if not isinstance(num, int):
            raise ValueError(f'{__class__.__name__} Use um número inteiro para referência de páginas, não {type(num)}')
        if (num > self.num_pages) or (num < 1):
            return None
        if self.is_null():
            return None
        return self.pages[num - 1]
    
    def get_pages_numbers(self, numbers: List[int]) -> List[PageDocumentPdf]:
        """
            Retorna uma lista de páginas correspondentes aos números fornecidos.
            Se algum número estiver fora do intervalo, ele será ignorado.
        """
        if not isinstance(numbers, list):
            raise ValueError(
                f'{__class__.__name__} Use List[int], não {type(numbers)}')
        if self.is_null():
            return []
        
        new_pages:List[PageDocumentPdf] = []
        for num in numbers:
            pg = self.get_page_number(num)
            if pg is not None:
                new_pages.append(pg)
        return new_pages

    def get_document_with_text(self, text) -> DocumentPdf:
        """
            Retorna uma lista de páginas que contêm o texto especificado.
            Se o texto não for encontrado, retorna uma lista vazia.
        """
        doc = DocumentPdf(self.library)
        for page in self.pages:
            current_text:str = page.to_string()
            if (current_text is not None) and (text in current_text):
                doc.add_page(page)
        return doc


class DocumentPdf(ABCDocumentPdf):

    def __init__(
                self,
                library: LibraryPDF = LibraryPDF.FITZ,
                *,
                progress_bar: ProgressBarAdapter = ProgressBarAdapter(ProgressBarSimple())
            ):
        super().__init__(library, progress_bar=progress_bar)
        self.library: LibraryPDF = library
        if self.library == LibraryPDF.PYPDF:
            self.document: ABCDocumentPdf = DocumentPyPdf2(progress_bar=progress_bar)
        elif self.library == LibraryPDF.FITZ:
            self.document: ABCDocumentPdf = DocumentFitz(progress_bar=progress_bar)
        else:
            raise NotImplementedError(f'{__class__.__name__}\nLibraryPDF não implementada: {type(library)}')
        
    @property
    def max_num_pages(self) -> int:
        return self.document.max_num_pages

    @max_num_pages.setter
    def max_num_pages(self, new:int):
        if isinstance(new, int):
            self.document.max_num_pages = new
        
    @property
    def num_pages(self) -> int:
        return self.document.num_pages
    
    @num_pages.setter
    def num_pages(self, new:int):
        self.document.num_pages = new
    
    @property
    def pages(self) -> List[PageDocumentPdf]:
        return self.document.pages
    
    @pages.setter
    def pages(self, new:List[PageDocumentPdf]):
        self.num_pages = 0
        for pg in new:
            self.add_page(pg)
    
    def is_null(self) -> bool:
        return self.document.is_null()
        
    def add_page(self, page:PageDocumentPdf):
        if self.library != page.current_library:
            if self.library == LibraryPDF.FITZ:
                page.set_page_fitz()
            elif self.library == LibraryPDF.PYPDF:
                page.set_page_pypdf2()
        if self.document.add_page(page):
            print(f'Página PDF adicionada: {self.num_pages}')
        
    def add_pages(self, pages: List[ABCPagePdf]):
        max_num: int = len(pages)
        for n, p in enumerate(pages):
            self.progress_bar.update(
                ((n + 1) / max_num) * 100,
                f'Adicionando página: [{p.page_number} de {max_num}]'
            )
            self.add_page(p)

    def add_file_pdf(self, file:File):
        print(f'Adicionando páginas do arquivo: {file.basename()}')
        self.document.add_file_pdf(file)
        
    def add_files_pdf(self, files:List[File]):
        for f in files:
            self.add_file_pdf(f)

    def add_bytes_page(self, page_bytes:bytes):
        self.document.add_bytes_page(page_bytes)

    def add_bytes_file_pdf(self, file_bytes:BytesIO):
        self.document.add_bytes_file_pdf(file_bytes)
        
    def add_file_url(self, url):
        print(f'Adicionando URL: {url}')
        self.document.add_file_url(url)
        
    def remove_page(self, page_number:int) -> None:
        self.document.remove_page(page_number)
        
    def remove_pages(self, num_pages:List[int]):
        self.document.remove_pages(num_pages)
        
    def rotate_page(self, page_number: int, degrees:int):
        print(f'Rotacionando a página {page_number}  [{degrees}]')
        self.document.rotate_page(page_number, degrees)
        
    def set_paisagem(self):
        self.document.set_paisagem()
    
    def to_file_pdf(self, file:File) -> bool:
        if self.is_null():
            print(f'O documento está vazio, adicione páginas ou arquivos para prosseguir!')
            return False
        self.progress_bar.update_text(f'Salvando arquivo: {file.basename()}')
        self.document.to_file_pdf(file)
        return False
    
    def to_data(self, separator: str = '\n') -> DataFrame:
        return self.document.to_data(separator)
    
    def to_excel(self, file, *, separator = '\n'):
        self.progress_bar.update_text(f'Salvando planilha: {file.basename()}')
        self.document.to_excel(file, separator=separator)
    
    def to_list(self, separator='\n') -> List[str]:
        return self.document.to_list(separator)
    
    def clear(self):
        self.document.clear()

    def get_page_number(self, num) -> PageDocumentPdf:
        return self.document.get_page_number(num)
    
    def get_pages_numbers(self, numbers) -> List[PageDocumentPdf]:
        return self.document.get_pages_numbers(numbers)
    
    def get_document_with_text(self, text) -> DocumentPdf:
        """
            Retorna um novo documento com as páginas que contém o texto informado no parâmetro,
        se o texto não for encontrado, retorna um documento vazio.
        """
        return self.document.get_document_with_text(text)
    
    @classmethod
    def create_from_file(cls, file:File, *, library:LibraryPDF=LibraryPDF.PYPDF) -> DocumentPdf:
        doc = cls(library)
        doc.add_file_pdf(file)
        return doc
    
        

 