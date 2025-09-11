import google.generativeai as gemini
import json
def geminiInuput(user_input):
    with open('config.json') as f:
        config=json.load(f)
    gemini.configure(api_key=config["GOOGLE_API"])
    model=gemini.GenerativeModel("models/gemini-1.5-flash")
    response=model.generate_content("""
    Your task is to generate a formatted output in HTML only.
    Rules:
    Do not return plain text.
    Do not include <html>, <head>, <body>, or <!DOCTYPE html>.
    Use only inline HTML tags for styling/formatting:
    <strong> for bold text
    <em> for italic text
    <u> for underline
    <br> for line breaks
    <a href="..."> for  and links must be real
    <ul>/<ol>/<li> for lists
    <p> for paragraphs
    and more...s
    If text includes keywords like "important", "note", or "warning", emphasize them with <strong> or <span style="color:red">.
    User input: """+user_input)
    return response.text
