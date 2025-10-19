from flask import Blueprint, request, jsonify
from ai_service import TaskAIService

ai_bp = Blueprint('ai', __name__, url_prefix='/api/analyze')
ai_service = TaskAIService()


@ai_bp.route('/task', methods=['POST'])
def analyze_task_text():
    """Analyze task text and get AI predictions"""
    data = request.get_json()

    if not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400

    category, confidence = ai_service.categorize_task(
        data['title'],
        data.get('description', '')
    )

    priority = ai_service.predict_priority(
        data['title'],
        data.get('description', ''),
        data.get('deadline')
    )

    estimated_hours = ai_service.estimate_hours(
        data['title'],
        data.get('description', ''),
        category
    )

    return jsonify({
        'title': data['title'],
        'predicted_category': category,
        'category_confidence': confidence,
        'predicted_priority': priority,
        'estimated_hours': estimated_hours
    }), 200
