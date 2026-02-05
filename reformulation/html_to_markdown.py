from bs4 import BeautifulSoup
import html2text
import re


class HTMLToMarkdown:
    def __init__(self):
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = True
        self.h2t.ignore_emphasis = False
        self.h2t.body_width = 0
    
    def clean_html(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Remove Angular/React artifacts
        for tag in soup.find_all(attrs={"ng-class": True}):
            del tag["ng-class"]
        for tag in soup.find_all(attrs={"ng-style": True}):
            del tag["ng-style"]
        
        return str(soup)
    
    def convert(self, html_content: str) -> str:
        if not html_content or not html_content.strip():
            return ""
        
        try:
            cleaned = self.clean_html(html_content)
            markdown = self.h2t.handle(cleaned)
            
            markdown = re.sub(r'\n{3,}', '\n\n', markdown)
            markdown = markdown.strip()
            
            return markdown
        except Exception as e:
            # Fallback to basic text extraction
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text(separator='\n', strip=True)
