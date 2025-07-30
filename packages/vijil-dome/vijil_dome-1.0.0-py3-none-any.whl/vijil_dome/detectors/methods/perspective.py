import os
from typing import Optional, Dict
from googleapiclient import discovery
from vijil_dome.detectors import (
    DetectionMethod,
    register_method,
    DetectionCategory,
    DetectionResult,
    MODERATION_PERSPECTIVE,
)


@register_method(DetectionCategory.Moderation, MODERATION_PERSPECTIVE)
class PerspectiveAPI(DetectionMethod):
    def __init__(
        self,
        api_key: Optional[str] = None,
        attributes: Dict = {"TOXICITY": {}},
        score_threshold: Dict = {"TOXICITY": 0.5},
    ):
        self.api_key = (
            api_key if api_key is not None else os.getenv("PERSPECTIVE_API_KEY")
        )
        self.client = discovery.build(
            "commentanalyzer",
            "v1alpha1",
            developerKey=self.api_key,
            discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
            static_discovery=False,
        )
        self.attributes = attributes
        self.score_threshold = score_threshold
        self.blocked_response_string = f"Method:{MODERATION_PERSPECTIVE}"

    async def detect(self, query_string: str) -> DetectionResult:
        # Handle empty query string gracefully
        if not len(query_string):
            return False, {"type": type(self), "response": None}
        perspective_response = (
            self.client.comments()
            .analyze(
                body={
                    "comment": {"text": query_string},
                    "requestedAttributes": {attr: {} for attr in self.attributes},
                }
            )
            .execute()
        )
        flagged = False
        for attr in self.attributes:
            attr_score = perspective_response["attributeScores"][attr]["summaryScore"][
                "value"
            ]
            if attr in self.score_threshold:
                if attr_score > self.score_threshold[attr]:
                    flagged = True
        return flagged, {
            "type": type(self),
            "response": perspective_response,
            "response_string": self.blocked_response_string
            if flagged
            else query_string,
        }
