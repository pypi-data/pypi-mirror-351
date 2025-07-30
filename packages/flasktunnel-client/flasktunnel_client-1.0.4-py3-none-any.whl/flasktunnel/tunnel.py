# =============================================================================
# flasktunnel/tunnel.py - VERSION CORRIGÉE AVEC PRÉSERVATION DU SUBDOMAIN
# =============================================================================

import time
import threading
import socketio
import requests
from enum import Enum
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
import base64
import re
from urllib.parse import urljoin, urlparse


class TunnelStatus(Enum):
    """États possibles d'un tunnel."""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    EXPIRED = "expired"


@dataclass
class TunnelInfo:
    tunnel_id: str
    public_url: str
    local_url: str
    subdomain: str
    status: TunnelStatus
    created_at: float
    expires_at: float
    port: int
    requests_count: int = 0
    password_protected: bool = False
    custom_domain: Optional[str] = None


class Tunnel:
    """Représentation d'un tunnel FlaskTunnel - VERSION CORRIGÉE AVEC SUBDOMAIN."""
    
    def __init__(self, info: TunnelInfo, server_url: str = "https://flasktunnel.up.railway.app/"):
        self.info = info
        self.server_url = server_url.rstrip('/')
        self.connection = None
        self.status = TunnelStatus.CONNECTING
        self.event_handlers = {}
        self._stop_event = threading.Event()
        self._connection_retries = 0
        self._max_retries = 5
        
        # Extraire le base_url du serveur pour les redirections
        parsed_url = urlparse(self.info.public_url)
        self.tunnel_base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
    @property
    def tunnel_id(self) -> str:
        return self.info.tunnel_id
    
    @property
    def public_url(self) -> str:
        return self.info.public_url
    
    @property
    def local_url(self) -> str:
        return self.info.local_url
    
    @property
    def dashboard_url(self) -> str:
        return f"{self.server_url}/dashboard/{self.tunnel_id}"
    
    @property
    def is_active(self) -> bool:
        return self.status == TunnelStatus.CONNECTED
    
    @property
    def is_expired(self) -> bool:
        return time.time() > self.info.expires_at
    
    @property
    def remaining_time(self) -> int:
        """Temps restant en secondes."""
        remaining = int(self.info.expires_at - time.time())
        return max(0, remaining)
    
    def _rewrite_html_urls(self, html_content: str, base_path: str = "/") -> str:
        """Réécrire les URLs dans le contenu HTML pour préserver le subdomain."""
        if not html_content or not isinstance(html_content, str):
            return html_content
        
        # Construire le préfixe du subdomain
        subdomain_prefix = f"/{self.info.subdomain}"
        
        # Patterns pour différents types d'URLs
        patterns = [
            # href="/" ou href="/path"
            (r'href\s*=\s*["\'](\s*/[^"\']*)["\']', lambda m: f'href="{subdomain_prefix}{m.group(1)}"'),
            
            # src="/" ou src="/path" 
            (r'src\s*=\s*["\'](\s*/[^"\']*)["\']', lambda m: f'src="{subdomain_prefix}{m.group(1)}"'),
            
            # action="/" ou action="/path"
            (r'action\s*=\s*["\'](\s*/[^"\']*)["\']', lambda m: f'action="{subdomain_prefix}{m.group(1)}"'),
            
            # URLs dans les scripts JavaScript - fetch('/path')
            (r'fetch\s*\(\s*["\'](\s*/[^"\']*)["\']', lambda m: f'fetch("{subdomain_prefix}{m.group(1)}"'),
            
            # URLs dans les scripts JavaScript - axios.get('/path')
            (r'axios\.(get|post|put|delete|patch)\s*\(\s*["\'](\s*/[^"\']*)["\']', 
             lambda m: f'axios.{m.group(1)}("{subdomain_prefix}{m.group(2)}"'),
            
            # XMLHttpRequest.open('GET', '/path')
            (r'\.open\s*\(\s*["\'][^"\']*["\']\s*,\s*["\'](\s*/[^"\']*)["\']', 
             lambda m: m.group(0).replace(m.group(1), f"{subdomain_prefix}{m.group(1)}")),
            
            # window.location.href = '/path'
            (r'window\.location\.href\s*=\s*["\'](\s*/[^"\']*)["\']', 
             lambda m: f'window.location.href = "{subdomain_prefix}{m.group(1)}"'),
            
            # location.href = '/path'
            (r'location\.href\s*=\s*["\'](\s*/[^"\']*)["\']', 
             lambda m: f'location.href = "{subdomain_prefix}{m.group(1)}"'),
        ]
        
        modified_html = html_content
        
        for pattern, replacement in patterns:
            try:
                modified_html = re.sub(pattern, replacement, modified_html, flags=re.IGNORECASE)
            except Exception as e:
                print(f"⚠️ Erreur lors de la réécriture d'URL avec le pattern {pattern}: {e}")
                continue
        
        return modified_html
    
    def _rewrite_redirect_location(self, location_header: str) -> str:
        """Réécrire les headers Location pour les redirections."""
        if not location_header:
            return location_header
        
        # Si c'est une URL relative qui commence par /
        if location_header.startswith('/'):
            return f"/{self.info.subdomain}{location_header}"
        
        # Si c'est une URL absolue pointant vers localhost
        if 'localhost' in location_header or '127.0.0.1' in location_header:
            parsed = urlparse(location_header)
            # Remplacer par l'URL du tunnel avec le subdomain
            new_path = f"/{self.info.subdomain}{parsed.path}"
            if parsed.query:
                new_path += f"?{parsed.query}"
            if parsed.fragment:
                new_path += f"#{parsed.fragment}"
            return f"{self.tunnel_base_url}{new_path}"
        
        return location_header
    
    def connect_websocket(self):
        """Établir la connexion WebSocket pour le tunneling - VERSION CORRIGÉE."""
        try:
            print(f"🔄 Tentative de connexion WebSocket à {self.server_url}")
            
            # Configuration du client Socket.IO avec options améliorées
            sio = socketio.Client(
                reconnection=True,
                reconnection_attempts=self._max_retries,
                reconnection_delay=2,
                reconnection_delay_max=10,
                logger=False,  # Désactiver les logs verbeux
                engineio_logger=False
            )
            
            # =================================================================
            # GESTIONNAIRES D'ÉVÉNEMENTS WEBSOCKET
            # =================================================================
            
            @sio.on('connect')
            def on_connect():
                print(f"🔗 WebSocket connecté pour le tunnel {self.tunnel_id}")
                self.status = TunnelStatus.CONNECTED
                self._connection_retries = 0
                
                # Rejoindre la room du tunnel immédiatement
                sio.emit('join_tunnel', {'tunnel_id': self.tunnel_id})
            
            @sio.on('connection_confirmed')
            def on_connection_confirmed(data):
                print(f"✅ Connexion confirmée: {data}")
            
            @sio.on('tunnel_joined')
            def on_tunnel_joined(data):
                print(f"✅ Tunnel rejoint avec succès: {data}")
                self._trigger_event('connected', data)
            
            @sio.on('tunnel_request')
            def on_tunnel_request(data):
                """Traiter une requête HTTP reçue via WebSocket - CORRIGÉ AVEC SUBDOMAIN."""
                try:
                    request_id = data.get('request_id')
                    method = data.get('method', 'GET')
                    path = data.get('path', '/')
                    headers = data.get('headers', {})
                    body = data.get('body')
                    params = data.get('params', {})
                    
                    print(f"📥 Requête reçue: {method} {path} (ID: {request_id})")
                    
                    # Enlever le préfixe du subdomain du chemin si présent
                    subdomain_prefix = f"/{self.info.subdomain}"
                    if path.startswith(subdomain_prefix):
                        clean_path = path[len(subdomain_prefix):]
                        if not clean_path.startswith('/'):
                            clean_path = '/' + clean_path
                    else:
                        clean_path = path
                    
                    # Construire l'URL locale
                    local_url = f"http://localhost:{self.info.port}{clean_path}"
                    
                    # Nettoyer les headers problématiques
                    cleaned_headers = {}
                    skip_headers = {
                        'host', 'connection', 'upgrade', 'sec-websocket-key',
                        'sec-websocket-version', 'sec-websocket-extensions',
                        'content-length'  # Sera recalculé automatiquement
                    }
                    
                    for key, value in headers.items():
                        if key.lower() not in skip_headers:
                            cleaned_headers[key] = value
                    
                    # Préparer les paramètres de la requête
                    request_kwargs = {
                        'method': method,
                        'url': local_url,
                        'headers': cleaned_headers,
                        'params': params,
                        'timeout': 25,  # Timeout plus court que le serveur
                        'allow_redirects': False,  # Gérer manuellement les redirections
                        'stream': False
                    }
                    
                    # Ajouter le body si présent
                    if body and method.upper() in ['POST', 'PUT', 'PATCH']:
                        if isinstance(body, str):
                            request_kwargs['data'] = body
                        else:
                            request_kwargs['data'] = str(body)
                    
                    # Faire la requête vers l'application locale
                    try:
                        response = requests.request(**request_kwargs)
                        
                        # Déterminer si le contenu est binaire
                        content_type = response.headers.get('content-type', '').lower()
                        is_binary = self._is_binary_content(content_type)
                        
                        # Préparer les headers de réponse
                        response_headers = dict(response.headers)
                        
                        # Traiter les redirections
                        if response.status_code in [301, 302, 303, 307, 308]:
                            location = response_headers.get('location', '')
                            if location:
                                rewritten_location = self._rewrite_redirect_location(location)
                                response_headers['location'] = rewritten_location
                                print(f"🔄 Redirection réécrite: {location} → {rewritten_location}")
                        
                        # Préparer la réponse
                        response_data = {
                            'request_id': request_id,
                            'status_code': response.status_code,
                            'headers': response_headers,
                            'binary': is_binary
                        }
                        
                        # Encoder le contenu selon son type
                        if is_binary:
                            import base64
                            response_data['content'] = base64.b64encode(response.content).decode('ascii')
                        else:
                            try:
                                content = response.content.decode('utf-8')
                                
                                # Réécrire les URLs dans le contenu HTML
                                if 'text/html' in content_type:
                                    content = self._rewrite_html_urls(content, clean_path)
                                    print(f"🔧 URLs réécrites dans le contenu HTML pour le subdomain {self.info.subdomain}")
                                
                                response_data['content'] = content
                                
                            except UnicodeDecodeError:
                                try:
                                    content = response.content.decode('utf-8', errors='replace')
                                    # Réécrire les URLs même avec les erreurs de décodage
                                    if 'text/html' in content_type:
                                        content = self._rewrite_html_urls(content, clean_path)
                                    response_data['content'] = content
                                except:
                                    # En dernier recours, traiter comme binaire
                                    import base64
                                    response_data['content'] = base64.b64encode(response.content).decode('ascii')
                                    response_data['binary'] = True
                        
                        print(f"✅ Réponse {response.status_code} pour {method} {clean_path}")
                        
                    except requests.ConnectionError:
                        print(f"❌ Service local non disponible sur le port {self.info.port}")
                        response_data = {
                            'request_id': request_id,
                            'error': f'Connection refused to localhost:{self.info.port}',
                            'status_code': 502,
                            'headers': {'content-type': 'text/html'},
                            'content': f'''<!DOCTYPE html>
<html>
<head>
    <title>Service Unavailable</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .error {{ background: #fee; border: 1px solid #fcc; padding: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="error">
        <h1>Service Unavailable</h1>
        <p>No application is running on localhost:{self.info.port}</p>
        <p>Please start your application and try again.</p>
        <p><strong>Tunnel:</strong> {self.info.public_url}</p>
    </div>
</body>
</html>'''
                        }
                    
                    except requests.Timeout:
                        print(f"⏰ Timeout pour {method} {clean_path}")
                        response_data = {
                            'request_id': request_id,
                            'error': 'Local service timeout',
                            'status_code': 504,
                            'headers': {'content-type': 'text/html'},
                            'content': '''<!DOCTYPE html>
<html>
<head>
    <title>Gateway Timeout</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .error { background: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="error">
        <h1>Gateway Timeout</h1>
        <p>The local service took too long to respond (>25s).</p>
    </div>
</body>
</html>'''
                        }
                    
                    except Exception as req_error:
                        print(f"❌ Erreur requête locale: {req_error}")
                        response_data = {
                            'request_id': request_id,
                            'error': f'Local request error: {str(req_error)}',
                            'status_code': 500,
                            'headers': {'content-type': 'text/html'},
                            'content': f'''<!DOCTYPE html>
<html>
<head>
    <title>Internal Server Error</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .error {{ background: #fee; border: 1px solid #fcc; padding: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="error">
        <h1>Internal Server Error</h1>
        <p>Error while processing the request:</p>
        <pre>{str(req_error)}</pre>
    </div>
</body>
</html>'''
                        }
                    
                    # Envoyer la réponse au serveur
                    try:
                        sio.emit('tunnel_response', response_data)
                        self.info.requests_count += 1
                        
                        # Déclencher l'événement de requête
                        self._trigger_event('request', {
                            'method': method,
                            'path': clean_path,
                            'original_path': path,
                            'subdomain': self.info.subdomain,
                            'ip': data.get('ip', 'unknown'),
                            'user_agent': headers.get('user-agent', 'unknown'),
                            'status_code': response_data.get('status_code', 500)
                        })
                        
                    except Exception as emit_error:
                        print(f"❌ Erreur lors de l'envoi de la réponse: {emit_error}")
                
                except Exception as e:
                    print(f"❌ Erreur critique dans on_tunnel_request: {e}")
                    try:
                        # Envoyer une réponse d'erreur en dernier recours
                        error_response = {
                            'request_id': data.get('request_id', 'unknown'),
                            'error': f'Critical error: {str(e)}',
                            'status_code': 500,
                            'headers': {'content-type': 'text/html'},
                            'content': f'''<!DOCTYPE html>
<html>
<head>
    <title>Critical Error</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .error {{ background: #fee; border: 1px solid #fcc; padding: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="error">
        <h1>Critical Error</h1>
        <p>An unexpected error occurred:</p>
        <pre>{str(e)}</pre>
    </div>
</body>
</html>'''
                        }
                        sio.emit('tunnel_response', error_response)
                    except:
                        pass  # Ignorer si même l'envoi d'erreur échoue
            
            @sio.on('tunnel_expired')
            def on_tunnel_expired(data):
                print("⏰ Le tunnel a expiré")
                self.status = TunnelStatus.EXPIRED
                self._trigger_event('expired', data)
            
            @sio.on('tunnel_error')
            def on_tunnel_error(data):
                error_msg = data.get('message', 'Erreur inconnue')
                print(f"❌ Erreur tunnel: {error_msg}")
                self.status = TunnelStatus.ERROR
                self._trigger_event('error', data)
            
            @sio.on('error')
            def on_error(data):
                error_msg = data.get('message', 'Erreur WebSocket inconnue')
                print(f"❌ Erreur WebSocket: {error_msg}")
            
            @sio.on('disconnect')
            def on_disconnect(reason=None):
                print(f"❌ WebSocket déconnecté: {reason}")
                self.status = TunnelStatus.DISCONNECTED
                
                # Tentative de reconnexion si pas d'arrêt explicite
                if not self._stop_event.is_set() and self._connection_retries < self._max_retries:
                    self._connection_retries += 1
                    print(f"🔄 Tentative de reconnexion {self._connection_retries}/{self._max_retries}")
                    threading.Timer(2.0, self._reconnect_websocket).start()
            
            # =================================================================
            # CONNEXION AU SERVEUR
            # =================================================================
            
            # Se connecter au serveur Socket.IO
            sio.connect(
                self.server_url,
                transports=['websocket', 'polling'],
                wait_timeout=10
            )
            
            self.connection = sio
            
        except Exception as e:
            print(f"❌ Erreur de connexion WebSocket: {e}")
            self.status = TunnelStatus.ERROR
            
            # Tentative de reconnexion si pas d'arrêt explicite
            if not self._stop_event.is_set() and self._connection_retries < self._max_retries:
                self._connection_retries += 1
                print(f"🔄 Reconnexion dans 5s... ({self._connection_retries}/{self._max_retries})")
                threading.Timer(5.0, self._reconnect_websocket).start()
            else:
                raise Exception(f"Impossible d'établir la connexion WebSocket après {self._max_retries} tentatives: {e}")
    
    def _reconnect_websocket(self):
        """Tentative de reconnexion WebSocket."""
        if not self._stop_event.is_set():
            try:
                self.connect_websocket()
            except Exception as e:
                print(f"❌ Échec de reconnexion: {e}")
    
    def _is_binary_content(self, content_type: str) -> bool:
        """Déterminer si le contenu est binaire."""
        if not content_type:
            return False
            
        # Types de contenu binaire
        binary_types = [
            'image/', 'video/', 'audio/', 'application/pdf',
            'application/zip', 'application/octet-stream',
            'application/x-binary', 'font/', 'application/msword',
            'application/vnd.', 'application/x-', 'multipart/form-data'
        ]
        
        # Types de contenu texte explicites
        text_types = [
            'text/', 'application/json', 'application/xml',
            'application/javascript', 'application/x-javascript',
            'application/x-www-form-urlencoded'
        ]
        
        content_type_lower = content_type.lower()
        
        # Vérifier d'abord les types texte
        if any(content_type_lower.startswith(tt) for tt in text_types):
            return False
        
        # Puis vérifier les types binaires
        return any(content_type_lower.startswith(bt) for bt in binary_types)
    
    def on(self, event: str, handler: Callable):
        """Enregistrer un gestionnaire d'événement."""
        self.event_handlers[event] = handler
    
    def _trigger_event(self, event: str, data: Any = None) -> None:
        """Déclencher un événement."""
        if event in self.event_handlers:
            try:
                callback = self.event_handlers[event]
                if data is not None:
                    callback(data)
                else:
                    callback()
            except Exception as e:
                print(f"⚠️  Erreur dans callback {event}: {e}")
    
    def send_status(self, status: str, message: str = None):
        """Envoyer le statut du tunnel au serveur."""
        if self.connection and self.connection.connected:
            try:
                self.connection.emit('tunnel_status', {
                    'tunnel_id': self.tunnel_id,
                    'status': status,
                    'message': message,
                    'timestamp': time.time()
                })
            except Exception as e:
                print(f"⚠️  Erreur envoi statut: {e}")
    
    def disconnect(self):
        """Fermer la connexion."""
        print(f"🔌 Fermeture du tunnel {self.tunnel_id}")
        self._stop_event.set()
        
        if self.connection and self.connection.connected:
            try:
                # Quitter la room avant de se déconnecter
                self.connection.emit('leave_tunnel', {'tunnel_id': self.tunnel_id})
                time.sleep(0.5)  # Laisser le temps au message d'être envoyé
                self.connection.disconnect()
            except Exception as e:
                print(f"⚠️  Erreur lors de la déconnexion: {e}")
        
        self.status = TunnelStatus.DISCONNECTED
    
    def wait_until_expired(self) -> None:
        """Attendre jusqu'à l'expiration du tunnel."""
        print(f"⏰ Attente d'expiration du tunnel (dans {self.remaining_time}s)")
        print(f"🌐 URL publique: {self.public_url}")
        print(f"📁 Subdomain: {self.info.subdomain}")
        
        while not self._stop_event.is_set() and not self.is_expired and self.status != TunnelStatus.EXPIRED:
            self._stop_event.wait(1)
            
            # Envoyer un ping périodique
            if time.time() % 30 == 0:  # Toutes les 30 secondes
                self.send_status('active', f'Tunnel actif, expire dans {self.remaining_time}s')
        
        if self.is_expired or self.status == TunnelStatus.EXPIRED:
            print("⏰ Tunnel expiré")
            self.status = TunnelStatus.EXPIRED
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupérer les statistiques du tunnel."""
        return {
            'tunnel_id': self.tunnel_id,
            'public_url': self.public_url,
            'local_url': self.local_url,
            'subdomain': self.info.subdomain,
            'status': self.status.value,
            'requests_count': self.info.requests_count,
            'created_at': self.info.created_at,
            'expires_at': self.info.expires_at,
            'remaining_time': self.remaining_time,
            'is_active': self.is_active,
            'is_expired': self.is_expired,
            'connection_retries': self._connection_retries,
            'tunnel_base_url': self.tunnel_base_url
        }