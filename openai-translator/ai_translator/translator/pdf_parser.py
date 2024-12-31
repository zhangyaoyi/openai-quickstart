# Start of Selection
import pdfplumber
from typing import Optional
from book import Book, Page, Content, ContentType, TableContent
from translator.exceptions import PageOutOfRangeException
from utils import LOG

class PDFParser:
    """
    PDF 解析器，用于将 PDF 文件解析成 Book 对象。
    """
    def __init__(self):
        """
        初始化 PDFParser 对象。
        """
        pass

    def parse_pdf(self, pdf_file_path: str, pages: Optional[int] = None) -> Book:
        """
        解析指定的 PDF 文件。

        Args:
            pdf_file_path (str): PDF 文件的路径。
            pages (Optional[int], optional): 需要解析的页数。如果为 None，则解析所有页。默认为 None。

        Returns:
            Book: 解析后的 Book 对象。

        Raises:
            PageOutOfRangeException: 如果指定的页数超出 PDF 文件的总页数。
        """
        book = Book(pdf_file_path)

        with pdfplumber.open(pdf_file_path) as pdf:
            num_pages = len(pdf.pages)
            if pages is not None and pages > num_pages:
                raise PageOutOfRangeException(num_pages, pages)

            # 确定要解析的页码范围
            pages_to_parse = pdf.pages if pages is None else pdf.pages[:pages]

            for pdf_page in pages_to_parse:
                page = Page()

                # 提取页面文本和表格
                raw_text = pdf_page.extract_text()
                tables = pdf_page.extract_tables()

                # 移除表格内容以避免重复
                for table_data in tables:
                    for row in table_data:
                        for cell in row:
                            if cell:
                                raw_text = raw_text.replace(cell, "", 1)

                # 处理提取出的文本内容
                if raw_text:
                    cleaned_raw_text = "\n".join(line.strip() for line in raw_text.splitlines() if line.strip())
                    text_content = Content(content_type=ContentType.TEXT, original=cleaned_raw_text)
                    page.add_content(text_content)
                    LOG.debug(f"[raw_text]\n {cleaned_raw_text}")

                # 处理提取出的表格内容
                if tables:
                    table_content = TableContent(tables)
                    page.add_content(table_content)
                    LOG.debug(f"[table]\n{table_content}")

                book.add_page(page)

        return book
