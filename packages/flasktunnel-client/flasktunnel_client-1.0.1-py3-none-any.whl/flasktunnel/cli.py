# =============================================================================
# flasktunnel/cli.py  
# =============================================================================

"""Interface en ligne de commande pour FlaskTunnel."""

import click
import signal
import sys
import time
import threading
from typing import Optional
from .client import FlaskTunnelClient
from .config import FlaskTunnelConfig
from .auth import FlaskTunnelAuth
from .utils import (
    print_banner, print_tunnel_info, print_success, print_error, 
    print_warning, print_info, format_time_remaining, check_service_running
)


def signal_handler(signum, frame):
    """Gestionnaire pour les signaux système (Ctrl+C)."""
    print_info("\nArrêt du tunnel en cours...")
    sys.exit(0)


@click.command()
@click.option('--port', '-p', type=int, help='Port local à exposer')
@click.option('--subdomain', '-s', help='Nom de sous-domaine personnalisé')
@click.option('--password', help='Mot de passe pour protéger le tunnel')
@click.option('--duration', '-d', default='2h', help='Durée du tunnel (1h, 2h, 4h, 8h, 12h, 24h)')
@click.option('--cors', is_flag=True, help='Activer CORS automatiquement')
@click.option('--https', is_flag=True, help='Forcer HTTPS (si app locale en HTTPS)')
@click.option('--webhook', is_flag=True, help='Mode webhook (durée prolongée)')
@click.option('--auth', help='Clé API FlaskTunnel')
@click.option('--name', help='Alias pour --subdomain')
@click.option('--config', help='Fichier de configuration personnalisé')
@click.option('--local-mode', is_flag=True, help='Mode local (serveur sur localhost:8080)')
@click.option('--server-url', help='URL du serveur FlaskTunnel personnalisé')
@click.option('--verbose', '-v', is_flag=True, help='Mode verbeux')
@click.option('--test', is_flag=True, help='Tester la connexion')
@click.option('--diagnose', is_flag=True, help='Diagnostic du système')
@click.option('--login', is_flag=True, help='Se connecter à FlaskTunnel')
@click.option('--register', is_flag=True, help='Créer un compte FlaskTunnel')
@click.option('--logout', is_flag=True, help='Se déconnecter')
@click.option('--list', 'list_tunnels', is_flag=True, help='Lister les tunnels actifs')
def main(
    port: Optional[int],
    subdomain: Optional[str],
    password: Optional[str],
    duration: str,
    cors: bool,
    https: bool,
    webhook: bool,
    auth: Optional[str],
    name: Optional[str],
    config: Optional[str],
    local_mode: bool,
    server_url: Optional[str], 
    verbose: bool,
    test: bool,
    diagnose: bool,
    login: bool,
    register: bool,
    logout: bool,
    list_tunnels: bool
):
    """FlaskTunnel - Créez des tunnels HTTP sécurisés vers vos applications locales."""
    
    # Gestionnaire de signaux
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Bannière
    if not any([test, diagnose, login, register, logout, list_tunnels]):
        print_banner()
    
    # Charger la configuration
    if config:
        tunnel_config = FlaskTunnelConfig.from_file(config)
    else:
        # Fusionner : fichier -> env -> args
        tunnel_config = FlaskTunnelConfig.from_file()
        env_config = FlaskTunnelConfig.from_env()
        tunnel_config = tunnel_config.merge_with_args(**env_config.__dict__)
    
    # Arguments de ligne de commande (priorité maximale)
    cli_args = {
        'port': port,
        'subdomain': subdomain or name,  # --name est un alias pour --subdomain
        'password': password,
        'duration': duration,
        'cors': cors,
        'https': https,  
        'webhook': webhook,
        'auth_token': auth,
        'local_mode': local_mode,
        'server_url': server_url
    }
    
    tunnel_config = tunnel_config.merge_with_args(**{k: v for k, v in cli_args.items() if v is not None and v is not False})
    
    # Client FlaskTunnel
    client = FlaskTunnelClient(tunnel_config)
    auth_manager = FlaskTunnelAuth(tunnel_config.get_effective_server_url())
    
    # Information sur le mode utilisé
    if verbose:
        server_mode = "LOCAL" if tunnel_config.local_mode else "PRODUCTION"
        print_info(f"Mode: {server_mode} | Serveur: {tunnel_config.get_effective_server_url()}")
    
    # Commandes spéciales
    if login:
        email = click.prompt('Email')
        password = click.prompt('Mot de passe', hide_input=True)
        auth_manager.login(email, password)
        return
    
    if register:
        email = click.prompt('Email')
        password = click.prompt('Mot de passe', hide_input=True)
        confirm_password = click.prompt('Confirmer mot de passe', hide_input=True)
        
        if password != confirm_password:
            print_error("Les mots de passe ne correspondent pas")
            return
        
        auth_manager.register(email, password)
        return
    
    if logout:
        auth_manager.logout()
        return
    
    if test:
        print_info("Test de connexion à FlaskTunnel...")
        if client.test_connection():
            print_success("Connexion OK - FlaskTunnel est accessible")
        else:
            print_error("Impossible de se connecter à FlaskTunnel")
            if tunnel_config.local_mode:
                print_info("💡 Mode local activé - Démarrez le serveur FlaskTunnel local")
            else:
                print_info("💡 Vérifiez votre connexion internet ou essayez --local-mode")
        return
    
    if diagnose:
        print_info("Diagnostic du système FlaskTunnel...")
        results = client.diagnose()
        
        print(f"\n📊 Résultats du diagnostic:")
        print(f"  - Mode: {'LOCAL' if tunnel_config.local_mode else 'PRODUCTION'}")
        print(f"  - Serveur: {tunnel_config.get_effective_server_url()}")
        print(f"  - Connexion serveur: {'✅' if results['server_connection'] else '❌'}")
        print(f"  - Services locaux détectés: {len(results['local_ports'])}")
        print(f"  - Clé API valide: {'✅' if results['api_key_valid'] else '❌'}")
        
        if results['local_ports']:
            print(f"  - Ports actifs: {', '.join(map(str, results['local_ports']))}")
        
        if not results['server_connection']:
            print(f"\n💡 Solutions suggérées:")
            if tunnel_config.local_mode:
                print("  - Démarrez le serveur FlaskTunnel local sur le port 8080")
                print("  - Ou désactivez le mode local pour utiliser le service en ligne")
            else:
                print("  - Vérifiez votre connexion internet")
                print("  - Essayez le mode local avec --local-mode")
                print("  - Le service pourrait être temporairement indisponible")
        
        return
    
    if list_tunnels:
        print_info("Récupération des tunnels actifs...")
        tunnels = client.list_tunnels()
        
        if not tunnels:
            print_warning("Aucun tunnel actif trouvé")
            return
        
        print(f"\n📋 Tunnels actifs ({len(tunnels)}):")
        for tunnel in tunnels:
            status_icon = "🟢" if tunnel['status'] == 'active' else "🔴"
            print(f"  {status_icon} {tunnel['public_url']} → localhost:{tunnel['port']}")
            print(f"     ID: {tunnel['tunnel_id']} | Expire: {tunnel['expires_at']}")
     
        return
    
    # Validation de la configuration
    if not tunnel_config.validate():
        print_error("Configuration invalide")
        return
    
    # Vérifier le port
    if not check_service_running(tunnel_config.port):
        print_warning(f"Aucun service détecté sur le port {tunnel_config.port}")
        print_info("Le tunnel sera créé mais ne pourra pas traiter les requêtes")
        print_info(f"Démarrez votre application sur le port {tunnel_config.port} après création du tunnel")
    
    try:
        # Créer le tunnel
        print_info(f"Création du tunnel vers localhost:{tunnel_config.port}...")
        
        tunnel = client.create_tunnel(
            port=tunnel_config.port,
            subdomain=tunnel_config.subdomain,
            password=tunnel_config.password,
            duration=tunnel_config.duration,
            cors=tunnel_config.cors,
            https=tunnel_config.https,
            webhook=tunnel_config.webhook,
            auth_token=tunnel_config.auth_token
        )
        
        # Connexion WebSocket
        tunnel.connect_websocket()
        
        # Afficher les informations
        print_tunnel_info(tunnel)
        
        # Callbacks pour les événements
        def on_request(data):
            if verbose:
                method = data.get('method', 'GET')
                path = data.get('path', '/')
                ip = data.get('ip', 'unknown')
                print(f"📨 {method} {path} from {ip}")
        
        def on_error(data):
            print_error(f"Erreur tunnel: {data.get('message', 'Erreur inconnue')}")
        
        def on_expired(data):
            print_warning("Le tunnel a expiré")
        
        tunnel.on('request', on_request)
        tunnel.on('error', on_error)
        tunnel.on('expired', on_expired)
        
        # Monitoring en temps réel
        def monitor_tunnel():
            while tunnel.is_active and not tunnel.is_expired:
                time.sleep(30)  # Vérifier toutes les 30 secondes
                
                if verbose:
                    stats = tunnel.get_stats()
                    remaining = format_time_remaining(stats['remaining_time'])
                    print_info(f"Tunnel actif - {stats['requests_count']} requêtes - Expire dans {remaining}")
        
        # Démarrer le monitoring en arrière-plan
        monitor_thread = threading.Thread(target=monitor_tunnel, daemon=True)
        monitor_thread.start()
        
        # Attendre l'expiration ou l'interruption
        tunnel.wait_until_expired()
        
        if tunnel.is_expired:
            print_warning("Le tunnel a expiré")
        
    except KeyboardInterrupt:
        print_info("\nArrêt demandé par l'utilisateur")
    except Exception as e:
        print_error(f"Erreur: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
    finally:
        # Nettoyage
        client.close_all_tunnels()
        print_success("Tunnel fermé")


if __name__ == '__main__':
    main()