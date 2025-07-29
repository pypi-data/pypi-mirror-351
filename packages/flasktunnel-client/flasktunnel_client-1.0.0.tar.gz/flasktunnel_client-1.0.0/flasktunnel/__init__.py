# =============================================================================
# flasktunnel/__init__.py
# =============================================================================

"""
FlaskTunnel Client - Créez des tunnels HTTP sécurisés vers vos applications locales
====================================================================================

Alternative gratuite et open-source à ngrok pour partager vos applications
de développement local via des URLs publiques sécurisées.

Usage basique:
    >>> from flasktunnel import FlaskTunnelClient
    >>> client = FlaskTunnelClient()
    >>> tunnel = client.create_tunnel(port=3000)
    >>> print(tunnel.public_url)

Usage CLI:
    $ flasktunnel --port 3000
"""

__version__ = "1.0.0"
__author__ = "FlaskTunnel Team"
__email__ = "support@flasktunnel.dev"
__license__ = "MIT"
__url__ = "https://flasktunnel.up.railway.app/"


from .client import FlaskTunnelClient
from .config import FlaskTunnelConfig
from .auth import FlaskTunnelAuth
from .tunnel import Tunnel, TunnelInfo, TunnelStatus

__all__ = [
    'FlaskTunnelClient',
    'FlaskTunnelConfig', 
    'FlaskTunnelAuth',
    'Tunnel',
    'TunnelInfo',
    'TunnelStatus'
]