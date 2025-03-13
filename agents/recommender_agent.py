from typing import Dict, Any
from .base_agent import BaseAgent

class RecommenderAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Recommender",
            instructions="""Generate a final recommendation based on the analysis, screening, job match, and comparison results.
            Provide a recommendation summary and detailed explanation.""",
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Generate a final recommendation"""
        print("💡 Recommender: Generating final recommendation")

        workflow_context = eval(messages[-1]["content"])
        recommendation_prompt = f"""
        Based on the following workflow context, generate a final recommendation and return a JSON object with the following structure:
        {{
            "final_recommendation": "string",
            "recommendation_details": "string"
        }}

        Workflow context:
        {workflow_context}

        Return ONLY the JSON object, no other text.
        """

        print(f"Recommendation prompt: {recommendation_prompt}")

        recommendation_results = self._query_ollama(recommendation_prompt)
        print(f"Recommendation results: {recommendation_results}")

        parsed_results = self._parse_json_safely(recommendation_results)
        print(f"Parsed recommendation results: {parsed_results}")

        # Ensure we have valid data even if parsing fails
        if "final_recommendation" not in parsed_results or "recommendation_details" not in parsed_results:
            parsed_results = {
                "final_recommendation": "No recommendation available",
                "recommendation_details": "Unable to generate recommendation due to an error.",
            }

        return {
            "final_recommendation": parsed_results["final_recommendation"],
            "recommendation_details": parsed_results["recommendation_details"],
        }