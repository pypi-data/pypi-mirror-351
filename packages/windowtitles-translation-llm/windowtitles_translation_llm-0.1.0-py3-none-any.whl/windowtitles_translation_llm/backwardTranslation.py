import re
from collections import defaultdict
import constants

class BackwardTranslation:
    def __init__(self, alteredData=None):
        self.alteredData = alteredData or {}

    def back_translate_all(self, alteredData) -> dict:
        restored = {}
        for eng_title, info in alteredData.items():
            fwd_map = info.get("tokenMapping", {})
            if not fwd_map:
                raise ValueError(error=constants.ERROR_MESSAGES['tokenMappingEmpty'])

            #invert mapping
            rev_map = defaultdict(list)
            for orig_fr, trans_en in fwd_map.items():
                rev_map[trans_en].append(orig_fr)

            #sort chunks
            chunks = sorted(rev_map.keys(), key=len, reverse=True)

            text = eng_title
            for chunk in chunks:
                fr_pieces = rev_map[chunk]
                replacement = " ".join(fr_pieces)
                #replace chunks
                text = re.sub(re.escape(chunk), replacement, text)

            #remove extra spaces
            text = re.sub(r"\s+", " ", text).strip()
            restored[eng_title] = text

        return restored

    @staticmethod
    def backwardTranslate(altered_data: dict) -> dict:
        mapper = BackwardTranslation(altered_data)
        return {'originalData':mapper.back_translate_all(altered_data)}
