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
