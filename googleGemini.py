import google.generativeai as gemini
import json
def geminiInuput(user_input):
    with open('config.json') as f:
        config=json.load(f)
    gemini.configure(api_key=config["GOOGLE_API"])
    model=gemini.GenerativeModel("models/gemini-1.5-flash")
    response=model.generate_content(user_input)
    return response
