import google.generativeai as gemini
def geminiInuput(user_input):
    gemini.configure(api_key="AIzaSyCSdK2F4eG_RGSJ-1w2nIMBToGLLXLCc7g")
    model=gemini.GenerativeModel("models/gemini-1.5-flash")
    response=model.generate_content(user_input)
    return response
