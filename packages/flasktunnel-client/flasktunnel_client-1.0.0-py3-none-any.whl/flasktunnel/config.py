# =============================================================================
# flasktunnel/config.py
# =============================================================================

"""Configuration management pour FlaskTunnel."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class FlaskTunnelConfig:
    """Configuration pour FlaskTunnel."""
    
    port: int = 5000  # Port par défaut pour Flask
    subdomain: Optional[str] = None
    auth_token: Optional[str] = None
    duration: str = "2h"
    password: Optional[str] = None
    cors: bool = False
    https: bool = False
    webhook: bool = False
    custom_domain: Optional[str] = None
    server_url: str = "https://flasktunnel.up.railway.app/"  # URL du serveur de production
    local_mode: bool = False  # Mode local pour développement
    
    @classmethod
    def from_file(cls, config_path: str = ".flasktunnel.json") -> "FlaskTunnelConfig":
        """Charger la configuration depuis un fichier JSON."""
        if not os.path.exists(config_path):
            return cls()
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls(**data)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"⚠️  Erreur de configuration dans {config_path}: {e}")
            return cls()
    
    @classmethod
    def from_env(cls) -> "FlaskTunnelConfig":
        """Charger la configuration depuis les variables d'environnement."""
        config = cls()
        
        # Mapping des variables d'environnement
        env_mapping = {
            'FLASKTUNNEL_PORT': 'port',
            'FLASKTUNNEL_SUBDOMAIN': 'subdomain', 
            'FLASKTUNNEL_API_KEY': 'auth_token',
            'FLASKTUNNEL_AUTH_TOKEN': 'auth_token',
            'FLASKTUNNEL_DURATION': 'duration',
            'FLASKTUNNEL_PASSWORD': 'password',
            'FLASKTUNNEL_CORS': 'cors',
            'FLASKTUNNEL_HTTPS': 'https',
            'FLASKTUNNEL_WEBHOOK': 'webhook',
            'FLASKTUNNEL_CUSTOM_DOMAIN': 'custom_domain',
            'FLASKTUNNEL_SERVER_URL': 'server_url',
            'FLASKTUNNEL_LOCAL_MODE': 'local_mode',
        }
        
        for env_var, attr in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Conversion de types pour les booléens et entiers
                if attr in ['cors', 'https', 'webhook', 'local_mode']:
                    value = value.lower() in ('true', '1', 'yes', 'on')
                elif attr == 'port':
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                
                setattr(config, attr, value)
        
        return config
    
    def get_effective_server_url(self) -> str:
        """Obtenir l'URL effective du serveur selon le mode."""
        if self.local_mode:
            return "http://localhost:8080"
        return self.server_url
    
    def save_to_file(self, config_path: str = ".flasktunnel.json") -> None:
        """Sauvegarder la configuration dans un fichier JSON."""
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Impossible de sauvegarder la configuration: {e}")
    
    def merge_with_args(self, **kwargs) -> "FlaskTunnelConfig":
        """Fusionner avec des arguments de ligne de commande."""
        data = asdict(self)
        
        # Supprimer les valeurs None des kwargs
        filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None and (v is not False or k in ['cors', 'https', 'webhook', 'local_mode'])}
        data.update(filtered_kwargs)
        
        return FlaskTunnelConfig(**data)
    
    def validate(self) -> bool:
        """Valider la configuration."""
        errors = []
        
        # Validation du port
        if not isinstance(self.port, int) or self.port < 1 or self.port > 65535:
            errors.append(f"Port invalide: {self.port} (doit être entre 1-65535)")
        
        # Ports système bloqués
        blocked_ports = [22, 25, 53, 80, 443, 993, 995]
        if self.port in blocked_ports:
            errors.append(f"Port {self.port} est bloqué pour des raisons de sécurité")
        
        # Validation de la durée
        valid_durations = ['1h', '2h', '4h', '8h', '12h', '24h']
        if self.duration not in valid_durations:
            errors.append(f"Durée invalide: {self.duration} (doit être: {', '.join(valid_durations)})")
        
        # Validation du sous-domaine
        if self.subdomain:
            if not self.subdomain.replace('-', '').replace('_', '').isalnum():
                errors.append("Le sous-domaine ne peut contenir que des lettres, chiffres, - et _")
            if len(self.subdomain) > 50:
                errors.append("Le sous-domaine ne peut pas dépasser 50 caractères")
        
        if errors:
            for error in errors:
                print(f"❌ {error}")
            return False
        
        return True