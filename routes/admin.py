from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import hashlib
from database import get_admin_stats, get_all_users, delete_user, reset_user_password, get_user_by_id

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Décorateur pour protéger les routes admin"""
    from functools import wraps
    import sqlite3
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        # Vérifier si l'utilisateur est admin
        conn = sqlite3.connect('conversations.db')
        cursor = conn.cursor()
        cursor.execute('SELECT is_admin FROM users WHERE id = ?', (session['user_id'],))
        result = cursor.fetchone()
        conn.close()
        
        if not result or not result[0]:
            flash('Accès refusé - Droits administrateur requis', 'error')
            return redirect(url_for('web.index'))
        
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def dashboard():
    """Tableau de bord administrateur"""
    stats = get_admin_stats()
    users = get_all_users()
    return render_template('admin/dashboard.html', stats=stats, users=users)

@admin_bp.route('/users')
@admin_required
def users():
    """Gestion des utilisateurs"""
    users_list = get_all_users()
    return render_template('admin/users.html', users=users_list)

@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user_route(user_id):
    """Supprimer un utilisateur"""
    try:
        delete_user(user_id)
        flash('Utilisateur supprimé avec succès', 'success')
    except Exception as e:
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/reset-password/<int:user_id>', methods=['POST'])
@admin_required
def reset_password_route(user_id):
    """Réinitialiser le mot de passe d'un utilisateur"""
    new_password = request.form.get('new_password', 'password123')
    
    try:
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        reset_user_password(user_id, password_hash)
        flash(f'Mot de passe réinitialisé à: {new_password}', 'success')
    except Exception as e:
        flash(f'Erreur lors de la réinitialisation: {str(e)}', 'error')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/api/stats')
@admin_required
def api_stats():
    """API pour les statistiques en temps réel"""
    stats = get_admin_stats()
    return jsonify(stats)