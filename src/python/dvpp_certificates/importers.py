from __future__ import annotations

from typing import Mapping

from dvpp_cert_extraction import ExtractionResult, extract_certificates


class GeminiCertificateImporter:
    def __init__(self, extractor=extract_certificates):
        self.extractor = extractor

    def import_file(
        self,
        file_path: str,
        *,
        model_name: str,
        api_key: str | None = None,
        env: Mapping[str, str] | None = None,
    ) -> ExtractionResult:
        return self.extractor(
            file_path,
            model_name,
            api_key=api_key,
            env=env,
        )
