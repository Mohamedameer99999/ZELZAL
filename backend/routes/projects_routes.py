from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import Project, Task, Activity
from datetime import datetime, timezone

projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')


@projects_bp.route('', methods=['GET'])
@jwt_required()
def get_projects():
    user_id = get_jwt_identity()
    status = request.args.get('status')
    query = db.session.query(Project).filter(Project.user_id == user_id)
    if status:
        query = query.filter(Project.status == status)
    projects = query.order_by(Project.created_at.desc()).all()
    result = []
    for p in projects:
        p_dict = p.to_dict()
        tasks = db.session.query(Task).filter(Task.project_id == p.id).all()
        p_dict['tasks'] = [t.to_dict() for t in tasks]
        result.append(p_dict)
    return jsonify({'projects': result}), 200


@projects_bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Project name is required'}), 400
    project = Project(
        user_id=user_id,
        name=name,
        description=data.get('description', ''),
        priority=data.get('priority', 'medium'),
        due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
    )
    db.session.add(project)
    activity = Activity(user_id=user_id, action=f'Created project: {name}', category='project')
    db.session.add(activity)
    db.session.commit()
    return jsonify(project.to_dict()), 201


@projects_bp.route('/<project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    project = db.session.query(Project).get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    p_dict = project.to_dict()
    tasks = db.session.query(Task).filter(Task.project_id == project.id).all()
    p_dict['tasks'] = [t.to_dict() for t in tasks]
    return jsonify(p_dict), 200


@projects_bp.route('/<project_id>', methods=['PATCH'])
@jwt_required()
def update_project(project_id):
    project = db.session.query(Project).get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    data = request.get_json() or {}
    for field in ['name', 'description', 'status', 'progress', 'priority']:
        if field in data:
            setattr(project, field, data[field])
    if data.get('due_date'):
        project.due_date = datetime.fromisoformat(data['due_date'])
    project.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify(project.to_dict()), 200


@projects_bp.route('/<project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    project = db.session.query(Project).get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': 'Project deleted'}), 200


@projects_bp.route('/<project_id>/tasks', methods=['POST'])
@jwt_required()
def create_task(project_id):
    project = db.session.query(Project).get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Task title is required'}), 400
    task = Task(
        project_id=project_id,
        title=title,
        description=data.get('description', ''),
        assignee=data.get('assignee', ''),
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@projects_bp.route('/tasks/<task_id>', methods=['PATCH'])
@jwt_required()
def update_task(task_id):
    task = db.session.query(Task).get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    data = request.get_json() or {}
    for field in ['title', 'description', 'status', 'assignee']:
        if field in data:
            setattr(task, field, data[field])
    task.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify(task.to_dict()), 200


@projects_bp.route('/tasks/<task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    task = db.session.query(Task).get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted'}), 200
