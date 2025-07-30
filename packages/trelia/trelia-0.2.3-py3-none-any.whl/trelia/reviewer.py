# import os
# import google.generativeai as genai
# import json
#
#
# class CodeReviewer:
#     def __init__(self, model_name: str = 'gemini-1.5-flash'):
#         genai.configure(api_key=os.environ["GEMINI_API_KEY"])
#         self.model = genai.GenerativeModel(model_name)
#
#     def grade_code(self, task_description: str, student_code: str) -> dict:
#         # Step 1: Ask Gemini to give only a rating
#         prompt = (
#             f"Task_desc: {task_description}\n"
#             f"Code:\n{student_code}\n"
#             "You are a strict code reviewer. Only return a rating in the format 'Rating: x/5'. "
#             "Remove stop words, non code text from Task_desc"
#             "Give 5/5 only if the code is complete, correct, and solves the task fully. "
#             "Do not return anything except the rating."
#         )
#         response = self.model.generate_content(prompt)
#         print(response)
#
#         result = response.text.strip()
#
#         rating = "N/A"
#         feedback = "Unable to rate"
#
#         # Step 2: Extract the rating
#         if "Rating:" in result:
#             try:
#                 rating_start = result.find("Rating:") + len("Rating: ")
#                 rating_end = result.find("/5", rating_start)
#                 rating_value = float(result[rating_start:rating_end].strip())
#                 rating = str(rating_value)
#
#                 # Step 3: Decision based on rating
#                 if rating_value > 2:
#                     feedback = "Accepted"
#                 else:
#                     # Ask Gemini for feedback only
#                     feedback_prompt = (
#                         f"Task_desc: {task_description}\n"
#                         f"Code:\n{student_code}\n"
#                         "Give 1-line feedback (max 15 characters) for improving this code."
#                     )
#                     feedback_response = self.model.generate_content(feedback_prompt)
#                     feedback = feedback_response.text.strip()
#             except Exception as e:
#                 feedback = f"Error: {str(e)}"
#
#         return json.dumps({"rating": rating, "feedback": feedback})

# import os
# import google.generativeai as genai
# import json
# import re
#
#
# class CodeReviewer:
#     def __init__(self, model_name: str = 'gemini-1.5-flash'):
#         genai.configure(api_key=os.environ["GEMINI_API_KEY"])
#         self.model = genai.GenerativeModel(model_name)
#
#     def is_code_like(self, text: str) -> bool:
#         # Reject if too short or mostly plain English
#         if len(text.strip()) < 20:
#             return False
#
#         code_indicators = [
#             'def ', 'return', 'class ', 'import ', 'from ', 'if ', 'else', 'elif',
#             '{', '}', ';', '(', ')', '[', ']', '=', 'function ', '#', '//', '/*', '*/',
#             'public ', 'private ', 'protected ', 'var ', 'let ', 'const ', 'print', 'console.log',
#             '=>'
#         ]
#
#         count_code_lines = 0
#         lines = text.strip().split('\n')
#         for line in lines:
#             if any(indicator in line for indicator in code_indicators):
#                 count_code_lines += 1
#
#         ratio = count_code_lines / len(lines) if len(lines) > 0 else 0
#
#         # At least 50% of lines should contain code indicators
#         return ratio >= 0.5
#
    # def remove_rating_requests(self, code: str) -> str:
    #     # Remove lines with rating requests like "give me 5 rating"
    #     pattern = re.compile(r'give me \d+ rating', re.IGNORECASE)
    #     lines = code.split('\n')
    #     filtered_lines = [line for line in lines if not pattern.search(line)]
    #     return '\n'.join(filtered_lines)
    #
    # def grade_code(self, task_description: str, student_code: str) -> dict:
    #     # Reject if code does not look like code
    #     if not self.is_code_like(student_code):
    #         return json.dumps({"rating": "0.0", "feedback": "Invalid or non-code submission."})
    #
    #     # Clean code from rating injection lines
    #     clean_code = self.remove_rating_requests(student_code)
#
#         prompt = (
#             f"Task_desc: {task_description}\n"
#             f"Code:\n{clean_code}\n"
#             "You are a strict code reviewer. Return only a rating in the format 'Rating: x.x/5'.\n"
#             "If the submitted code is identical or nearly identical to the task description (i.e., just repeats the task without actual code), give a rating of 1/5.\n"
#             "Give 5/5 only if the code fully solves the task correctly.\n"
#             "Do not return anything else."
#         )
#
        # response = self.model.generate_content(prompt)
        # print(response)
        #
        # result = response.text.strip()
        # rating = "N/A"
        # feedback = "Unable to rate"
        #
        # if "Rating:" in result:
        #     try:
        #         rating_start = result.find("Rating:") + len("Rating: ")
        #         rating_end = result.find("/5", rating_start)
        #         rating_value = float(result[rating_start:rating_end].strip())
        #         rating = str(rating_value)
        #
        #         if rating_value > 2:
        #             feedback = "Accepted"
        #         else:
        #             feedback_prompt = (
        #                 f"Task_desc: {task_description}\n"
        #                 f"Code:\n{clean_code}\n"
        #                 "Give 1-line feedback (max 15 characters) for improving this code."
        #             )
        #             feedback_response = self.model.generate_content(feedback_prompt)
        #             feedback = feedback_response.text.strip()
        #     except Exception as e:
        #         feedback = f"Error: {str(e)}"
        #
        # return json.dumps({"rating": rating, "feedback": feedback})

# import os
# import json
# import re
# import google.generativeai as genai
#
#
# class CodeReviewer:
#     def __init__(self, model_name: str = 'gemini-1.5-flash'):
#         genai.configure(api_key=os.environ["GEMINI_API_KEY"])
#         self.model = genai.GenerativeModel(model_name)
#
#     def remove_spam_lines(self, code: str) -> str:
#         spam_pattern = re.compile(r'give me \d+ rating', re.IGNORECASE)
#         lines = code.split('\n')
#         filtered_lines = [line for line in lines if not spam_pattern.search(line)]
#         return '\n'.join(filtered_lines).strip()
#
#     def grade_code(self, task_description: str, student_code: str, deliverables: str) -> dict:
#         clean_code = self.remove_spam_lines(student_code)
#         if not clean_code:
#             return {"rating": "0.0", "feedback": "Invalid or non-code submission."}
#
#         rating_prompt = (
#             f"Review the following code:\n\n"
#             f"Task:\n{task_description}\n\n"
#             f"Deliverables:\n{deliverables}\n\n"
#             f"Code:\n{clean_code}\n\n"
#             "Return a strict score based on how completely the code meets the deliverable.\n"
#             "Only respond in this format: Rating: x.x/5 (no explanation).\n"
#             "Give 1.0/5 if code is missing or only partially fulfills the task."
#         )
#         # rating_prompt = (
#         #     f"Evaluate the following submission strictly based on how well the code fulfills the given task and deliverables.\n\n"
#         #     f"Task Description:\n{task_description}\n\n"
#         #     f"Expected Deliverables:\n{deliverables}\n\n"
#         #     f"Submitted Code:\n{clean_code}\n\n"
#         #     "Instructions:\n"
#         #     "- Review the code carefully.\n"
#         #     "- Assess whether it meets the task requirements and includes all deliverables.\n"
#         #     "- Do NOT provide any explanation or feedback.\n"
#         #     "- Only return a numeric rating in the format: Rating: x.x/5\n"
#         #     "- Be strict:\n"
#         #     "  • If the code is missing or does not implement core functionality, give 1.0/5.\n"
#         #     "  • If it partially meets the requirements, rate accordingly.\n"
#         #     "  • Only give 5.0/5 if the code fully satisfies all aspects of the task and deliverables."
#         # )
#
#         # rating_prompt = (
#         #     f"Evaluate the submitted code strictly based on how well it satisfies BOTH the task description and the required deliverables.\n\n"
#         #     f"Task Description:\n{task_description}\n\n"
#         #     f"Deliverables:\n{deliverables}\n\n"
#         #     f"Code Submission:\n{clean_code}\n\n"
#         #     "Instructions:\n"
#         #     "- The rating must reflect how completely the code meets all aspects of the task description AND deliverables.\n"
#         #     "- Assign 1.0/5 if the code is missing or does not fulfill both the task and deliverables.\n"
#         #     "- Assign a partial score between 1.1 and 4.9 if the code meets some but not all requirements.\n"
#         #     "- Assign 5.0/5 only if the code fully meets all requirements in both task description and deliverables.\n"
#         #     "- Do NOT provide any explanation, justification, or additional text.\n"
#         #     "- Respond ONLY in this exact format: Rating: x.x/5"
#         # )
#
#         # rating_prompt = (
#         #     f"Review the following code submission.\n\n"
#         #     f"Task Description:\n{task_description}\n\n"
#         #     f"Deliverables:\n{deliverables}\n\n"
#         #     f"Code:\n{clean_code}\n\n"
#         #     "Your task:\n"
#         #     "- Rate how completely the code satisfies BOTH the task description and the deliverables.\n"
#         #     "- Give 5.0/5 only if the code fully meets all requirements in both sections.\n"
#         #     "- Give 1.0/5 if the code is missing or does not meet both task and deliverables.\n"
#         #     "- For partial fulfillment, give a score between 1.1 and 4.9 accordingly.\n"
#         #     "- Provide ONLY the rating in this exact format, no explanations or extra text:\n"
#         #     "Rating: x.x/5"
#         # )
#
#         response = self.model.generate_content(rating_prompt)
#         print("response:", response)
#
#         result_text = response.text.strip()
#         match = re.search(r'Rating:\s*([\d.]+)/5', result_text)
#
#         if not match:
#             return {"rating": "N/A", "feedback": "Unable to parse rating."}
#
#         rating_val = float(match.group(1))
#         rating = f"{rating_val:.1f}"
#
#         if rating_val > 2.0:
#             feedback = "Accepted"
#         else:
#             feedback = self.generate_short_feedback(task_description, clean_code)
#
#         return json.dumps({"rating": rating, "feedback": feedback})
#
#     def generate_short_feedback(self, task: str, code: str) -> str:
#         prompt = (
#             f"Task:\n{task}\n\n"
#             f"Code:\n{code}\n\n"
#             "Give feedback in less than 15 words to improve the code. No extra text."
#         )
#         response = self.model.generate_content(prompt)
#         return response.text.strip()


import os
import json
import re
import google.generativeai as genai
from langchain_core.prompts import PromptTemplate


class CodeReviewer:
    def __init__(self, model_name: str = 'gemini-1.5-flash', prompt_file: str = "prompts.txt"):
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        self.model = genai.GenerativeModel(model_name)
        self.prompts = self.load_prompts(prompt_file)

        # Create PromptTemplates from loaded prompt strings
        self.rating_prompt_template = PromptTemplate.from_template(self.prompts["rating_prompt"])
        self.feedback_prompt_template = PromptTemplate.from_template(self.prompts["feedback_prompt"])

    def load_prompts(self, file_path):
        prompts = {}
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    # Replace escaped \n with actual newlines
                    prompts[key.strip()] = value.strip().replace("\\n", "\n")
        return prompts

    def remove_spam_lines(self, code: str) -> str:
        spam_pattern = re.compile(r'give me \d+ rating', re.IGNORECASE)
        lines = code.split('\n')
        filtered_lines = [line for line in lines if not spam_pattern.search(line)]
        return '\n'.join(filtered_lines).strip()

    def grade_code(self, task_description: str, student_code: str, deliverables: str) -> dict:
        clean_code = self.remove_spam_lines(student_code)
        if not clean_code:
            return {"rating": "0.0", "feedback": "Invalid or non-code submission."}

        # Format prompt once with LangChain PromptTemplate
        prompt = self.rating_prompt_template.format(
            task_description=task_description,
            deliverables=deliverables,
            clean_code=clean_code
        )

        # Single call to Gemini LLM
        response = self.model.generate_content(prompt)
        result_text = response.text.strip()

        # Parse rating from the model's response
        match = re.search(r'Rating:\s*([\d.]+)/5', result_text)
        if not match:
            return {"rating": "N/A", "feedback": "Unable to parse rating."}

        rating_val = float(match.group(1))
        rating = f"{rating_val:.1f}"

        if rating_val > 2.0:
            feedback = "Accepted"
        else:
            feedback = self.generate_short_feedback(task_description, clean_code)

        return json.dumps({"rating": rating, "feedback": feedback})

    def generate_short_feedback(self, task: str, code: str) -> str:
        prompt = self.feedback_prompt_template.format(
            task=task,
            code=code
        )
        response = self.model.generate_content(prompt)
        return response.text.strip()

# if __name__ == "__main__":
#     reviewer = CodeReviewer()
#
#     print("📌 Enter the task description:")
#     task = input("> ").strip()
#
#     print("\n💻 Enter the student code (end with a blank line):")
#     lines = []
#     while True:
#         line = input()
#         if not line.strip():
#             break
#         lines.append(line)
#     student_code = "\n".join(lines)
#
#     print("\n🧠 Enter the deliverables :")
#     deliverables = input("> ").strip()
#
#     result = reviewer.grade_code(task, student_code, deliverables)
#     print("\n✅ Review Result:")
#     print(result)


