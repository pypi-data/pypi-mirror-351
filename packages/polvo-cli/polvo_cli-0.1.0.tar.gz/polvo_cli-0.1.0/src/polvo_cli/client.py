import httpx
from pathlib import Path
from typing import List, Dict, Any, Optional
from .models import EvaluationRequest


class PolvoClient:
    """HTTP client for Polvo API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=300.0)  # 5 min timeout for large datasets

    def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        response = self.client.get(f"{self.base_url}/api/health")
        response.raise_for_status()
        return response.json()

    def get_models(self) -> Dict[str, Any]:
        """Get available models."""
        response = self.client.get(f"{self.base_url}/api/models")
        response.raise_for_status()
        return response.json()

    def upload_file(self, file_path: Path) -> Dict[str, Any]:
        """Upload a dataset file."""
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f)}
            response = self.client.post(
                f"{self.base_url}/api/upload",
                files=files
            )
        response.raise_for_status()
        return response.json()

    def evaluate(self, texts: List[str], models: List[str],
                queries: Optional[List[str]] = None) -> Dict[str, Any]:
        """Evaluate models on texts."""
        request = EvaluationRequest(
            texts=texts,
            models=models,
            queries=queries
        )
        response = self.client.post(
            f"{self.base_url}/api/evaluate",
            json=request.model_dump()
        )
        response.raise_for_status()
        return response.json()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.client.close() 