DATA_INPUT_PATH = (
    r"windowtitles-translation-llm\data\input-data\translationDataInput.json"
)

DATA_OUTPUT_PATH = (
    r"windowtitles-translation-llm\data\output-data\translatedWindowTitles(es).json"
)


ERROR_MESSAGES = {
    "windowTitlesEmpty": "Window titles (windowTitles) input missing.",
    "alteredWindowTitlesEmpty": "Altered window titles (alteredWindowTitles) input missing.",
    "translationTypeEmpty": "Translation type (translationType) input missing.",
    "translationTypeValueError": 'Translation type (translationType) can only be "forward" or "backward"',
    "tokenMappingEmpty": "Token Mapping (tokenMapping) input missing.",
}

OUTPUT_SAMPLE_FORMAT = {
    "translatedWindowTitles": {
        "original_title_here": {
            "language": "detected_language_code_of_original_windowtitle_here",
            "translation": "string",
            "tokenMapping": {
                "token1_here": "mapping1_here",
                " - ": " - ",
                "token2_here": "mapping2_here",
            },
        }
    }
}


MAPPING_SAMPLE_FORMAT = {
    "Comptes financiers - Boîte de réception - Comptes financiers - Outlook": {
        "language": "fr",
        "translation": "Accounts Financial - Box of the receipt - Accounts Financial - Outlook",
        "tokenMapping": {
            "Comptes": "Accounts",
            " ": " ",
            "financiers": "Financial",
            " - ": " - ",
            "Boîte": "Box",
            "de": "of the",
            "réception": "receipt",
            "Outlook": "Outlook",
        },
    }
}


BATCH_SIZE = 3
MODEL = "llama3.2"
TEMPERATURE = 0
PROMPT_RETRIES = 5