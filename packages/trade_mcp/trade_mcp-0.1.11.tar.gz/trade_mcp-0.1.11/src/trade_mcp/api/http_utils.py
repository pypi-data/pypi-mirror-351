import aiohttp
import hmac
import hashlib
import time
from typing import Dict, Any, Optional
from urllib.parse import urlencode, quote
import json

class APIClient:
    # BINANCE_TESTNET_BASE_URL = "https://mcp-gateway-759711950494.asia-southeast1.run.app/binance_testnet"
    BINANCE_TESTNET_BASE_URL = "http://localhost:8080/binance_testnet"
    ASTER_BASE_URL = "https://fapi.asterdex.com"
    
    def __init__(self, axgrad_key: str, api_key: str, api_secret: str, venue: str):
        self.axgrad_key = axgrad_key
        self.api_key = api_key
        self.api_secret = api_secret
        self.venue = venue
        self.base_url = None
        if venue == "live":
            self.base_url = self.ASTER_BASE_URL
        else:
            self.base_url = self.BINANCE_TESTNET_BASE_URL

    def _get_signature(self, params: Dict[str, Any]) -> str:
        """Generate HMAC SHA256 signature using the working bash script style."""
        # Remove non-API parameters
        params_for_sig = params.copy()
        for key in ['security_type', 'axgrad_key', 'api_key', 'api_secret']:
            params_for_sig.pop(key, None)
        
        # Handle orderIdList using the working bash script approach
        if 'orderIdList' in params_for_sig and isinstance(params_for_sig['orderIdList'], list):
            order_ids = params_for_sig['orderIdList']
            # Create JSON string without spaces like bash script - handle any length
            json_str = f"[{','.join(map(str, order_ids))}]"
            # URL encode the JSON string
            encoded_json = quote(json_str)
            
            # Build query string manually in the same order as bash script
            query_string = f"orderIdList={encoded_json}&symbol={params_for_sig['symbol']}&timestamp={params_for_sig['timestamp']}"
        else:
            # For other parameters, convert arrays to JSON and use standard approach
            for key, value in list(params_for_sig.items()):
                if isinstance(value, list):
                    params_for_sig[key] = json.dumps(value, separators=(',', ':'))
            
            query_string = urlencode(sorted(params_for_sig.items()))
        
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    async def _request_testnet(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None, 
        security_type: str = "NONE"
    ) -> Dict[str, Any]:
        """Make an HTTP request to the exchange API, sending all parameters directly including security_type and axgrad_key."""
        if params is None:
            params = {}
        # Always include security_type in the parameters
        params['security_type'] = security_type
        # Always include axgrad_key in the parameters
        params['axgrad_key'] = self.axgrad_key
        if self.venue == "test":
            params['api_key'] = self.api_key
            params['api_secret'] = self.api_secret
        headers = {}
        url = f"{self.base_url}{endpoint}"
        request_params = None
        json_body = None

        if method == 'GET':
            request_params = params
            json_body = None
        else:
            request_params = None
            json_body = params

        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(method, url, headers=headers, params=request_params, json=json_body) as response:
                    if response.content_type == 'application/json':
                        return await response.json()
                    else:
                        # Handle non-JSON responses (like HTML error pages)
                        text = await response.text()
                        print(f"Non-JSON response ({response.status}): {text}")
                        return {"error": f"HTTP {response.status}", "message": text}
            except Exception as e:
                print(f"Request failed: {e}")
                return {"error": "Request failed", "message": str(e)}

    async def _request_live(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None, 
        security_type: str = "NONE"
    ) -> Dict[str, Any]:
        """Make an HTTP request to the exchange API with security type handling."""
        if params is None:
            params = {}

        headers = {}
        url = f"{self.base_url}{endpoint}"
        request_params = None
        json_body = None

        if security_type in ("TRADE", "USER_DATA"):  # SIGNED endpoints
            params['timestamp'] = int(time.time() * 1000)
            
            # Use the dedicated _get_signature method
            signature = self._get_signature(params)
            params['signature'] = signature
            
            # Clean and process parameters for the actual request
            processed_params = params.copy()
            # Remove non-API parameters that shouldn't be sent to the exchange
            for key in ['security_type', 'axgrad_key', 'api_key', 'api_secret']:
                processed_params.pop(key, None)
            
            headers['X-MBX-APIKEY'] = self.api_key
            
            # Handle different request methods and parameter types
            if 'orderIdList' in processed_params and isinstance(processed_params['orderIdList'], list):
                # Special handling for orderIdList requests (batchOrders)
                order_ids = processed_params['orderIdList']
                symbol = processed_params['symbol']
                timestamp = processed_params['timestamp']
                signature = processed_params['signature']
                
                # Use the same URL-encoded format for both signature and request
                json_str = f"[{','.join(map(str, order_ids))}]"
                encoded_json = quote(json_str)
                
                if method == 'GET':
                    # For GET requests, use query parameters
                    request_params = {
                        'orderIdList': f"[{','.join(map(str, order_ids))}]",
                        'symbol': symbol,
                        'timestamp': timestamp,
                        'signature': signature
                    }
                    json_body = None
                else:
                    # For POST/DELETE requests, use request body
                    headers['Content-Type'] = 'application/x-www-form-urlencoded'
                    request_body = f"orderIdList={encoded_json}&symbol={symbol}&timestamp={timestamp}&signature={signature}"
                    request_params = request_body
                    json_body = None
            else:
                # Standard handling for other requests
                for key, value in list(processed_params.items()):
                    if isinstance(value, list):
                        processed_params[key] = json.dumps(value, separators=(',', ':'))
                
                if method == 'GET':
                    request_params = processed_params
                    json_body = None
                else:
                    headers['Content-Type'] = 'application/x-www-form-urlencoded'
                    request_params = urlencode(sorted(processed_params.items()))
                    json_body = None
                    
        elif security_type in ("USER_STREAM", "MARKET_DATA"):
            headers['X-MBX-APIKEY'] = self.api_key
            request_params = params if method == 'GET' else None
            json_body = params if method != 'GET' else None
        else:
            request_params = params if method == 'GET' else None
            json_body = params if method != 'GET' else None

        async with aiohttp.ClientSession() as session:
            try:
                if method == 'GET':
                    async with session.get(url, headers=headers, params=request_params) as response:
                        if response.content_type == 'application/json':
                            return await response.json()
                        else:
                            text = await response.text()
                            print(f"Non-JSON response ({response.status}): {text}")
                            return {"error": f"HTTP {response.status}", "message": text}
                else:
                    async with session.request(method, url, headers=headers, data=request_params) as response:
                        if response.content_type == 'application/json':
                            return await response.json()
                        else:
                            text = await response.text()
                            print(f"Non-JSON response ({response.status}): {text}")
                            return {"error": f"HTTP {response.status}", "message": text}
            except Exception as e:
                print(f"Request failed: {e}")
                return {"error": "Request failed", "message": str(e)}

    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None, 
        security_type: str = "NONE"
    ) -> Dict[str, Any]:
        if self.venue == "live":
            return await self._request_live(method, endpoint, params, security_type)
        else:
            return await self._request_testnet(method, endpoint, params, security_type)

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, security_type: str = "NONE") -> Dict[str, Any]:
        """Make a GET request to the exchange API with security type."""
        return await self._request('GET', endpoint, params, security_type)
    
    async def post(self, endpoint: str, params: Optional[Dict[str, Any]] = None, security_type: str = "TRADE") -> Dict[str, Any]:
        """Make a POST request to the exchange API with security type."""
        return await self._request('POST', endpoint, params, security_type)
    
    async def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None, security_type: str = "TRADE") -> Dict[str, Any]:
        """Make a DELETE request to the exchange API with security type."""
        return await self._request('DELETE', endpoint, params, security_type)