from typing import Dict, Any
from .base_agent import BaseAgent

class JobMatcherAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="JobMatcher",
            instructions="""Match the candidate's resume with the job description.
            Provide a match report indicating the alignment between the resume and the job description.
            Include details such as:
            - Skills match percentage
            - Experience relevance
            - Education alignment
            - Overall match score""",
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Match the resume with the job description"""
        print("🔍 JobMatcher: Matching resume with job description")

        workflow_context = eval(messages[-1]["content"])
        job_match_prompt = f"""
        Match the following resume data with the job description and return a JSON object with the following structure:
        {{
            "skills_match_percentage": number,
            "experience_relevance": "string",
            "education_alignment": "string",
            "overall_match_score": number
        }}

        Resume data:
        {workflow_context["resume_data"]}

        Job description:
        {workflow_context["resume_data"]["job_description"]}

        Return ONLY the JSON object, no other text.
        """

        job_match_results = self._query_ollama(job_match_prompt)
        parsed_results = self._parse_json_safely(job_match_results)

        # Ensure we have valid data even if parsing fails
        if "error" in parsed_results:
            parsed_results = {
                "skills_match_percentage": 0,
                "experience_relevance": "Unknown",
                "education_alignment": "Unknown",
                "overall_match_score": 0,
            }

        return {
            "match_report": parsed_results,
            "match_status": "completed"
        }