# =============================================================================
# flasktunnel/client.py - VERSION CORRIGÉE
# =============================================================================

"""Client principal FlaskTunnel."""

import requests
import time
import threading
from typing import Optional, Dict, Any, List
from .config import FlaskTunnelConfig
from .auth import FlaskTunnelAuth
from .tunnel import Tunnel, TunnelInfo, TunnelStatus
from .utils import (
    check_service_running, generate_tunnel_id, print_success, 
    print_error, print_warning, print_info, validate_subdomain
)


class FlaskTunnelClient:
    """Client FlaskTunnel pour créer et gérer des tunnels."""
    
    def __init__(self, config: Optional[FlaskTunnelConfig] = None):
        self.config = config or FlaskTunnelConfig()
        self.server_url = self.config.get_effective_server_url()
        self.auth = FlaskTunnelAuth(self.server_url)
        self.active_tunnels: Dict[str, Tunnel] = {}
        self.session = requests.Session()
        
        # Headers par défaut
        self.session.headers.update({
            'User-Agent': 'FlaskTunnel-Client/1.0.0',
            'Content-Type': 'application/json'
        })
    
    def _check_server_availability(self) -> bool:
        """Vérifier si le serveur FlaskTunnel est disponible."""
        try:
            response = self.session.get(
                f"{self.server_url}/api/health",
                timeout=5
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def _suggest_alternatives(self) -> None:
        """Suggérer des alternatives en cas de problème de connexion."""
        print_info("Solutions possibles:")
        print("  1. Vérifiez votre connexion internet")
        print("  2. Le service FlaskTunnel pourrait être temporairement indisponible")
        print("  3. Pour un serveur local, définissez FLASKTUNNEL_LOCAL_MODE=true")
        print("  4. Ou utilisez: flasktunnel --local-mode --port 5000")
        print("\n💡 Alternatives:")
        print("  - ngrok: https://ngrok.com")
        print("  - localtunnel: https://localtunnel.github.io/www/")
        print("  - serveo: https://serveo.net")
    
    def create_tunnel(
        self,
        port: int,
        subdomain: Optional[str] = None,
        password: Optional[str] = None,
        duration: str = "2h",
        cors: bool = False,
        https: bool = False,
        webhook: bool = False,
        custom_domain: Optional[str] = None,
        auth_token: Optional[str] = None
    ) -> Tunnel:
        """Créer un nouveau tunnel."""
        
        # Vérifier si le service local tourne
        if not check_service_running(port):
            print_warning(f"Aucun service détecté sur le port {port}")
            response = input(f"Voulez-vous créer le tunnel quand même ? (y/N): ")
            if response.lower() not in ['y', 'yes', 'o', 'oui']:
                raise Exception(f"Création annulée - Aucun service sur le port {port}")
        
        # Vérifier la disponibilité du serveur
        if not self._check_server_availability():
            print_error(f"Impossible de se connecter au serveur FlaskTunnel ({self.server_url})")
            if self.config.local_mode:
                print_error("Mode local activé mais aucun serveur local détecté sur le port 8080")
                print_info("Démarrez le serveur FlaskTunnel local ou désactivez le mode local")
            else:
                self._suggest_alternatives()
            raise Exception("Serveur FlaskTunnel inaccessible")
        
        # Validation du sous-domaine
        if subdomain and not validate_subdomain(subdomain):
            raise Exception("Nom de sous-domaine invalide")
        
        # Préparer les données avec le bon nommage
        tunnel_data = {
            'port': port,
            'subdomain': subdomain,
            'password': password,
            'duration': duration,
            'cors': cors,
            'https': https,
            'webhook': webhook,
            'custom_domain': custom_domain
        }
        
        # Supprimer les valeurs None
        tunnel_data = {k: v for k, v in tunnel_data.items() if v is not None}
        
        # Préparer les headers
        headers = {'Content-Type': 'application/json'}
        
        # Ajouter l'authentification si disponible
        api_key = auth_token or self.auth.get_api_key()
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        try:
            print_info(f"Envoi de la requête vers: {self.server_url}/api/tunnels")
            print_info(f"Données: {tunnel_data}")
            print_info(f"Headers: {headers}")
            
            response = self.session.post(
                f"{self.server_url}/api/tunnels",
                json=tunnel_data,
                headers=headers,
                timeout=30
            )
            
            print_info(f"Réponse status: {response.status_code}")
            print_info(f"Réponse content: {response.text}")
            
            if response.status_code == 201:
                data = response.json()
                tunnel_info = TunnelInfo(
                    tunnel_id=data['tunnel_id'],
                    public_url=data['public_url'],
                    local_url=f"http://localhost:{port}",
                    subdomain=data['subdomain'],
                    status=TunnelStatus.CONNECTING,
                    created_at=time.time(),
                    expires_at=time.time() + data.get('expires_in', 7200),
                    port=port,
                    password_protected=bool(password),
                    custom_domain=custom_domain
                )
                
                tunnel = Tunnel(tunnel_info, self.server_url)
                self.active_tunnels[tunnel.tunnel_id] = tunnel
                
                # Établir la connexion WebSocket
                try:
                    print_info("🔌 Établissement de la connexion WebSocket...")
                    tunnel.connect_websocket()
                    
                    # Attendre la confirmation de connexion
                    max_wait = 10  # 10 secondes max
                    waited = 0
                    while tunnel.status == TunnelStatus.CONNECTING and waited < max_wait:
                        time.sleep(0.5)
                        waited += 0.5
                    
                    if tunnel.status == TunnelStatus.CONNECTED:
                        print_success(f"Tunnel créé: {tunnel.public_url}")
                        print_info(f"Dashboard: {tunnel.dashboard_url}")
                        print_info("🚀 Le tunnel est maintenant actif et prêt à recevoir des requêtes")
                        return tunnel
                    else:
                        print_warning("Tunnel créé mais connexion WebSocket non confirmée")
                        print_info("Le tunnel pourrait ne pas fonctionner correctement")
                        return tunnel
                        
                except Exception as ws_error:
                    print_error(f"Erreur WebSocket: {ws_error}")
                    print_warning("Tunnel créé mais connexion WebSocket échouée")
                    print_info("Le tunnel ne pourra pas traiter les requêtes")
                    return tunnel
            
            elif response.status_code == 401:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('error', 'Authentification requise')
                print_error(f"Erreur d'authentification: {error_msg}")
                
                if 'token' in error_msg.lower() or 'auth' in error_msg.lower():
                    print_info("💡 Solutions possibles:")
                    print("  1. Le serveur peut nécessiter une authentification")
                    print("  2. Obtenez un token API si nécessaire")
                    print("  3. Vérifiez les paramètres du serveur")
                
                raise Exception(f"Authentification échouée: {error_msg}")
            
            elif response.status_code == 402:
                raise Exception("Plan gratuit limité. Upgrader vers Pro pour plus de fonctionnalités.")
            elif response.status_code == 409:
                error_data = response.json()
                raise Exception(f"Sous-domaine déjà utilisé: {error_data.get('error', 'Conflit')}")
            elif response.status_code == 400:
                error_data = response.json()
                raise Exception(f"Données invalides: {error_data.get('error', 'Erreur de validation')}")
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Erreur inconnue')
                except:
                    error_msg = f"Erreur HTTP {response.status_code}"
                raise Exception(f"Échec de création du tunnel: {error_msg}")
                
        except requests.ConnectionError as e:
            print_error(f"Erreur de connexion au serveur: {e}")
            self._suggest_alternatives()
            raise Exception("Impossible de se connecter au serveur FlaskTunnel")
        except requests.Timeout:
            raise Exception("Timeout lors de la connexion au serveur")
        except requests.RequestException as e:
            raise Exception(f"Erreur de connexion au serveur: {e}")
    
    def list_tunnels(self) -> List[Dict[str, Any]]:
        """Lister tous les tunnels actifs."""
        api_key = self.auth.get_api_key()
        if not api_key:
            print_warning("Aucune clé API configurée - impossible de lister les tunnels")
            return []
        
        if not self._check_server_availability():
            print_warning("Serveur FlaskTunnel inaccessible")
            return []
        
        try:
            response = self.session.get(
                f"{self.server_url}/api/tunnels",
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()['tunnels']
            else:
                print_warning("Impossible de récupérer la liste des tunnels")
                return []
                
        except requests.RequestException as e:
            print_error(f"Erreur lors de la récupération des tunnels: {e}")
            return []
    
    def delete_tunnel(self, tunnel_id: str) -> bool:
        """Supprimer un tunnel."""
        api_key = self.auth.get_api_key()
        headers = {}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        try:
            response = self.session.delete(
                f"{self.server_url}/api/tunnels/{tunnel_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                if tunnel_id in self.active_tunnels:
                    self.active_tunnels[tunnel_id].disconnect()
                    del self.active_tunnels[tunnel_id]
                print_success(f"Tunnel {tunnel_id} supprimé")
                return True
            else:
                print_error(f"Impossible de supprimer le tunnel {tunnel_id}")
                return False
                
        except requests.RequestException as e:
            print_error(f"Erreur lors de la suppression: {e}")
            return False
    
    def get_tunnel_stats(self, tunnel_id: str) -> Optional[Dict[str, Any]]:
        """Récupérer les statistiques d'un tunnel."""
        try:
            response = self.session.get(
                f"{self.server_url}/api/tunnels/{tunnel_id}/stats",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except requests.RequestException:
            return None
    
    def test_connection(self) -> bool:
        """Tester la connexion au serveur FlaskTunnel."""
        return self._check_server_availability()
    
    def diagnose(self) -> Dict[str, Any]:
        """Effectuer un diagnostic du système."""
        results = {
            'server_connection': False,
            'local_ports': [],
            'api_key_valid': False,
            'system_info': {
                'server_url': self.server_url,
                'local_mode': self.config.local_mode
            }
        }
        
        # Test de connexion serveur
        print_info(f"Test de connexion au serveur ({self.server_url})...")
        results['server_connection'] = self.test_connection()
        
        if results['server_connection']:
            print_success("Connexion au serveur OK")
        else:
            print_error("Impossible de se connecter au serveur")
            if self.config.local_mode:
                print_info("Mode local activé - Vérifiez que le serveur local tourne sur le port 8080")
            else:
                print_info("Mode production - Vérifiez votre connexion internet")
        
        # Test des ports locaux courants
        print_info("Vérification des ports locaux...")
        common_ports = [3000, 5000, 8000, 8080, 3001, 4000, 9000]
        
        for port in common_ports:
            if check_service_running(port):
                results['local_ports'].append(port)
                print_success(f"Service détecté sur le port {port}")
        
        if not results['local_ports']:
            print_warning("Aucun service local détecté sur les ports courants")
        
        # Test de la clé API
        api_key = self.auth.get_api_key()
        if api_key:
            print_info("Validation de la clé API...")
            results['api_key_valid'] = self.auth.validate_api_key(api_key)
            
            if results['api_key_valid']:
                print_success("Clé API valide")
            else:
                print_error("Clé API invalide ou expirée")
        else:
            print_info("Aucune clé API configurée (mode gratuit)")
        
        return results
    
    def close_all_tunnels(self) -> None:
        """Fermer tous les tunnels actifs."""
        for tunnel in self.active_tunnels.values():
            tunnel.disconnect()
        self.active_tunnels.clear()
        # SUPPRIMER cette ligne incorrecte :
        # if self.active_tunnels:  # Cette condition sera toujours False après clear()
        print_success("Tous les tunnels ont été fermés")