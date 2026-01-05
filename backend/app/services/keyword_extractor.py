"""Keyword extraction service using TF-IDF and embedding analysis."""
import re
from typing import List, Tuple, Optional, Dict, Any
from collections import Counter

import jieba
import jieba.analyse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np


class KeywordExtractor:
    """
    Service for extracting keywords using NLP algorithms.
    
    Combines TF-IDF statistics with embedding-based semantic clustering
    for comprehensive topic discovery.
    """
    
    # Chinese stopwords (common words to filter out)
    STOPWORDS = set([
        "的", "是", "在", "了", "和", "与", "或", "等", "及", "也",
        "有", "为", "对", "到", "以", "可以", "可", "中", "上", "下",
        "这", "那", "之", "如", "其", "不", "就", "都", "而", "被",
        "着", "个", "把", "将", "使", "用", "能", "于", "但", "如果",
        "因为", "所以", "虽然", "但是", "然而", "因此", "并且", "或者",
        "一个", "一种", "一些", "这个", "那个", "什么", "怎么", "如何",
        "进行", "通过", "根据", "按照", "由于", "例如", "比如", "即",
    ])
    
    def __init__(self):
        """Initialize the keyword extractor with jieba."""
        # Load jieba for Chinese tokenization
        jieba.initialize()
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize Chinese text using jieba.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            List of tokens (words)
        """
        # Use jieba for Chinese word segmentation
        words = jieba.cut(text, cut_all=False)
        
        # Filter: keep only meaningful words (length >= 2, not stopwords, mostly Chinese/alphanumeric)
        filtered = []
        for word in words:
            word = word.strip()
            if len(word) >= 2 and word not in self.STOPWORDS:
                # Check if word contains meaningful characters
                if re.search(r'[\u4e00-\u9fff]|[a-zA-Z]{2,}', word):
                    filtered.append(word)
        
        return filtered
    
    def extract_tfidf_keywords(
        self,
        texts: List[str],
        top_n: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Extract keywords using TF-IDF algorithm.
        
        Args:
            texts: List of text documents to analyze
            top_n: Number of top keywords to return
            
        Returns:
            List of (keyword, tfidf_score) tuples sorted by score
        """
        if not texts:
            return []
        
        # Tokenize all texts
        tokenized_texts = [" ".join(self._tokenize(t)) for t in texts]
        
        # Filter empty texts
        tokenized_texts = [t for t in tokenized_texts if t.strip()]
        if not tokenized_texts:
            return []
        
        try:
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=1000,
                min_df=1,
                max_df=0.95,
            )
            
            # Fit and transform
            tfidf_matrix = vectorizer.fit_transform(tokenized_texts)
            
            # Get feature names (words)
            feature_names = vectorizer.get_feature_names_out()
            
            # Calculate average TF-IDF score across all documents
            avg_scores = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
            
            # Create (word, score) pairs and sort
            word_scores = list(zip(feature_names, avg_scores))
            word_scores.sort(key=lambda x: x[1], reverse=True)
            
            return word_scores[:top_n]
            
        except Exception as e:
            print(f"TF-IDF extraction error: {e}")
            return []
    
    def extract_jieba_keywords(
        self,
        text: str,
        top_n: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Extract keywords using jieba's built-in TF-IDF implementation.
        
        This is a simpler alternative that works well for single documents.
        
        Args:
            text: Input text
            top_n: Number of keywords to extract
            
        Returns:
            List of (keyword, weight) tuples
        """
        try:
            keywords = jieba.analyse.extract_tags(
                text,
                topK=top_n,
                withWeight=True
            )
            return keywords
        except Exception as e:
            print(f"Jieba keyword extraction error: {e}")
            return []
    
    def extract_frequent_terms(
        self,
        texts: List[str],
        top_n: int = 10
    ) -> List[Tuple[str, int]]:
        """
        Extract most frequent terms (simple frequency count).
        
        Useful as a baseline or fallback method.
        
        Args:
            texts: List of texts
            top_n: Number of terms to return
            
        Returns:
            List of (term, count) tuples
        """
        all_words = []
        for text in texts:
            all_words.extend(self._tokenize(text))
        
        counter = Counter(all_words)
        return counter.most_common(top_n)
    
    def cluster_by_embedding(
        self,
        texts: List[str],
        embeddings: Optional[List[List[float]]] = None,
        n_clusters: int = 5
    ) -> Dict[int, List[str]]:
        """
        Cluster texts by their embeddings using K-Means.
        
        If embeddings are not provided, falls back to TF-IDF vectors.
        
        Args:
            texts: List of text documents
            embeddings: Optional pre-computed embeddings
            n_clusters: Number of clusters
            
        Returns:
            Dict mapping cluster_id to list of representative terms
        """
        if len(texts) < n_clusters:
            n_clusters = max(1, len(texts))
        
        try:
            if embeddings is None:
                # Use TF-IDF as fallback embedding
                tokenized = [" ".join(self._tokenize(t)) for t in texts]
                tokenized = [t for t in tokenized if t.strip()]
                
                if len(tokenized) < 2:
                    return {0: self._tokenize(texts[0])[:5] if texts else []}
                
                vectorizer = TfidfVectorizer(max_features=500)
                vectors = vectorizer.fit_transform(tokenized).toarray()
                feature_names = vectorizer.get_feature_names_out()
            else:
                vectors = np.array(embeddings)
                feature_names = None
            
            # Apply K-Means
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(vectors)
            
            # Group texts by cluster
            clusters = {}
            for i, label in enumerate(labels):
                if label not in clusters:
                    clusters[label] = []
                # Extract keywords from this text
                if i < len(texts):
                    keywords = self.extract_jieba_keywords(texts[i], top_n=3)
                    clusters[label].extend([kw[0] for kw in keywords])
            
            # Deduplicate within clusters
            for label in clusters:
                clusters[label] = list(set(clusters[label]))[:5]
            
            return clusters
            
        except Exception as e:
            print(f"Embedding clustering error: {e}")
            return {}
    
    def get_trending_topics(
        self,
        texts: List[str],
        top_n: int = 10
    ) -> List[str]:
        """
        Get trending topics by combining TF-IDF and frequency analysis.
        
        This is the main method to call for comprehensive keyword extraction.
        
        Args:
            texts: List of text documents
            top_n: Number of topics to return
            
        Returns:
            List of trending topic keywords
        """
        if not texts:
            return []
        
        # Combine all texts for analysis
        combined_text = "\n".join(texts)
        
        # Method 1: Jieba TF-IDF (optimized for Chinese)
        jieba_keywords = self.extract_jieba_keywords(combined_text, top_n=top_n)
        
        # Method 2: Sklearn TF-IDF (more configurable)
        sklearn_keywords = self.extract_tfidf_keywords(texts, top_n=top_n)
        
        # Merge results, prioritizing jieba for Chinese text
        seen = set()
        result = []
        
        # Add jieba keywords first
        for kw, _ in jieba_keywords:
            if kw not in seen:
                seen.add(kw)
                result.append(kw)
        
        # Add sklearn keywords
        for kw, _ in sklearn_keywords:
            if kw not in seen:
                seen.add(kw)
                result.append(kw)
        
        return result[:top_n]


# Global instance
_keyword_extractor: Optional[KeywordExtractor] = None


def get_keyword_extractor() -> KeywordExtractor:
    """Get or create keyword extractor instance."""
    global _keyword_extractor
    if _keyword_extractor is None:
        _keyword_extractor = KeywordExtractor()
    return _keyword_extractor
