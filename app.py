# Streamlit Web Application
import streamlit as st
import asyncio
import os
from datetime import datetime
from pathlib import Path
from streamlit_option_menu import option_menu
from agents.orchestrator import OrchestratorAgent
from utils.logger import setup_logger
from utils.exceptions import ResumeProcessingError

# Configure Streamlit page
st.set_page_config(
    page_title="Resume Screening",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize logger
logger = setup_logger()


async def process_resume(file_path: str, job_description: str) -> dict:
    """Process resume through the AI recruitment pipeline"""
    try:
        orchestrator = OrchestratorAgent()
        resume_data = {
            "file_path": file_path,
            "submission_timestamp": datetime.now().isoformat(),
            "job_description": job_description,
        }
        result = await orchestrator.process_application(resume_data)
        logger.debug(f"Process result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        raise


def save_uploaded_file(uploaded_file) -> str:
    """Save uploaded file and return the file path"""
    try:
        # Create uploads directory if it doesn't exist
        save_dir = Path("uploads")
        save_dir.mkdir(exist_ok=True)

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = save_dir / f"resume_{timestamp}_{uploaded_file.name}"

        # Save the file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return str(file_path)
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        raise


def main():
    # Sidebar navigation
    with st.sidebar:
        st.image(
            "https://img.icons8.com/resume",
            width=50,
        )
        st.title("Resume Screening")
        selected = option_menu(
            menu_title="Navigation",
            options=["Upload Resume"],
            icons=["cloud-upload", "info-circle"],
            menu_icon="cast",
            default_index=0,
        )

    if selected == "Upload Resume":
        st.header("📄 Resume Analysis")
        st.write("Upload a resume to get AI-powered insights and job matches.")

        uploaded_file = st.file_uploader(
            "Choose a PDF resume file",
            type=["pdf"],
            help="Upload a PDF resume to analyze",
        )

        job_description = st.text_area(
            "Insert Job Description",
            help="Paste the job description to compare with the resume",
        )

        if uploaded_file and job_description:
            try:
                with st.spinner("Saving uploaded file..."):
                    file_path = save_uploaded_file(uploaded_file)

                st.info("Resume uploaded successfully! Processing...")

                # Create placeholder for progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Process resume
                try:
                    status_text.text("Analyzing resume...")
                    progress_bar.progress(25)

                    # Run analysis asynchronously
                    result = asyncio.run(process_resume(file_path, job_description))

                    logger.debug(f"Process result: {result}")  # Add logging here

                    if result["status"] == "completed":
                        progress_bar.progress(100)
                        status_text.text("Analysis complete!")

                        # Display results in tabs
                        tab1, tab2, tab4, tab5 = st.tabs(
                            [
                                "📊 Analysis",
                                "🎯 Screening",
                                # "💡 Recommendation",
                                "📝 Job Match",
                                "🔍 Comparison",
                            ]
                        )

                        with tab1:
                            st.subheader("Skills Analysis")
                            skills_analysis = result["analysis_results"]["skills_analysis"]
                            st.write(f"**Technical Skills:** {', '.join(skills_analysis['technical_skills'])}")
                            st.write(f"**Years of Experience:** {skills_analysis['years_of_experience']}")
                            st.write(f"**Education Level:** {skills_analysis['education']['level']}")
                            st.write(f"**Field of Study:** {skills_analysis['education']['field']}")
                            st.write(f"**Experience Level:** {skills_analysis['experience_level']}")
                            st.write(f"**Key Achievements:** {', '.join(skills_analysis['key_achievements'])}")
                            st.write(f"**Domain Expertise:** {', '.join(skills_analysis['domain_expertise'])}")
                            st.metric(
                                "Confidence Score",
                                f"{result['analysis_results']['confidence_score']:.0%}",
                            )

                        with tab2:
                            st.subheader("Screening Results")
                            if "screening_results" in result:
                                st.metric(
                                    "Screening Score",
                                    f"{result['screening_results']['screening_score']}%",
                                )
                                st.write(result["screening_results"]["screening_report"])
                            else:
                                st.warning("No screening report available.")
                                logger.warning("No screening report available in the result.")

 

                        with tab4:
                            st.subheader("Job Match Analysis")
                            if "job_match" in result:
                                job_match = result["job_match"]["match_report"]
                                st.write(f"**Skills Match Percentage:** {job_match['skills_match_percentage']}%")
                                st.write(f"**Experience Relevance:** {job_match['experience_relevance']}")
                                st.write(f"**Education Alignment:** {job_match['education_alignment']}")
                                st.write(f"**Overall Match Score:** {job_match['overall_match_score']}")
                            else:
                                st.warning("Job match analysis not available.")
                                logger.warning("Job match analysis not available in the result.")

                        with tab5:
                            st.subheader("Resume and Job Description Comparison")
                            if "comparison" in result:
                                comparison = result["comparison"]["comparison_report"]
                                st.write(f"**Skills Match:** {', '.join(comparison['skills_match'])}")
                                st.write(f"**Experience Match:** {', '.join(comparison['experience_match'])}")
                                st.write(f"**Education Match:** {', '.join(comparison['education_match'])}")
                                st.write(f"**Key Differences:** {', '.join(comparison['key_differences'])}")
                            else:
                                st.warning("Comparison report not available.")
                                logger.warning("Comparison report not available in the result.")

                        # Save results
                        output_dir = Path("results")
                        output_dir.mkdir(exist_ok=True)
                        output_file = (
                            output_dir
                            / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        )

                        with open(output_file, "w") as f:
                            f.write(str(result))

                        st.success(f"Results saved to: {output_file}")

                    else:
                        st.error(
                            f"Process failed at stage: {result['current_stage']}\n"
                            f"Error: {result.get('error', 'Unknown error')}"
                        )
                        logger.error(f"Process failed at stage: {result['current_stage']}\nError: {result.get('error', 'Unknown error')}")

                except Exception as e:
                    st.error(f"Error processing resume: {str(e)}")
                    logger.error(f"Processing error: {str(e)}", exc_info=True)

                finally:
                    # Cleanup uploaded file
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        logger.error(f"Error removing temporary file: {str(e)}")

            except Exception as e:
                st.error(f"Error handling file upload: {str(e)}")
                logger.error(f"Upload error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()