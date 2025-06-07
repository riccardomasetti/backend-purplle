import os
import google.generativeai as genai
from dotenv import load_dotenv
from app.utils.file_processor import extract_text_from_file
import random
# Load environment variables
load_dotenv()

# Configure the Gemini API with your API key
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))


def generate_question_from_document(file_path, topic=None):
    """
    Generate a question and its answer based on the content of a document.

    Args:
        file_path (str): Path to the document file
        topic (str, optional): A specific topic to focus on. Defaults to None.

    Returns:
        tuple: (question, answer)
    """
    # Extract text from the document
    text = extract_text_from_file(file_path)

    # If text extraction failed or returned an error message
    if text.startswith("Error") or text.startswith("Unsupported"):
        return f"Could not generate question", text

    # Truncate text if too long (Gemini has token limits)
    max_length = 10000  # Adjust as needed based on Gemini's limits
    if len(text) > max_length:
        text = text[:max_length] + "..."

    question_types = [
        "factual", "conceptual", "analytical", "application", "comparative",
        "evaluative"
    ]

    difficulty_levels = ["introductory", "intermediate"]

    # Randomly select question characteristics
    chosen_type = random.choice(question_types)
    chosen_difficulty = random.choice(difficulty_levels)

    random_seed = random.randint(1, 10000)

    # Create a prompt for Gemini
    prompt = f"""
        Based on the following content, generate an educational question and its detailed answer.
        The question should test understanding of a key concept from the text.

        CONTENT:
        {text}

        INSTRUCTIONS:
        - Create one meaningful {chosen_difficulty}-level {chosen_type} question 
        - Choose a different topic or concept than might be obvious at first glance
        - Question seed: {random_seed} (use this to make your question unique)
        - Provide a comprehensive answer to the question
        - Format your response as a JSON with 'question' and 'answer' fields
        - Don't include any other text outside the JSON format
        """

    if topic:
        prompt += f"\n- Focus the question on the topic of: {topic}"

    # Generate content using Gemini
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)

        # Extract question and answer from the response
        response_text = response.text

        # Parse the response
        try:
            # Clean up response text to extract just the JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].strip()

            import json
            result = json.loads(response_text)
            return result.get("question"), result.get("answer")
        except Exception as e:
            # Fallback parsing if JSON extraction fails
            if "question" in response_text and "answer" in response_text:
                parts = response_text.split("answer")
                question = parts[0].replace("question", "").replace(":", "").strip()
                answer = parts[1].replace(":", "").strip()
                return question, answer
            else:
                return "Failed to generate a proper question", f"Error parsing response: {str(e)}"

    except Exception as e:
        return f"Error generating question", f"An error occurred: {str(e)}"