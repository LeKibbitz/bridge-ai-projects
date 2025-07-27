#!/usr/bin/env python3
"""
Complete Bridge PDF Parser System
=================================

Integrated system combining all enhanced features:
- PDF parsing with multiple methods
- Progress tracking with visual feedback
- Smart law cross-referencing
- Supabase integration with duplicate prevention
- Comprehensive error handling and logging

Usage:
    python complete_bridge_parser.py <pdf_directory> <supabase_url> <supabase_key>

Author: BridgeFacile Team
Date: 2025-01-07
Version: 3.0 - Complete Integration
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse
from datetime import datetime

# Import our enhanced modules
try:
    from enhanced_bridge_parser import EnhancedBridgePDFParser, ProcessingStats
    from law_navigation_system import LawNavigationAPI
    from supabase_integration import EnhancedSupabaseManager, create_enhanced_manager
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all parser files are in the same directory!")
    sys.exit(1)

# Configure comprehensive logging
def setup_logging(log_level: str = 'INFO', log_file: str = None):
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )
    
    # Reduce noise from external libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)

class CompleteBridgeParserSystem:
    def __init__(self, supabase_url: str, supabase_key: str, log_level: str = 'INFO'):
        self.logger = logging.getLogger(__name__)
        
        try:
            # Initialize Supabase manager
            self.db_manager = create_enhanced_manager(supabase_url, supabase_key)
            self.logger.info("✅ Database manager initialized")
            
            # Initialize PDF parser
            self.pdf_parser = EnhancedBridgePDFParser(supabase_url, supabase_key)
            self.logger.info("✅ PDF parser initialized")
            
            # Initialize navigation system
            self.navigation_api = LawNavigationAPI(self.db_manager)
            self.logger.info("✅ Navigation system initialized")
            
            self.logger.info("🚀 Complete Bridge Parser System ready!")
            
        except Exception as e:
            self.logger.error(f"💥 System initialization failed: {e}")
            raise
    
    def run_complete_processing(self, 
                              pdf_directory: str, 
                              clear_existing: bool = True,
                              test_mode: bool = False,
                              max_files: int = None) -> Dict[str, Any]:
        
        self.logger.info("🎯 Starting complete processing pipeline")
        self.logger.info(f"📁 Source directory: {pdf_directory}")
        self.logger.info(f"🗑️  Clear existing data: {clear_existing}")
        self.logger.info(f"🧪 Test mode: {test_mode}")
        
        results = {
            'start_time': datetime.now(),
            'pdf_processing': None,
            'database_stats': None,
            'navigation_setup': None,
            'errors': [],
            'success': False
        }
        
        try:
            # Step 1: Validate input directory
            if not os.path.exists(pdf_directory):
                raise FileNotFoundError(f"PDF directory not found: {pdf_directory}")
            
            pdf_files = list(Path(pdf_directory).glob("*.pdf"))
            if not pdf_files:
                raise ValueError(f"No PDF files found in {pdf_directory}")
            
            if max_files:
                pdf_files = pdf_files[:max_files]
            
            self.logger.info(f"📄 Found {len(pdf_files)} PDF files to process")
            
            # Step 2: Clear existing data if requested
            if clear_existing:
                self.logger.info("🗑️  Clearing existing database data...")
                clear_results = self.db_manager.clear_tables(
                    ['code_laws', 'law_references'], 
                    confirm=True
                )
                self.logger.info(f"✅ Cleared data: {clear_results}")
            
            # Step 3: Process PDFs
            self.logger.info("📚 Starting PDF processing...")
            processing_stats = self.pdf_parser.process_directory(
                pdf_directory, 
                clear_data=False  # Already cleared above
            )
            results['pdf_processing'] = processing_stats
            
            # Step 4: Get database statistics
            self.logger.info("📊 Gathering database statistics...")
            db_stats = self.db_manager.get_database_stats()
            results['database_stats'] = db_stats
            
            # Step 5: Setup navigation system
            self.logger.info("🧭 Setting up navigation system...")
            test_session = self.navigation_api.create_session("test_session")
            results['navigation_setup'] = {
                'session_created': True,
                'session_id': test_session.session_id
            }
            
            # Step 6: Run optimization
            self.logger.info("⚡ Running database optimization...")
            optimization_results = self.db_manager.optimize_database()
            results['optimization'] = optimization_results
            
            results['success'] = True
            results['end_time'] = datetime.now()
            
            # Log final summary
            self._log_processing_summary(results)
            
        except Exception as e:
            error_msg = f"Processing pipeline failed: {e}"
            self.logger.error(f"💥 {error_msg}")
            results['errors'].append(error_msg)
            results['success'] = False
        
        return results
    
    def _log_processing_summary(self, results: Dict[str, Any]):
        self.logger.info("=" * 60)
        self.logger.info("🎉 PROCESSING COMPLETE - SUMMARY")
        self.logger.info("=" * 60)
        
        # Processing stats
        if results.get('pdf_processing'):
            stats = results['pdf_processing']
            duration = (stats.end_time - stats.start_time).total_seconds()
            self.logger.info(f"📄 PDF Processing:")
            self.logger.info(f"   Files processed: {stats.processed_files}/{stats.total_files}")
            self.logger.info(f"   Laws extracted: {stats.total_laws}")
            self.logger.info(f"   References found: {stats.total_references}")
            self.logger.info(f"   Duration: {duration:.1f} seconds")
            self.logger.info(f"   Errors: {len(stats.errors)}")
        
        # Database stats
        if results.get('database_stats'):
            db_stats = results['database_stats']
            self.logger.info(f"🗄️  Database Status:")
            for table, stats in db_stats.items():
                if isinstance(stats, dict) and 'count' in stats:
                    self.logger.info(f"   {table}: {stats['count']} records")
        
        # Navigation system
        if results.get('navigation_setup'):
            self.logger.info(f"🧭 Navigation: Ready")
        
        # Overall success
        if results['success']:
            self.logger.info("✅ PIPELINE COMPLETED SUCCESSFULLY")
        else:
            self.logger.info("❌ PIPELINE COMPLETED WITH ERRORS")
            for error in results.get('errors', []):
                self.logger.info(f"   Error: {error}")
        
        self.logger.info("=" * 60)
    
    def test_system_functionality(self) -> Dict[str, bool]:
        self.logger.info("🧪 Running system functionality tests...")
        
        tests = {
            'database_connection': False,
            'pdf_parsing_methods': False,
            'duplicate_detection': False,
            'navigation_system': False,
            'law_references': False
        }
        
        try:
            # Test 1: Database connection
            stats = self.db_manager.get_database_stats()
            tests['database_connection'] = 'code_laws' in stats
            
            # Test 2: PDF parsing methods
            available_methods = self.pdf_parser.available_methods
            tests['pdf_parsing_methods'] = len(available_methods) > 0
            
            # Test 3: Duplicate detection
            test_law = {
                'law_number': 'TEST_001',
                'title': 'Test Law',
                'content': 'This is a test law for duplicate detection.',
                'category': 'test'
            }
            duplicate_result = self.db_manager.duplicate_detector.check_duplicate(test_law)
            tests['duplicate_detection'] = not duplicate_result.is_duplicate
            
            # Test 4: Navigation system
            session = self.navigation_api.create_session("test_functionality")
            tests['navigation_system'] = session is not None
            
            # Test 5: Law references (basic pattern matching)
            test_text = "According to Article 12.3, players must follow the rules."
            references = self.navigation_api.cross_ref_engine.find_references_in_text(test_text)
            tests['law_references'] = len(references) > 0
            
        except Exception as e:
            self.logger.error(f"System test failed: {e}")
        
        # Log test results
        self.logger.info("🧪 Test Results:")
        for test_name, passed in tests.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            self.logger.info(f"   {test_name}: {status}")
        
        return tests
    
    def create_sample_data(self) -> bool:
        self.logger.info("📝 Creating sample data...")
        
        sample_laws = [
            {
                'law_number': 'SAMPLE_001',
                'title': 'Basic Bidding Rules',
                'content': 'Players must bid in turn according to Article SAMPLE_002. The auction continues until three consecutive passes occur.',
                'category': 'bidding',
                'source_file': 'sample_laws.pdf',
                'page_number': 1
            },
            {
                'law_number': 'SAMPLE_002',
                'title': 'Turn Order',
                'content': 'The turn order proceeds clockwise starting with the dealer. See Article SAMPLE_001 for bidding procedures.',
                'category': 'procedures',
                'source_file': 'sample_laws.pdf',
                'page_number': 2
            },
            {
                'law_number': 'SAMPLE_003',
                'title': 'Scoring System',
                'content': 'Points are awarded based on contract level and vulnerability. Penalties apply according to Article SAMPLE_004.',
                'category': 'scoring',
                'source_file': 'sample_laws.pdf',
                'page_number': 3
            }
        ]
        
        try:
            batch_result = self.db_manager.batch_insert_laws(sample_laws, skip_duplicates=True)
            success = batch_result.successful > 0
            
            if success:
                self.logger.info(f"✅ Created {batch_result.successful} sample laws")
            else:
                self.logger.warning("⚠️  No sample laws were created")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create sample data: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(
        description="Complete Bridge PDF Parser System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python complete_bridge_parser.py ./pdfs https://your-project.supabase.co your-anon-key
  
  # Test mode with limited files
  python complete_bridge_parser.py ./pdfs https://your-project.supabase.co your-anon-key --test-mode --max-files 2
  
  # Keep existing data
  python complete_bridge_parser.py ./pdfs https://your-project.supabase.co your-anon-key --no-clear
  
  # Run system tests only
  python complete_bridge_parser.py --test-only https://your-project.supabase.co your-anon-key
        """
     )
    
    parser.add_argument('pdf_directory', nargs='?', help='Directory containing PDF files')
    parser.add_argument('supabase_url', help='Supabase project URL')
    parser.add_argument('supabase_key', help='Supabase anon key')
    parser.add_argument('--no-clear', action='store_true', help='Keep existing database data')
    parser.add_argument('--test-mode', action='store_true', help='Run in test mode (limited processing)')
    parser.add_argument('--max-files', type=int, help='Maximum number of files to process')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    parser.add_argument('--log-file', help='Log file path')
    parser.add_argument('--test-only', action='store_true', help='Run system tests only')
    parser.add_argument('--create-sample', action='store_true', help='Create sample data for testing')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize system
        system = CompleteBridgeParserSystem(args.supabase_url, args.supabase_key, args.log_level)
        
        # Run tests only
        if args.test_only:
            logger.info("🧪 Running system tests only...")
            test_results = system.test_system_functionality()
            all_passed = all(test_results.values())
            
            if all_passed:
                logger.info("🎉 All tests passed!")
                sys.exit(0)
            else:
                logger.error("❌ Some tests failed!")
                sys.exit(1)
        
        # Create sample data
        if args.create_sample:
            logger.info("📝 Creating sample data...")
            success = system.create_sample_data()
            if success:
                logger.info("✅ Sample data created successfully")
            else:
                logger.error("❌ Failed to create sample data")
                sys.exit(1)
        
        # Validate PDF directory
        if not args.pdf_directory:
            logger.error("❌ PDF directory is required unless using --test-only")
            sys.exit(1)
        
        # Run complete processing
        results = system.run_complete_processing(
            pdf_directory=args.pdf_directory,
            clear_existing=not args.no_clear,
            test_mode=args.test_mode,
            max_files=args.max_files
        )
        
        # Exit with appropriate code
        if results['success']:
            logger.info("🎉 Processing completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Processing completed with errors!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("⏹️  Processing interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

