# =============================================================================
# flasktunnel/server.py - Serveur FlaskTunnel Local
# =============================================================================

"""
Serveur FlaskTunnel local pour développement et tests.
Permet de créer des tunnels HTTP sans dépendre du service en ligne.
"""

import asyncio
import json
import uuid
import time
import threading
import requests
from flask import Flask, request, jsonify, redirect
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LocalTunnel:
    """Représentation d'un tunnel local."""
    tunnel_id: str
    port: int
    subdomain: str
    public_url: str
    created_at: float
    expires_at: float
    requests_count: int = 0
    password: Optional[str] = None
    cors: bool = False
    https: bool = False

class FlaskTunnelServer:
    """Serveur FlaskTunnel local."""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'dev-secret-key'
        
        # Configuration CORS
        CORS(self.app, origins="*")
        
        # Configuration SocketIO
        self.socketio = SocketIO(
            self.app, 
            cors_allowed_origins="*",
            async_mode='threading'
        )
        
        # Stockage des tunnels actifs
        self.tunnels: Dict[str, LocalTunnel] = {}
        
        # Configuration des routes
        self._setup_routes()
        self._setup_socket_events()
        
        # Thread de nettoyage des tunnels expirés
        self._cleanup_thread = threading.Thread(target=self._cleanup_expired_tunnels, daemon=True)
        self._cleanup_thread.start()
    
    def _setup_routes(self):
        """Configuration des routes API."""
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Vérification de santé du serveur."""
            return jsonify({
                'status': 'ok',
                'server': 'FlaskTunnel Local Server',
                'version': '1.0.0',
                'timestamp': time.time()
            })
        
        @self.app.route('/api/tunnels', methods=['POST'])
        def create_tunnel():
            """Créer un nouveau tunnel."""
            data = request.get_json()
            
            # Validation des données
            port = data.get('port')
            if not port or not isinstance(port, int):
                return jsonify({'error': 'Port requis et doit être un entier'}), 400
            
            # Vérifier si le service local tourne
            if not self._check_service_running(port):
                return jsonify({'error': f'Aucun service ne tourne sur le port {port}'}), 400
            
            # Générer les identifiants
            tunnel_id = str(uuid.uuid4())[:8]
            subdomain = data.get('subdomain') or f'tunnel-{tunnel_id}'
            
            # Vérifier l'unicité du sous-domaine
            for tunnel in self.tunnels.values():
                if tunnel.subdomain == subdomain:
                    return jsonify({'error': 'Sous-domaine déjà utilisé'}), 409
            
            # Calculer l'expiration
            duration = data.get('duration', '2h')
            expires_in = self._parse_duration(duration)
            
            # Créer le tunnel
            tunnel = LocalTunnel(
                tunnel_id=tunnel_id,
                port=port,
                subdomain=subdomain,
                public_url=f"http://{subdomain}.{self.host}:{self.port}",
                created_at=time.time(),
                expires_at=time.time() + expires_in,
                password=data.get('password'),
                cors=data.get('cors', False),
                https=data.get('https', False)
            )
            
            self.tunnels[tunnel_id] = tunnel
            
            logger.info(f"Tunnel créé: {tunnel.public_url} -> localhost:{port}")
            
            return jsonify({
                'tunnel_id': tunnel_id,
                'public_url': tunnel.public_url,
                'subdomain': subdomain,
                'expires_in': expires_in,
                'created_at': tunnel.created_at
            }), 201
        
        @self.app.route('/api/tunnels', methods=['GET'])
        def list_tunnels():
            """Lister tous les tunnels actifs."""
            active_tunnels = []
            current_time = time.time()
            
            for tunnel in self.tunnels.values():
                if tunnel.expires_at > current_time:
                    active_tunnels.append({
                        'tunnel_id': tunnel.tunnel_id,
                        'public_url': tunnel.public_url,
                        'port': tunnel.port,
                        'status': 'active',
                        'requests_count': tunnel.requests_count,
                        'expires_at': datetime.fromtimestamp(tunnel.expires_at).isoformat()
                    })
            
            return jsonify({'tunnels': active_tunnels})
        
        @self.app.route('/api/tunnels/<tunnel_id>', methods=['DELETE'])
        def delete_tunnel(tunnel_id):
            """Supprimer un tunnel."""
            if tunnel_id in self.tunnels:
                del self.tunnels[tunnel_id]
                logger.info(f"Tunnel {tunnel_id} supprimé")
                return jsonify({'message': 'Tunnel supprimé'})
            else:
                return jsonify({'error': 'Tunnel introuvable'}), 404
        
        @self.app.route('/api/tunnels/<tunnel_id>/stats', methods=['GET'])
        def get_tunnel_stats(tunnel_id):
            """Récupérer les statistiques d'un tunnel."""
            if tunnel_id not in self.tunnels:
                return jsonify({'error': 'Tunnel introuvable'}), 404
            
            tunnel = self.tunnels[tunnel_id]
            return jsonify({
                'tunnel_id': tunnel_id,
                'requests_count': tunnel.requests_count,
                'created_at': tunnel.created_at,
                'expires_at': tunnel.expires_at,
                'remaining_time': max(0, int(tunnel.expires_at - time.time()))
            })
        
        @self.app.route('/api/auth/validate', methods=['GET'])
        def validate_auth():
            """Validation de l'authentification (mode local = toujours valide)."""
            return jsonify({'valid': True, 'mode': 'local'})
        
        # Route pour rediriger les requêtes vers les applications locales
        @self.app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
        @self.app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
        def proxy_request(path):
            """Router les requêtes vers les applications locales."""
            host_header = request.headers.get('Host', '')
            subdomain = host_header.split('.')[0] if '.' in host_header else None
            
            # Trouver le tunnel correspondant
            target_tunnel = None
            for tunnel in self.tunnels.values():
                if tunnel.subdomain == subdomain:
                    target_tunnel = tunnel
                    break
            
            if not target_tunnel:
                return jsonify({
                    'error': 'Tunnel introuvable',
                    'message': f'Aucun tunnel actif pour le sous-domaine: {subdomain}'
                }), 404
            
            # Vérifier l'expiration
            if time.time() > target_tunnel.expires_at:
                return jsonify({
                    'error': 'Tunnel expiré',
                    'message': 'Ce tunnel a expiré'
                }), 410
            
            # Incrémenter le compteur de requêtes
            target_tunnel.requests_count += 1
            
            # Émettre l'événement via WebSocket
            self.socketio.emit('tunnel_request', {
                'tunnel_id': target_tunnel.tunnel_id,
                'method': request.method,
                'path': f"/{path}" if path else "/",
                'ip': request.remote_addr,
                'timestamp': time.time()
            }, room=target_tunnel.tunnel_id)
            
            # Proxy vers l'application locale
            try:
                target_url = f"http://localhost:{target_tunnel.port}/{path}"
                
                # Préparer les headers
                headers = dict(request.headers)
                headers.pop('Host', None)  # Supprimer le header Host original
                
                # Faire la requête vers l'application locale
                response = requests.request(
                    method=request.method,
                    url=target_url,
                    params=request.args,
                    json=request.get_json() if request.is_json else None,
                    data=request.get_data() if not request.is_json else None,
                    headers=headers,
                    timeout=30
                )
                
                # Retourner la réponse
                return response.content, response.status_code, dict(response.headers)
                
            except requests.ConnectionError:
                return jsonify({
                    'error': 'Service local inaccessible',
                    'message': f'Impossible de se connecter à localhost:{target_tunnel.port}'
                }), 502
            except requests.Timeout:
                return jsonify({
                    'error': 'Timeout',
                    'message': 'Le service local ne répond pas'
                }), 504
            except Exception as e:
                return jsonify({
                    'error': 'Erreur proxy',
                    'message': str(e)
                }), 500
    
    def _setup_socket_events(self):
        """Configuration des événements WebSocket."""
        
        @self.socketio.on('connect')
        def handle_connect():
            logger.info(f"Client WebSocket connecté: {request.sid}")
            emit('connected', {'message': 'Connexion WebSocket établie'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info(f"Client WebSocket déconnecté: {request.sid}")
        
        @self.socketio.on('join_tunnel')
        def handle_join_tunnel(data):
            tunnel_id = data.get('tunnel_id')
            if tunnel_id and tunnel_id in self.tunnels:
                join_room(tunnel_id)
                logger.info(f"Client {request.sid} a rejoint le tunnel {tunnel_id}")
                emit('joined_tunnel', {'tunnel_id': tunnel_id})
        
        @self.socketio.on('leave_tunnel')
        def handle_leave_tunnel(data):
            tunnel_id = data.get('tunnel_id')
            if tunnel_id:
                leave_room(tunnel_id)
                logger.info(f"Client {request.sid} a quitté le tunnel {tunnel_id}")
    
    def _check_service_running(self, port: int) -> bool:
        """Vérifier si un service tourne sur un port."""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result == 0
        except socket.error:
            return False
    
    def _parse_duration(self, duration: str) -> int:
        """Convertir une durée en secondes."""
        duration_map = {
            '1h': 3600,
            '2h': 7200,
            '4h': 14400,
            '8h': 28800,
            '12h': 43200,
            '24h': 86400
        }
        return duration_map.get(duration, 7200)  # 2h par défaut
    
    def _cleanup_expired_tunnels(self):
        """Nettoyer les tunnels expirés."""
        while True:
            current_time = time.time()
            expired_tunnels = []
            
            for tunnel_id, tunnel in self.tunnels.items():
                if tunnel.expires_at <= current_time:
                    expired_tunnels.append(tunnel_id)
            
            for tunnel_id in expired_tunnels:
                logger.info(f"Nettoyage du tunnel expiré: {tunnel_id}")
                
                # Émettre l'événement d'expiration
                self.socketio.emit('tunnel_expired', {
                    'tunnel_id': tunnel_id,
                    'message': 'Tunnel expiré'
                }, room=tunnel_id)
                
                del self.tunnels[tunnel_id]
            
            # Attendre 60 secondes avant la prochaine vérification
            time.sleep(60)
    
    def run(self, debug: bool = False):
        """Démarrer le serveur."""
        logger.info(f"🚀 Démarrage du serveur FlaskTunnel Local sur {self.host}:{self.port}")
        logger.info(f"📊 Interface d'administration: http://{self.host}:{self.port}/api/health")
        
        self.socketio.run(
            self.app,
            host=self.host,
            port=self.port,
            debug=debug,
            allow_unsafe_werkzeug=True
        )

def main():
    """Point d'entrée pour le serveur local."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Serveur FlaskTunnel Local')
    parser.add_argument('--host', default='localhost', help='Adresse d\'écoute')
    parser.add_argument('--port', type=int, default=8080, help='Port d\'écoute')
    parser.add_argument('--debug', action='store_true', help='Mode débogage')
    
    args = parser.parse_args()
    
    server = FlaskTunnelServer(host=args.host, port=args.port)
    
    try:
        server.run(debug=args.debug)
    except KeyboardInterrupt:
        logger.info("Arrêt du serveur demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur du serveur: {e}")

if __name__ == '__main__':
    main()