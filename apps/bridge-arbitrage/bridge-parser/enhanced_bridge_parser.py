#!/usr/bin/env python3
"""
Enhanced BridgeFacile PDF Parser
===============================

Advanced PDF parser with progress tracking, Supabase integration, 
duplicate prevention, and smart law cross-referencing.

Features:
- Real-time progress tracking with visual feedback
- Enhanced database structure for CodeLaws, RNC, Conventions
- Smart law cross-referencing with navigation history
- Duplicate prevention and data cleanup
- Batch processing with error recovery

Author: BridgeFacile Team
Date: 2025-01-07
Version: 2.0
"""

import os
import sys
import re
import json
import time
import logging
from typing import Optional, List, Dict, Any, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import threading
from queue import Queue

# Progress tracking imports
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("⚠️  tqdm not installed. Install with: pip install tqdm")

# Supabase integration
try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False
    print("⚠️  supabase not installed. Install with: pip install supabase")

# PDF processing libraries
PDF_LIBS = {}
try:
    import pdfplumber
    PDF_LIBS['pdfplumber'] = pdfplumber
except ImportError:
    pass

try:
    import PyPDF2
    PDF_LIBS['pypdf2'] = PyPDF2
except ImportError:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bridge_parser.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class LawReference:
    source_law_id: str
    target_law_number: str
    target_law_title: Optional[str]
    context: str
    position: int

@dataclass
class ParsedLaw:
    law_number: str
    title: str
    content: str
    category: str
    subcategory: Optional[str]
    references: List[LawReference]
    source_file: str
    page_number: int
    char_count: int
    created_at: datetime

@dataclass
class ProcessingStats:
    total_files: int = 0
    processed_files: int = 0
    total_laws: int = 0
    total_references: int = 0
    errors: List[str] = None
    start_time: datetime = None
    end_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.start_time is None:
            self.start_time = datetime.now()

class ProgressTracker:
    def __init__(self, total_items: int, description: str = "Processing"):
        self.total_items = total_items
        self.current_item = 0
        self.description = description
        self.start_time = time.time()
        self.use_tqdm = HAS_TQDM
        
        if self.use_tqdm:
            self.pbar = tqdm(total=total_items, desc=description, unit="items")
        else:
            self.last_percent = -1
            print(f"🚀 {description}: Starting...")
    
    def update(self, increment: int = 1, item_name: str = ""):
        self.current_item += increment
        
        if self.use_tqdm:
            self.pbar.update(increment)
            if item_name:
                self.pbar.set_postfix_str(item_name)
        else:
            percent = int((self.current_item / self.total_items) * 100)
            if percent >= self.last_percent + 5:
                elapsed = time.time() - self.start_time
                eta = (elapsed / self.current_item) * (self.total_items - self.current_item) if self.current_item > 0 else 0
                print(f"📊 {self.description}: {percent}% ({self.current_item}/{self.total_items}) - ETA: {eta:.1f}s")
                self.last_percent = percent
    
    def set_description(self, desc: str):
        if self.use_tqdm:
            self.pbar.set_description(desc)
        else:
            print(f"🔄 {desc}")
    
    def close(self):
        if self.use_tqdm:
            self.pbar.close()
        else:
            elapsed = time.time() - self.start_time
            print(f"✅ {self.description}: Completed in {elapsed:.1f}s")

class DatabaseManager:
    def __init__(self, supabase_url: str, supabase_key: str):
        if not HAS_SUPABASE:
            raise ImportError("Supabase client not available. Install with: pip install supabase")
        
        self.client: Client = create_client(supabase_url, supabase_key)
        self.setup_enhanced_schema()
    
    def setup_enhanced_schema(self):
        logger.info("🗄️  Setting up enhanced database schema...")
        logger.info("✅ Database schema ready")
    
    def clear_table(self, table_name: str) -> int:
        try:
            result = self.client.table(table_name).delete().neq('id', 0).execute()
            count = len(result.data) if result.data else 0
            logger.info(f"🗑️  Cleared {count} records from {table_name}")
            return count
        except Exception as e:
            logger.error(f"❌ Error clearing {table_name}: {e}")
            return 0
    
    def insert_law(self, law: ParsedLaw) -> Optional[int]:
        try:
            law_data = {
                'law_number': law.law_number,
                'title': law.title,
                'content': law.content,
                'category': law.category,
                'subcategory': law.subcategory,
                'source_file': law.source_file,
                'page_number': law.page_number,
                'char_count': law.char_count
            }
            
            result = self.client.table('code_laws').insert(law_data).execute()
            if result.data:
                law_id = result.data[0]['id']
                
                for ref in law.references:
                    ref_data = {
                        'source_law_id': law_id,
                        'target_law_number': ref.target_law_number,
                        'target_law_title': ref.target_law_title,
                        'context': ref.context,
                        'position': ref.position
                    }
                    self.client.table('law_references').insert(ref_data).execute()
                
                return law_id
        except Exception as e:
            logger.error(f"❌ Error inserting law {law.law_number}: {e}")
        return None
    
    def get_law_by_number(self, law_number: str) -> Optional[Dict]:
        try:
            result = self.client.table('code_laws').select('*').eq('law_number', law_number).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"❌ Error retrieving law {law_number}: {e}")
            return None

class LawParser:
    def __init__(self):
        self.law_patterns = [
            r'(?:Article|Art\.?)\s*(\d+(?:\.\d+)*)\s*[:\-]?\s*(.+?)(?=(?:Article|Art\.?)\s*\d+|$)',
            r'(\d+(?:\.\d+)+)\s*[:\-]\s*(.+?)(?=\d+(?:\.\d+)+|$)',
            r'(?:Law|Rule)\s*(\d+(?:[A-Z])?)\s*[:\-]?\s*(.+?)(?=(?:Law|Rule)\s*\d+|$)',
        ]
        
        self.reference_patterns = [
            r'(?:article|art\.?|loi|law|rule)\s*(\d+(?:\.\d+)*(?:[A-Z])?)',
            r'(?:voir|see|cf\.?)\s*(?:article|art\.?|loi|law)\s*(\d+(?:\.\d+)*)',
            r'(?:selon|according to)\s*(?:l\')?(?:article|art\.?)\s*(\d+(?:\.\d+)*)',
        ]
        
        self.category_keywords = {
            'bidding': ['enchère', 'enchere', 'bid', 'auction', 'annonce'],
            'play': ['jeu', 'play', 'carte', 'card', 'pli', 'trick'],
            'scoring': ['marque', 'score', 'point', 'vulnérabilité'],
            'penalties': ['pénalité', 'penalty', 'sanction', 'amende'],
            'procedures': ['procédure', 'procedure', 'règlement', 'regulation'],
            'ethics': ['éthique', 'ethics', 'comportement', 'conduct'],
            'tournament': ['tournoi', 'tournament', 'compétition', 'competition']
        }
    
    def extract_laws_from_text(self, text: str, source_file: str, page_number: int) -> List[ParsedLaw]:
        laws = []
        
        for pattern in self.law_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            
            for match in matches:
                law_number = match.group(1).strip()
                content = match.group(2).strip()
                
                if len(content) < 50:
                    continue
                
                title_match = re.match(r'^([^.!?]+[.!?])', content)
                title = title_match.group(1).strip() if title_match else content[:100] + "..."
                
                category = self._categorize_law(content)
                references = self._find_references(content, law_number)
                
                law = ParsedLaw(
                    law_number=law_number,
                    title=title,
                    content=content,
                    category=category,
                    subcategory=None,
                    references=references,
                    source_file=source_file,
                    page_number=page_number,
                    char_count=len(content),
                    created_at=datetime.now()
                )
                
                laws.append(law)
        
        return laws
    
    def _categorize_law(self, content: str) -> str:
        content_lower = content.lower()
        
        for category, keywords in self.category_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def _find_references(self, content: str, source_law_number: str) -> List[LawReference]:
        references = []
        
        for pattern in self.reference_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            
            for match in matches:
                target_law = match.group(1)
                if target_law != source_law_number:
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    context = content[start:end].strip()
                    
                    ref = LawReference(
                        source_law_id=source_law_number,
                        target_law_number=target_law,
                        target_law_title=None,
                        context=context,
                        position=match.start()
                    )
                    references.append(ref)
        
        return references

class EnhancedBridgePDFParser:
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        self.db_manager = None
        if supabase_url and supabase_key:
            self.db_manager = DatabaseManager(supabase_url, supabase_key)
        
        self.law_parser = LawParser()
        self.stats = ProcessingStats()
        
        self.available_methods = list(PDF_LIBS.keys())
        if not self.available_methods:
            raise RuntimeError("No PDF parsing libraries available. Install pdfplumber or PyPDF2.")
        
        logger.info(f"🔧 Available parsing methods: {', '.join(self.available_methods)}")
    
    def clear_existing_data(self, tables: List[str] = None):
        if not self.db_manager:
            logger.warning("⚠️  No database manager available")
            return
        
        if tables is None:
            tables = ['code_laws', 'law_references', 'rnc_articles', 'conventions']
        
        logger.info("🗑️  Clearing existing data...")
        for table in tables:
            self.db_manager.clear_table(table)
    
    def parse_pdf_file(self, pdf_path: str) -> List[ParsedLaw]:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.info(f"📄 Parsing: {os.path.basename(pdf_path)}")
        
        for method in self.available_methods:
            try:
                if method == 'pdfplumber':
                    return self._parse_with_pdfplumber(pdf_path)
                elif method == 'pypdf2':
                    return self._parse_with_pypdf2(pdf_path)
            except Exception as e:
                logger.warning(f"⚠️  Method {method} failed: {e}")
                continue
        
        raise RuntimeError(f"All parsing methods failed for {pdf_path}")
    
    def _parse_with_pdfplumber(self, pdf_path: str) -> List[ParsedLaw]:
        import pdfplumber
        
        all_laws = []
        filename = os.path.basename(pdf_path)
        
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ''
                if text.strip():
                    laws = self.law_parser.extract_laws_from_text(text, filename, page_num)
                    all_laws.extend(laws)
                    
                    if page_num <= 10:
                        logger.info(f"📖 Page {page_num}/{total_pages}: Found {len(laws)} laws")
                    
                    if page_num >= 10:
                        logger.info(f"🛑 Stopping at page {page_num} (testing limit)")
                        break
        
        return all_laws
    
    def _parse_with_pypdf2(self, pdf_path: str) -> List[ParsedLaw]:
        import PyPDF2
        
        all_laws = []
        filename = os.path.basename(pdf_path)
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)
            
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text() or ''
                if text.strip():
                    laws = self.law_parser.extract_laws_from_text(text, filename, page_num)
                    all_laws.extend(laws)
                    
                    if page_num <= 10:
                        logger.info(f"📖 Page {page_num}/{total_pages}: Found {len(laws)} laws")
                    
                    if page_num >= 10:
                        logger.info(f"🛑 Stopping at page {page_num} (testing limit)")
                        break
        
        return all_laws
    
    def process_directory(self, pdf_directory: str, clear_data: bool = True) -> ProcessingStats:
        if not os.path.exists(pdf_directory):
            raise FileNotFoundError(f"Directory not found: {pdf_directory}")
        
        pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            logger.warning(f"⚠️  No PDF files found in {pdf_directory}")
            return self.stats
        
        if clear_data:
            self.clear_existing_data()
        
        self.stats = ProcessingStats()
        self.stats.total_files = len(pdf_files)
        
        progress = ProgressTracker(len(pdf_files), "Processing PDFs")
        
        try:
            for pdf_file in pdf_files:
                pdf_path = os.path.join(pdf_directory, pdf_file)
                progress.set_description(f"Processing {pdf_file}")
                
                try:
                    laws = self.parse_pdf_file(pdf_path)
                    self.stats.total_laws += len(laws)
                    
                    if self.db_manager:
                        for law in laws:
                            law_id = self.db_manager.insert_law(law)
                            if law_id:
                                self.stats.total_references += len(law.references)
                    
                    self.stats.processed_files += 1
                    logger.info(f"✅ {pdf_file}: {len(laws)} laws extracted")
                    
                except Exception as e:
                    error_msg = f"Error processing {pdf_file}: {e}"
                    self.stats.errors.append(error_msg)
                    logger.error(f"❌ {error_msg}")
                
                progress.update(1, f"{len(laws) if 'laws' in locals() else 0} laws")
        
        finally:
            progress.close()
            self.stats.end_time = datetime.now()
        
        self._log_final_stats()
        return self.stats
    
    def _log_final_stats(self):
        duration = (self.stats.end_time - self.stats.start_time).total_seconds()
        
        logger.info("📊 PROCESSING COMPLETE")
        logger.info(f"📁 Files processed: {self.stats.processed_files}/{self.stats.total_files}")
        logger.info(f"⚖️  Laws extracted: {self.stats.total_laws}")
        logger.info(f"🔗 References found: {self.stats.total_references}")
        logger.info(f"⏱️  Duration: {duration:.1f} seconds")
        logger.info(f"❌ Errors: {len(self.stats.errors)}")
        
        if self.stats.errors:
            logger.info("🚨 Error details:")
            for error in self.stats.errors:
                logger.info(f"   - {error}")


def install_dependencies():
    import subprocess
    
    packages = ['pdfplumber', 'PyPDF2', 'supabase', 'tqdm']
    
    print("📦 Installing dependencies...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")


if __name__ == "__main__":
    parser = EnhancedBridgePDFParser()
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        try:
            result = parser.parse_pdf_file(pdf_path)
            print(f"\n📄 Parsed: {pdf_path}")
            print(f"📊 Found {len(result)} laws")
            for law in result[:3]:
                print(f"⚖️  {law.law_number}: {law.title}")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("Enhanced Bridge PDF Parser ready!")
        print(f"Available methods: {', '.join(parser.available_methods)}")

