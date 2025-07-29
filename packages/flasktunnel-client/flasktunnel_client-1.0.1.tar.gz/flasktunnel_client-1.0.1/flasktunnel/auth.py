# =============================================================================
# flasktunnel/auth.py
# =============================================================================

"""Gestion de l'authentification FlaskTunnel."""

import os
import json
import requests
from pathlib import Path
from typing import Optional, Dict, Any

class FlaskTunnelAuth:
    """Gestion de l'authentification FlaskTunnel."""
    
    def __init__(self, server_url: str = "https://flasktunnel.up.railway.app/"):
        self.server_url = server_url.rstrip('/')
        self.credentials_file = Path.home() / ".flasktunnel" / "credentials.json"
        self.credentials_file.parent.mkdir(exist_ok=True)
    
    def load_credentials(self) -> Optional[Dict[str, Any]]:
        """Charger les identifiants sauvegardés."""
        if not self.credentials_file.exists():
            return None
        
        try:
            with open(self.credentials_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            return None
    
    def save_credentials(self, credentials: Dict[str, Any]) -> None:
        """Sauvegarder les identifiants."""
        try:
            with open(self.credentials_file, 'w', encoding='utf-8') as f:
                json.dump(credentials, f, indent=2)
            
            # Sécuriser le fichier (lecture seule pour le propriétaire)
            os.chmod(self.credentials_file, 0o600)
        except Exception as e:
            print(f"⚠️  Impossible de sauvegarder les identifiants: {e}")
    
    def get_api_key(self) -> Optional[str]:
        """Récupérer la clé API depuis les identifiants ou variables d'environnement."""
        # 1. Depuis les variables d'environnement
        api_key = os.getenv('FLASKTUNNEL_API_KEY') or os.getenv('FLASKTUNNEL_AUTH_TOKEN')
        if api_key:
            return api_key
        
        # 2. Depuis le fichier de credentials
        credentials = self.load_credentials()
        if credentials and 'api_key' in credentials:
            return credentials['api_key']
        
        return None
    
    def login(self, email: str, password: str) -> bool:
        """Se connecter avec email/mot de passe."""
        try:
            response = requests.post(
                f"{self.server_url}/api/auth/login",
                json={"email": email, "password": password},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                credentials = {
                    "api_key": data["api_key"],
                    "user_id": data["user_id"],
                    "email": email,
                    "plan": data.get("plan", "free")
                }
                self.save_credentials(credentials)
                print(f"✅ Connexion réussie en tant que {email}")
                return True
            else:
                print(f"❌ Échec de connexion: {response.json().get('error', 'Erreur inconnue')}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    def register(self, email: str, password: str) -> bool:
        """Créer un nouveau compte."""
        try:
            response = requests.post(
                f"{self.server_url}/api/auth/register",
                json={"email": email, "password": password},
                timeout=30
            )
            
            if response.status_code == 201:
                print(f"✅ Compte créé avec succès pour {email}")
                print("📧 Vérifiez votre email pour activer votre compte")
                return self.login(email, password)
            else:
                print(f"❌ Échec de création de compte: {response.json().get('error', 'Erreur inconnue')}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Erreur de création de compte: {e}")
            return False
    
    def validate_api_key(self, api_key: str) -> bool:
        """Valider une clé API."""
        try:
            response = requests.get(
                f"{self.server_url}/api/auth/validate",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def logout(self) -> None:
        """Se déconnecter (supprimer les identifiants locaux)."""
        if self.credentials_file.exists():
            try:
                self.credentials_file.unlink()
                print("✅ Déconnexion réussie")
            except Exception as e:
                print(f"⚠️  Erreur lors de la déconnexion: {e}")
        else:
            print("ℹ️  Vous n'étiez pas connecté")