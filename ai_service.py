from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
import os


class TaskAIService:
    """Handles AI-powered task analysis"""

    def __init__(self):
        self.model_path = 'models/task_classifier.pkl'
        self.model = None
        self.load_or_train_model()

    def load_or_train_model(self):
        """Load existing model or train new one"""
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
        else:
            self.train_initial_model()

    def train_initial_model(self):
        """Train initial model with sample data"""
        # Sample training data (title + description -> category)
        training_data = [
            ("Fix bug in login", "work"),
            ("Debug authentication issue", "work"),
            ("Complete project report", "work"),
            ("Buy groceries", "personal"),
            ("Call mom", "personal"),
            ("Go to gym", "personal"),
            ("Team meeting on strategy", "meeting"),
            ("Standup with team", "meeting"),
            ("Deploy to production", "work"),
            ("Review pull request", "work"),
        ]

        texts = [item[0] for item in training_data]
        categories = [item[1] for item in training_data]

        # Create pipeline: TF-IDF vectorizer + Naive Bayes classifier
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(lowercase=True, stop_words='english')),
            ('clf', MultinomialNB())
        ])

        self.model.fit(texts, categories)

        # Save model
        os.makedirs('models', exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)

    def categorize_task(self, title, description):
        """Predict task category from title and description"""
        if not self.model:
            return 'general'

        # Combine title and description for better prediction
        text = f"{title} {description}" if description else title
        category = self.model.predict([text])[0]
        confidence = max(self.model.predict_proba([text])[0])

        return category, float(confidence)

    def predict_priority(self, title, description, deadline=None):
        """Predict task priority (1-5)"""
        # Priority heuristics based on task characteristics
        priority = 3  # Default to medium

        keywords_high = ['urgent', 'asap', 'critical', 'emergency', 'bug', 'production']
        keywords_low = ['someday', 'maybe', 'nice to have', 'optional']

        text = f"{title} {description}".lower()

        # Check keywords
        if any(kw in text for kw in keywords_high):
            priority = 5
        elif any(kw in text for kw in keywords_low):
            priority = 1

        # Check deadline urgency
        if deadline:
            from datetime import datetime, timedelta
            days_until = (deadline - datetime.utcnow()).days
            if days_until < 1:
                priority = max(priority, 5)
            elif days_until < 3:
                priority = max(priority, 4)

        return priority

    def estimate_hours(self, title, description, category):
        """Estimate hours needed to complete task"""
        # Category-based estimation (in a real system, this would be more sophisticated)
        estimates = {
            'work': 2.0,
            'meeting': 1.0,
            'personal': 0.5,
            'general': 1.5
        }

        base_estimate = estimates.get(category, 1.5)

        # Adjust based on description length (longer = more complex)
        if description and len(description) > 200:
            base_estimate *= 1.5

        return round(base_estimate, 1)
