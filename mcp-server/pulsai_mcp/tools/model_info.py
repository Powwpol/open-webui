"""
Model Info Tool

Provides introspection and information about available models.
"""

from typing import Dict, Any, List
import aiohttp


async def model_info_tool(
    model_name: str = None,
    backend_url: str = "http://localhost:8080"
) -> Dict[str, Any]:
    """
    Get information about available models
    
    Args:
        model_name: Specific model to get info about (optional)
        backend_url: Pulsai backend URL
        
    Returns:
        Dictionary with model information
    """
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{backend_url}/api/v1/models"
            async with session.get(url) as response:
                if response.status == 200:
                    models = await response.json()
                    
                    if model_name:
                        # Filter for specific model
                        model_data = [m for m in models if m.get("id") == model_name]
                        return {
                            "success": True,
                            "model": model_data[0] if model_data else None,
                            "found": len(model_data) > 0
                        }
                    else:
                        # Return all models
                        return {
                            "success": True,
                            "models": models,
                            "count": len(models)
                        }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to fetch models: {response.status}"
                    }
                    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

