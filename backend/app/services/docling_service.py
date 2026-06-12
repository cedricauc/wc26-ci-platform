"""
Docling PDF extraction service for FIFA World Cup documents
"""
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import json

try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    logging.warning("Docling not available. PDF extraction will be limited.")

logger = logging.getLogger(__name__)


class DoclingExtractionService:
    """Service for extracting structured data from PDFs using Docling"""
    
    def __init__(self):
        if DOCLING_AVAILABLE:
            try:
                # Docling v2+ API: pipeline options go inside format_options
                from docling.document_converter import DocumentConverter, PdfFormatOption
                from docling.datamodel.pipeline_options import PdfPipelineOptions

                pipeline_options = PdfPipelineOptions()
                pipeline_options.do_ocr = True
                pipeline_options.do_table_structure = True

                self.converter = DocumentConverter(
                    allowed_formats=[InputFormat.PDF],
                    format_options={
                        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                    }
                )
            except (ImportError, TypeError):
                # Fallback: plain converter with no custom options
                self.converter = DocumentConverter()
        else:
            self.converter = None
    
    def extract_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract structured data from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted data with structure:
            {
                "text": "full text content",
                "tables": [...],
                "paragraphs": [...],
                "metadata": {...},
                "structure": {...}
            }
        """
        if not DOCLING_AVAILABLE or not self.converter:
            logger.error("Docling not available for extraction")
            return self._fallback_extraction(pdf_path)
        
        try:
            logger.info(f"Starting Docling extraction for: {pdf_path}")
            
            # Convert the document
            result = self.converter.convert(pdf_path)
            
            # Extract structured data
            extracted_data = {
                "text": result.document.export_to_text(),
                "markdown": result.document.export_to_markdown(),
                "tables": self._extract_tables(result),
                "paragraphs": self._extract_paragraphs(result),
                "key_values": self._extract_key_values(result),
                "metadata": self._extract_metadata(result),
                "structure": self._extract_structure(result)
            }
            
            logger.info(f"Extraction completed. Found {len(extracted_data['tables'])} tables, "
                       f"{len(extracted_data['paragraphs'])} paragraphs")
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error during Docling extraction: {e}")
            return self._fallback_extraction(pdf_path)
    
    def _extract_tables(self, result) -> List[Dict[str, Any]]:
        """Extract tables from Docling result"""
        tables = []
        try:
            # Docling v2 uses items iterator
            for item, level in result.document.iterate_items():
                if item.label == "table":
                    table_data = {
                        "headers": [],
                        "rows": [],
                        "text": item.text if hasattr(item, 'text') else ""
                    }
                    
                    # Try to extract table structure
                    if hasattr(item, 'data') and item.data:
                        # Parse table data if available
                        table_data["raw_data"] = str(item.data)
                    
                    tables.append(table_data)
        except AttributeError:
            # Fallback: try old API
            try:
                if hasattr(result.document, 'tables'):
                    for table in result.document.tables:
                        table_data = {
                            "headers": [],
                            "rows": [],
                            "text": str(table)
                        }
                        tables.append(table_data)
            except Exception as e2:
                logger.warning(f"Error with fallback table extraction: {e2}")
        except Exception as e:
            logger.warning(f"Error extracting tables: {e}")
        
        return tables
    
    def _extract_paragraphs(self, result) -> List[Dict[str, Any]]:
        """Extract paragraphs from Docling result"""
        paragraphs = []
        try:
            # Docling v2 uses items iterator
            for item, level in result.document.iterate_items():
                if item.label in ["paragraph", "text", "title", "section_header"]:
                    para_data = {
                        "text": item.text if hasattr(item, 'text') else str(item),
                        "type": item.label if hasattr(item, 'label') else "paragraph",
                        "level": level
                    }
                    paragraphs.append(para_data)
        except AttributeError:
            # Fallback: try to extract from text
            try:
                text = result.document.export_to_text()
                # Split into paragraphs
                for para_text in text.split('\n\n'):
                    if para_text.strip():
                        paragraphs.append({
                            "text": para_text.strip(),
                            "type": "paragraph"
                        })
            except Exception as e2:
                logger.warning(f"Error with fallback paragraph extraction: {e2}")
        except Exception as e:
            logger.warning(f"Error extracting paragraphs: {e}")
        
        return paragraphs
    
    def _extract_key_values(self, result) -> Dict[str, Any]:
        """Extract key-value pairs from Docling result"""
        key_values = {}
        try:
            if hasattr(result.document, 'key_value_items'):
                for item in result.document.key_value_items:
                    if hasattr(item, 'key') and hasattr(item, 'value'):
                        key_values[item.key] = item.value
        except Exception as e:
            logger.warning(f"Error extracting key-values: {e}")
        
        return key_values
    
    def _extract_metadata(self, result) -> Dict[str, Any]:
        """Extract document metadata"""
        metadata = {}
        try:
            if hasattr(result.document, 'metadata'):
                metadata = result.document.metadata
        except Exception as e:
            logger.warning(f"Error extracting metadata: {e}")
        
        return metadata
    
    def _extract_structure(self, result) -> Dict[str, Any]:
        """Extract document structure information"""
        structure = {
            "page_count": 0,
            "has_tables": False,
            "has_images": False,
            "sections": []
        }
        
        try:
            if hasattr(result.document, 'pages'):
                structure["page_count"] = len(result.document.pages)
            
            if hasattr(result.document, 'tables'):
                structure["has_tables"] = len(result.document.tables) > 0
            
            if hasattr(result.document, 'images'):
                structure["has_images"] = len(result.document.images) > 0
        except Exception as e:
            logger.warning(f"Error extracting structure: {e}")
        
        return structure
    
    def _fallback_extraction(self, pdf_path: str) -> Dict[str, Any]:
        """
        Fallback extraction using PyPDF2 when Docling is not available
        """
        try:
            from PyPDF2 import PdfReader
            
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return {
                "text": text,
                "markdown": text,
                "tables": [],
                "paragraphs": [{"text": text, "type": "paragraph"}],
                "key_values": {},
                "metadata": {"page_count": len(reader.pages)},
                "structure": {
                    "page_count": len(reader.pages),
                    "has_tables": False,
                    "has_images": False,
                    "sections": []
                }
            }
        except Exception as e:
            logger.error(f"Fallback extraction failed: {e}")
            return {
                "text": "",
                "markdown": "",
                "tables": [],
                "paragraphs": [],
                "key_values": {},
                "metadata": {},
                "structure": {},
                "error": str(e)
            }


# Singleton instance
docling_service = DoclingExtractionService()
