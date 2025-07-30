class FlaskTunnelMiddleware:
    """Middleware pour les applications Flask utilisant FlaskTunnel."""
    
    def __init__(self, app):
        self.app = app
        self.subdomain = None
        
        # Wrapper pour tous les URL rules
        self._wrap_url_rules()
    
    def _wrap_url_rules(self):
        """Modifier les règles d'URL pour prendre en compte le subdomain."""
        # Cette fonction pourrait être utilisée pour automatiquement
        # préfixer toutes les routes avec le subdomain détecté
        pass
    
    def __call__(self, environ, start_response):
        """Traiter la requête et ajouter le contexte subdomain."""
        
        # Détecter le subdomain depuis les headers
        subdomain = environ.get('HTTP_X_FLASKTUNNEL_SUBDOMAIN')
        
        if subdomain:
            # Ajouter le subdomain au contexte de la requête
            environ['flasktunnel.subdomain'] = subdomain
            
            # Modifier SCRIPT_NAME pour que Flask génère les bonnes URLs
            if not environ.get('SCRIPT_NAME', '').startswith(f'/{subdomain}'):
                environ['SCRIPT_NAME'] = f'/{subdomain}' + environ.get('SCRIPT_NAME', '')
        
        return self.app(environ, start_response)


# Usage du middleware dans l'application Flask:
# from flasktunnel.middleware import FlaskTunnelMiddleware
# app.wsgi_app = FlaskTunnelMiddleware(app.wsgi_app)


# =============================================================================
# 4. MIDDLEWARE FLASK POUR APPLICATIONS LOCALES (OPTIONNEL)
# =============================================================================

class FlaskTunnelMiddleware:
    """Middleware pour les applications Flask qui utilisent FlaskTunnel."""
    
    def __init__(self, app):
        self.app = app
        self.app.wsgi_app = self
        
    def __call__(self, environ, start_response):
        """Modifier l'environnement WSGI pour tenir compte du préfixe tunnel."""
        
        # Récupérer les headers FlaskTunnel
        subdomain = environ.get('HTTP_X_FLASKTUNNEL_SUBDOMAIN')
        script_name = environ.get('HTTP_X_SCRIPT_NAME')
        
        if subdomain and script_name:
            # Modifier SCRIPT_NAME pour que Flask génère les bons URLs
            environ['SCRIPT_NAME'] = script_name
            
            # Ajuster PATH_INFO si nécessaire
            path_info = environ.get('PATH_INFO', '')
            if path_info.startswith(f'/{subdomain}'):
                environ['PATH_INFO'] = path_info[len(f'/{subdomain}'):]
                if not environ['PATH_INFO']:
                    environ['PATH_INFO'] = '/'
        
        return self.app.wsgi_app(environ, start_response)


# =============================================================================
# 5. EXEMPLE D'UTILISATION DU MIDDLEWARE
# =============================================================================

"""
# Dans votre application Flask locale:

from flask import Flask, url_for, redirect

app = Flask(__name__)

# Appliquer le middleware FlaskTunnel
app = FlaskTunnelMiddleware(app)

@app.route('/')
def index():
    return f'''
    <h1>Page d'accueil</h1>
    <a href="{url_for('login')}">Login</a>
    <a href="{url_for('dashboard')}">Dashboard</a>
    '''

@app.route('/auth/login')
def login():
    return f'''
    <h1>Login</h1>
    <form action="{url_for('do_login')}" method="post">
        <input type="submit" value="Login">
    </form>
    <a href="{url_for('index')}">Retour accueil</a>
    '''

@app.route('/auth/login', methods=['POST'])
def do_login():
    # Redirection qui sera automatiquement corrigée
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return f'''
    <h1>Dashboard</h1>
    <a href="{url_for('index')}">Accueil</a>
    '''

if __name__ == '__main__':
    app.run(debug=True, port=5000)
"""