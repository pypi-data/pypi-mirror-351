# from .base_executor import BaseExecutor

# class PythonExecutor():
#     def execute(self, code: str) -> str:
#         """Executes Python code and returns the result or an error message."""

#         # if not self.validate_code(code):
#         #     return "Code validation failed: Unsafe code detected."

#         local_vars = {}
#         try:
#             exec(code, {}, local_vars)  # Execute code in an isolated environment
#             return local_vars.get("output", "Code executed successfully.")
#         except Exception as e:
#             # return self.handle_error(e)
#             print("error in running python code", e)

import subprocess
import tempfile
import os
from typing import Dict
import textwrap
import sys

class PythonExecutor:
    def __init__(self):
        self.forbidden_terms = [
            'import os', 'import sys', 'import subprocess',
            'open(', 'exec(', 'eval(',
        ]

    def basic_code_check(self, code: str) -> bool:
        """Simple check for potentially dangerous code"""
        code_lower = code.lower()
        return not any(term.lower() in code_lower for term in self.forbidden_terms)

    def execute(self, code: str) -> Dict[str, str]:
        """Executes Python code in a separate process and returns the result"""
        
        # Basic safety check
        if not self.basic_code_check(code):
            return {
                'success': False,
                'output': 'Error: Code contains potentially unsafe operations. You can try and use tools to achieve same functionality.',
                'error': 'Security check failed'
            }

        # Create a temporary file to store the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Properly indent the code to fit inside the try block
            indented_code = textwrap.indent(code, '    ')
            # Wrap the indented code to capture output
            wrapped_code = f"""
try:
{indented_code}
except Exception as e:
    print(f"Error: {{str(e)}}")
"""
            f.write(wrapped_code)
            temp_file = f.name

        try:
            # Execute the code in a subprocess
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )

            return {
                'success': result.returncode == 0,
                'output': result.stdout if result.returncode == 0 else result.stderr,
                'error': result.stderr if result.returncode != 0 else ''
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': 'Execution timed out after 30 seconds',
                'error': 'Timeout error'
            }
        except Exception as e:
            return {
                'success': False,
                'output': f'Error: {str(e)}',
                'error': str(e)
            }
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_file)
            except:
                pass  # Ignore cleanup errors
    

