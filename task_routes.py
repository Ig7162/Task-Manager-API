from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Task, db
from ai_service import TaskAIService
from datetime import datetime

task_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')
ai_service = TaskAIService()


@task_bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    """Get all tasks for current user with filtering and pagination"""
    user_id = get_jwt_identity()

    # Get query parameters
    status = request.args.get('status')
    priority = request.args.get('priority')
    category = request.args.get('category')
    sort_by = request.args.get('sort_by', 'created_at')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    # Start query
    query = Task.query.filter_by(user_id=user_id)

    # Apply filters
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=int(priority))
    if category:
        query = query.filter_by(category=category)

    # Sorting
    if sort_by == 'deadline':
        query = query.order_by(Task.deadline.asc())
    elif sort_by == 'priority':
        query = query.order_by(Task.priority.desc())
    else:
        query = query.order_by(Task.created_at.desc())

    # Pagination
    paginated = query.paginate(page=page, per_page=limit)

    return jsonify({
        'tasks': [task.to_dict() for task in paginated.items],
        'total': paginated.total,
        'page': page,
        'pages': paginated.pages
    }), 200


@task_bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    """Create new task with AI analysis"""
    user_id = get_jwt_identity()
    data = request.get_json()

    # Validation
    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400

    # AI Analysis
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

    # Parse deadline if provided
    deadline = None
    if data.get('deadline'):
        try:
            deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            deadline = None

    # Create task
    task = Task(
        user_id=user_id,
        title=data['title'],
        description=data.get('description'),
        category=category,
        priority=priority,
        estimated_hours=estimated_hours,
        deadline=deadline,
        status='todo',
        tags=','.join(data.get('tags', []))
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({
        'message': 'Task created successfully',
        'task': task.to_dict(),
        'ai_analysis': {
            'category': category,
            'category_confidence': confidence,
            'priority': priority,
            'estimated_hours': estimated_hours
        }
    }), 201


@task_bp.route('/<task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get specific task"""
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    return jsonify({'task': task.to_dict()}), 200


@task_bp.route('/<task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update task"""
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    data = request.get_json()

    # Update fields
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'priority' in data:
        task.priority = data['priority']
    if 'status' in data:
        task.status = data['status']
    if 'deadline' in data:
        if data['deadline']:
            try:
                task.deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                task.deadline = None
        else:
            task.deadline = None
    if 'tags' in data:
        task.tags = ','.join(data['tags'])

    db.session.commit()

    return jsonify({
        'message': 'Task updated successfully',
        'task': task.to_dict()
    }), 200


@task_bp.route('/<task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete task"""
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({'message': 'Task deleted successfully'}), 200


@task_bp.route('/<task_id>/status', methods=['PATCH'])
@jwt_required()
def update_task_status(task_id):
    """Update only task status"""
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    data = request.get_json()

    if not data.get('status'):
        return jsonify({'error': 'Status is required'}), 400

    if data['status'] not in ['todo', 'in_progress', 'completed']:
        return jsonify({'error': 'Invalid status'}), 400

    task.status = data['status']
    db.session.commit()

    return jsonify({
        'message': 'Task status updated',
        'task': task.to_dict()
    }), 200
