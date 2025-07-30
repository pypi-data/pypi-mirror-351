import json
from typing import Any, Dict
import constants
from forwardTranslation import ForwardTranslation
from backwardTranslation import BackwardTranslation

def getOriginalData(payload: str) -> Dict[str, Any]:
    alteredWindowTitles = payload.get('alteredWindowTitles', [])
    if not alteredWindowTitles:
        raise ValueError(error=constants.ERROR_MESSAGES['alteredWindowTitlesEmpty'])
    restored = BackwardTranslation.backwardTranslate(alteredWindowTitles)
    return restored
    
def getData():
    inputPath = constants.DATA_INPUT_PATH
    with open(inputPath, 'r', encoding='utf-8') as f:
        payload = json.load(f)
        translationType = payload.get("translationType")
        print(translationType)
        if not translationType:
            raise ValueError(error=constants.ERROR_MESSAGES['translationTypeEmpty'])
        if (translationType.lower() not in ("forward", "backward")):
            raise ValueError(error=constants.ERROR_MESSAGES['translationTypeValueError'])
         
    if (translationType.lower() == "forward"): 
        ForwardTranslation().forwardTranslate() 
    if (translationType.lower() == "backward"):
        result = getOriginalData(payload)
        with open(constants.DATA_OUTPUT_PATH, 'w', encoding='utf-8') as out_f:
            json.dump(result, out_f, indent=2, ensure_ascii=False)
    return result

if __name__ == '__main__':
    result = getData()  
 