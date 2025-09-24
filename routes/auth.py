from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import hashlib
from database import create_user, get_user_by_email

auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    """Hash un mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email et mot de passe requis', 'error')
            return render_template('auth/login.html')
        
        user = get_user_by_email(email)
        if user and user[3] == hash_password(password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            
            # Mettre à jour la dernière connexion
            from database import update_last_login
            update_last_login(user[0])
            
            return redirect(url_for('web.index'))
        else:
            flash('Email ou mot de passe incorrect', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Page d'inscription"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([username, email, password, confirm_password]):
            flash('Tous les champs sont requis', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères', 'error')
            return render_template('auth/register.html')
        
        password_hash = hash_password(password)
        user_id = create_user(username, email, password_hash)
        
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            flash('Compte créé avec succès!', 'success')
            return redirect(url_for('web.index'))
        else:
            flash('Email ou nom d\'utilisateur déjà utilisé', 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    """Déconnexion"""
    session.clear()
    return redirect(url_for('auth.login'))