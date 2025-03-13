from typing import Dict, Any
from .base_agent import BaseAgent

class ComparisonAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Comparison",
            instructions="""Compare the candidate's resume with the job description.
            Highlight the matches and differences between the resume and the job description.
            Include details such as:
            - Skills match
            - Experience match
            - Education match
            - Key differences""",
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Compare the resume with the job description"""
        print("🔍 Comparison: Comparing resume with job description")

        workflow_context = eval(messages[-1]["content"])
        comparison_prompt = f"""
        Compare the following resume data with the job description and return a JSON object with the following structure:
        {{
            "skills_match": ["skill1", "skill2"],
            "experience_match": ["experience1", "experience2"],
            "education_match": ["education1", "education2"],
            "key_differences": ["difference1", "difference2"]
        }}

        Resume data:
        {workflow_context["resume_data"]}

        Job description:
        {workflow_context["resume_data"]["job_description"]}

        Return ONLY the JSON object, no other text.
        """

        comparison_results = self._query_ollama(comparison_prompt)
        parsed_results = self._parse_json_safely(comparison_results)

        # Ensure we have valid data even if parsing fails
        if "error" in parsed_results:
            parsed_results = {
                "skills_match": [],
                "experience_match": [],
                "education_match": [],
                "key_differences": [],
            }

        return {
            "comparison_report": parsed_results,
            "comparison_status": "completed"
        }