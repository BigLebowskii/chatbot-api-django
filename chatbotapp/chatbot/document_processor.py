from langchain_text_splitters import RecursiveCharacterTextSplitter
import PyPDF2
import io

class DocumentProcessor:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    
    def process_file(self, file):
        """Process file and return extracted content"""
        content = self.extract_content(file)
        return content
    
    def extract_content(self, file):
        """Extract text content from various file types"""
        content = ""
        
        # Handle text files
        if file.content_type.startswith('text/'):
            try:
                for chunk in file.chunks():
                    content += chunk.decode('utf-8')
            except UnicodeDecodeError:
                content = "Could not decode file content"
        
        # Handle PDF files
        elif file.content_type == 'application/pdf':
            try:
                # Reset file pointer to beginning
                file.seek(0)
                
                # Read PDF content
                pdf_content = io.BytesIO(file.read())
                pdf_reader = PyPDF2.PdfReader(pdf_content)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        content += page_text + "\n"
            except Exception as e:
                content = f"Error extracting PDF content: {str(e)}"
        
        # Add more handlers for other file types as needed
        
        return content
    
    def split_text(self, text):
        """Split text into chunks for vector embedding"""
        return self.text_splitter.split_text(text)