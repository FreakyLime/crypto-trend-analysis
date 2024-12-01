import openai
import logging

logger = logging.getLogger(__name__)

class OpenAIUtils:
    def __init__(self, api_key, model="gpt-4", max_tokens=1000, temperature=0.7):
        """
        Initialize the OpenAI utility class.
        """
        openai.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def analyze_data(self, input_text):
        """
        Send data to OpenAI for analysis and process the response.
        """
        try:
            logger.info("Sending data to OpenAI for analysis.")
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a cryptocurrency trading expert."},
                    {"role": "user", "content": input_text}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            # Extract the response content
            analysis = response['choices'][0]['message']['content']
            logger.info(f"OpenAI response received.")

            # Extract actionable suggestions from the analysis
            suggestion = self._extract_suggestion(analysis)
            return suggestion, analysis

        except openai.error.OpenAIError as oe:
            logger.error(f"OpenAI API Error: {oe}")
            return "Error analyzing data.", "No reasoning available."
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return "Error analyzing data.", "No reasoning available."

    def _extract_suggestion(self, analysis):
        """
        Extract actionable suggestions based on analysis content.
        """
        analysis_lower = analysis.lower()
        if 'buy' in analysis_lower:
            return 'Buy'
        elif 'sell' in analysis_lower:
            return 'Sell'
        elif 'long' in analysis_lower:
            return 'Long Position'
        elif 'short' in analysis_lower:
            return 'Short Position'
        else:
            return 'Hold'  # Default action if no suggestion is found
