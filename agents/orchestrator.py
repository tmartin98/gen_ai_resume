from typing import Dict, Any
from .base_agent import BaseAgent
from .extractor_agent import ExtractorAgent
from .analyzer_agent import AnalyzerAgent
from .screener_agent import ScreenerAgent
from .recommender_agent import RecommenderAgent
from .job_matcher_agent import JobMatcherAgent
from .comparison_agent import ComparisonAgent

class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Orchestrator",
            instructions="""Coordinate the recruitment workflow and delegate tasks to specialized agents.
            Ensure proper flow of information between extraction, analysis, matching, screening, and recommendation phases.
            Maintain context and aggregate results from each stage.""",
        )
        self._setup_agents()

    def _setup_agents(self):
        """Initialize all specialized agents"""
        self.extractor = ExtractorAgent()
        self.analyzer = AnalyzerAgent()
        self.screener = ScreenerAgent()
        self.recommender = RecommenderAgent()
        self.job_matcher = JobMatcherAgent()
        self.comparison = ComparisonAgent()

    async def run(self, messages: list) -> Dict[str, Any]:
        """Process a single message through the agent"""
        prompt = messages[-1]["content"]
        response = self._query_ollama(prompt)
        return self._parse_json_safely(response)

    async def process_application(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main workflow orchestrator for processing job applications"""
        print("🎯 Orchestrator: Starting application process")

        workflow_context = {
            "resume_data": resume_data,
            "status": "initiated",
            "current_stage": "extraction",
        }

        try:
            # Extract resume information
            extracted_data = await self.extractor.run(
                [{"role": "user", "content": str(resume_data)}]
            )
            workflow_context.update(
                {"extracted_data": extracted_data, "current_stage": "analysis"}
            )

            # Analyze candidate profile
            analysis_results = await self.analyzer.run(
                [{"role": "user", "content": str(extracted_data)}]
            )
            workflow_context.update(
                {"analysis_results": analysis_results, "current_stage": "screening"}
            )

            # Screen candidate
            screening_results = await self.screener.run(
                [{"role": "user", "content": str(workflow_context)}]
            )
            workflow_context.update(
                {
                    "screening_results": screening_results,
                    "current_stage": "job_matching",
                }
            )

            # Match job description
            job_match_results = await self.job_matcher.run(
                [{"role": "user", "content": str(workflow_context)}]
            )
            workflow_context.update(
                {
                    "job_match": job_match_results,
                    "current_stage": "comparison",
                }
            )

            # Compare resume and job description
            comparison_results = await self.comparison.run(
                [{"role": "user", "content": str(workflow_context)}]
            )
            workflow_context.update(
                {
                    "comparison": comparison_results,
                    "current_stage": "recommendation",
                }
            )

            # Generate recommendations
            final_recommendation = await self.recommender.run(
                [{"role": "user", "content": str(workflow_context)}]
            )
            workflow_context.update(
                {"final_recommendation": final_recommendation, "status": "completed"}
            )

            return workflow_context

        except Exception as e:
            workflow_context.update({"status": "failed", "error": str(e)})
            raise