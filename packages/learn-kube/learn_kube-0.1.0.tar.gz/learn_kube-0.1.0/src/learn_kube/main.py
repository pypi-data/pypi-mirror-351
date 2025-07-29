from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
import os
from pathlib import Path
from .models import ConceptRequest, ConceptExplanation, ChallengeAttempt, ChallengeFeedback, QuizRequest, QuizQuestion, GenerateChallengeRequest, GeneratedChallenge, DynamicChallengeAttempt, MindMapRequest, MindMap, MindMapNode, MindMapEdge
# Import the LLM service
from .llm_service import generate_structured_response, instructor_client, generate_text 
import uuid # For generating unique IDs
from google import genai
from google.genai import types
import json
from typing import AsyncGenerator
from pydantic import BaseModel



app = FastAPI(title="LearnKube - DevOps Learning Platform")

# Determine project root and path to static and templates directories
# Check if we're running in Docker (where directories are at /app level)
if os.path.exists('/app/static'):
    static_dir = Path('/app/static')
    templates_dir = Path('/app/templates')
else:
    # We're in development mode
    project_root = Path(__file__).parent.parent.parent
    static_dir = project_root / "static"
    templates_dir = project_root / "templates"

# Ensure templates directory exists
templates_dir.mkdir(exist_ok=True)

# Mount static files directory (learn_kube/static)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Initialize templates
templates = Jinja2Templates(directory=str(templates_dir))

# Add UI routes
@app.get("/", response_class=HTMLResponse)
async def get_home_page(request: Request):
    """Serve the main application page."""
    return templates.TemplateResponse("index.html", {"request": request})

# class User(BaseModel): # Moved to models.py if still needed, or remove
#     name: str

class Prompt(BaseModel):
    text: str

# @app.post("/greet/") # Keeping for now, can be removed if not part of core learning platform
# async def greet_user(user: User):
#     return {"message": f"Hello, {user.name}!"}

@app.post("/generate/")
async def generate_text_endpoint(prompt: Prompt):
    """Generate text using Google Generative AI"""
    try:
        #print(prompt.text)
        response = generate_text(prompt.text)
        if response is None:
            raise HTTPException(status_code=500, detail="Failed to generate text")
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error generating text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating text: {str(e)}")
        


@app.post("/explain/", response_model=ConceptExplanation)
async def explain_concept(request: ConceptRequest):
    if not instructor_client:
        raise HTTPException(status_code=503, detail="LLM service is not available. Check API key and configuration.")

    system_prompt = f"""You are an expert DevOps tutor with deep knowledge of cloud computing, containerization, CI/CD, infrastructure as code, and system administration.

TASK:
You must create a highly educational explanation of '{request.topic}' tailored for a learner with '{request.proficiency_level}' proficiency level.

FORMAT REQUIREMENTS:
Structure your response precisely according to the ConceptExplanation model with these fields:

1. concept_name: The specific concept being explained (be precise about the topic)
2. definition: A clear, concise, and technically accurate definition of the concept
3. analogy: A relatable, intuitive analogy that simplifies understanding (use real-world comparisons)
4. core_principles: 3-6 fundamental principles that form the foundation of the concept
5. example_use_case: A practical, realistic example with actual code snippets, commands, or configuration where appropriate
6. common_pitfalls: 2-5 specific mistakes, misconceptions, or challenges users typically encounter
7. detailed_explanation: A comprehensive deep dive that explains:
   - The internal workings and architecture
   - How it interacts with related components/systems
   - Performance considerations and optimization techniques
   - Security implications and best practices
   - Real-world implementation details with examples

PROFICIENCY LEVEL ADAPTATIONS:
'{request.proficiency_level}' level specifically requires:

For 'beginner':
- Use simple, jargon-free language with clear definitions for any technical terms
- Provide step-by-step examples with explanations of each part
- Focus on fundamental concepts and practical application without overwhelming details
- Use visualization cues (suggest diagrams where helpful)
- Compare to familiar technologies or concepts when possible

For 'intermediate':
- Assume working knowledge of basic DevOps concepts and tools
- Include more technical implementation details and command examples
- Discuss integration with related systems
- Cover typical workflows and common design patterns
- Address performance considerations and trade-offs

For 'advanced':
- Dive deep into internal mechanisms and design philosophies
- Discuss scaling considerations, edge cases, and advanced configurations
- Cover architectural patterns, performance optimizations, and security hardening
- Include nuanced technical considerations and advanced troubleshooting
- Reference relevant specifications, RFCs, or documentation where applicable

QUALITY GUIDELINES:
- Be technically accurate and current with industry best practices
- Use specific examples rather than general statements
- Include actual commands, code snippets, or configuration examples where relevant
- Explain WHY certain approaches are recommended, not just WHAT to do
- Reference key tools, projects, or technologies related to the concept

Consider what makes a truly excellent educational explanation - one that not only informs but also builds a mental model that the learner can apply to new situations."""
    
    
    user_content_for_llm = f"Please explain the concept: {request.topic} for a {request.proficiency_level} level learner."

    try:
        explanation = generate_structured_response(
            system_prompt=system_prompt,
            user_prompt=user_content_for_llm, # Passing user's topic as the main query to LLM
            response_model=ConceptExplanation
        )
        if not explanation:
            raise HTTPException(status_code=500, detail="Failed to generate explanation from LLM.")
        return explanation
    except ValueError as ve: # Catching the ValueError from llm_service if client not configured
        raise HTTPException(status_code=503, detail=str(ve))
    except Exception as e:
        # Log the exception e for more details on the server side
        print(f"Unhandled error in /explain endpoint: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {type(e).__name__}")

# --- Placeholder for Challenge Definitions ---
# In a real app, these would come from a CMS, database, or config files
PREDEFINED_CHALLENGES = {
    "k8s_debug_pod_crashloop": {
        "title": "Debug Pod CrashLoopBackOff",
        "description": "A Kubernetes Pod named 'my-app-pod' is in a CrashLoopBackOff state. What are the first three kubectl commands you would use to investigate the cause? List them in order.",
        "criteria_for_llm": "Evaluate the user's list of kubectl commands. They should generally include checking logs, describing the pod, and possibly checking events. Correct order is a plus but focus on the relevance of the commands for initial investigation of a CrashLoopBackOff."
    },
    "git_merge_conflict": {
        "title": "Resolve Git Merge Conflict",
        "description": "You are trying to merge a feature branch named 'new-feature' into 'main'. Git indicates there's a merge conflict in a file named 'config.yaml'. Describe the general steps you would take to resolve this conflict and complete the merge.",
        "criteria_for_llm": "Evaluate the user's description of resolving a Git merge conflict. Key steps include identifying conflicting files, opening the file to manually edit and choose changes, using 'git add' on the resolved file, and then 'git commit' or 'git merge --continue'."
    }
}

@app.post("/challenge/evaluate/", response_model=ChallengeFeedback)
async def evaluate_challenge_attempt(request: ChallengeAttempt):
    if not instructor_client:
        raise HTTPException(status_code=503, detail="LLM service is not available.")

    challenge = PREDEFINED_CHALLENGES.get(request.challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail=f"Challenge with ID '{request.challenge_id}' not found.")

    system_prompt = f"""You are an AI DevOps instructor evaluating a user's solution to a challenge.
Challenge Title: {challenge['title']}
Challenge Description: {challenge['description']}
Evaluation Criteria: {challenge['criteria_for_llm']}

User's Submitted Solution:
{request.user_solution}

Based on the criteria, evaluate the user's solution. Provide an overall assessment, 
list positive points, areas for improvement, a suggested next step if applicable, 
and a detailed explanation. Structure your response according to the ChallengeFeedback model."""

    user_content_for_llm = f"Evaluate this solution for the challenge '{challenge['title']}'."

    try:
        feedback = generate_structured_response(
            system_prompt=system_prompt,
            user_prompt=user_content_for_llm, 
            response_model=ChallengeFeedback
        )
        if not feedback:
            raise HTTPException(status_code=500, detail="Failed to generate feedback from LLM.")
        return feedback
    except ValueError as ve:
        raise HTTPException(status_code=503, detail=str(ve))
    except Exception as e:
        print(f"Unhandled error in /challenge/evaluate endpoint: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {type(e).__name__}")

@app.post("/quiz/generate/", response_model=QuizQuestion)
async def generate_quiz_question(request: QuizRequest):
    if not instructor_client:
        raise HTTPException(status_code=503, detail="LLM service is not available.")

    valid_question_types = ["multiple_choice", "true_false", "short_answer_explanation"]
    selected_question_type = request.requested_question_type

    if selected_question_type and selected_question_type not in valid_question_types:
        raise HTTPException(status_code=400, 
                            detail=f"Invalid requested_question_type. Must be one of {valid_question_types}")
    
    if not selected_question_type:
        selected_question_type = random.choice(valid_question_types)
    
    difficulty = request.difficulty if request.difficulty else "Intermediate" # Default if None

    system_prompt = f"""You are an AI DevOps Quiz Generator. Your goal is to create a high-quality quiz question.
Topic: '{request.topic}'
Requested Difficulty: '{difficulty}'
Requested Question Type: '{selected_question_type}'

General Instructions:
- The question must be relevant to the topic and appropriate for the requested difficulty level.
- For 'Beginner' difficulty, focus on foundational concepts and definitions.
- For 'Intermediate' difficulty, focus on application, comparison, or slightly more complex scenarios.
- For 'Advanced' difficulty, focus on best practices, troubleshooting complex issues, or in-depth understanding of nuanced concepts.
- Ensure the question is clear, unambiguous, and solvable.
- ALWAYS provide a detailed `answer_explanation` that clarifies why the correct answer is right and, if applicable, why other options might be wrong.
- Structure your response strictly according to the `QuizQuestion` Pydantic model.

Type-Specific Instructions:
- If `question_type` is 'multiple_choice':
    - Generate 3-4 distinct and plausible options.
    - Each option should have a simple letter ID (A, B, C, D).
    - Clearly indicate the `correct_option_id`.
    - Avoid "all of the above" or "none of the above" if possible; prefer specific, informative distractors.
- If `question_type` is 'true_false':
    - The `question_text` should be a declarative statement that is definitively true or false.
    - Options should be [{{'id': 'True', 'text': 'True'}}, {{'id': 'False', 'text': 'False'}}].
    - `correct_option_id` must be either 'True' or 'False'.
- If `question_type` is 'short_answer_explanation':
    - The `question_text` should prompt for a brief explanation or definition.
    - `options` list should be empty.
    - `correct_option_id` should be null/None.
    - The `answer_explanation` should be the model answer or a comprehensive guide to what a good answer includes.

Adhere to these instructions meticulously to generate an effective quiz question.
"""    
    user_content_for_llm = f"Generate a '{selected_question_type}' quiz question about '{request.topic}' at '{difficulty}' difficulty. Ensure all fields of the QuizQuestion model are populated correctly for this type."

    try:
        quiz_question_response = generate_structured_response(
            system_prompt=system_prompt,
            user_prompt=user_content_for_llm,
            response_model=QuizQuestion
        )
        if not quiz_question_response:
            raise HTTPException(status_code=500, detail="Failed to generate quiz question from LLM.")
        
        # --- Post-processing and Validation ---
        quiz_question_response.topic = request.topic 
        quiz_question_response.question_type = selected_question_type # Ensure type is set as requested/chosen

        if not quiz_question_response.question_text:
            raise HTTPException(status_code=500, detail="LLM failed to generate question text.")

        if not quiz_question_response.answer_explanation:
            raise HTTPException(status_code=500, detail="LLM failed to provide an answer explanation.")

        if selected_question_type == "multiple_choice":
            if not quiz_question_response.options or len(quiz_question_response.options) < 2 or len(quiz_question_response.options) > 4:
                # Attempt to regenerate or error out
                print(f"LLM failed to produce valid options for multiple_choice: {quiz_question_response.options}")
                raise HTTPException(status_code=500, detail="LLM generated an invalid number of options for multiple choice (must be 2-4). Options: " + str(quiz_question_response.options) )
            if not quiz_question_response.correct_option_id or not any(opt.id == quiz_question_response.correct_option_id for opt in quiz_question_response.options):
                print(f"LLM failed to specify a valid correct_option_id for multiple_choice. Got: {quiz_question_response.correct_option_id}, Options: {quiz_question_response.options}")
                raise HTTPException(status_code=500, detail="LLM failed to specify a valid correct option ID for multiple choice question.")
        
        
        elif selected_question_type == "true_false":
            # Ensure options are correctly formatted as True/False and correct_option_id is one of them
            expected_options = [{"id": "True", "text": "True"}, {"id": "False", "text": "False"}]
            # Allow some flexibility in how LLM returns options as long as ids are True/False
            if not quiz_question_response.options or len(quiz_question_response.options) != 2 or \
               not all(opt.id in ["True", "False"] for opt in quiz_question_response.options) or \
               len(set(opt.id for opt in quiz_question_response.options)) != 2 :
                quiz_question_response.options = [QuizOption(id="True", text="True"), QuizOption(id="False", text="False")] # Force correct options
                # Consider logging a warning that LLM needed correction for true/false options
            if quiz_question_response.correct_option_id not in ["True", "False"]:
                # This is harder to fix if the explanation contradicts. Best to fail.
                raise HTTPException(status_code=500, detail=f"LLM provided an invalid correct_option_id for true/false: {quiz_question_response.correct_option_id}")

        elif selected_question_type == "short_answer_explanation":
            quiz_question_response.options = [] # Ensure no options
            quiz_question_response.correct_option_id = "" # Ensure empty string for correct_option_id

        return quiz_question_response
    except ValueError as ve: # From instructor_client not being available
        raise HTTPException(status_code=503, detail=str(ve))
    except Exception as e:
        print(f"Unhandled error in /quiz/generate endpoint: {type(e).__name__} - {str(e)}")
        # Potentially log the full error e for debugging
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while generating quiz: {type(e).__name__}")

@app.post("/challenges/generate/", response_model=GeneratedChallenge)
async def generate_new_challenge(request: GenerateChallengeRequest):
    if not instructor_client:
        raise HTTPException(status_code=503, detail="LLM service is not available.")

    system_prompt = f"""You are an AI Challenge Designer for a DevOps learning platform.
Your primary goal is to create a new, original, and engaging challenge for a user learning about '{request.topic}'.
The desired difficulty is around '{request.difficulty_hint}'.

The challenge MUST include:
1.  `title`: A clear, concise, and descriptive title for the challenge.
2.  `topic`: The specific DevOps topic this challenge relates to (this should be '{request.topic}').
3.  `difficulty`: Your assessed difficulty (e.g., Beginner, Intermediate, Advanced), considering the topic and the scenario you create. Align this with the user's hint ('{request.difficulty_hint}') but use your judgment based on the generated task.
4.  `description`: A detailed problem statement, scenario, or task. Make it practical. For example, instead of asking 'What is a Dockerfile?', present a scenario like 'You have a Python application with these files [app.py, requirements.txt]. Create a Dockerfile to containerize it.'.
5.  `evaluation_criteria`: This is CRITICAL. Define clear, specific, and actionable criteria that an AI tutor (another LLM instance) MUST use to assess a user's solution. These criteria should be detailed enough for the tutor to give constructive feedback. 
    - GOOD Example for `evaluation_criteria` (if challenge is 'Create a Dockerfile for a Python app'): 
        - 'Does the Dockerfile use an appropriate Python base image? (e.g., python:3.9-slim)'
        - 'Does it correctly copy application files into the image? (e.g., COPY . /app)'
        - 'Does it install dependencies from requirements.txt? (e.g., RUN pip install -r requirements.txt)'
        - 'Does it set a WORKDIR? (e.g., WORKDIR /app)'
        - 'Does it specify the correct command to run the application? (e.g., CMD [\"python\", \"app.py\"])'
        - 'Are there any obvious security bad practices (e.g., running as root if not necessary, exposing unnecessary ports)?'
    - BAD Example for `evaluation_criteria`: 'Is the Dockerfile correct?' (This is too vague for the tutor LLM).
    - The criteria should guide the tutor to check for specific elements, commands, configurations, or conceptual understanding demonstrated by the user's solution.
6.  `solution_keywords`: Optional. If applicable, list a few key terms, commands, or concepts that are highly likely to appear in a good solution. This can further aid the AI tutor.

Things to AVOID when generating challenges:
- Do NOT create challenges that are simple definition lookups (e.g., 'What is Kubernetes?').
- Do NOT create challenges with ambiguous solutions or multiple vastly different correct approaches unless the evaluation criteria can handle that ambiguity.
- Do NOT make the `evaluation_criteria` a single question like 'Is the solution good?'. It must be a list of checkable points or guiding questions for the tutor.
- Avoid overly complex or multi-stage challenges unless the difficulty is explicitly 'Advanced' and the evaluation criteria can be broken down per stage.

Ensure your entire response is structured strictly according to the `GeneratedChallenge` Pydantic model.
"""

    user_content_for_llm = f"Create a new DevOps challenge about the topic '{request.topic}' with a targeted difficulty of '{request.difficulty_hint}'. Pay close attention to generating detailed and actionable evaluation_criteria."

    try:
        new_challenge = generate_structured_response(
            system_prompt=system_prompt,
            user_prompt=user_content_for_llm,
            response_model=GeneratedChallenge
        )
        if not new_challenge:
            raise HTTPException(status_code=500, detail="Failed to generate new challenge from LLM.")
        
        # Post-processing/validation for the generated challenge
        if not new_challenge.title or not new_challenge.description or not new_challenge.evaluation_criteria:
            raise HTTPException(status_code=500, detail="LLM failed to generate all required fields for the challenge (title, description, evaluation_criteria).")
        
        # Ensure topic and difficulty are set, even if LLM was spotty
        new_challenge.topic = request.topic # Override LLM if it changed the topic
        if not new_challenge.difficulty: # If LLM didn't set difficulty, use the hint
            new_challenge.difficulty = request.difficulty_hint
            
        return new_challenge
    except ValueError as ve: # From instructor_client not being available
        raise HTTPException(status_code=503, detail=str(ve))
    except Exception as e:
        print(f"Unhandled error in /challenges/generate endpoint: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while generating challenge: {type(e).__name__}")

@app.post("/challenge/evaluate_dynamic/", response_model=ChallengeFeedback)
async def evaluate_dynamic_challenge_attempt(request: DynamicChallengeAttempt):
    if not instructor_client:
        raise HTTPException(status_code=503, detail="LLM service is not available.")


    system_prompt = f"""You are an AI DevOps instructor evaluating a user's solution to a dynamically generated challenge.
Challenge Topic: {request.challenge_topic}
Challenge Difficulty: {request.challenge_difficulty}
Challenge Title: {request.challenge_title}
Challenge Description: {request.challenge_description}

Evaluation Criteria Provided by Challenge Generator:
{request.challenge_evaluation_criteria}

Optional Solution Keywords Provided by Challenge Generator: {request.challenge_solution_keywords if request.challenge_solution_keywords else 'None provided'}

User's Submitted Solution:
{request.user_solution}

Based on the provided evaluation criteria (and optionally considering the solution keywords), 
evaluate the user's solution. Provide an overall assessment, list positive points, areas for improvement, 
a suggested next step if applicable, and a detailed explanation. 
Structure your response according to the ChallengeFeedback Pydantic model.
Be thorough and fair in your assessment, adhering strictly to the provided evaluation criteria.
"""

    user_content_for_llm = f"Evaluate this solution for the dynamically generated challenge titled '{request.challenge_title}'."

    try:
        feedback = generate_structured_response(
            system_prompt=system_prompt,
            user_prompt=user_content_for_llm, 
            response_model=ChallengeFeedback
        )
        if not feedback:
            raise HTTPException(status_code=500, detail="Failed to generate feedback from LLM for the dynamic challenge.")
        return feedback
    except ValueError as ve: # From instructor_client not being available
        raise HTTPException(status_code=503, detail=str(ve))
    except Exception as e:
        print(f"Unhandled error in /challenge/evaluate_dynamic endpoint: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {type(e).__name__}")

@app.post("/mindmap/generate/", response_model=MindMap)
async def generate_mind_map(request: MindMapRequest):
    if not instructor_client:
        raise HTTPException(status_code=503, detail="LLM service is not available.")
    
    # Limit depth to reasonable values
    depth = min(max(request.depth, 1), 3)
    
    system_prompt = f"""You are an expert DevOps knowledge graph creator.
Your task is to create a comprehensive mind map about the DevOps topic: '{request.topic}'
The mind map should be hierarchical with {depth} levels of depth.

Follow these guidelines:
1. Create a root node for the main topic
2. Create 3-7 main concept nodes (level 1) that are key aspects of this topic
3. For each level 1 node, create 2-4 more specific subconcepts (level 2)
{'' if depth < 3 else '4. For selected important level 2 nodes, add 1-3 even more specific nodes (level 3)'}

If a focus area of '{request.focus_area}' is specified, ensure that branch is more detailed.

For each node:
- Create a clear, concise label (1-5 words max)
- Provide a brief description explaining the concept
- Assign an appropriate group category (e.g., "concept", "tool", "practice", "principle")

Each node must have a unique ID and be properly connected to its parent with edges.
Ensure the mind map is technically accurate and represents current DevOps best practices.

Structure your response exactly according to the MindMap model with nodes and edges arrays.
"""

    user_content_for_llm = f"Create a DevOps mind map for the topic '{request.topic}' with {depth} levels of depth{' focusing on ' + request.focus_area if request.focus_area else ''}."

    try:
        mind_map = generate_structured_response(
            system_prompt=system_prompt,
            user_prompt=user_content_for_llm,
            response_model=MindMap
        )
        
        if not mind_map:
            raise HTTPException(status_code=500, detail="Failed to generate mind map from LLM.")
        
        # Validate the mind map has at least some nodes and edges
        if not mind_map.nodes or not mind_map.edges:
            raise HTTPException(status_code=500, detail="Generated mind map is incomplete. Try a different topic.")
        
        # Ensure the topic is set
        mind_map.topic = request.topic
        
        return mind_map
    except ValueError as ve:
        raise HTTPException(status_code=503, detail=str(ve))
    except Exception as e:
        print(f"Unhandled error in /mindmap/generate endpoint: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {type(e).__name__}")

@app.get("/healthz")
async def health_check():
    """Simple liveness probe endpoint."""
    llm_status = "ok"
    if not instructor_client:
        llm_status = "unavailable"
    return {"status": "healthy", "llm_service": llm_status}

@app.get("/readyz")
async def readiness_check():
    """Simple readiness probe endpoint."""
    # For now, same as liveness. Could check instructor_client more deeply.
    llm_status = "ready"
    if not instructor_client:
        llm_status = "not_ready"
    return {"status": "ready", "llm_service": llm_status}

if __name__ == "__main__":
    import uvicorn
    # # Ensure GEMINI_API_KEY and MODEL_NAME are available if you run this directly
    # print(f"GEMINI_API_KEY set: {bool(os.environ.get('GEMINI_API_KEY'))}")
    # print(f"MODEL_NAME: {os.environ.get('MODEL_NAME', 'gemini-1.5-flash-latest')}")
    # print(f"Instructor client available in main: {bool(instructor_client)}")
    uvicorn.run(app, host="0.0.0.0", port=8000)

