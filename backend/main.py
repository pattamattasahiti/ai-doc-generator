from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

class CodeInput(BaseModel):
    code: str
    language: str
    doc_type: str

@app.post("/generate-docs")
async def generate_documentation(input_data: CodeInput):
    try:
        prompt = create_documentation_prompt(
            input_data.code, 
            input_data.language, 
            input_data.doc_type
        )
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {"documentation": message.content[0].text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def create_documentation_prompt(code: str, language: str, doc_type: str) -> str:
    if doc_type == "function":
        return create_function_docs_prompt(code, language)
    elif doc_type == "readme":
        return create_readme_prompt(code, language)
    elif doc_type == "explanation":
        return create_explanation_prompt(code, language)
    elif doc_type == "architecture":
        return create_architecture_prompt(code, language)
    else:
        return create_general_prompt(code, language)

def create_function_docs_prompt(code: str, language: str) -> str:
    return f"""You are a senior software engineer writing API documentation.

Analyze this {language} code and generate comprehensive function/method documentation.

Code:
```{language}
{code}
```

YOUR RESPONSE MUST FOLLOW THIS EXACT JSON STRUCTURE:
{{
  "functions": [
    {{
      "name": "function_name",
      "purpose": "clear one-line description",
      "parameters": [
        {{
          "name": "param_name",
          "type": "param_type",
          "description": "what it does"
        }}
      ],
      "returns": {{
        "type": "return_type",
        "description": "what it returns"
      }},
      "examples": [
        "usage example 1",
        "usage example 2"
      ],
      "complexity": "time and space complexity if applicable",
      "edge_cases": ["edge case 1", "edge case 2"]
    }}
  ]
}}

CRITICAL REQUIREMENTS:
- Output ONLY valid JSON, no other text
- Include ALL functions/methods found
- Be specific and technical
- Include practical examples
"""

def create_readme_prompt(code: str, language: str) -> str:
    return f"""You are a technical writer creating professional GitHub README documentation.

CONTEXT:
- Language: {language}
- Audience: Developers who want to use this code
- Goal: Create a complete, professional README

Code to document:
```{language}
{code}
```

Generate a comprehensive README.md that includes:

# Project Title
[Infer from code]

## Description
[What this code does - 2-3 sentences]

## Features
- [Key feature 1]
- [Key feature 2]
- [Key feature 3]

## Installation
```bash
[Step-by-step installation commands]
```

## Usage
```{language}
[Clear usage examples with actual code]
```

## API Reference
[If applicable - document main functions/classes]

## Requirements
[List dependencies]

## Examples
[2-3 practical examples]

## Contributing
[Standard contribution guidelines]

## License
[Suggest appropriate license]

REQUIREMENTS:
- Use proper Markdown formatting
- Be comprehensive but concise
- Include code blocks with syntax highlighting
- Make it copy-paste ready
"""

def create_explanation_prompt(code: str, language: str) -> str:
    return f"""You are a patient programming instructor explaining code to a junior developer.

Code to explain:
```{language}
{code}
```

Use this STEP-BY-STEP analysis approach:

**Step 1: High-Level Overview**
First, explain what this code does in one paragraph, as if explaining to a non-programmer.

**Step 2: Component Breakdown**
Then, break down the code into logical sections and explain each part:
- What is this section?
- Why does it exist?
- How does it work?

**Step 3: Line-by-Line Analysis**
For complex or critical lines, provide detailed explanations:
- Line [X]: [What it does and why]
- Line [Y]: [What it does and why]

**Step 4: Data Flow**
Trace how data moves through the code:
- Input: [What comes in]
- Processing: [What happens to it]
- Output: [What comes out]

**Step 5: Key Concepts**
Identify and explain any important programming concepts used:
- [Concept 1]: [Explanation]
- [Concept 2]: [Explanation]

**Step 6: Potential Issues**
Note any edge cases, gotchas, or areas for improvement.

FORMAT: Use clear headers, bullet points, and be conversational but technical.
"""

def create_architecture_prompt(code: str, language: str) -> str:
    return f"""You are a software architect creating system design documentation.

EXAMPLE OF GOOD ARCHITECTURE DOCUMENTATION:
```
## System Architecture

### Overview
This is a RESTful API service built with FastAPI that handles user authentication.

### Components
1. **API Layer** (main.py)
   - Handles HTTP requests
   - Routes: /login, /register, /logout
   
2. **Business Logic** (auth.py)
   - Password hashing with bcrypt
   - JWT token generation
   
3. **Data Layer** (database.py)
   - PostgreSQL connection
   - User model with SQLAlchemy

### Data Flow
Request → API Layer → Validation → Business Logic → Database → Response

### Key Design Decisions
- Used JWT for stateless authentication
- Bcrypt with cost factor 12 for security
- Connection pooling for database efficiency
```

NOW, analyze this {language} code and create similar architecture documentation:
```{language}
{code}
```

YOUR ARCHITECTURE DOCUMENTATION MUST INCLUDE:

## System Architecture

### Overview
[High-level description]

### Components
[List major components with their responsibilities]

### Data Flow
[How data moves through the system]

### Key Design Decisions
[Why certain approaches were chosen]

### Technology Stack
[Libraries/frameworks used and why]

### Scalability Considerations
[How this could scale]

### Potential Improvements
[Architectural enhancements for production]

FORMAT: Use Markdown, be detailed but clear.
"""

def create_general_prompt(code: str, language: str) -> str:
    return f"""Generate comprehensive technical documentation for this {language} code.

Code:
```{language}
{code}
```

MANDATORY CONSTRAINTS:
✓ Length: 200-400 words
✓ Technical level: Intermediate developer
✓ Format: Markdown with proper headers
✓ Include: Purpose, usage, and examples
✓ Tone: Professional but approachable
✗ Do NOT: Include installation steps unless code imports external libraries
✗ Do NOT: Be overly verbose or use filler words
✗ Do NOT: Make assumptions about code you can't see

STRUCTURE:
1. Brief summary (2-3 sentences)
2. Detailed explanation
3. Usage example
4. Important notes or caveats

Begin your documentation now:
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)