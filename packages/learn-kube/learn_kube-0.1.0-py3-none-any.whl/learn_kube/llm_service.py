import instructor
from google.genai import types
from google import genai
import os

# Configuration (Consider moving to a central config or using environment variables directly)
GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY")

GEMINI_MODEL_NAME = os.environ.get("MODEL_NAME", "gemini-2.5-flash-preview-04-17") # Updated to a common model

# Default configuration for content generation, ensuring JSON output for instructor
generate_content_config = types.GenerationConfig( # Note: it's GenerationConfig not GenerateContentConfig
    temperature=0.15,
    # thinking_config = types.ThinkingConfig( # Not available in all SDK versions or models
    #     thinking_budget=1024,
    # ),
    response_mime_type="application/json", # Crucial for instructor
)

instructor_client = None
if GOOGLE_API_KEY:
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        instructor_client = instructor.from_genai(client, mode=instructor.Mode.GENAI_TOOLS,config=generate_content_config)

    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
        instructor_client = None
else:
    print("Error: Google API Key (GEMINI_API_KEY) not configured. LLM functionality will be disabled.")


def generate_text(prompt: str):
    """Generate text using Google Generative AI"""
    try:
        response = client.models.generate_content(
        model=GEMINI_MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=1024)
        ),
        )
        #print(response.text)
        return {"response": response.text}
    except Exception as e:
        print(f"Error generating text: {e}")
        return None

def generate_structured_response(system_prompt: str, response_model, user_prompt: str = "Please process the request based on the system guidelines."):
    """
    Generates a structured response from the LLM using instructor.
    
    Args:
        system_prompt: The system prompt to guide the LLM.
        response_model: The Pydantic model for the desired structured response.
        user_prompt: The user message/query, defaults to a generic instruction.

    Returns:
        An instance of the response_model populated by the LLM, or None if an error occurs.
    """
    if not instructor_client:
        # print("Error: Instructor client not configured.") # Already printed above
        raise ValueError("Instructor client not configured due to missing API key or initialization error.")

    try:
        response = instructor_client.chat.completions.create(
            model=GEMINI_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt}, # System prompt to provide context and instructions
                {"role": "user", "content": user_prompt}      # User's specific query or data
            ],
            response_model=response_model,
            max_retries=2 # Keep retries reasonable
        )
        return response
    except Exception as e:
        print(f"Error generating structured response: {type(e).__name__} - {str(e)}")
        # Consider more specific error handling or re-raising
        return None

# Example Usage (for testing this module directly)
if __name__ == "__main__":
    if not GOOGLE_API_KEY:
        print("Please set the GEMINI_API_KEY environment variable to run this example.")
    else:
        from pydantic import BaseModel
        class UserDetails(BaseModel):
            name: str
            age: int

        prompt_for_user = "Extract the user's name and age: John Doe is 30 years old."
        system_guide = "You are an expert extraction system. Please extract entities based on the user's request and structure it."
        
        # If using instructor with a client that expects `generate_content` directly (not chat.completions):
        # The call might look more like:
        # user_details = instructor_client.generate_content(
        #     contents=prompt, # or construct types.Content(...)
        #     response_model=UserDetails 
        # )
        # But since we used Mode.GEMINI_TOOLS, chat.completions.create should be available.

        print(f"Attempting to generate structured response for: '{prompt_for_user}'")
        details = generate_structured_response(system_prompt=system_guide, user_prompt=prompt_for_user, response_model=UserDetails)
        
        if details:
            print("Successfully extracted details:")
            print(f"Name: {details.name}, Age: {details.age}")
        else:
            print("Failed to extract details.") 