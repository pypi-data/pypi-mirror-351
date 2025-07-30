import os
import logging

from typing import Optional, List
from flashtext import KeywordProcessor
from vijil_dome.detectors import (
    MODERATION_FLASHTXT_BANLIST,
    register_method,
    DetectionMethod,
    DetectionResult,
    DetectionCategory,
)

logger = logging.getLogger("vijil.dome")


@register_method(DetectionCategory.Moderation, MODERATION_FLASHTXT_BANLIST)
class KWBanList(DetectionMethod):
    def __init__(self, banlist_filepaths: Optional[List[str]] = None):
        super().__init__()
        try:
            self.processor = KeywordProcessor()
            if banlist_filepaths is None:
                banlist_filepaths = [
                    os.path.join(
                        os.path.dirname(__file__),
                        "configs/banlists",
                        "default_banlist.txt",
                    )
                ]
            for banlist in banlist_filepaths:
                self.processor.add_keyword_from_file(banlist)
            self.blocked_response_string = f"Method:{MODERATION_FLASHTXT_BANLIST}"
        except Exception as e:
            logger.error(f"Error loading banlists: {str(e)}")
            raise

    async def detect(self, query_string: str) -> DetectionResult:
        hits = self.processor.extract_keywords(query_string)
        flagged = bool(hits)
        return flagged, {
            "type": type(self),
            "hits": hits,
            "response_string": self.blocked_response_string
            if flagged
            else query_string,
        }
