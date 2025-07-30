"""
Gemini integration utilities for template generation.
"""

import os
import json
import logging
import google.generativeai as genai
from typing import Dict, Optional, List
from pydantic import BaseModel, Field, validator
import re

logger = logging.getLogger("pykickstart")

class TemplateFile(BaseModel):
    """Model for a single template file."""
    content: str = Field(..., description="The content of the file")
    
    @validator('content')
    def validate_content(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError("Content must be a non-empty string")
        return v

class TemplateResponse(BaseModel):
    """Model for the complete template response."""
    files: Dict[str, str] = Field(..., description="Dictionary mapping file paths to their contents")
    
    @validator('files')
    def validate_files(cls, v):
        if not v:
            raise ValueError("Files dictionary cannot be empty")
        for path, content in v.items():
            if not path or not isinstance(path, str):
                raise ValueError(f"Invalid file path: {path}")
            if not content or not isinstance(content, str):
                raise ValueError(f"Invalid content for file {path}")
        return v

def setup_gemini(api_key: str) -> None:
    """
    Set up Gemini API with the provided key.
    
    Args:
        api_key: Gemini API key
    """
    try:
        genai.configure(api_key=api_key)
        logger.info("Gemini API configured successfully")
    except Exception as e:
        logger.error(f"Failed to configure Gemini API: {str(e)}")
        raise RuntimeError(f"Failed to configure Gemini API: {str(e)}")

def clean_json_response(response_text: str) -> str:
    """
    Clean and fix common JSON formatting issues in Gemini responses.
    
    Args:
        response_text: Raw response text from Gemini
    
    Returns:
        Cleaned JSON string
    """
    # Remove markdown code blocks if present
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    
    # Strip whitespace
    response_text = response_text.strip()
    
    # Try to fix common JSON issues
    try:
        # First attempt: parse as-is
        json.loads(response_text)
        return response_text
    except json.JSONDecodeError as e:
        logger.warning(f"Initial JSON parse failed: {str(e)}")
        
        # Try to fix common issues
        # Fix unescaped quotes in strings
        # This is a more robust approach to handle string content with quotes
        lines = response_text.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Check if this line contains a file content value
            if '": "' in line and not line.strip().endswith('",'):
                # This might be a string value that spans multiple lines or has unescaped quotes
                # For now, let's try a simple fix for obvious cases
                if line.count('"') % 2 == 1 and not line.strip().endswith(','):
                    # Odd number of quotes and doesn't end with comma - might need closing quote
                    if not line.strip().endswith('"'):
                        line = line.rstrip() + '"'
            fixed_lines.append(line)
        
        fixed_response = '\n'.join(fixed_lines)
        
        try:
            json.loads(fixed_response)
            return fixed_response
        except json.JSONDecodeError:
            # If still failing, try more aggressive fixes
            return fix_json_aggressive(response_text)

def fix_json_aggressive(response_text: str) -> str:
    """
    Apply more aggressive JSON fixes when standard cleaning fails.
    
    Args:
        response_text: Raw response text
    
    Returns:
        Fixed JSON string
    """
    try:
        # Try to extract just the JSON object part
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            json_part = response_text[start_idx:end_idx + 1]
            
            # Try to fix the specific issue mentioned in the error
            # The error mentions line 11, column 1180 - likely in a long string value
            
            # Split by lines and try to identify problematic strings
            lines = json_part.split('\n')
            fixed_lines = []
            
            for i, line in enumerate(lines):
                stripped_line = line.strip()
                
                # If this looks like a file content line with issues
                if '": "' in stripped_line and not stripped_line.endswith('",') and not stripped_line.endswith('"'):
                    # Find the last quote and see if we need to close the string
                    last_quote_idx = stripped_line.rfind('"')
                    if last_quote_idx > stripped_line.find('": "') + 3:  # After the opening quote
                        # Check if next non-empty line starts with a key (indicating we need to close this string)
                        next_line_idx = i + 1
                        while next_line_idx < len(lines) and not lines[next_line_idx].strip():
                            next_line_idx += 1
                        
                        if next_line_idx < len(lines):
                            next_line = lines[next_line_idx].strip()
                            if next_line.startswith('"') and '":' in next_line:
                                # Next line is a new key, so we need to close current string
                                if not stripped_line.endswith('"'):
                                    line = line.rstrip() + '",'
                                elif not stripped_line.endswith(','):
                                    line = line.rstrip() + ','
                
                fixed_lines.append(line)
            
            fixed_json = '\n'.join(fixed_lines)
            
            # Test if it's valid JSON now
            json.loads(fixed_json)
            return fixed_json
            
    except Exception as e:
        logger.warning(f"Aggressive JSON fix failed: {str(e)}")
    
    # If all else fails, return original
    return response_text

def get_template_specific_prompt(template_type: str) -> str:
    """
    Get template-specific prompt for Gemini.
    
    Args:
        template_type: Type of template to generate
    
    Returns:
        Template-specific prompt
    """
    logger.info(f"Getting prompt for template type: {template_type}")
    
    base_prompt = """Generate a complete, working Python project template.
    
    CRITICAL JSON FORMAT REQUIREMENTS:
    - The response MUST be ONLY a valid JSON object
    - NO markdown formatting, NO code blocks, NO ```json
    - NO additional text or explanation outside the JSON
    - String values must have properly escaped quotes and newlines
    - Use \\n for newlines in file content
    - Use \\" for quotes within strings
    - Each file content must be a single string value
    
    Format the response EXACTLY like this:
    {
        "files": {
            "src/app.py": "import os\\nfrom fastapi import FastAPI\\napp = FastAPI()",
            "README.md": "# My Project\\nThis is a sample project"
        }
    }
    
    IMPORTANT RULES:
    1. Response must be valid JSON that can be parsed by json.loads()
    2. All string content must be properly escaped
    3. No trailing commas
    4. All file paths as keys, file contents as string values
    5. Include proper Python imports and error handling
    6. Add comprehensive comments and type hints
    7. Make code production-ready
    8. Include detailed README.md with setup instructions
    
    The response must be parseable JSON with a "files" key containing file mappings."""
    
    template_specific = {
        "web-app": """
        Create a FastAPI web application with:
        1. Complete CRUD operations for users
        2. SQLAlchemy for database operations  
        3. Pydantic models for validation
        4. Basic authentication
        5. Error handling and status codes
        6. Environment configuration
        
        Required files:
        - src/app.py - Main FastAPI application
        - src/models.py - SQLAlchemy models  
        - src/schemas.py - Pydantic schemas
        - src/database.py - Database configuration
        - src/crud.py - CRUD operations
        - src/auth.py - Authentication utilities
        - .env.example - Environment template
        - requirements.txt - Dependencies
        - README.md - Documentation
        """,
        
        "cli-tool": """
        Create a CLI tool with:
        1. Click for command-line interface
        2. Multiple subcommands
        3. Configuration management
        4. Progress bars and output
        5. Error handling and logging
        
        Required files:
        - src/main.py - Main CLI application
        - src/commands/ - Command modules
        - src/utils/ - Utility functions
        - src/config.py - Configuration
        - requirements.txt - Dependencies
        - README.md - Documentation
        """,
        
        "game": """
        Create a Pygame game with:
        1. Basic game loop
        2. Sprite management
        3. Collision detection
        4. Sound effects
        5. Score tracking
        6. Menu system
        
        Required files:
        - src/main.py - Main game loop
        - src/sprites.py - Game sprites
        - src/levels.py - Game levels  
        - src/sounds.py - Sound management
        - src/menu.py - Menu system
        - requirements.txt - Dependencies
        - README.md - Documentation
        """,
        
        "data-science": """
        Create a data science project with:
        1. Data loading and preprocessing
        2. Analysis and visualization
        3. Model training and evaluation
        4. Results reporting
        
        Required files:
        - src/data_loader.py - Data loading
        - src/preprocessing.py - Data preprocessing
        - src/analysis.py - Data analysis
        - src/visualization.py - Plotting
        - notebooks/ - Jupyter notebooks
        - requirements.txt - Dependencies
        - README.md - Documentation
        """
    }
    
    if template_type not in template_specific:
        logger.warning(f"Unknown template type: {template_type}")
        return base_prompt
    
    return base_prompt + template_specific[template_type]

def generate_template_code(template_type: str, gemini_key: str) -> Dict[str, str]:
    """
    Generate template code using Gemini.
    
    Args:
        template_type: Type of template to generate
        gemini_key: Gemini API key
    
    Returns:
        Dictionary mapping file paths to their generated content
    """
    try:
        setup_gemini(gemini_key)
        
        # Configure the model with specific parameters for better JSON output
        generation_config = {
            "temperature": 0.1,  # Lower temperature for more consistent output
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config=generation_config
        )
        logger.info("Gemini model configured")
        
        # Get template-specific prompt
        prompt = get_template_specific_prompt(template_type)
        logger.info("Generated prompt for template")
        
        # Generate response with retries
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Sending request to Gemini API (attempt {attempt + 1}/{max_retries})")
                response = model.generate_content(prompt)
                logger.info("Received response from Gemini API")
                
                # Clean and validate response
                response_text = response.text.strip()
                logger.info(f"Response length: {len(response_text)} characters")
                
                # Clean JSON response
                cleaned_response = clean_json_response(response_text)
                
                # Parse and validate response using Pydantic
                json_data = json.loads(cleaned_response)
                template_response = TemplateResponse(**json_data)
                logger.info(f"Successfully validated template response with {len(template_response.files)} files")
                
                return template_response.files
                
            except json.JSONDecodeError as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed with JSON error: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info("Retrying with modified prompt...")
                    # Modify prompt to be more explicit about JSON format
                    prompt = prompt.replace(
                        "The response must be parseable JSON", 
                        "CRITICAL: Return ONLY valid JSON. No extra text. Test your JSON before responding."
                    )
                continue
                
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    continue
                break
        
        # If all attempts failed
        if last_error:
            if isinstance(last_error, json.JSONDecodeError):
                logger.error(f"All attempts failed with JSON parsing error: {str(last_error)}")
                raise ValueError(f"Failed to get valid JSON response from Gemini after {max_retries} attempts: {str(last_error)}")
            else:
                logger.error(f"Template validation failed: {str(last_error)}")
                raise ValueError(f"Invalid template response format: {str(last_error)}")
            
    except Exception as e:
        logger.error(f"Error in template generation: {str(e)}", exc_info=True)
        raise ValueError(f"Error processing template: {str(e)}")