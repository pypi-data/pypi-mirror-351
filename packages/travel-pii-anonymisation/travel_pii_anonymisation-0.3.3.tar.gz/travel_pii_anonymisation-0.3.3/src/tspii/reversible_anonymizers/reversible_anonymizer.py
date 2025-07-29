from typing import Dict, Optional
import re
import json
from tspii.anonymizers.instance_counter_anonymizer import InstanceCounterAnonymizer
from tspii.deanonymizers.instance_counter_deanonymizer import (
    InstanceCounterDeanonymizer,
)
from typing import List, Dict, Optional
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer.predefined_recognizers import AzureAILanguageRecognizer
from presidio_analyzer.recognizer_result import RecognizerResult
from presidio_analyzer import EntityRecognizer
from presidio_anonymizer import (
    AnonymizerEngine,
    DeanonymizeEngine,
    OperatorConfig,
    EngineResult,
)
from tspii.helpers.helpers import create_configuration_en


class ReversibleAnonymizer:
    def __init__(self, configuration: Optional[Dict] = None):
        # Initialize text to process
        self._text = None

        # Initialize results to none
        self._analyzer_results = None
        self._anonymizer_results = None
        self._deanonymizer_results = None

        # Creating analyzer
        configuration = configuration if configuration else create_configuration_en()
        provider = NlpEngineProvider(nlp_configuration=configuration)
        self._analyzer_engine = AnalyzerEngine(nlp_engine=provider.create_engine())

        # Creating anonymizer
        self._anonymizer = AnonymizerEngine()
        self._anonymizer.add_anonymizer(InstanceCounterAnonymizer)

        # Creating deanonymizer
        self._deanonymizer = DeanonymizeEngine()
        self._deanonymizer.add_deanonymizer(InstanceCounterDeanonymizer)

        # Create entity mapping
        self._entity_mapping = dict()

        # Create operators
        self._anonymizer_operators = {
            "DEFAULT": OperatorConfig(
                "entity_counter", {"entity_mapping": self._entity_mapping}
            )
        }
        self._deanonymizer_operators = {
            "DEFAULT": OperatorConfig(
                "entity_counter_deanonymizer", {"entity_mapping": self._entity_mapping}
            )
        }
        self._entity_mapping_operators = dict()

    def analyze(self, text: str, language_code: str = "en") -> List[RecognizerResult]:
        self._text = text
        self._analyzer_results = self._analyzer_engine.analyze(
            text=text, language=language_code
        )
        return self._analyzer_results

    def anonymize(self) -> EngineResult:
        if not self._analyzer_results:
            raise ValueError("Anonymization can only be done after analysis!")

        self._anonymizer_results = self._anonymizer.anonymize(
            text=self._text,
            analyzer_results=self._analyzer_results,
            operators=self._anonymizer_operators,
        )

        if len(self._entity_mapping_operators) > 0:
            self._update_anonymization_results_with_generators()

        return self._anonymizer_results

    def deanonymize(self, text=None) -> str:
        if not self._anonymizer_results:
            if not text:
                raise ValueError("Impossible to deanonymize.")
            if text:
                for category, replacements in self._entity_mapping.items():
                    for original_value, replacement_value in replacements.items():
                        text = re.sub(
                            re.escape(replacement_value), original_value, text
                        )
            return text

        self._deanonymizer_results = self._deanonymizer.deanonymize(
            text=self._anonymizer_results.text,
            entities=self._anonymizer_results.items,
            operators=self._deanonymizer_operators,
        )
        return self._deanonymizer_results.text

    def add_recognizer(self, entity_recognizer: EntityRecognizer) -> None:
        self._analyzer_engine.registry.add_recognizer(recognizer=entity_recognizer)

    def add_azure_ai_language_recognizer(
        self,
        azure_ai_language_key: str,
        azure_ai_language_endpoint: str,
        supported_language: str = "en",
    ) -> None:
        self._analyzer_engine.registry.add_recognizer(
            AzureAILanguageRecognizer(
                supported_language=supported_language,
                azure_ai_key=azure_ai_language_key,
                azure_ai_endpoint=azure_ai_language_endpoint,
            )
        )

    def add_operators(self, operators: Dict[str, OperatorConfig]):
        self._entity_mapping_operators = self._entity_mapping_operators | operators

    def save_mapping(self, file_path: str) -> None:
        if self._entity_mapping == dict():
            print("No mapping to save.")
            return
        with open(file_path, "w") as file:
            json.dump(self._entity_mapping, file)
        print(f"Mapping saved to {file_path}")

    def load_mapping(self, file_path: str) -> None:
        with open(file_path, "r") as file:
            self._entity_mapping = json.load(file)
        print(f"Mapping loaded from {file_path}")

    def _update_anonymization_results_with_generators(self) -> None:
        old_new_values_mapping = dict()
        for operator, operator_value in self._entity_mapping_operators.items():
            lambda_function = operator_value.params.get("lambda", None)
            if not lambda_function:
                continue

            values_of_operator_type = self._entity_mapping.get(operator, None)
            if values_of_operator_type is None:
                continue

            for original_value, old_replacement in values_of_operator_type.items():
                new_replacement = lambda_function()
                values_of_operator_type[original_value] = new_replacement
                old_new_values_mapping[new_replacement] = old_replacement

                for entity in self._anonymizer_results.items:
                    if entity.text == old_replacement:
                        entity.text = new_replacement

        new_text = self._anonymizer_results.text
        for entity in reversed(self._anonymizer_results.items):
            old_value = old_new_values_mapping.get(entity.text, None)

            if old_value:
                for match in re.finditer(re.escape(old_value), new_text):
                    start_pos = match.start()
                    end_pos = match.end()
                    new_text = new_text[:start_pos] + entity.text + new_text[end_pos:]
                    entity.start = start_pos
                    entity.end = start_pos + len(entity.text)
                    break
            else:
                for match in re.finditer(re.escape(entity.text), new_text):
                    start_pos = match.start()
                    end_pos = match.end()
                    new_text = new_text[:start_pos] + entity.text + new_text[end_pos:]
                    entity.start = start_pos
                    entity.end = start_pos + len(entity.text)
                    break

        self._anonymizer_results.text = new_text
