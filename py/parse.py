import PyPDF2

def read_pdf_text(file_path):
    """
    Reads the text content from a PDF file and returns it as a string.
    :param file_path: The path to the PDF file to read.
    :return: A string containing the text content of the PDF.
    """
    # Open the PDF file using PyPDF2
    with open(file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)

        # Initialize an empty string to store the text content
        text_content = ""

        # Iterate over each page in the PDF
        for page_num in range(pdf_reader.getNumPages()):
            page = pdf_reader.getPage(page_num)

            # Extract the text content from the page
            page_text = page.extractText()

            # Add the text content to the result string
            text_content += page_text

        # Return the text content as a string
        return text_content

pdf_text = read_pdf_text('example_file.pdf')
print(pdf_text)

