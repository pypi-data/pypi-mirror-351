import json
from ollama import chat
import constants

class ForwardTranslation:
    def __init__(self):
        self.inputPath = constants.DATA_INPUT_PATH
        self.outputPath = constants.DATA_OUTPUT_PATH
        self.BATCH_SIZE = constants.BATCH_SIZE
        self.model = constants.MODEL
        self.temperature = constants.TEMPERATURE

    def translateWindowTitle(self, prompt: str):
        max_retries = constants.PROMPT_RETRIES
        for attempt in range(1, max_retries + 1):
            response = chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": self.temperature},
            )
            content = response.get("message", {}).get("content", "") or ""
            print(f"[Attempt {attempt}] RESPONSE: {content}")

            try:
                data = json.loads(content)
                return data
            except json.JSONDecodeError as e:
                print(f"[Attempt {attempt}] JSONDecodeError: {e}")
                if attempt == max_retries:
                    raise ValueError(f"translateWindowTitle failed after {max_retries} attempts. Last response: {content}")
                correction_prompt = (
                    f"Format the following text into a valid JSON and return the valid JSON"
                )
                retry_resp = chat(
                    model=self.model,
                    messages=[{"role": "user", "content": correction_prompt}],
                    options={"temperature": self.temperature},
                )
                corrected = retry_resp.get("message", {}).get("content", "") or ""
                print(f"[Attempt {attempt}] RETRY RESPONSE: {corrected}")
                content = corrected
                try:
                    data = json.loads(content)
                    return data
                except json.JSONDecodeError:
                    continue
        raise RuntimeError("Unexpected error in translateWindowTitle")

    def promptErrorHandling(self, e: Exception):
        response = chat(
            model=self.model,
            messages=[
                {"role": "user", "content": (
                    "The JSON you provided is invalid because "
                    f"{e}. "
                    "Please output **only** valid JSON conforming to the schema."
                )}
            ],
            options={"temperature": self.temperature},
        )
        data = json.loads(response["message"]["content"])
        return data

    def setPrompt(self, payload: json):
        preserveWords = payload.get("preserveWordsList", [])
        getTokenList = payload.get("getTokenList", False)
        sourceLanguage = payload.get("windowTitlesLanguage", None)

        outputSampleFormat = constants.OUTPUT_SAMPLE_FORMAT

        if getTokenList == False:
            if preserveWords == []:
                prompt = (
                    "Translate the following JSON object to English, preserving its structure. "
                    "Save the translated output in a JSON object with the key 'translatedWindowTitles'. "
                    "Do not give any additional text. \n\n"
                    f"{json.dumps(payload, ensure_ascii=False)}"
                )
                print("Translating windowtitles")
            else:
                prompt = (
                    "Translate the following JSON object to English, preserving its structure. "
                    "Do not translate these words: "
                    f"{preserveWords}"
                    ". Save the translated output in a JSON object with the key 'translatedWindowTitles'. "
                    "Do not give any additional text. \n\n"
                    f"{json.dumps(payload, ensure_ascii=False)}"
                )
                print("Translate window titles and add preserve words. ")

            return prompt
        else:
            mappingSampleFormat = constants.MAPPING_SAMPLE_FORMAT

            if sourceLanguage == None:
                prompt = (
                    "You are an API that only outputs JSON. Do not include any explanations, titles, or markdown—only raw JSON."
                    "Translate the following JSON object to English, preserving its structure and capitalization of text: \n"
                    f"{json.dumps(payload, ensure_ascii=False)}"
                    "Save the detected language of the original title."
                    "Save the word token mappings including characters, punctuations, and spaces. Example: "
                    f"{json.dumps(mappingSampleFormat, ensure_ascii=False)}"
                    "Save the translated output in a **VALID JSON** object in the following format: \n "
                    f"{json.dumps(outputSampleFormat, ensure_ascii=False)}"
                )
                print("Translate, save mapping, and detect source language")
            elif sourceLanguage != None:
                prompt = (
                    "You are an API that only outputs JSON. Do not include any explanations, titles, or markdown—only raw JSON. "
                    "Translate the following JSON object to English, preserving its structure and capitalization of text: \n"
                    f"{json.dumps(payload, ensure_ascii=False)} "
                    "Save the word token mappings including characters, punctuations, and spaces. Example: "
                    f"{json.dumps(mappingSampleFormat, ensure_ascii=False)} "
                    "Save the translated output in a JSON object in the following format: \n "
                    f"{json.dumps(outputSampleFormat, ensure_ascii=False)} "
                )
                print("Translate, save mapping, and set source language")

            return prompt

    def forwardTranslate(self):
        with open(self.inputPath, "r", encoding="utf-8") as f:
            payload = json.load(f)

        all_titles = payload.get("windowTitles", [])
        if not all_titles:
            raise ValueError(constants.ERROR_MESSAGES["windowTitlesEmpty"])

        total = len(all_titles)
        total_batches = (total + self.BATCH_SIZE - 1) // self.BATCH_SIZE

        aggregated = {"translatedWindowTitles": []}

        for batch_num in range(1, total_batches + 1):
            print(f"Sending prompt for batch {batch_num}/{total_batches}...")
            start = (batch_num - 1) * self.BATCH_SIZE
            batch = all_titles[start : start + self.BATCH_SIZE]

            batch_payload = {k: v for k, v in payload.items() if k != "windowTitles"}
            batch_payload["windowTitles"] = batch

            print(batch_payload)

            prompt = self.setPrompt(batch_payload)
            data = self.translateWindowTitle(prompt)

            if "translatedWindowTitles" in data:
                entries = [
                    {orig: info}
                    for orig, info in data["translatedWindowTitles"].items()
                ]
            else:
                entries = [data]

            aggregated["translatedWindowTitles"].extend(entries)

            with open(self.outputPath, "w", encoding="utf-8") as out_f:
                json.dump(aggregated, out_f, indent=2, ensure_ascii=False)

            print(f"Processed batch {batch_num}/{total_batches}: {len(entries)} titles, "
                  f"total translated: {len(aggregated['translatedWindowTitles'])}/{total}")

        print(f"All done: translated {len(aggregated['translatedWindowTitles'])} titles in {total_batches} batches.")

# if __name__ == "__main__":
#     ForwardTranslation().forwardTranslate()