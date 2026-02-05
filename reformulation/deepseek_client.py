import requests
import json
import re
import time
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class DeepSeekClient:
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.max_retries = 5
        self.timeout = 120
    
    def _clean_json_string(self, text: str) -> str:
        """Nettoie le JSON malformé"""
        # Fix common issues
        text = text.strip()
        
        # Remove trailing commas
        text = re.sub(r',(\s*[}\]])', r'\1', text)
        
        # Fix unclosed strings (basic attempt)
        lines = text.split('\n')
        fixed_lines = []
        
        for line in lines:
            if '"content":' in line and line.count('"') % 2 != 0:
                # Odd number of quotes, try to close
                if not line.rstrip().endswith('"'):
                    line = line.rstrip() + '"'
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def reformulate(self, content: str, system_prompt: str) -> Optional[Dict]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            "temperature": 0.7,
            "response_format": {"type": "json_object"}
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        content_text = data["choices"][0]["message"]["content"]
                        
                        # Try direct parsing first
                        try:
                            return json.loads(content_text)
                        except json.JSONDecodeError:
                            # Try cleaning
                            cleaned = self._clean_json_string(content_text)
                            try:
                                return json.loads(cleaned)
                            except json.JSONDecodeError as e:
                                logger.warning(f"JSON parsing failed even after cleaning: {e}")
                                
                                # Retry with new request
                                if attempt < self.max_retries - 1:
                                    logger.info("Retrying with new request...")
                                    time.sleep(3)
                                    continue
                                return None
                                
                    except (KeyError, IndexError) as e:
                        logger.error(f"Invalid response structure: {e}")
                        return None
                
                elif response.status_code == 429:
                    wait_time = (attempt + 1) * 10
                    logger.warning(f"Rate limited, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                
                elif response.status_code == 401:
                    logger.error("Invalid API key")
                    return None
                
                else:
                    logger.error(f"API error {response.status_code}")
                    if attempt < self.max_retries - 1:
                        time.sleep(5)
                        continue
                    return None
                    
            except requests.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(5)
                    
            except requests.RequestException as e:
                logger.error(f"Network error: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(5)
                    
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return None
        
        logger.error("Max retries reached")
        return None

