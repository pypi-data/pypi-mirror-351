# =============================================================================
# flasktunnel/cli.py  
# =============================================================================

"""Interface en ligne de commande moderne pour FlaskTunnel."""

import click
import signal
import sys
import time
import threading
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.box import ROUNDED
from rich import print as rprint
from rich.prompt import Prompt, Confirm
from rich.spinner import Spinner
import pyfiglet
from datetime import datetime, timedelta

from .client import FlaskTunnelClient
from .config import FlaskTunnelConfig
from .auth import FlaskTunnelAuth
from .utils import check_service_running

# Console Rich globale avec support responsive
console = Console()

# Classe personnalisée pour l'aide colorée
class ColoredHelpFormatter(click.HelpFormatter):
    """Formateur d'aide personnalisé avec couleurs."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = Console(force_terminal=True, width=self.width if hasattr(self, 'width') else None)
    
    def write_usage(self, prog, args='', prefix='Usage: '):
        """Écrire l'usage avec couleurs."""
        if prefix:
            self.console.print(f"[bold cyan]{prefix}[/bold cyan][white]{prog}[/white] [dim]{args}[/dim]")
        else:
            self.console.print(f"[white]{prog}[/white] [dim]{args}[/dim]")
    
    def write_heading(self, heading):
        """Écrire les en-têtes avec couleurs."""
        self.console.print(f"\n[bold yellow]{heading}:[/bold yellow]")
    
    def write_paragraph(self):
        """Écrire un paragraphe vide."""
        self.console.print()
    
    def write_text(self, text):
        """Écrire du texte normal."""
        if text:
            self.console.print(f"[green]{text}[/green]")

class ColoredCommand(click.Command):
    """Commande Click personnalisée avec aide colorée."""
    
    def get_help(self, ctx):
        """Obtenir l'aide formatée avec couleurs."""
        formatter = ColoredHelpFormatter()
        self.format_help(ctx, formatter)
        return ""  # Rich affiche directement
    
    def format_help(self, ctx, formatter):
        """Formater l'aide avec couleurs personnalisées."""
        console = Console()
        
        # Bannière pour l'aide
        help_banner = Panel(
            "[bold cyan]FlaskTunnel CLI[/bold cyan]\n"
            "[dim]Créez des tunnels HTTP sécurisés vers vos applications locales[/dim]",
            border_style="bright_blue",
            title="[bold white]🚀 Aide FlaskTunnel[/bold white]",
        )
        console.print(help_banner)
        
        # Usage
        console.print(f"\n[bold yellow]Usage:[/bold yellow]")
        prog_name = ctx.find_root().info_name
        console.print(f"  [white]{prog_name}[/white] [dim][OPTIONS][/dim]")
        
        # Description
        if self.help:
            console.print(f"\n[bold yellow]Description:[/bold yellow]")
            console.print(f"  [green]{self.help}[/green]")
        
        # Options
        console.print(f"\n[bold yellow]Options:[/bold yellow]")
        
        # Grouper les options par catégorie
        basic_options = []
        config_options = []
        auth_options = []
        advanced_options = []
        
        for param in self.get_params(ctx):
            if isinstance(param, click.Option):
                option_info = self._format_option_help(param)
                
                # Catégoriser les options
                option_name = param.name
                if option_name in ['port', 'subdomain', 'name', 'password', 'duration']:
                    basic_options.append(option_info)
                elif option_name in ['config', 'local_mode', 'server_url', 'verbose']:
                    config_options.append(option_info)
                elif option_name in ['auth', 'login', 'register', 'logout']:
                    auth_options.append(option_info)
                else:
                    advanced_options.append(option_info)
        
        # Afficher les options par catégorie
        if basic_options:
            console.print("  [bold blue]Options Principales:[/bold blue]")
            for opt in basic_options:
                console.print(f"    {opt}")
        
        if config_options:
            console.print("\n  [bold blue]Configuration:[/bold blue]")
            for opt in config_options:
                console.print(f"    {opt}")
        
        if auth_options:
            console.print("\n  [bold blue]Authentification:[/bold blue]")
            for opt in auth_options:
                console.print(f"    {opt}")
        
        if advanced_options:
            console.print("\n  [bold blue]Options Avancées:[/bold blue]")
            for opt in advanced_options:
                console.print(f"    {opt}")
        
        # Exemples
        console.print(f"\n[bold yellow]Exemples:[/bold yellow]")
        examples = [
            ("[white]flasktunnel --port 3000[/white]", "Expose le port 3000 avec un sous-domaine automatique"),
            ("[white]flasktunnel -p 8000 -s myapp[/white]", "Expose le port 8000 avec le sous-domaine 'myapp'"),
            ("[white]flasktunnel --port 5000 --password secretpass[/white]", "Tunnel protégé par mot de passe"),
            ("[white]flasktunnel --diagnose[/white]", "Diagnostic du système"),
            ("[white]flasktunnel --list[/white]", "Liste des tunnels actifs"),
        ]
        
        for cmd, desc in examples:
            console.print(f"  {cmd}")
            console.print(f"    [green]{desc}[/green]")
            console.print()
        
        # Aide supplémentaire
        console.print(Panel(
            "[bold blue]💡 Besoin d'aide ?[/bold blue]\n\n"
            "• 📚 Documentation: https://flasktunnel.up.railway.app/docs\n"
            "• 🐛 Signaler un bug: https://github.com/flasktunnel/issues\n"
            "• 💬 Support: support@flasktunnel.app",
            title="[bold white]🤝 Support[/bold white]",
            border_style="blue"
        ))
    
    def _format_option_help(self, param):
        """Formater l'aide d'une option."""
        opts = []
        
        # Collecter tous les noms d'options
        for opt in param.opts:
            opts.append(opt)
        
        if param.secondary_opts:
            opts.extend(param.secondary_opts)
        
        opts_str = ", ".join(f"[white]{opt}[/white]" for opt in opts)
        
        # Type de paramètre
        if param.type.name != 'BOOL':
            if hasattr(param.type, 'name'):
                type_hint = param.type.name.upper()
            else:
                type_hint = "VALUE"
            opts_str += f" [dim]{type_hint}[/dim]"
        
        # Description
        help_text = param.help or ""
        
        # Valeur par défaut
        if param.default is not None and param.default != () and not param.is_flag:
            if isinstance(param.default, str) and param.default:
                help_text += f" [dim](défaut: {param.default})[/dim]"
            elif not isinstance(param.default, str):
                help_text += f" [dim](défaut: {param.default})[/dim]"
        
        return f"{opts_str:<30} [green]{help_text}[/green]"

class ModernUI:
    """Interface utilisateur moderne avec Rich."""
    
    def __init__(self):
        """Initialiser l'UI avec détection de taille de terminal."""
        self.console = Console()
        self.terminal_width = self.console.size.width
        self.is_narrow = self.terminal_width < 80
    
    def print_banner(self):
        """Affiche la bannière modernisée et responsive."""
        # ASCII Art adaptatif
        if self.is_narrow:
            title = "FlaskTunnel"
            font = "small"
        else:
            title = pyfiglet.figlet_format("FlaskTunnel", font="slant")
            font = "slant"
        
        # Adapter le contenu selon la largeur
        if self.is_narrow:
            banner_content = (
                f"[bold cyan]{title}[/bold cyan]\n"
                f"[dim]Tunnels HTTP sécurisés[/dim]\n"
                f"[bold green]v2.1.0[/bold green]"
            )
        else:
            banner_content = (
                f"[bold cyan]{title}[/bold cyan]\n"
                f"[dim]Créez des tunnels HTTP sécurisés vers vos applications locales[/dim]\n"
                f"[bold green]v2.1.0[/bold green] • [blue]https://flasktunnel.up.railway.app[/blue]"
            )
        
        banner_panel = Panel(
            banner_content,
            border_style="bright_blue",
            padding=(1, 2),
            title="[bold white]🚀 FlaskTunnel[/bold white]",
            title_align="center"
        )
        
        self.console.print(banner_panel)
        self.console.print()
    
    def print_tunnel_info(self, tunnel):
        """Affiche les informations du tunnel de manière moderne et responsive."""
         # AJOUTER une vérification de sécurité :
        local_port = getattr(tunnel, 'local_port', getattr(tunnel, 'port', 'N/A'))
        # Adapter l'affichage selon la largeur du terminal
        if self.is_narrow:
            # Mode étroit - informations verticales
            info_text = (
                f"[bold green]🌐 {tunnel.public_url}[/bold green]\n"
                f"[yellow]🏠 Port: {local_port}[/yellow]\n"  # Utiliser la variable sécurisée
                f"[cyan]🔗 Sous-domaine: {getattr(tunnel, 'subdomain', 'auto')}[/cyan]\n"
                f"[red]⏰ Expire: {getattr(tunnel, 'expires_at', 'N/A')}[/red]"
            )
            
            info_panel = Panel(
                info_text,
                title="[bold white]📊 Tunnel[/bold white]",
                border_style="green",
                padding=(1, 1)
            )
        else:
            # Mode large - tableau
            table = Table(show_header=False, box=ROUNDED, border_style="cyan")
            table.add_column("Property", style="bold magenta", width=20)
            table.add_column("Value", style="bright_white")
            
            table.add_row("🌐 URL Publique", f"[bold green]{tunnel.public_url}[/bold green]")
            table.add_row("🏠 Port Local", f"[yellow]{local_port}[/yellow]")  # Utiliser la variable sécurisée
            table.add_row("🔗 Sous-domaine", f"[cyan]{getattr(tunnel, 'subdomain', 'auto-généré')}[/cyan]")
            table.add_row("⏰ Expire le", f"[red]{getattr(tunnel, 'expires_at', 'N/A')}[/red]")
            table.add_row("🔐 Protégé", f"[green]Oui[/green]" if getattr(tunnel, 'password', None) else "[dim]Non[/dim]")
            table.add_row("🌍 CORS", f"[green]Activé[/green]" if getattr(tunnel, 'cors', False) else "[dim]Désactivé[/dim]")
            table.add_row("🔒 HTTPS", f"[green]Forcé[/green]" if getattr(tunnel, 'https', False) else "[yellow]Auto[/yellow]")
            
            info_panel = Panel(
                table,
                title="[bold white]📊 Informations du Tunnel[/bold white]",
                border_style="green",
                padding=(1, 2)
            )
        
        self.console.print(info_panel)
        
        # Instructions adaptées
        if self.is_narrow:
            instructions_text = (
                "[bold blue]💡[/bold blue] Copiez l'URL dans votre navigateur\n"
                "[bold blue]🔍[/bold blue] Utilisez -v pour voir les requêtes\n"
                "[bold blue]⏹️[/bold blue] Ctrl+C pour arrêter"
            )
        else:
            instructions = Table(show_header=False, box=None, padding=(0, 1))
            instructions.add_column(style="bold blue")
            instructions.add_column(style="dim")
            
            instructions.add_row("💡", "Copiez l'URL publique dans votre navigateur")
            instructions.add_row("🔍", "Utilisez --verbose pour voir les requêtes en temps réel")
            instructions.add_row("⏹️", "Appuyez sur Ctrl+C pour arrêter le tunnel")
            
            instructions_text = instructions
        
        self.console.print(Panel(
            instructions_text,
            title="[bold yellow]💡 Conseils[/bold yellow]",
            border_style="yellow",
            padding=(0, 1)
        ))
        self.console.print()
    
    def print_success(self, message: str, title: str = "Succès"):
        """Affiche un message de succès."""
        self.console.print(Panel(
            f"[bold green]✅ {message}[/bold green]",
            title=f"[bold white]{title}[/bold white]",
            border_style="green"
        ))
    
    def print_error(self, message: str, title: str = "Erreur"):
        """Affiche un message d'erreur."""
        self.console.print(Panel(
            f"[bold red]❌ {message}[/bold red]",
            title=f"[bold white]{title}[/bold white]",
            border_style="red"
        ))
    
    def print_warning(self, message: str, title: str = "Attention"):
        """Affiche un message d'avertissement."""
        self.console.print(Panel(
            f"[bold yellow]⚠️ {message}[/bold yellow]",
            title=f"[bold white]{title}[/bold white]",
            border_style="yellow"
        ))
    
    def print_info(self, message: str, title: str = "Information"):
        """Affiche un message d'information."""
        self.console.print(Panel(
            f"[bold blue]ℹ️ {message}[/bold blue]",
            title=f"[bold white]{title}[/bold white]",
            border_style="blue"
        ))
    
    def show_progress(self, description: str):
        """Affiche une barre de progression."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        )
    
    def show_tunnels_table(self, tunnels):
        """Affiche la liste des tunnels dans un tableau moderne et responsive."""
        if not tunnels:
            self.print_warning("Aucun tunnel actif trouvé", "Tunnels")
            return
        
        if self.is_narrow:
            # Mode étroit - liste verticale
            for i, tunnel in enumerate(tunnels, 1):
                status_icon = "🟢" if tunnel['status'] == 'active' else "🔴"
                status_text = "ACTIF" if tunnel['status'] == 'active' else "FERMÉ"
                
                tunnel_info = (
                    f"{status_icon} [bold]{status_text}[/bold]\n"
                    f"[cyan]{tunnel['public_url']}[/cyan]\n"
                    f"Port: [yellow]{tunnel['port']}[/yellow]\n"
                    f"ID: [dim]{tunnel['tunnel_id'][:8]}...[/dim]\n"
                    f"Expire: [red]{tunnel['expires_at']}[/red]"
                )
                
                self.console.print(Panel(
                    tunnel_info,
                    title=f"[bold white]Tunnel #{i}[/bold white]",
                    border_style="cyan"
                ))
        else:
            # Mode large - tableau
            table = Table(title="[bold cyan]🌐 Tunnels Actifs[/bold cyan]", box=ROUNDED)
            table.add_column("Status", justify="center", style="bold", width=8)
            table.add_column("URL Publique", style="cyan")
            table.add_column("Port Local", justify="center", style="yellow")
            table.add_column("ID Tunnel", style="dim")
            table.add_column("Expire", style="red")
            
            for tunnel in tunnels:
                status_icon = "🟢" if tunnel['status'] == 'active' else "🔴"
                status_text = "ACTIF" if tunnel['status'] == 'active' else "FERMÉ"
                
                table.add_row(
                    f"{status_icon}\n{status_text}",
                    f"[bold]{tunnel['public_url']}[/bold]",
                    str(tunnel['port']),
                    tunnel['tunnel_id'][:8] + "...",
                    tunnel['expires_at']
                )
            
            self.console.print(table)
    
    def show_diagnostic_results(self, results, config):
        """Affiche les résultats du diagnostic de manière responsive."""
        if self.is_narrow:
            # Mode étroit - informations compactes
            mode_text = "🏠 LOCAL" if config.local_mode else "🌐 PRODUCTION"
            server_status = "✅ OK" if results['server_connection'] else "❌ ÉCHEC"
            local_count = len(results['local_ports'])
            local_status = f"✅ {local_count} service(s)" if local_count > 0 else "⚠️ Aucun"
            api_status = "✅ VALIDE" if results['api_key_valid'] else "❌ INVALIDE"
            
            diagnostic_text = (
                f"Mode: {mode_text}\n"
                f"Serveur: {server_status}\n"
                f"Services: {local_status}\n"
                f"API: {api_status}"
            )
            
            self.console.print(Panel(
                diagnostic_text,
                title="[bold magenta]🔍 Diagnostic[/bold magenta]",
                border_style="magenta"
            ))
        else:
            # Mode large - tableau complet
            table = Table(title="[bold magenta]🔍 Diagnostic du Système[/bold magenta]", box=ROUNDED)
            table.add_column("Composant", style="bold")
            table.add_column("Status", justify="center")
            table.add_column("Détails", style="dim")
            
            # Mode
            mode_icon = "🏠" if config.local_mode else "🌐"
            mode_text = "LOCAL" if config.local_mode else "PRODUCTION"
            table.add_row(f"{mode_icon} Mode", f"[cyan]{mode_text}[/cyan]", config.get_effective_server_url())
            
            # Connexion serveur
            server_status = "✅ CONNECTÉ" if results['server_connection'] else "❌ ÉCHEC"
            server_style = "green" if results['server_connection'] else "red"
            table.add_row("🌐 Serveur", f"[{server_style}]{server_status}[/{server_style}]", "Connexion au serveur FlaskTunnel")
            
            # Services locaux
            local_count = len(results['local_ports'])
            local_status = f"✅ {local_count} DÉTECTÉ(S)" if local_count > 0 else "⚠️ AUCUN"
            local_style = "green" if local_count > 0 else "yellow"
            local_ports = ", ".join(map(str, results['local_ports'])) if results['local_ports'] else "Aucun"
            table.add_row("🏠 Services Locaux", f"[{local_style}]{local_status}[/{local_style}]", f"Ports: {local_ports}")
            
            # Clé API
            api_status = "✅ VALIDE" if results['api_key_valid'] else "❌ INVALIDE"
            api_style = "green" if results['api_key_valid'] else "red"
            table.add_row("🔑 Clé API", f"[{api_style}]{api_status}[/{api_style}]", "Authentification FlaskTunnel")
            
            self.console.print(table)
        
        # Suggestions si problèmes
        if not results['server_connection']:
            suggestions = []
            if config.local_mode:
                suggestions.extend([
                    "🔧 Démarrez le serveur FlaskTunnel local sur le port 8080",
                    "🔄 Ou désactivez le mode local pour utiliser le service en ligne"
                ])
            else:
                suggestions.extend([
                    "🌐 Vérifiez votre connexion internet",
                    "🏠 Essayez le mode local avec --local-mode",
                    "⏰ Le service pourrait être temporairement indisponible"
                ])
            
            self.console.print(Panel(
                "\n".join(suggestions),
                title="[bold yellow]💡 Solutions Suggérées[/bold yellow]",
                border_style="yellow"
            ))
    
    def show_real_time_stats(self, tunnel, stats):
        """Affiche les statistiques en temps réel de manière responsive."""
        # AJOUTER ces vérifications de sécurité au début :
        try:
            public_url = getattr(tunnel, 'public_url', 'N/A')
            local_port = getattr(tunnel, 'local_port', getattr(tunnel, 'port', 'N/A'))
            subdomain = getattr(tunnel, 'subdomain', 'auto')
            expires_at = getattr(tunnel, 'expires_at', 'N/A')
            created_at = getattr(tunnel, 'created_at', datetime.now())
        except Exception:
            # Valeurs par défaut en cas d'erreur
            public_url = 'N/A'
            local_port = 'N/A'
            subdomain = 'auto'
            expires_at = 'N/A'
            created_at = datetime.now()
        
        if self.is_narrow:
            # Mode étroit - informations compactes
            uptime = datetime.now() - created_at
            remaining = format_time_remaining(stats.get('remaining_time', 0))
            
            stats_text = (
                f"[cyan]{public_url}[/cyan]\n"
                f"📊 Requêtes: [green]{stats.get('requests_count', 0)}[/green]\n"
                f"⏰ Durée: [yellow]{uptime}[/yellow]\n"
                f"⏳ Restant: [red]{remaining}[/red]\n"
                f"📈 Débit: [cyan]{stats.get('bandwidth', '0 B/s')}[/cyan]"
                f" Quitter: [red]CTRL + C[/red]\n"
            )
            
            return Panel(
                stats_text,
                title="[bold cyan]🚀 FlaskTunnel Live[/bold cyan]",
                border_style="cyan"
            )
        else:
            # Mode large - layout complet
            layout = Layout()
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="stats", size=10),
                Layout(name="footer", size=3)
            )
            
            # En-tête
            header_text = Text("🚀 FlaskTunnel - Monitoring en Temps Réel", style="bold cyan")
            layout["header"].update(Align.center(header_text))
            
            # Stats principales
            stats_table = Table(show_header=False, box=None)
            stats_table.add_column(style="bold blue", width=20)
            stats_table.add_column(style="bright_white")
            
            uptime = datetime.now() - tunnel.created_at if hasattr(tunnel, 'created_at') else timedelta(seconds=0)
            remaining = format_time_remaining(stats.get('remaining_time', 0))
            
            stats_table.add_row("🌐 URL:", f"[link]{tunnel.public_url}[/link]")
            stats_table.add_row("📊 Requêtes:", f"[green]{stats.get('requests_count', 0)}[/green]")
            stats_table.add_row("⏰ Durée de vie:", f"[yellow]{uptime}[/yellow]")
            stats_table.add_row("⏳ Temps restant:", f"[red]{remaining}[/red]")
            stats_table.add_row("📈 Débit:", f"[cyan]{stats.get('bandwidth', '0 B/s')}[/cyan]")
            
            layout["stats"].update(Panel(stats_table, title="📊 Statistiques", border_style="cyan"))
            
            # Pied de page
            footer_text = Text("Appuyez sur Ctrl+C pour arrêter", style="dim")
            layout["footer"].update(Align.center(footer_text))
            
            return layout


def signal_handler(signum, frame):
    """Gestionnaire pour les signaux système (Ctrl+C) avec gestion d'erreur."""
    try:
        console.print("\n[bold yellow]⏹️ Arrêt du tunnel en cours...[/bold yellow]")
        # AJOUTER cette partie pour éviter l'arrêt immédiat :
        if hasattr(signal_handler, 'tunnel_instance'):
            signal_handler.tunnel_instance.close()
    except Exception as e:
        print(f"\nErreur lors de l'arrêt: {e}")
    finally:
        # CHANGER sys.exit(0) par :
        raise KeyboardInterrupt()  # Permet une gestion propre


def format_time_remaining(seconds):
    """Formate le temps restant de manière lisible."""
    if seconds <= 0:
        return "Expiré"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return f"{seconds}s"


@click.command(cls=ColoredCommand, context_settings={'help_option_names': ['-h', '--help']})
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
@click.option('--verbose', '-v', is_flag=True, help='Mode verbeux avec logs détaillés')
@click.option('--test', is_flag=True, help='Tester la connexion au serveur')
@click.option('--diagnose', is_flag=True, help='Diagnostic complet du système')
@click.option('--login', is_flag=True, help='Se connecter à FlaskTunnel')
@click.option('--register', is_flag=True, help='Créer un compte FlaskTunnel')
@click.option('--logout', is_flag=True, help='Se déconnecter de FlaskTunnel')
@click.option('--list', 'list_tunnels', is_flag=True, help='Lister tous les tunnels actifs')
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
    
    # Interface moderne
    ui = ModernUI()
    
    # Gestionnaire de signaux
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Bannière
    if not any([test, diagnose, login, register, logout, list_tunnels]):
        ui.print_banner()
    
    # Charger la configuration
    if config:
        tunnel_config = FlaskTunnelConfig.from_file(config)
    else:
        tunnel_config = FlaskTunnelConfig.from_file()
        env_config = FlaskTunnelConfig.from_env()
        tunnel_config = tunnel_config.merge_with_args(**env_config.__dict__)
    
    # Arguments de ligne de commande
    cli_args = {
        'port': port,
        'subdomain': subdomain or name,
        'password': password,
        'duration': duration,
        'cors': cors,
        'https': https,
        'webhook': webhook,
        'auth_token': auth,
        'local_mode': local_mode,
        'server_url': server_url
    }
    
    tunnel_config = tunnel_config.merge_with_args(**{k: v for k, v in cli_args.items() if v is not None})
    
    # Client FlaskTunnel
    client = FlaskTunnelClient(tunnel_config)
    auth_manager = FlaskTunnelAuth(tunnel_config.get_effective_server_url())
    
    # Information sur le mode utilisé
    if verbose:
        server_mode = "LOCAL" if tunnel_config.local_mode else "PRODUCTION"
        ui.print_info(f"Mode: {server_mode} | Serveur: {tunnel_config.get_effective_server_url()}", "Configuration")
    
    # Commandes spéciales
    if login:
        ui.print_info("Connexion à FlaskTunnel", "Authentification")
        email = Prompt.ask("📧 [bold cyan]Email[/bold cyan]")
        password = Prompt.ask("🔒 [bold cyan]Mot de passe[/bold cyan]", password=True)
        
        try:
            auth_manager.login(email, password)
            ui.print_success("Connexion réussie !")
        except Exception as e:
            ui.print_error(f"Échec de la connexion: {e}")
        return
    
    if register:
        ui.print_info("Création d'un compte FlaskTunnel", "Inscription")
        email = Prompt.ask("📧 [bold cyan]Email[/bold cyan]")
        password = Prompt.ask("🔒 [bold cyan]Mot de passe[/bold cyan]", password=True)
        confirm_password = Prompt.ask("🔒 [bold cyan]Confirmer le mot de passe[/bold cyan]", password=True)
        
        if password != confirm_password:
            ui.print_error("Les mots de passe ne correspondent pas")
            return
        
        try:
            auth_manager.register(email, password)
            ui.print_success("Compte créé avec succès !")
        except Exception as e:
            ui.print_error(f"Échec de l'inscription: {e}")
        return
    
    if logout:
        try:
            auth_manager.logout()
            ui.print_success("Déconnexion réussie")
        except Exception as e:
            ui.print_error(f"Erreur lors de la déconnexion: {e}")
        return
    
    if test:
        with ui.show_progress("Test de connexion à FlaskTunnel...") as progress:
            task = progress.add_task("Connexion en cours...", total=100)
            progress.update(task, advance=50)
            
            connection_ok = client.test_connection()
            progress.update(task, advance=50)
        
        if connection_ok:
            ui.print_success("Connexion OK - FlaskTunnel est accessible", "Test de Connexion")
        else:
            ui.print_error("Impossible de se connecter à FlaskTunnel", "Test de Connexion")
            if tunnel_config.local_mode:
                ui.print_info("💡 Mode local activé - Démarrez le serveur FlaskTunnel local", "Suggestion")
            else:
                ui.print_info("💡 Vérifiez votre connexion internet ou essayez --local-mode", "Suggestion")
        return
    
    if diagnose:
        with ui.show_progress("Diagnostic du système FlaskTunnel...") as progress:
            task = progress.add_task("Analyse en cours...", total=100)
            
            progress.update(task, advance=25, description="Vérification de la connexion...")
            results = client.diagnose()
            progress.update(task, advance=75, description="Analyse terminée")
        
        ui.show_diagnostic_results(results, tunnel_config)
        return
    
    if list_tunnels:
        with ui.show_progress("Récupération des tunnels actifs...") as progress:
            task = progress.add_task("Chargement...", total=100)
            progress.update(task, advance=50)
            
            tunnels = client.list_tunnels()
            progress.update(task, advance=50)
        
        ui.show_tunnels_table(tunnels)
        return
    
    # Validation de la configuration
    if not tunnel_config.validate():
        ui.print_error("Configuration invalide - Vérifiez vos paramètres", "Configuration")
        return
    
    # Vérifier le port
    if not check_service_running(tunnel_config.port):
        ui.print_warning(
            f"Aucun service détecté sur le port {tunnel_config.port}\n"
            f"Le tunnel sera créé mais ne pourra pas traiter les requêtes\n"
            f"Démarrez votre application sur le port {tunnel_config.port} après création du tunnel",
            "Service Local"
        )
        
        if not Confirm.ask("[bold yellow]Continuer quand même ?[/bold yellow]"):
            ui.print_info("Création du tunnel annulée")
            return
    
    try:
        # Créer le tunnel avec progress
        with ui.show_progress("Création du tunnel en cours...") as progress:
            task = progress.add_task(f"Connexion vers localhost:{tunnel_config.port}...", total=100)
            
            progress.update(task, advance=30, description="Connexion au serveur...")
            
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
            
            tunnel.local_port = tunnel_config.port
            
            progress.update(task, advance=40, description="Configuration du tunnel...")
            
            # Connexion WebSocket
            tunnel.connect_websocket()
            
            progress.update(task, advance=30, description="Tunnel créé avec succès !")
        
        # Afficher les informations du tunnel
        ui.print_tunnel_info(tunnel)
        
        # AJOUTER cette ligne pour le gestionnaire de signaux :
        signal_handler.tunnel_instance = tunnel
        
        # Variables pour le monitoring
        stats = {
            'requests_count': 0,
            'bandwidth': '0 B/s',
            'remaining_time': tunnel.remaining_time if hasattr(tunnel, 'remaining_time') else 0
        }
        
        # Callbacks pour les événements
        def on_request(data):
            stats['requests_count'] += 1
            if verbose:
                method = data.get('method', 'GET')
                path = data.get('path', '/')
                ip = data.get('ip', 'unknown')
                timestamp = datetime.now().strftime("%H:%M:%S")
                console.print(f"[dim]{timestamp}[/dim] [bold blue]📨[/bold blue] [green]{method}[/green] [cyan]{path}[/cyan] [dim]from {ip}[/dim]")
        
        def on_response(data):
            if verbose:
                status = data.get('status', 200)
                size = data.get('size', 0)
                duration = data.get('duration', 0)
                status_color = "green" if status < 400 else "red"
                console.print(f"[dim]   ↳[/dim] [bold {status_color}]{status}[/bold {status_color}] [dim]{size}B in {duration}ms[/dim]")
        
        def on_error(data):
            error_msg = data.get('message', 'Erreur inconnue')
            ui.print_error(f"Erreur tunnel: {error_msg}", "Tunnel")
        
        def on_expired(data):
            ui.print_warning("Le tunnel a expiré", "Expiration")
        
        def on_stats_update(data):
            stats.update(data)
        
        # Enregistrer les callbacks
        tunnel.on('request', on_request)
        tunnel.on('response', on_response)
        tunnel.on('error', on_error)
        tunnel.on('expired', on_expired)
        tunnel.on('stats', on_stats_update)
        
        # Monitoring en temps réel avec interface moderne
        if verbose:
            def run_live_monitoring():
                with Live(ui.show_real_time_stats(tunnel, stats), refresh_per_second=2, console=console) as live:
                    while tunnel.is_active and not tunnel.is_expired:
                        time.sleep(0.5)
                        
                        # Mettre à jour les stats
                        if hasattr(tunnel, 'get_stats'):
                            current_stats = tunnel.get_stats()
                            stats.update(current_stats)
                        
                        # Mettre à jour l'affichage
                        live.update(ui.show_real_time_stats(tunnel, stats))
            
            # Démarrer le monitoring live
            monitor_thread = threading.Thread(target=run_live_monitoring, daemon=True)
            monitor_thread.start()
        else:
            # Monitoring simple en arrière-plan
            def monitor_tunnel():
                while tunnel.is_active and not tunnel.is_expired:
                    time.sleep(30)  # Vérifier toutes les 30 secondes
                    
                    if hasattr(tunnel, 'get_stats'):
                        current_stats = tunnel.get_stats()
                        remaining = format_time_remaining(current_stats.get('remaining_time', 0))
                        console.print(f"[dim]{datetime.now().strftime('%H:%M:%S')}[/dim] [blue]ℹ️[/blue] Tunnel actif - [green]{current_stats.get('requests_count', 0)}[/green] requêtes - Expire dans [red]{remaining}[/red]")
            
            monitor_thread = threading.Thread(target=monitor_tunnel, daemon=True)
            monitor_thread.start()
        
        # Message de statut
        if not verbose:
            console.print(Panel(
                "[bold green]✅ Tunnel actif et prêt à recevoir des requêtes[/bold green]\n"
                "[dim]Utilisez --verbose (-v) pour voir les requêtes en temps réel[/dim]\n"
                "[dim]Appuyez sur Ctrl+C pour arrêter le tunnel[/dim]",
                title="[bold cyan]🚀 FlaskTunnel[/bold cyan]",
                border_style="green"
            ))
        
        try:
            # Attendre l'expiration ou l'interruption
            while tunnel.is_active and not tunnel.is_expired:
                time.sleep(1)  # Vérification chaque seconde
            
            if tunnel.is_expired:
                ui.print_warning("Le tunnel a expiré automatiquement", "Expiration")
            
        except KeyboardInterrupt:
            console.print("\n[bold yellow]⏹️ Arrêt demandé par l'utilisateur[/bold yellow]")
        
    except KeyboardInterrupt:
        console.print("\n[bold yellow]⏹️ Arrêt demandé par l'utilisateur[/bold yellow]")
    except Exception as e:
        ui.print_error(f"Erreur: {e}", "Erreur Critique")
        if verbose:
            console.print_exception()
    finally:
    # Nettoyage avec indication visuelle
        try:
            console.print("[dim]Fermeture des connexions...[/dim]")
            if 'tunnel' in locals():  # AJOUTER cette vérification
                tunnel.close()
            client.close_all_tunnels()
            ui.print_success("Tunnel fermé proprement", "Nettoyage")
        except Exception as e:
            if verbose:
                ui.print_warning(f"Erreur lors du nettoyage: {e}", "Nettoyage")


if __name__ == '__main__':
    main()