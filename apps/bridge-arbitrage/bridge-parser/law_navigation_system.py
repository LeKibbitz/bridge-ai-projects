#!/usr/bin/env python3
"""
Law Navigation System
====================

Smart navigation system for bridge laws with cross-referencing,
history tracking, and breadcrumb navigation.

Features:
- Click-to-navigate between referenced laws
- Navigation history with back/forward functionality
- Breadcrumb trails for complex navigation paths
- Search and filter capabilities
- Related laws suggestions

Author: BridgeFacile Team
Date: 2025-01-07
"""

from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
import json
import re

@dataclass
class NavigationNode:
    law_id: int
    law_number: str
    title: str
    timestamp: datetime = field(default_factory=datetime.now)
    source_context: Optional[str] = None
    
@dataclass 
class NavigationSession:
    session_id: str
    history: List[NavigationNode] = field(default_factory=list)
    current_index: int = -1
    bookmarks: Set[int] = field(default_factory=set)
    search_history: List[str] = field(default_factory=list)
    
    def add_navigation(self, node: NavigationNode):
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
        
        self.history.append(node)
        self.current_index = len(self.history) - 1
    
    def can_go_back(self) -> bool:
        return self.current_index > 0
    
    def can_go_forward(self) -> bool:
        return self.current_index < len(self.history) - 1
    
    def go_back(self) -> Optional[NavigationNode]:
        if self.can_go_back():
            self.current_index -= 1
            return self.history[self.current_index]
        return None
    
    def go_forward(self) -> Optional[NavigationNode]:
        if self.can_go_forward():
            self.current_index += 1
            return self.history[self.current_index]
        return None
    
    def get_current(self) -> Optional[NavigationNode]:
        if 0 <= self.current_index < len(self.history):
            return self.history[self.current_index]
        return None
    
    def get_breadcrumbs(self, max_items: int = 5) -> List[NavigationNode]:
        if not self.history:
            return []
        
        end_idx = self.current_index + 1
        start_idx = max(0, end_idx - max_items)
        return self.history[start_idx:end_idx]

class LawCrossReferenceEngine:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.reference_cache = {}
        
    def find_references_in_text(self, text: str) -> List[Dict]:
        references = []
        
        patterns = [
            r'(?:Article|Art\.?)\s*(\d+(?:\.\d+)*(?:[A-Z])?)',
            r'(?:Law|Rule|Loi|Règle)\s*(\d+(?:[A-Z])?)',
            r'(?:Section|§)\s*(\d+(?:\.\d+)*)',
            r'(?:voir|see|cf\.?|selon|per)\s*(?:l\')?(?:article|art\.?|law|rule)\s*(\d+(?:\.\d+)*)',
            r'(?:conformément à|according to|as per)\s*(?:l\')?(?:article|art\.?)\s*(\d+(?:\.\d+)*)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                law_number = match.group(1)
                start_pos = match.start()
                end_pos = match.end()
                
                context_start = max(0, start_pos - 100)
                context_end = min(len(text), end_pos + 100)
                context = text[context_start:context_end].strip()
                
                references.append({
                    'law_number': law_number,
                    'position': start_pos,
                    'context': context,
                    'match_text': match.group(0)
                })
        
        return references
    
    def resolve_reference(self, law_number: str) -> Optional[Dict]:
        if law_number in self.reference_cache:
            return self.reference_cache[law_number]
        
        law_data = self.db_manager.get_law_by_number(law_number)
        
        if law_data:
            self.reference_cache[law_number] = law_data
            return law_data
        
        return None
    
    def get_related_laws(self, law_id: int, max_results: int = 10) -> List[Dict]:
        try:
            incoming_refs = self.db_manager.client.table('law_references')\
                .select('source_law_id, code_laws!inner(*)')\
                .eq('target_law_number', law_id)\
                .limit(max_results)\
                .execute()
            
            outgoing_refs = self.db_manager.client.table('law_references')\
                .select('target_law_number')\
                .eq('source_law_id', law_id)\
                .execute()
            
            related = []
            
            if incoming_refs.data:
                for ref in incoming_refs.data:
                    if 'code_laws' in ref:
                        related.append({
                            'law': ref['code_laws'],
                            'relationship': 'references_this',
                            'type': 'incoming'
                        })
            
            if outgoing_refs.data:
                for ref in outgoing_refs.data:
                    target_law = self.resolve_reference(ref['target_law_number'])
                    if target_law:
                        related.append({
                            'law': target_law,
                            'relationship': 'referenced_by_this',
                            'type': 'outgoing'
                        })
            
            return related[:max_results]
            
        except Exception as e:
            print(f"Error finding related laws: {e}")
            return []
    
    def create_clickable_text(self, text: str, current_law_id: int) -> str:
        references = self.find_references_in_text(text)
        
        references.sort(key=lambda x: x['position'], reverse=True)
        
        clickable_text = text
        
        for ref in references:
            law_data = self.resolve_reference(ref['law_number'])
            if law_data and law_data['id'] != current_law_id:
                link_html = f'<a href="#" class="law-reference" data-law-id="{law_data["id"]}" data-law-number="{ref["law_number"]}" title="{law_data.get("title", "")}">{ref["match_text"]}</a>'
                
                start = ref['position']
                end = start + len(ref['match_text'])
                clickable_text = clickable_text[:start] + link_html + clickable_text[end:]
        
        return clickable_text

class LawSearchEngine:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def search_laws(self, query: str, filters: Dict = None, limit: int = 20) -> List[Dict]:
        try:
            query_builder = self.db_manager.client.table('code_laws').select('*')
            
            if query:
                query_builder = query_builder.or_(f'title.ilike.%{query}%,content.ilike.%{query}%,law_number.ilike.%{query}%')
            
            if filters:
                if 'category' in filters:
                    query_builder = query_builder.eq('category', filters['category'])
                if 'source_file' in filters:
                    query_builder = query_builder.eq('source_file', filters['source_file'])
                if 'min_char_count' in filters:
                    query_builder = query_builder.gte('char_count', filters['min_char_count'])
            
            result = query_builder.limit(limit).execute()
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def get_law_suggestions(self, partial_number: str) -> List[Dict]:
        try:
            result = self.db_manager.client.table('code_laws')\
                .select('law_number, title')\
                .ilike('law_number', f'{partial_number}%')\
                .limit(10)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Suggestion error: {e}")
            return []

class LawNavigationAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.cross_ref_engine = LawCrossReferenceEngine(db_manager)
        self.search_engine = LawSearchEngine(db_manager)
        self.active_sessions = {}
    
    def create_session(self, session_id: str) -> NavigationSession:
        session = NavigationSession(session_id=session_id)
        self.active_sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[NavigationSession]:
        return self.active_sessions.get(session_id)
    
    def navigate_to_law(self, session_id: str, law_id: int, context: str = None) -> Dict:
        session = self.get_session(session_id)
        if not session:
            session = self.create_session(session_id)
        
        try:
            result = self.db_manager.client.table('code_laws')\
                .select('*')\
                .eq('id', law_id)\
                .single()\
                .execute()
            
            if not result.data:
                return {'error': 'Law not found'}
            
            law_data = result.data
            
            node = NavigationNode(
                law_id=law_id,
                law_number=law_data['law_number'],
                title=law_data['title'],
                source_context=context
            )
            
            session.add_navigation(node)
            
            enhanced_data = self._enhance_law_data(law_data, session_id)
            
            return {
                'law': enhanced_data,
                'navigation': {
                    'can_go_back': session.can_go_back(),
                    'can_go_forward': session.can_go_forward(),
                    'breadcrumbs': [
                        {'law_number': n.law_number, 'title': n.title} 
                        for n in session.get_breadcrumbs()
                    ]
                }
            }
            
        except Exception as e:
            return {'error': f'Navigation error: {e}'}
    
    def navigate_back(self, session_id: str) -> Dict:
        session = self.get_session(session_id)
        if not session:
            return {'error': 'No active session'}
        
        previous_node = session.go_back()
        if not previous_node:
            return {'error': 'Cannot go back'}
        
        return self.navigate_to_law(session_id, previous_node.law_id, "Back navigation")
    
    def navigate_forward(self, session_id: str) -> Dict:
        session = self.get_session(session_id)
        if not session:
            return {'error': 'No active session'}
        
        next_node = session.go_forward()
        if not next_node:
            return {'error': 'Cannot go forward'}
        
        return self.navigate_to_law(session_id, next_node.law_id, "Forward navigation")
    
    def _enhance_law_data(self, law_data: Dict, session_id: str) -> Dict:
        enhanced = law_data.copy()
        
        enhanced['clickable_content'] = self.cross_ref_engine.create_clickable_text(
            law_data['content'], 
            law_data['id']
        )
        
        enhanced['related_laws'] = self.cross_ref_engine.get_related_laws(law_data['id'])
        
        enhanced['references'] = self.cross_ref_engine.find_references_in_text(law_data['content'])
        
        return enhanced
    
    def search(self, session_id: str, query: str, filters: Dict = None) -> Dict:
        session = self.get_session(session_id)
        if session and query:
            session.search_history.append(query)
        
        results = self.search_engine.search_laws(query, filters)
        
        return {
            'results': results,
            'total': len(results),
            'query': query,
            'filters': filters or {}
        }
    
    def get_suggestions(self, partial_number: str) -> List[Dict]:
        return self.search_engine.get_law_suggestions(partial_number)
    
    def export_session_data(self, session_id: str) -> Dict:
        session = self.get_session(session_id)
        if not session:
            return {}
        
        return {
            'session_id': session.session_id,
            'history': [
                {
                    'law_id': node.law_id,
                    'law_number': node.law_number,
                    'title': node.title,
                    'timestamp': node.timestamp.isoformat(),
                    'source_context': node.source_context
                }
                for node in session.history
            ],
            'current_index': session.current_index,
            'bookmarks': list(session.bookmarks),
            'search_history': session.search_history
        }


if __name__ == "__main__":
    print("Law Navigation System - Ready for integration!")
    print("Features:")
    print("✅ Click-to-navigate between laws")
    print("✅ Back/Forward navigation with history")
    print("✅ Breadcrumb trails")
    print("✅ Related laws suggestions")
    print("✅ Advanced search with filters")
    print("✅ Session persistence")

