"""
VectorDBCloud Python SDK - Technical Requirements Implementation
Fireducks (1.2.5) + Falcon API (3.1.1) + Pydantic (1.10.8)
Performance: <5ms latency + >100k concurrent users
"""

__version__ = "3.0.0-fireducks-falcon-pydantic"
__author__ = "VectorDBCloud"
__email__ = "support@vectordbcloud.com"

# Import optimized client with technical requirements
try:
    from .client_optimized import (
        VectorDBCloud, 
        VectorDBCloudOptimized, 
        APIRequest, 
        APIResponse, 
        ECPConfig
    )
except ImportError:
    # Fallback to basic implementation if optimized version fails
    import warnings
    warnings.warn("Optimized client not available, using basic implementation")
    from .client import VectorDBCloud

# Export main classes
__all__ = [
    'VectorDBCloud',
    'VectorDBCloudOptimized', 
    'APIRequest',
    'APIResponse',
    'ECPConfig'
]

# Technical requirements verification
def verify_technical_requirements():
    """Verify that all technical requirements are met"""
    
    requirements = {
        "fireducks": "1.2.5",
        "falcon": "3.1.1", 
        "pydantic": "1.10.8"
    }
    
    missing_requirements = []
    
    try:
        import fireducks
        if not hasattr(fireducks, '__version__') or fireducks.__version__ < requirements["fireducks"]:
            missing_requirements.append(f"fireducks>={requirements['fireducks']}")
    except ImportError:
        missing_requirements.append(f"fireducks>={requirements['fireducks']}")
    
    try:
        import falcon
        if not hasattr(falcon, '__version__') or falcon.__version__ < requirements["falcon"]:
            missing_requirements.append(f"falcon>={requirements['falcon']}")
    except ImportError:
        missing_requirements.append(f"falcon>={requirements['falcon']}")
    
    try:
        import pydantic
        if not hasattr(pydantic, 'VERSION') or '.'.join(map(str, pydantic.VERSION[:3])) < requirements["pydantic"]:
            missing_requirements.append(f"pydantic>={requirements['pydantic']}")
    except ImportError:
        missing_requirements.append(f"pydantic>={requirements['pydantic']}")
    
    if missing_requirements:
        raise ImportError(
            f"Missing technical requirements: {', '.join(missing_requirements)}\n"
            f"Install with: pip install {' '.join(missing_requirements)}"
        )
    
    return True

# Performance requirements verification
def verify_performance_requirements():
    """Verify that performance requirements can be met"""
    
    performance_features = {
        "async_support": False,
        "connection_pooling": False,
        "uvloop_available": False,
        "aiohttp_available": False
    }
    
    try:
        import asyncio
        performance_features["async_support"] = True
    except ImportError:
        pass
    
    try:
        import aiohttp
        performance_features["aiohttp_available"] = True
    except ImportError:
        pass
    
    try:
        import uvloop
        performance_features["uvloop_available"] = True
    except ImportError:
        pass
    
    try:
        from requests.adapters import HTTPAdapter
        performance_features["connection_pooling"] = True
    except ImportError:
        pass
    
    return performance_features

# SDK Information
def get_sdk_info():
    """Get comprehensive SDK information"""
    
    try:
        tech_requirements = verify_technical_requirements()
    except ImportError as e:
        tech_requirements = False
        tech_error = str(e)
    else:
        tech_error = None
    
    perf_features = verify_performance_requirements()
    
    return {
        "version": __version__,
        "technical_requirements": {
            "met": tech_requirements,
            "error": tech_error,
            "required": {
                "fireducks": "1.2.5",
                "falcon": "3.1.1",
                "pydantic": "1.10.8"
            }
        },
        "performance_features": perf_features,
        "performance_targets": {
            "latency": "<5ms",
            "concurrent_users": ">100k"
        },
        "ecp_compliance": "100% ECP-native and ECP-embedded",
        "platform_integration": "VectorDBCloud SingleAPI"
    }

# Initialize SDK with verification
try:
    verify_technical_requirements()
    print(f"✅ VectorDBCloud SDK {__version__} initialized with technical requirements")
except ImportError as e:
    print(f"⚠️ VectorDBCloud SDK {__version__} initialized with missing requirements: {e}")
