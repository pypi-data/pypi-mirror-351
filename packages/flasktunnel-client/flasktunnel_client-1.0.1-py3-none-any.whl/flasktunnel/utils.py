# =============================================================================
# flasktunnel/utils.py
# =============================================================================

"""Utilitaires pour FlaskTunnel."""

import socket
import time
import random
import string
import sys
from typing import Optional
from colorama import init, Fore, Style

# Initialiser colorama pour Windows
init()


def check_port_available(port: int, host: str = 'localhost') -> bool:
    """Vérifier si un port est disponible."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0  # Port disponible si connexion échoue
    except socket.error:
        return False


def check_service_running(port: int, host: str = 'localhost') -> bool:
    """Vérifier si un service tourne sur un port."""
    return not check_port_available(port, host)


def generate_tunnel_id(length: int = 8) -> str:
    """Générer un ID de tunnel aléatoire."""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def format_time_remaining(seconds: int) -> str:
    """Formater le temps restant de manière lisible."""
    if seconds <= 0:
        return "Expiré"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes:02d}m {seconds:02d}s"
    elif minutes > 0:
        return f"{minutes}m {seconds:02d}s"
    else:
        return f"{seconds}s"


def format_size(bytes_count: int) -> str:
    """Formater une taille en bytes de manière lisible."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} PB"


def print_success(message: str) -> None:
    """Afficher un message de succès coloré."""
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")


def print_error(message: str) -> None:
    """Afficher un message d'erreur coloré."""
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")


def print_warning(message: str) -> None:
    """Afficher un message d'avertissement coloré."""
    print(f"{Fore.YELLOW}⚠️  {message}{Style.RESET_ALL}")


def print_info(message: str) -> None:
    """Afficher un message d'information coloré."""
    print(f"{Fore.CYAN}ℹ️  {message}{Style.RESET_ALL}")


def print_tunnel_info(tunnel) -> None:
    """Afficher les informations d'un tunnel de manière formatée."""
    print(f"\n{Fore.GREEN}🚀 FlaskTunnel Client Démarré!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ Tunnel créé: {Fore.BLUE}{tunnel.public_url}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}🔗 Redirige vers: {Fore.BLUE}{tunnel.local_url}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}⏰ Expire dans: {Fore.YELLOW}{format_time_remaining(tunnel.remaining_time)}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}📊 Dashboard: {Fore.BLUE}{tunnel.dashboard_url}{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}💡 Appuyez sur Ctrl+C pour arrêter le tunnel{Style.RESET_ALL}\n")


def print_banner() -> None:
    """Afficher la bannière FlaskTunnel."""
    banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════╗
║           🚀 FlaskTunnel v1.0.0       ║
║     Tunnels HTTP sécurisés & gratuits ║
╚═══════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def validate_subdomain(subdomain: str) -> bool:
    """Valider un nom de sous-domaine."""
    if not subdomain:
        return False
    
    # Longueur
    if len(subdomain) > 50:
        return False
    
    # Caractères autorisés
    allowed_chars = set(string.ascii_lowercase + string.digits + '-_')
    if not set(subdomain.lower()).issubset(allowed_chars):
        return False
    
    # Ne doit pas commencer ou finir par - ou _
    if subdomain.startswith(('-', '_')) or subdomain.endswith(('-', '_')):
        return False
    
    return True


def parse_duration(duration: str) -> int:
    """Convertir une durée en secondes."""
    duration = duration.lower().strip()
    
    # Mapping des unités
    multipliers = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400
    }
    
    if duration[-1] in multipliers:
        try:
            number = int(duration[:-1])
            return number * multipliers[duration[-1]]
        except ValueError:
            pass
    
    # Valeurs par défaut reconnues
    defaults = {
        '1h': 3600,
        '2h': 7200,
        '4h': 14400,
        '8h': 28800,
        '12h': 43200,
        '24h': 86400
    }
    
    return defaults.get(duration, 7200)  # 2h par défaut


def get_local_ip() -> str:
    """Récupérer l'adresse IP locale."""
    try:
        # Créer une connexion UDP vers Google DNS pour obtenir l'IP locale
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
    except Exception:
        return '127.0.0.1'


def is_url_accessible(url: str, timeout: int = 5) -> bool:
    """Vérifier si une URL est accessible."""
    import requests
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except requests.RequestException:
        return False