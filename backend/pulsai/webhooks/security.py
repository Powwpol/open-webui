"""
Webhook security and signature verification
"""

import hmac
import hashlib
import secrets
from typing import Optional


class WebhookSecurity:
    """Security utilities for webhooks"""
    
    @staticmethod
    def generate_secret() -> str:
        """
        Generate a secure random webhook secret
        
        Returns:
            Random hex string (64 characters)
        """
        return secrets.token_hex(32)
    
    @staticmethod
    def compute_signature(payload: bytes, secret: str) -> str:
        """
        Compute HMAC-SHA256 signature for webhook payload
        
        Args:
            payload: Request body as bytes
            secret: Webhook secret
            
        Returns:
            Hex-encoded signature
        """
        return hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def verify_signature(
        payload: bytes,
        signature: str,
        secret: str
    ) -> bool:
        """
        Verify webhook signature
        
        Args:
            payload: Request body as bytes
            signature: Provided signature
            secret: Webhook secret
            
        Returns:
            True if signature is valid
        """
        expected_signature = WebhookSecurity.compute_signature(payload, secret)
        return hmac.compare_digest(signature, expected_signature)
    
    @staticmethod
    def get_signature_header(payload: bytes, secret: str) -> dict[str, str]:
        """
        Get signature header for outgoing webhook
        
        Args:
            payload: Request body as bytes
            secret: Webhook secret
            
        Returns:
            Dictionary with signature header
        """
        signature = WebhookSecurity.compute_signature(payload, secret)
        return {
            'X-Pulsai-Signature': f'sha256={signature}'
        }
    
    @staticmethod
    def parse_signature_header(header: str) -> Optional[str]:
        """
        Parse signature from header value
        
        Args:
            header: Header value (e.g., "sha256=abc123...")
            
        Returns:
            Signature or None if invalid format
        """
        if not header or not header.startswith('sha256='):
            return None
        return header[7:]  # Remove "sha256=" prefix

