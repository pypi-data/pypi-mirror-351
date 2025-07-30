# =============================================================================
# flasktunnel/tunnel.py - VERSION CORRIGÉE
# =============================================================================

import time
import threading
import socketio
import requests
from enum import Enum
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
import base64


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
    """Représentation d'un tunnel FlaskTunnel - VERSION CORRIGÉE."""
    
    def __init__(self, info: TunnelInfo, server_url: str = "https://flasktunnel.up.railway.app/"):
        self.info = info
        self.server_url = server_url.rstrip('/')
        self.connection = None
        self.status = TunnelStatus.CONNECTING
        self.event_handlers = {}
        self._stop_event = threading.Event()
        self._connection_retries = 0
        self._max_retries = 5
        
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
                """Traiter une requête HTTP reçue via WebSocket - CORRIGÉ AVEC PRÉFIXE."""
                try:
                    request_id = data.get('request_id')
                    method = data.get('method', 'GET')
                    path = data.get('path', '/')
                    headers = data.get('headers', {})
                    body = data.get('body')
                    params = data.get('params', {})
                    subdomain = data.get('subdomain', '')  # NOUVEAU
                    public_url = data.get('public_url', '')  # NOUVEAU
                    
                    print(f"📥 Requête reçue: {method} {path} (Subdomain: {subdomain}, ID: {request_id})")
                    
                    # Construire l'URL locale
                    local_url = f"http://localhost:{self.info.port}{path}"
                    
                    # Nettoyer les headers problématiques
                    cleaned_headers = {}
                    skip_headers = {
                        'host', 'connection', 'upgrade', 'sec-websocket-key',
                        'sec-websocket-version', 'sec-websocket-extensions',
                        'content-length'
                    }
                    
                    for key, value in headers.items():
                        if key.lower() not in skip_headers:
                            cleaned_headers[key] = value
                    
                    # NOUVEAU: Ajouter des headers pour aider l'application locale à générer les bons liens
                    if subdomain:
                        cleaned_headers['X-Forwarded-Prefix'] = f'/{subdomain}'
                        cleaned_headers['X-Script-Name'] = f'/{subdomain}'
                    
                    if public_url:
                        cleaned_headers['X-Forwarded-Host'] = public_url.replace('https://', '').replace('http://', '')
                        cleaned_headers['X-Forwarded-Proto'] = 'https' if public_url.startswith('https') else 'http'
                    
                    # Préparer les paramètres de la requête
                    request_kwargs = {
                        'method': method,
                        'url': local_url,
                        'headers': cleaned_headers,
                        'params': params,
                        'timeout': 25,
                        'allow_redirects': False,  # Important: ne pas suivre les redirections automatiquement
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
                        
                        # Préparer la réponse
                        response_data = {
                            'request_id': request_id,
                            'status_code': response.status_code,
                            'headers': dict(response.headers),
                            'binary': is_binary
                        }
                        
                        # NOUVEAU: Modifier les headers de redirection si nécessaire
                        if 'location' in response.headers:
                            location = response.headers['location']
                            # Si c'est une redirection relative vers l'application locale
                            if location.startswith('/') and subdomain:
                                # Ne pas modifier si elle contient déjà le préfixe
                                if not location.startswith(f'/{subdomain}'):
                                    response_data['headers']['location'] = f"/{subdomain}{location}"
                        
                        # Encoder le contenu selon son type
                        if is_binary:
                            import base64
                            response_data['content'] = base64.b64encode(response.content).decode('ascii')
                        else:
                            try:
                                content = response.content.decode('utf-8')
                                
                                # NOUVEAU: Pour les réponses HTML, corriger les liens si nécessaire
                                if content_type.startswith('text/html') and subdomain:
                                    # Cette correction sera faite côté serveur pour plus d'efficacité
                                    pass
                                
                                response_data['content'] = content
                            except UnicodeDecodeError:
                                try:
                                    response_data['content'] = response.content.decode('utf-8', errors='replace')
                                except:
                                    import base64
                                    response_data['content'] = base64.b64encode(response.content).decode('ascii')
                                    response_data['binary'] = True
                        
                        print(f"✅ Réponse {response.status_code} pour {method} {path}")
                        
                    except requests.ConnectionError:
                        print(f"❌ Service local non disponible sur le port {self.info.port}")
                        response_data = {
                            'request_id': request_id,
                            'error': f'Connection refused to localhost:{self.info.port}',
                            'status_code': 502,
                            'headers': {'content-type': 'text/plain'},
                            'content': f'Service Unavailable\n\nNo application is running on localhost:{self.info.port}\n\nPlease start your application and try again.'
                        }
                    
                    except requests.Timeout:
                        print(f"⏰ Timeout pour {method} {path}")
                        response_data = {
                            'request_id': request_id,
                            'error': 'Local service timeout',
                            'status_code': 504,
                            'headers': {'content-type': 'text/plain'},
                            'content': 'Gateway Timeout\n\nThe local service took too long to respond (>25s).'
                        }
                    
                    except Exception as req_error:
                        print(f"❌ Erreur requête locale: {req_error}")
                        response_data = {
                            'request_id': request_id,
                            'error': f'Local request error: {str(req_error)}',
                            'status_code': 500,
                            'headers': {'content-type': 'text/plain'},
                            'content': f'Internal Server Error\n\nError while processing the request:\n{str(req_error)}'
                        }
                    
                    # Envoyer la réponse au serveur
                    try:
                        sio.emit('tunnel_response', response_data)
                        self.info.requests_count += 1
                        
                        # Déclencher l'événement de requête
                        self._trigger_event('request', {
                            'method': method,
                            'path': path,
                            'ip': data.get('ip', 'unknown'),
                            'user_agent': headers.get('user-agent', 'unknown'),
                            'status_code': response_data.get('status_code', 500),
                            'subdomain': subdomain
                        })
                        
                    except Exception as emit_error:
                        print(f"❌ Erreur lors de l'envoi de la réponse: {emit_error}")
                
                except Exception as e:
                    print(f"❌ Erreur critique dans on_tunnel_request: {e}")
                    try:
                        error_response = {
                            'request_id': data.get('request_id', 'unknown'),
                            'error': f'Critical error: {str(e)}',
                            'status_code': 500,
                            'headers': {'content-type': 'text/plain'},
                            'content': f'Critical Error\n\nAn unexpected error occurred:\n{str(e)}'
                        }
                        sio.emit('tunnel_response', error_response)
                    except:
                        pass
            
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
            'status': self.status.value,
            'requests_count': self.info.requests_count,
            'created_at': self.info.created_at,
            'expires_at': self.info.expires_at,
            'remaining_time': self.remaining_time,
            'is_active': self.is_active,
            'is_expired': self.is_expired,
            'connection_retries': self._connection_retries
        }