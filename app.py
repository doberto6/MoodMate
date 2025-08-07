from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
from config import Config
from models import db, Entry
from sentiment_analyzer import SentimentAnalyzer

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
sentiment_analyzer = SentimentAnalyzer()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/entries', methods=['GET', 'POST'])
def handle_entries():
    """Handle journal entries - GET all entries or POST new entry"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validate input
            if not data or 'mood' not in data or 'content' not in data:
                return jsonify({'success': False, 'error': 'Missing required fields'}), 400
            
            mood_rating = data['mood']
            content = data['content'].strip()
            
            # Validate mood rating
            if not isinstance(mood_rating, int) or mood_rating < 1 or mood_rating > 5:
                return jsonify({'success': False, 'error': 'Mood rating must be between 1 and 5'}), 400
            
            if not content:
                return jsonify({'success': False, 'error': 'Content cannot be empty'}), 400
            
            # Analyze sentiment
            sentiment_result = sentiment_analyzer.analyze(content)
            
            # Create new entry
            entry = Entry(
                mood_rating=mood_rating,
                content=content,
                sentiment_score=sentiment_result['compound_score'],
                sentiment_label=sentiment_result['sentiment_label'],
                timestamp=datetime.utcnow()
            )
            
            # Save to database
            db.session.add(entry)
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'entry_id': entry.id,
                'sentiment': sentiment_result['sentiment_label']
            })
            
        except Exception as e:
            db.session.rollback()
            print(f"Error saving entry: {e}")
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    # GET request - return all entries
    try:
        entries = Entry.query.order_by(Entry.timestamp.desc()).all()
        return jsonify([entry.to_dict() for entry in entries])
    except Exception as e:
        print(f"Error fetching entries: {e}")
        return jsonify([])

@app.route('/api/analytics')
def get_analytics():
    """Get analytics and insights for the dashboard"""
    try:
        entries = Entry.query.all()
        
        if not entries:
            return jsonify({
                'total_entries': 0,
                'avg_mood': 0.0,
                'streak_days': 0,
                'positive_ratio': 0,
                'insights': []
            })
        
        # Calculate basic statistics
        total_entries = len(entries)
        avg_mood = sum(entry.mood_rating for entry in entries) / total_entries
        positive_entries = sum(1 for entry in entries if entry.mood_rating >= 4)
        positive_ratio = round((positive_entries / total_entries) * 100)
        
        # Calculate current streak
        streak_days = calculate_journal_streak(entries)
        
        # Generate psychology insights
        insights = generate_psychology_insights(entries)
        
        return jsonify({
            'total_entries': total_entries,
            'avg_mood': round(avg_mood, 1),
            'streak_days': streak_days,
            'positive_ratio': positive_ratio,
            'insights': insights
        })
        
    except Exception as e:
        print(f"Error calculating analytics: {e}")
        return jsonify({
            'total_entries': 0,
            'avg_mood': 0.0,
            'streak_days': 0,
            'positive_ratio': 0,
            'insights': []
        })

def calculate_journal_streak(entries):
    """Calculate consecutive days of journaling"""
    if not entries:
        return 0
    
    # Sort entries by date (newest first)
    sorted_entries = sorted(entries, key=lambda x: x.timestamp, reverse=True)
    
    # Get unique dates
    entry_dates = []
    for entry in sorted_entries:
        date = entry.timestamp.date()
        if date not in entry_dates:
            entry_dates.append(date)
    
    if not entry_dates:
        return 0
    
    # Calculate streak
    streak = 0
    today = datetime.now().date()
    current_date = today
    
    # Check if user journaled today or yesterday (to account for time differences)
    if entry_dates[0] == today:
        streak = 1
        current_date = today - timedelta(days=1)
    elif entry_dates[0] == today - timedelta(days=1):
        streak = 1
        current_date = today - timedelta(days=2)
    else:
        return 0
    
    # Count consecutive days
    for date in entry_dates[1:]:
        if date == current_date:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    return streak

def generate_psychology_insights(entries):
    """Generate CBT-inspired insights based on journal entries"""
    insights = []
    
    if len(entries) < 3:
        return [{
            'title': 'Building Self-Awareness 🧠',
            'content': f"You've made {len(entries)} journal entries! Each entry contributes to better self-understanding. Regular journaling is a cornerstone of emotional wellness and cognitive behavioral therapy (CBT)."
        }]
    
    recent_entries = sorted(entries, key=lambda x: x.timestamp, reverse=True)[:7]
    all_moods = [entry.mood_rating for entry in entries]
    recent_moods = [entry.mood_rating for entry in recent_entries]
    
    avg_mood = sum(all_moods) / len(all_moods)
    recent_avg = sum(recent_moods) / len(recent_moods)
    
    # Mood trend analysis
    if recent_avg > avg_mood + 0.5:
        insights.append({
            'title': 'Positive Momentum Detected 📈',
            'content': 'Your recent entries show an upward trend in mood! This suggests that recent changes in your life, thoughts, or behaviors are having a positive impact. Consider what factors might be contributing to this improvement and how you can maintain them.'
        })
    elif recent_avg < avg_mood - 0.5:
        insights.append({
            'title': 'CBT Reflection Opportunity 🤔',
            'content': 'Your recent entries show some challenging periods. Remember that temporary setbacks are normal and part of the human experience. Try identifying any negative thought patterns and practice reframing them with evidence-based thinking.'
        })
    
    # Sentiment analysis insights
    positive_sentiment = sum(1 for entry in entries if entry.sentiment_label == 'positive')
    negative_sentiment = sum(1 for entry in entries if entry.sentiment_label == 'negative')
    
    if positive_sentiment > negative_sentiment * 1.5:
        insights.append({
            'title': 'Positive Language Patterns 😊',
            'content': 'Your journal entries show predominantly positive language patterns. This indicates good emotional regulation and optimistic thinking patterns, which are protective factors for mental health according to positive psychology research.'
        })
    elif negative_sentiment > positive_sentiment:
        insights.append({
            'title': 'Cognitive Reframing Practice 🔄',
            'content': 'Your entries show some negative language patterns. Try the CBT technique of examining one negative thought per day: What evidence supports this thought? What evidence challenges it? What would you tell a friend in this situation?'
        })
    
    # Consistency insight
    if len(entries) >= 7:
        recent_week_entries = [e for e in entries if e.timestamp > datetime.now() - timedelta(days=7)]
        if len(recent_week_entries) >= 5:
            insights.append({
                'title': 'Excellent Consistency! 🌟',
                'content': 'You\'ve been journaling regularly this week! Consistent self-reflection is a key component of emotional wellness and is strongly supported by psychological research on habit formation and mindfulness.'
            })
    
    # Mood variability insight
    if len(entries) >= 10:
        mood_variance = sum((mood - avg_mood) ** 2 for mood in all_moods) / len(all_moods)
        mood_std = mood_variance ** 0.5
        
        if mood_std > 1.2:
            insights.append({
                'title': 'Emotional Range Awareness 📊',
                'content': 'Your mood shows natural variation over time, which is completely normal. If you notice significant swings, consider tracking potential triggers like sleep quality, stress levels, or major life events to identify patterns.'
            })
    
    # Default insight if no specific patterns detected
    if not insights:
        insights.append({
            'title': 'Steady Progress 🎯',
            'content': f'You\'ve maintained an average mood of {avg_mood:.1f}/5 across {len(entries)} entries. This consistent self-monitoring is building emotional intelligence and self-awareness - key components of psychological well-being.'
        })
    
    return insights

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")
        print("Starting MoodMate server...")
        print("Open http://localhost:5000 in your browser")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
