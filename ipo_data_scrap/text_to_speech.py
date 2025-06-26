import pyttsx3

def text_to_audio(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    user_input = input("Enter the text you want to convert to speech: ")
    text_to_audio(user_input)
