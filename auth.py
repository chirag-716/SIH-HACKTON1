"""
Authentication routes for GUVNL Queue Management System
Handles user registration, login, logout, and JWT token management
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, get_jwt
)
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.user import User
from app.services.auth_service import AuthService
from app.utils.validators import validate_email, validate_phone
from app import db
import uuid

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user (citizen)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Validate phone format
        if not validate_phone(data['phone']):
            return jsonify({'message': 'Invalid phone number format'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already registered'}), 400
        
        if User.query.filter_by(phone=data['phone']).first():
            return jsonify({'message': 'Phone number already registered'}), 400
        
        # Create new user
        user = User(
            id=str(uuid.uuid4()),
            email=data['email'].lower().strip(),
            phone=data['phone'],
            password_hash=generate_password_hash(data['password']),
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip(),
            role='citizen'
        )
        
        # Add optional fields
        if data.get('date_of_birth'):
            user.date_of_birth = data['date_of_birth']
        if data.get('address'):
            user.address = data['address']
        
        db.session.add(user)
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            },
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'message': 'Registration failed'}), 500

@bp.route('/login', methods=['POST'])
def login():
    """User login with email/phone and password"""
    try:
        data = request.get_json()
        
        if not data.get('identifier') or not data.get('password'):
            return jsonify({'message': 'Email/phone and password are required'}), 400
        
        identifier = data['identifier'].strip().lower()
        password = data['password']
        
        # Find user by email or phone
        user = User.query.filter(
            (User.email == identifier) | (User.phone == identifier)
        ).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'message': 'Account is deactivated'}), 401
        
        # Update last login
        user.update_last_login()
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'is_verified': user.is_verified
            },
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'message': 'Login failed'}), 500

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using refresh token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'message': 'Invalid user'}), 401
        
        # Create new access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'message': 'Token refresh failed'}), 500

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user and invalidate token"""
    try:
        # In a production system, you'd want to blacklist the token
        # For now, we'll just return success as the frontend will remove the token
        jti = get_jwt()['jti']
        
        # Add token to blacklist (implement blacklist service)
        # BlacklistService.add_token(jti)
        
        return jsonify({'message': 'Logged out successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({'message': 'Logout failed'}), 500

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'phone': user.phone,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'is_verified': user.is_verified,
                'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
                'address': user.address,
                'profile_picture_url': user.profile_picture_url,
                'created_at': user.created_at.isoformat(),
                'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Profile fetch error: {str(e)}")
        return jsonify({'message': 'Failed to fetch profile'}), 500

@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name'].strip()
        if 'last_name' in data:
            user.last_name = data['last_name'].strip()
        if 'phone' in data:
            if not validate_phone(data['phone']):
                return jsonify({'message': 'Invalid phone number format'}), 400
            # Check if phone is already taken by another user
            existing_phone = User.query.filter(
                User.phone == data['phone'], User.id != user.id
            ).first()
            if existing_phone:
                return jsonify({'message': 'Phone number already in use'}), 400
            user.phone = data['phone']
        if 'address' in data:
            user.address = data['address']
        if 'date_of_birth' in data:
            user.date_of_birth = data['date_of_birth']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'phone': user.phone,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'address': user.address,
                'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Profile update error: {str(e)}")
        return jsonify({'message': 'Failed to update profile'}), 500

@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'message': 'Current password and new password are required'}), 400
        
        # Verify current password
        if not check_password_hash(user.password_hash, data['current_password']):
            return jsonify({'message': 'Current password is incorrect'}), 400
        
        # Validate new password
        if len(data['new_password']) < 6:
            return jsonify({'message': 'New password must be at least 6 characters long'}), 400
        
        # Update password
        user.password_hash = generate_password_hash(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Password change error: {str(e)}")
        return jsonify({'message': 'Failed to change password'}), 500

@bp.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify if the current token is valid"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'message': 'Invalid token'}), 401
        
        return jsonify({
            'valid': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        return jsonify({'valid': False, 'message': 'Invalid token'}), 401