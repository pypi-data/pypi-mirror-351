import os
import time
import uuid
from typing import Dict, Optional, Any
import aiohttp
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AsyncEvaluatorClient:
    """Asynchronous client for sending model outputs to evaluation service via AWS."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        client_secret: Optional[str] = None,
        source: Optional[str] = None,
        base_url: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        custom_headers: Optional[Dict[str, str]] = None,
        session_id: Optional[str] = None,
    ):
        # API authentication - Updated with adeptiv-ai prefix
        self.api_key = api_key or os.environ.get("ADEPTIV_AI_EVALUATOR_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set as ADEPTIV_AI_EVALUATOR_API_KEY environment variable")

        self.client_secret = client_secret or os.environ.get("ADEPTIV_AI_EVALUATOR_CLIENT_SECRET")
        self.source = source or os.environ.get("ADEPTIV_AI_EVALUATOR_SOURCE", "adeptiv-ai-default")
        self.base_url = base_url or os.environ.get("ADEPTIV_AI_EVALUATOR_BASE_URL", "http://api-dev.adeptiv.ai")
        self.api_endpoint = f"{base_url}/api/llm/process/output/"
        # Retry configuration
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Headers and session
        self.custom_headers = custom_headers or {}
        self.session_id = session_id or str(uuid.uuid4())

        # Connection status
        self.is_connected = False


    async def connect(self) -> bool:
        """
        Verifies API key and client secret by calling authentication endpoint.
        Returns:
            True if verification successful, False otherwise.
        """
        verify_url = f"{self.base_url}/api/project/verify-keys/"
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "X-SECRET-Key": self.client_secret, 
            "X-Adeptiv-AI-Source": self.source,
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(verify_url, headers=headers) as response:
                    if response.status == 200:
                        self.is_connected = True
                        logger.info("Adeptiv-AI SDK successfully connected and verified.")
                        return {'is_connected': True, 'project_id': (await response.json()).get('project_id', None)}
                    else:
                        logger.error(f"Verification failed: {response.status} - {await response.text()}")
                        return False
            except Exception as e:
                logger.error(f"Error during connection: {e}")
                return False

    def _prepare_payload(self, data, metadata, model, evaluation_type, project_id):
        """
        Prepare the payload for sending to the API.
        """
        payload = {
            "raw_output": data,
            "session_id": self.session_id,
            "timestamp": time.time(),
            "source": self.source,
            "api_key": self.api_key,
            "client_secret": self.client_secret,
            "project_id": project_id,
        }

        if metadata:
            payload["metadata"] = metadata
        if model:
            payload["model"] = model
        if evaluation_type:
            payload["evaluation_type"] = evaluation_type

        return payload

    async def send_output(self,
                        data: Any,
                        evaluation_type: str, 
                        project_id: str,
                        model: str,          
                        metadata: Optional[Dict] = None,
                        process_via_aws: Optional[bool] = None) -> Dict[str, Any]:
        """
        Asynchronously send model output for evaluation.
        In production, defaults to AWS processing.
        
        Args:
            data: The model output data to evaluate
            evaluation_type: Type of evaluation to perform (required)
            model: Model name/identifier (required)
            metadata: Optional metadata dictionary
            process_via_aws: Optional flag to force AWS processing
            
        Returns:
            Dict containing evaluation results
            
        Raises:
            RuntimeError: If not connected to the service
            ValueError: If evaluation_type or model is invalid
        """
        if not self.is_connected:
            raise RuntimeError("Not connected. Call `await connect()` first.")

        # Validate required parameters
        if not evaluation_type:
            raise ValueError("evaluation_type is required")
        if not model:
            raise ValueError("model is required")

        payload = self._prepare_payload(data, metadata, model, evaluation_type, project_id)
        return await self._process_via_api(payload)

    
    async def _process_via_api(self, payload: Dict) -> Dict[str, Any]:
        """
        Call an external API endpoint asynchronously using aiohttp with the given payload.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=self.api_endpoint,  
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:

                    status = response.status
                    response_text = await response.text()

                    logger.info(f"✅ API called successfully. Status Code: {status}")

                    if status == 200:
                        response_json = await response.json()
                        return {"status": "success", "api_response": response_json}
                    else:
                        logger.error(f"API returned non-200 status: {status}, Response: {response_text}")
                        return {"status": "error", "fallback": True, "details": response_text}

        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error during API call: {e}")
            return {"status": "error", "fallback": True, "details": str(e)}

        except Exception as e:
            logger.error(f"Unexpected error during API call: {e}")
        
        
    async def close(self):
        """
        Clean up resources.
        """
        self.is_connected = False
        self._batch_queue.clear()
        logger.info("Adeptiv-AI SDK connection closed")

