from Env.js_executor import JavaScriptExecutor #class import
from Env.python_executor import PythonExecutor #class import

# to perform funciton ask whether to execute code
    

class BaseEnv:


    def __init__(self, language,code):
        self.language = language


    def execute(self):
        raise NotImplementedError("This method should be overridden by subclasses")

      
def create_environment(language):
    if language == "python":
        return PythonExecutor()
    elif language == "javascript":
        return JavaScriptExecutor()
    else:
        raise ValueError(f"Unsupported language: {language}")
    

    # def stop(self):
    #         """
    #         Stops the execution of all active languages.
    #         """        
    #         for language in self._active_languages.values():
    #             language.stop()

    # def terminate(self):
    #     """
    #     Terminates all active language environments.
    #     """        
    #     for language_name in list(self._active_languages.keys()):
    #         language = self._active_languages[language_name]
    #         if (
    #             language
    #         ):  # Not sure why this is None sometimes. We should look into this
    #             language.terminate()
    #         del self._active_languages[language_name]