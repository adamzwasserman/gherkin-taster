"""
Gemini AI Service
Handles video analysis and Gherkin generation using Google's Gemini API
"""

import base64
import tempfile
import os
import google.generativeai as genai
from backend.config import get_settings


class GeminiService:
    """Service for interacting with Gemini AI"""

    def __init__(self):
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel("models/gemini-2.5-flash")

    async def analyze_video_and_generate_gherkin(
        self,
        video_base64: str,
        title: str,
        description: str,
        request_type: str,
    ) -> dict:
        """
        Analyze video and generate Gherkin specification

        Args:
            video_base64: Base64 encoded video (data:video/webm;base64,...)
            title: Feature request title
            description: Feature request description
            request_type: bug, enhancement, or feature

        Returns:
            dict with 'gherkin' and 'analysis' keys
        """
        # Remove data URL prefix if present
        if video_base64.startswith("data:"):
            video_base64 = video_base64.split(",")[1]

        # Decode base64 to bytes
        video_bytes = base64.b64decode(video_base64)

        # Check file size (Gemini limit is 1MB for inline data)
        size_mb = len(video_bytes) / (1024 * 1024)
        if size_mb > 1:
            # For large videos, generate Gherkin from text only
            return await self._generate_gherkin_from_text(
                title=title,
                description=description,
                request_type=request_type,
            )

        prompt = f"""
You are a Business Analyst expert at writing Gherkin specifications (Given-When-Then format).

**Context:**
- Request Type: {request_type}
- Title: {title}
- Description: {description or "No written description provided"}

**Task:**
Analyze the provided screen recording video and:
1. Understand what the user is demonstrating
2. Extract the acceptance criteria
3. Write a complete Gherkin feature specification

**Output Format (YAML):**
```yaml
feature:
  title: "Feature title"
  description: "High-level description"
  scenarios:
    - scenario: "Scenario name"
      given:
        - "Context step"
      when:
        - "Action step"
      then:
        - "Expected outcome"
    - scenario: "Another scenario"
      given:
        - "Context step"
      when:
        - "Action step"
      then:
        - "Expected outcome"

analysis:
  summary: "Brief summary of what was demonstrated"
  user_journey: "Step-by-step user journey observed"
  edge_cases: ["Potential edge case 1", "Potential edge case 2"]
  technical_notes: ["Technical consideration 1", "Technical consideration 2"]
```

**Guidelines:**
- Use clear, business-friendly language
- Be specific about expected behavior
- Include relevant context from the video
- Consider edge cases visible in the demonstration
- Write scenarios that are testable
"""

        # Save bytes to temporary file for Gemini upload
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
            tmp_file.write(video_bytes)
            tmp_file_path = tmp_file.name

        try:
            # Upload video for analysis
            video_file = genai.upload_file(path=tmp_file_path)

            # Wait for video to be processed
            import time
            while video_file.state.name == "PROCESSING":
                print("Waiting for video to be processed...")
                time.sleep(2)
                video_file = genai.get_file(video_file.name)

            if video_file.state.name != "ACTIVE":
                raise Exception(f"Video processing failed: {video_file.state.name}")

            print(f"Video ready for analysis: {video_file.name}")

            # Generate content with video
            response = self.model.generate_content([prompt, video_file])

            # Parse response
            result_text = response.text

            # Extract YAML content (simple parsing)
            if "```yaml" in result_text:
                yaml_start = result_text.find("```yaml") + 7
                yaml_end = result_text.find("```", yaml_start)
                yaml_content = result_text[yaml_start:yaml_end].strip()
            else:
                yaml_content = result_text

            return {
                "gherkin_yaml": yaml_content,
                "raw_response": result_text,
            }
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

    async def transcribe_audio(self, audio_base64: str) -> str:
        """
        Transcribe audio recording

        Args:
            audio_base64: Base64 encoded audio

        Returns:
            Transcribed text
        """
        # Remove data URL prefix if present
        if audio_base64.startswith("data:"):
            audio_base64 = audio_base64.split(",")[1]

        # Decode base64 to bytes
        audio_bytes = base64.b64decode(audio_base64)

        prompt = """
Transcribe this audio recording clearly and accurately.
Output only the transcribed text without any additional commentary.
"""

        # Upload audio for transcription
        audio_file = genai.upload_file(path=audio_bytes)

        # Generate transcription
        response = self.model.generate_content([prompt, audio_file])

        return response.text.strip()

    async def _generate_gherkin_from_text(
        self,
        title: str,
        description: str,
        request_type: str,
    ) -> dict:
        """
        Generate Gherkin from text description only (fallback for large videos)

        Args:
            title: Feature request title
            description: Feature request description
            request_type: bug, enhancement, or feature

        Returns:
            dict with 'gherkin_yaml' and 'raw_response' keys
        """
        prompt = f"""
You are a Business Analyst expert at writing Gherkin specifications (Given-When-Then format).

**Context:**
- Request Type: {request_type}
- Title: {title}
- Description: {description or "No written description provided"}

**Task:**
Based on the title and description, write a complete Gherkin feature specification.

**Output Format (YAML):**
```yaml
feature:
  title: "Feature title"
  description: "High-level description"
  scenarios:
    - scenario: "Scenario name"
      given:
        - "Context step"
      when:
        - "Action step"
      then:
        - "Expected outcome"
    - scenario: "Another scenario"
      given:
        - "Context step"
      when:
        - "Action step"
      then:
        - "Expected outcome"

analysis:
  summary: "Brief summary of the request"
  assumptions: ["Assumption 1", "Assumption 2"]
  edge_cases: ["Potential edge case 1", "Potential edge case 2"]
  technical_notes: ["Technical consideration 1", "Technical consideration 2"]
```

**Guidelines:**
- Use clear, business-friendly language
- Be specific about expected behavior
- Make reasonable assumptions based on the description
- Consider common edge cases for this type of request
- Write scenarios that are testable

**Note:** Video was provided but too large to analyze. Generated from text description only.
"""

        response = self.model.generate_content(prompt)
        result_text = response.text

        # Extract YAML content
        if "```yaml" in result_text:
            yaml_start = result_text.find("```yaml") + 7
            yaml_end = result_text.find("```", yaml_start)
            yaml_content = result_text[yaml_start:yaml_end].strip()
        else:
            yaml_content = result_text

        return {
            "gherkin_yaml": yaml_content,
            "raw_response": result_text,
        }
