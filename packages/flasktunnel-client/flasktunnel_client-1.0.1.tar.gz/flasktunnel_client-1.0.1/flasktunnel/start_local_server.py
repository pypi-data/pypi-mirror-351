#!/usr/bin/env python3
# =============================================================================
# start_local_server.py - Script pour démarrer le serveur FlaskTunnel local
# =============================================================================

"""
Script pour démarrer facilement le serveur FlaskTunnel local.
Utilisez ce script pour tester FlaskTunnel en mode local.
"""

import sys
import os
import subprocess
import signal
import time
import threading
import requests
from pathlib import Path

def check_port_available(port, host='localhost'):
    """Vérifier si un port est disponible."""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0
    except socket.error:
        return False

def check_dependencies():
    """Vérifier les dépendances requises."""
    required_packages = ['flask', 'flask-socketio', 'flask-cors', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Dépendances manquantes:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Installez-les avec:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def wait_for_server(host='localhost', port=8080, timeout=30):
    """Attendre que le serveur soit disponible."""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"http://{host}:{port}/api/health", timeout=2)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(1)
    
    return False

def main():
    """Fonction principale."""
    print("🚀 FlaskTunnel - Serveur Local")
    print("=" * 50)
    
    # Vérifier les dépendances
    if not check_dependencies():
        sys.exit(1)
    
    # Configuration
    host = os.getenv('FLASKTUNNEL_HOST', 'localhost')
    port = int(os.getenv('FLASKTUNNEL_PORT', '8080'))
    
    # Vérifier si le port est disponible
    if not check_port_available(port, host):
        print(f"❌ Le port {port} est déjà utilisé sur {host}")
        print("💡 Essayez un autre port ou arrêtez le service qui l'utilise")
        sys.exit(1)
    
    print(f"🔧 Configuration:")
    print(f"   - Hôte: {host}")
    print(f"   - Port: {port}")
    print(f"   - URL: http://{host}:{port}")
    
    # Import du serveur (après vérification des dépendances)
    try:
        from flasktunnel.server import FlaskTunnelServer
    except ImportError as e:
        print(f"❌ Impossible d'importer le serveur FlaskTunnel: {e}")
        print("💡 Assurez-vous que le module flasktunnel est installé")
        sys.exit(1)
    
    # Créer et démarrer le serveur
    server = FlaskTunnelServer(host=host, port=port)
    
    # Gestionnaire de signaux pour un arrêt propre
    def signal_handler(signum, frame):
        print("\n🛑 Arrêt du serveur...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        print(f"\n🟢 Démarrage du serveur sur http://{host}:{port}")
        print("📊 API Health Check: http://{host}:{port}/api/health")
        print("💡 Appuyez sur Ctrl+C pour arrêter")
        print("-" * 50)
        
        server.run(debug=False)
        
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur du serveur: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()