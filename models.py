from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Entry(db.Model):
    __tablename__ = 'entries'
    
    id = db.Column(db.Integer, primary_key=True)
    mood_rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    sentiment_score = db.Column(db.Float, default=0.0)
    sentiment_label = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'mood_rating': self.mood_rating,
            'content': self.content,
            'sentiment_score': self.sentiment_score,
            'sentiment_label': self.sentiment_label,
            'timestamp': self.timestamp.isoformat(),
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Entry {self.id}: Mood {self.mood_rating}>'

class UserStats(db.Model):
    __tablename__ = 'user_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    total_entries = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    avg_mood = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
