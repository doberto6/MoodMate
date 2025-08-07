import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import logging

class SentimentAnalyzer:
    """
    Professional sentiment analyzer using VADER and TextBlob
    with psychology-specific enhancements for mood journaling
    """
    
    def __init__(self):
        self.setup_nltk()
        self.sia = SentimentIntensityAnalyzer()
        
        # Psychology and mental health specific word lists
        self.positive_psychology_words = {
            'grateful': 2.0, 'thankful': 1.8, 'blessed': 1.5, 'accomplished': 2.2,
            'proud': 2.0, 'confident': 1.8, 'optimistic': 1.9, 'hopeful': 2.1,
            'peaceful': 1.7, 'content': 1.5, 'fulfilled': 2.3, 'motivated': 1.9,
            'inspired': 2.0, 'energetic': 1.6, 'relaxed': 1.4, 'calm': 1.3,
            'balanced': 1.5, 'centered': 1.4, 'empowered': 2.1, 'resilient': 2.0,
            'progress': 1.7, 'growth': 1.8, 'breakthrough': 2.2, 'healing': 1.9
        }
        
        self.negative_psychology_words = {
            'anxious': -2.1, 'overwhelmed': -2.3, 'depressed': -2.5, 'hopeless': -2.8,
            'frustrated': -1.9, 'lonely': -2.0, 'stressed': -2.2, 'worried': -1.8,
            'disappointed': -1.7, 'exhausted': -2.0, 'burnout': -2.4, 'numb': -1.9,
            'empty': -2.1, 'worthless': -2.7, 'helpless': -2.4, 'trapped': -2.2,
            'confused': -1.5, 'lost': -1.8, 'broken': -2.3, 'struggling': -1.9,
            'panic': -2.6, 'fear': -1.8, 'terror': -2.5, 'dread': -2.2
        }
        
        # Emotional intensity modifiers
        self.intensity_modifiers = {
            'very': 1.3, 'extremely': 1.5, 'incredibly': 1.4, 'really': 1.2,
            'quite': 1.1, 'pretty': 1.1, 'somewhat': 0.8, 'slightly': 0.7,
            'a bit': 0.6, 'a little': 0.6, 'totally': 1.4, 'completely': 1.5
        }
        
    def setup_nltk(self):
        """Download required NLTK data"""
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            print("Downloading VADER lexicon...")
            nltk.download('vader_lexicon', quiet=True)
        
        try:
            nltk.data.find('punkt')
        except LookupError:
            print("Downloading punkt tokenizer...")
            nltk.download('punkt', quiet=True)
    
    def analyze(self, text):
        """
        Comprehensive sentiment analysis combining multiple approaches
        
        Args:
            text (str): Journal entry text to analyze
            
        Returns:
            dict: Sentiment analysis results including scores and classification
        """
        if not text or not text.strip():
            return self._empty_result()
        
        # Preprocess text
        cleaned_text = self.preprocess_text(text)
        
        # VADER sentiment analysis
        vader_scores = self.sia.polarity_scores(cleaned_text)
        
        # TextBlob sentiment analysis
        blob = TextBlob(cleaned_text)
        textblob_polarity = blob.sentiment.polarity
        textblob_subjectivity = blob.sentiment.subjectivity
        
        # Psychology-specific analysis
        psych_score = self.psychology_weighted_analysis(cleaned_text)
        
        # Emotional intensity analysis
        intensity_score = self.analyze_emotional_intensity(cleaned_text)
        
        # Combined weighted score
        combined_score = self.calculate_combined_score(
            vader_scores['compound'],
            textblob_polarity,
            psych_score,
            intensity_score
        )
        
        # Classify sentiment
        sentiment_label = self.classify_sentiment(combined_score)
        
        # Confidence score
        confidence = self.calculate_confidence(
            vader_scores, textblob_polarity, psych_score
        )
        
        return {
            'compound_score': round(combined_score, 3),
            'sentiment_label': sentiment_label,
            'confidence': round(confidence, 3),
            'vader_scores': vader_scores,
            'textblob_polarity': round(textblob_polarity, 3),
            'textblob_subjectivity': round(textblob_subjectivity, 3),
            'psychology_score': round(psych_score, 3),
            'emotional_intensity': round(intensity_score, 3),
            'word_count': len(cleaned_text.split())
        }
    
    def preprocess_text(self, text):
        """Clean and normalize text for analysis"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Handle common contractions
        contractions = {
            "i'm": "i am", "i've": "i have", "i'll": "i will",
            "i'd": "i would", "you're": "you are", "you've": "you have",
            "you'll": "you will", "you'd": "you would", "he's": "he is",
            "she's": "she is", "it's": "it is", "we're": "we are",
            "they're": "they are", "can't": "cannot", "won't": "will not",
            "don't": "do not", "didn't": "did not", "couldn't": "could not",
            "wouldn't": "would not", "shouldn't": "should not"
        }
        
        for contraction, expansion in contractions.items():
            text = re.sub(r'\b' + contraction + r'\b', expansion, text, flags=re.IGNORECASE)
        
        return text.lower()
    
    def psychology_weighted_analysis(self, text):
        """Analyze sentiment using psychology-specific word weights"""
        words = text.split()
        total_score = 0.0
        word_count = len(words)
        
        if word_count == 0:
            return 0.0
        
        for i, word in enumerate(words):
            word_score = 0.0
            
            # Check psychology-specific words
            if word in self.positive_psychology_words:
                word_score = self.positive_psychology_words[word]
            elif word in self.negative_psychology_words:
                word_score = self.negative_psychology_words[word]
            
            # Apply intensity modifiers
            if i > 0 and words[i-1] in self.intensity_modifiers:
                modifier = self.intensity_modifiers[words[i-1]]
                word_score *= modifier
            
            total_score += word_score
        
        # Normalize by word count
        return total_score / word_count
    
    def analyze_emotional_intensity(self, text):
        """Analyze the emotional intensity of the text"""
        words = text.split()
        intensity_indicators = [
            'very', 'extremely', 'incredibly', 'totally', 'completely',
            'absolutely', 'utterly', 'deeply', 'intensely', 'overwhelming',
            'devastating', 'amazing', 'fantastic', 'terrible', 'awful'
        ]
        
        intensity_count = sum(1 for word in words if word in intensity_indicators)
        
        # Punctuation-based intensity (exclamation marks, caps)
        exclamation_count = text.count('!')
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        
        # Combine intensity factors
        intensity_score = (
            (intensity_count / max(len(words), 1)) * 0.5 +
            (exclamation_count / max(len(text.split('.')), 1)) * 0.3 +
            caps_ratio * 0.2
        )
        
        return min(intensity_score, 1.0)  # Cap at 1.0
    
    def calculate_combined_score(self, vader_compound, textblob_polarity, 
                                psych_score, intensity_score):
        """Calculate weighted combination of all sentiment scores"""
        # Weight the different components
        weights = {
            'vader': 0.35,        # VADER is good for social media text
            'textblob': 0.25,     # TextBlob for general sentiment
            'psychology': 0.30,    # Our psychology-specific analysis
            'intensity': 0.10      # Emotional intensity modifier
        }
        
        combined = (
            vader_compound * weights['vader'] +
            textblob_polarity * weights['textblob'] +
            psych_score * weights['psychology'] +
            intensity_score * weights['intensity']
        )
        
        # Ensure score stays within reasonable bounds
        return max(-1.0, min(1.0, combined))
    
    def classify_sentiment(self, combined_score):
        """Classify sentiment based on combined score"""
        if combined_score >= 0.15:
            return 'positive'
        elif combined_score <= -0.15:
            return 'negative'
        else:
            return 'neutral'
    
    def calculate_confidence(self, vader_scores, textblob_polarity, psych_score):
        """Calculate confidence score based on agreement between methods"""
        scores = [vader_scores['compound'], textblob_polarity, psych_score]
        
        # Remove zero scores for confidence calculation
        non_zero_scores = [s for s in scores if abs(s) > 0.05]
        
        if len(non_zero_scores) < 2:
            return 0.5  # Low confidence if only one method has opinion
        
        # Check if scores agree on sentiment direction
        positive_count = sum(1 for s in non_zero_scores if s > 0.1)
        negative_count = sum(1 for s in non_zero_scores if s < -0.1)
        neutral_count = len(non_zero_scores) - positive_count - negative_count
        
        # High confidence if methods agree
        max_agreement = max(positive_count, negative_count, neutral_count)
        agreement_ratio = max_agreement / len(non_zero_scores)
        
        # Factor in absolute values (stronger sentiments = higher confidence)
        avg_magnitude = sum(abs(s) for s in non_zero_scores) / len(non_zero_scores)
        
        confidence = (agreement_ratio * 0.7) + (avg_magnitude * 0.3)
        return min(confidence, 1.0)
    
    def _empty_result(self):
        """Return default result for empty text"""
        return {
            'compound_score': 0.0,
            'sentiment_label': 'neutral',
            'confidence': 0.0,
            'vader_scores': {'compound': 0.0, 'pos': 0.0, 'neu': 1.0, 'neg': 0.0},
            'textblob_polarity': 0.0,
            'textblob_subjectivity': 0.0,
            'psychology_score': 0.0,
            'emotional_intensity': 0.0,
            'word_count': 0
        }
    
    def get_sentiment_summary(self, text):
        """Get a human-readable summary of the sentiment analysis"""
        result = self.analyze(text)
        
        sentiment = result['sentiment_label'].title()
        confidence = result['confidence']
        intensity = result['emotional_intensity']
        
        # Create descriptive summary
        if confidence > 0.8:
            confidence_desc = "very confident"
        elif confidence > 0.6:
            confidence_desc = "confident"
        elif confidence > 0.4:
            confidence_desc = "somewhat confident"
        else:
            confidence_desc = "uncertain"
        
        if intensity > 0.7:
            intensity_desc = "highly emotional"
        elif intensity > 0.4:
            intensity_desc = "moderately emotional"
        else:
            intensity_desc = "calm"
        
        return {
            'sentiment': sentiment,
            'confidence_description': confidence_desc,
            'emotional_intensity_description': intensity_desc,
            'summary': f"{sentiment.lower()} sentiment detected with {confidence_desc} analysis ({intensity_desc} tone)",
            'detailed_scores': result
        }
