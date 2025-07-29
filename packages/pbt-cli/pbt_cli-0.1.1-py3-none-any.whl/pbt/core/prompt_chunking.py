"""Prompt-aware chunking for PBT - create embedding-safe chunks that retain context"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import tiktoken


class ChunkingStrategy(Enum):
    """Strategies for chunking prompts and content"""
    SEMANTIC = "semantic"
    SLIDING_WINDOW = "sliding_window"
    RECURSIVE = "recursive"
    PROMPT_AWARE = "prompt_aware"


@dataclass
class Chunk:
    """A chunk of text with metadata"""
    content: str
    index: int
    metadata: Dict[str, Any]
    token_count: int
    embedding_hints: List[str]
    overlap_start: Optional[str] = None
    overlap_end: Optional[str] = None


@dataclass
class ChunkingConfig:
    """Configuration for chunking"""
    max_tokens: int = 512
    overlap_tokens: int = 50
    min_chunk_size: int = 100
    preserve_sentences: bool = True
    preserve_prompts: bool = True
    add_context: bool = True
    embedding_model: str = "text-embedding-ada-002"


class PromptAwareChunker:
    """Create embedding-safe chunks that retain prompt context"""
    
    def __init__(self, config: Optional[ChunkingConfig] = None):
        self.config = config or ChunkingConfig()
        self.tokenizer = self._init_tokenizer()
        
    def _init_tokenizer(self):
        """Initialize tokenizer for the embedding model"""
        try:
            return tiktoken.encoding_for_model(self.config.embedding_model)
        except:
            # Fallback to cl100k_base encoding
            return tiktoken.get_encoding("cl100k_base")
    
    def chunk_prompt_content(
        self,
        prompt: str,
        content: str,
        strategy: ChunkingStrategy = ChunkingStrategy.PROMPT_AWARE
    ) -> List[Chunk]:
        """Chunk content while preserving prompt context"""
        
        if strategy == ChunkingStrategy.PROMPT_AWARE:
            return self._prompt_aware_chunking(prompt, content)
        elif strategy == ChunkingStrategy.SEMANTIC:
            return self._semantic_chunking(prompt, content)
        elif strategy == ChunkingStrategy.SLIDING_WINDOW:
            return self._sliding_window_chunking(prompt, content)
        elif strategy == ChunkingStrategy.RECURSIVE:
            return self._recursive_chunking(prompt, content)
        else:
            raise ValueError(f"Unknown chunking strategy: {strategy}")
    
    def _prompt_aware_chunking(self, prompt: str, content: str) -> List[Chunk]:
        """Create chunks that preserve prompt context"""
        chunks = []
        
        # Extract key elements from prompt
        prompt_elements = self._extract_prompt_elements(prompt)
        prompt_prefix = self._create_prompt_prefix(prompt_elements)
        prompt_tokens = len(self.tokenizer.encode(prompt_prefix))
        
        # Calculate available tokens for content
        available_tokens = self.config.max_tokens - prompt_tokens - 50  # Buffer
        
        # Split content into semantic units
        semantic_units = self._split_semantic_units(content)
        
        current_chunk = []
        current_tokens = 0
        chunk_index = 0
        
        for unit in semantic_units:
            unit_tokens = len(self.tokenizer.encode(unit))
            
            if current_tokens + unit_tokens > available_tokens and current_chunk:
                # Create chunk with prompt context
                chunk_content = self._format_chunk(
                    prompt_prefix,
                    '\n'.join(current_chunk),
                    chunk_index,
                    len(semantic_units)
                )
                
                chunks.append(Chunk(
                    content=chunk_content,
                    index=chunk_index,
                    metadata={
                        'prompt_elements': prompt_elements,
                        'has_prompt_context': True,
                        'unit_count': len(current_chunk)
                    },
                    token_count=len(self.tokenizer.encode(chunk_content)),
                    embedding_hints=self._generate_embedding_hints(prompt_elements, current_chunk)
                ))
                
                chunk_index += 1
                
                # Start new chunk with overlap
                if self.config.overlap_tokens > 0 and current_chunk:
                    overlap_content = current_chunk[-1]  # Keep last unit as overlap
                    current_chunk = [overlap_content, unit]
                    current_tokens = len(self.tokenizer.encode(overlap_content)) + unit_tokens
                else:
                    current_chunk = [unit]
                    current_tokens = unit_tokens
            else:
                current_chunk.append(unit)
                current_tokens += unit_tokens
        
        # Handle remaining content
        if current_chunk:
            chunk_content = self._format_chunk(
                prompt_prefix,
                '\n'.join(current_chunk),
                chunk_index,
                len(semantic_units)
            )
            
            chunks.append(Chunk(
                content=chunk_content,
                index=chunk_index,
                metadata={
                    'prompt_elements': prompt_elements,
                    'has_prompt_context': True,
                    'unit_count': len(current_chunk),
                    'is_final': True
                },
                token_count=len(self.tokenizer.encode(chunk_content)),
                embedding_hints=self._generate_embedding_hints(prompt_elements, current_chunk)
            ))
        
        return chunks
    
    def _semantic_chunking(self, prompt: str, content: str) -> List[Chunk]:
        """Chunk based on semantic boundaries"""
        chunks = []
        
        # Identify semantic boundaries
        sections = self._identify_sections(content)
        
        for i, section in enumerate(sections):
            # Add prompt context if section is large
            if len(self.tokenizer.encode(section['content'])) > self.config.max_tokens:
                # Recursively chunk large sections
                sub_chunks = self._recursive_chunking(prompt, section['content'])
                for sub_chunk in sub_chunks:
                    sub_chunk.metadata['section'] = section['title']
                chunks.extend(sub_chunks)
            else:
                chunk_content = f"{prompt}\n\nSection: {section['title']}\n{section['content']}"
                
                chunks.append(Chunk(
                    content=chunk_content,
                    index=i,
                    metadata={
                        'section': section['title'],
                        'semantic_type': section['type']
                    },
                    token_count=len(self.tokenizer.encode(chunk_content)),
                    embedding_hints=[section['title']] + section.get('keywords', [])
                ))
        
        return chunks
    
    def _sliding_window_chunking(self, prompt: str, content: str) -> List[Chunk]:
        """Create overlapping chunks with sliding window"""
        chunks = []
        
        # Tokenize content
        tokens = self.tokenizer.encode(content)
        prompt_tokens = self.tokenizer.encode(prompt)
        
        # Calculate window parameters
        content_window = self.config.max_tokens - len(prompt_tokens) - 50
        stride = content_window - self.config.overlap_tokens
        
        for i in range(0, len(tokens), stride):
            # Extract window
            window_tokens = tokens[i:i + content_window]
            
            if len(window_tokens) < self.config.min_chunk_size:
                break
            
            # Decode back to text
            window_text = self.tokenizer.decode(window_tokens)
            
            # Find clean boundaries
            if self.config.preserve_sentences:
                window_text = self._adjust_to_sentence_boundary(window_text)
            
            chunk_content = f"{prompt}\n\n{window_text}"
            
            chunks.append(Chunk(
                content=chunk_content,
                index=len(chunks),
                metadata={
                    'window_start': i,
                    'window_size': len(window_tokens)
                },
                token_count=len(prompt_tokens) + len(window_tokens),
                embedding_hints=self._extract_keywords(window_text)
            ))
        
        return chunks
    
    def _recursive_chunking(self, prompt: str, content: str) -> List[Chunk]:
        """Recursively chunk content based on hierarchical structure"""
        chunks = []
        
        # Define separators in order of preference
        separators = [
            "\n\n\n",  # Triple newline
            "\n\n",    # Double newline  
            "\n",      # Single newline
            ". ",      # Sentence
            ", ",      # Clause
            " "        # Word
        ]
        
        def recursive_split(text: str, depth: int = 0) -> List[str]:
            if len(self.tokenizer.encode(text)) <= self.config.max_tokens - len(self.tokenizer.encode(prompt)):
                return [text]
            
            if depth >= len(separators):
                # Force split at max tokens
                return self._force_split_at_tokens(text)
            
            separator = separators[depth]
            parts = text.split(separator)
            
            result = []
            current = ""
            
            for part in parts:
                if len(self.tokenizer.encode(current + separator + part)) <= self.config.max_tokens - len(self.tokenizer.encode(prompt)):
                    current += (separator if current else "") + part
                else:
                    if current:
                        result.extend(recursive_split(current, depth + 1))
                    current = part
            
            if current:
                result.extend(recursive_split(current, depth + 1))
            
            return result
        
        # Perform recursive splitting
        text_chunks = recursive_split(content)
        
        for i, chunk_text in enumerate(text_chunks):
            chunk_content = f"{prompt}\n\n{chunk_text}"
            
            chunks.append(Chunk(
                content=chunk_content,
                index=i,
                metadata={
                    'recursive_depth': 0,
                    'splitting_method': 'recursive'
                },
                token_count=len(self.tokenizer.encode(chunk_content)),
                embedding_hints=self._extract_keywords(chunk_text)
            ))
        
        return chunks
    
    def _extract_prompt_elements(self, prompt: str) -> Dict[str, Any]:
        """Extract key elements from prompt for context preservation"""
        elements = {
            'instructions': [],
            'constraints': [],
            'examples': [],
            'format': None,
            'keywords': []
        }
        
        # Extract instructions
        instruction_patterns = [
            r'(?:please|you should|you must|need to|have to)\s+([^.!?]+)',
            r'(?:analyze|summarize|extract|identify|find)\s+([^.!?]+)',
        ]
        
        for pattern in instruction_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            elements['instructions'].extend(matches)
        
        # Extract constraints
        constraint_patterns = [
            r'(?:must|should|cannot|don\'t|avoid)\s+([^.!?]+)',
            r'(?:only|exactly|at most|at least)\s+([^.!?]+)',
        ]
        
        for pattern in constraint_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            elements['constraints'].extend(matches)
        
        # Extract format requirements
        format_patterns = [
            r'(?:format|structure|organize|present)(?:\s+(?:as|in|using))?\s+([^.!?]+)',
            r'(?:json|xml|markdown|list|table|bullet\s*points?)',
        ]
        
        for pattern in format_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                elements['format'] = match.group(0)
                break
        
        # Extract keywords
        elements['keywords'] = self._extract_keywords(prompt)
        
        return elements
    
    def _create_prompt_prefix(self, prompt_elements: Dict[str, Any]) -> str:
        """Create a condensed prompt prefix for chunks"""
        prefix_parts = []
        
        # Add main instruction
        if prompt_elements['instructions']:
            prefix_parts.append(f"Task: {prompt_elements['instructions'][0]}")
        
        # Add key constraints
        if prompt_elements['constraints']:
            prefix_parts.append(f"Constraints: {'; '.join(prompt_elements['constraints'][:2])}")
        
        # Add format requirement
        if prompt_elements['format']:
            prefix_parts.append(f"Format: {prompt_elements['format']}")
        
        return '\n'.join(prefix_parts)
    
    def _format_chunk(self, prompt_prefix: str, content: str, index: int, total: int) -> str:
        """Format a chunk with context"""
        parts = [prompt_prefix]
        
        if self.config.add_context:
            parts.append(f"\n[Chunk {index + 1} of ~{total}]")
        
        parts.append(f"\n{content}")
        
        return '\n'.join(parts)
    
    def _split_semantic_units(self, content: str) -> List[str]:
        """Split content into semantic units"""
        units = []
        
        # Try paragraph splitting first
        paragraphs = content.split('\n\n')
        
        for para in paragraphs:
            if len(self.tokenizer.encode(para)) > self.config.max_tokens // 2:
                # Split large paragraphs by sentences
                sentences = re.split(r'(?<=[.!?])\s+', para)
                units.extend(sentences)
            else:
                units.append(para)
        
        return [u.strip() for u in units if u.strip()]
    
    def _identify_sections(self, content: str) -> List[Dict[str, Any]]:
        """Identify sections in content"""
        sections = []
        
        # Look for headers
        header_pattern = r'^(#{1,6}|[A-Z][A-Z\s]{2,}:)\s*(.+)$'
        lines = content.split('\n')
        
        current_section = {'title': 'Introduction', 'content': [], 'type': 'text'}
        
        for line in lines:
            header_match = re.match(header_pattern, line, re.MULTILINE)
            
            if header_match:
                # Save current section
                if current_section['content']:
                    current_section['content'] = '\n'.join(current_section['content'])
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    'title': header_match.group(2).strip(),
                    'content': [],
                    'type': 'section'
                }
            else:
                current_section['content'].append(line)
        
        # Save final section
        if current_section['content']:
            current_section['content'] = '\n'.join(current_section['content'])
            sections.append(current_section)
        
        return sections
    
    def _adjust_to_sentence_boundary(self, text: str) -> str:
        """Adjust text to end at sentence boundary"""
        # Find last sentence boundary
        sentence_ends = ['.', '!', '?']
        
        for i in range(len(text) - 1, max(0, len(text) - 100), -1):
            if text[i] in sentence_ends and i < len(text) - 1 and text[i + 1].isspace():
                return text[:i + 1]
        
        return text
    
    def _force_split_at_tokens(self, text: str) -> List[str]:
        """Force split text at token boundaries"""
        tokens = self.tokenizer.encode(text)
        chunks = []
        
        for i in range(0, len(tokens), self.config.max_tokens):
            chunk_tokens = tokens[i:i + self.config.max_tokens]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
        
        return chunks
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for embedding hints"""
        # Simple keyword extraction
        words = re.findall(r'\b[A-Za-z]{4,}\b', text.lower())
        word_freq = {}
        
        for word in words:
            if word not in ['this', 'that', 'these', 'those', 'which', 'where', 'when', 'what']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:5]]
    
    def _generate_embedding_hints(self, prompt_elements: Dict[str, Any], content_units: List[str]) -> List[str]:
        """Generate embedding hints for better retrieval"""
        hints = []
        
        # Add prompt keywords
        hints.extend(prompt_elements.get('keywords', [])[:3])
        
        # Extract content keywords
        content_text = ' '.join(content_units)
        content_keywords = self._extract_keywords(content_text)
        hints.extend(content_keywords[:3])
        
        # Add semantic type hints
        if any(word in content_text.lower() for word in ['definition', 'meaning', 'what is']):
            hints.append('definition')
        if any(word in content_text.lower() for word in ['example', 'instance', 'such as']):
            hints.append('example')
        if any(word in content_text.lower() for word in ['step', 'process', 'procedure']):
            hints.append('procedure')
        
        return list(set(hints))  # Remove duplicates
    
    def optimize_for_rag(self, chunks: List[Chunk]) -> List[Chunk]:
        """Optimize chunks for RAG systems"""
        optimized = []
        
        for chunk in chunks:
            # Add retrieval-optimized prefix
            keywords = ' '.join(chunk.embedding_hints)
            optimized_content = f"Keywords: {keywords}\n\n{chunk.content}"
            
            optimized_chunk = Chunk(
                content=optimized_content,
                index=chunk.index,
                metadata={**chunk.metadata, 'rag_optimized': True},
                token_count=len(self.tokenizer.encode(optimized_content)),
                embedding_hints=chunk.embedding_hints
            )
            
            optimized.append(optimized_chunk)
        
        return optimized