# img_viewer.py
from google.cloud import texttospeech
import PySimpleGUI as sg
import os.path

sourceList = []
targetList = []
lang_code = ""
# First the window layout in 2 columns
output = r""
file_list_column = [
    [
        sg.Text("Source Language:"), sg.Text("                                               Target Language:")
    ],
    [
        sg.Listbox(values=["English", "Italian", "German", "Japanese"],
                   enable_events=True,
                   size=(40, 10),
                   key="-SRC LANG-"),

        sg.Listbox(values=["English", "Italian", "German", "Japanese"],
                   enable_events=True,
                   size=(40, 10),
                   key="-TARGET LANG-")
    ],
    [
        sg.Text("Enter the word and its translation in the boxes below.")
    ],
    [
        sg.Text("Source Language:"),
        sg.In(size=(25, 1), enable_events=True, key="-SOURCE-"),
    ],

    [
        sg.Text("Target Language:"),
        sg.In(size=(25, 1), enable_events=True, key="-TARGET-"),
    ],
    [
        sg.Button(key="-ADD-", auto_size_button=True, button_text="Add words"),

        sg.Button("Go", enable_events=True, key="-GO-"),

    ],
    # [
    #     sg.Listbox(
    #         values=[], enable_events=True, size=(40, 20), key="-WORD LIST-"
    #     )
    # ]
]

# For now will only show the name of the file that was chosen


# ----- Full layout -----
layout = [
    [
        sg.Column(file_list_column)
    ]
]

window = sg.Window("Anki Language Deck Generator", layout)

# Run the Event Loop
while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    # Word list file was chosen, display words in the file
    if event == "-ADD-" and values["-SOURCE-"] != "" and values["-TARGET-"] != "":
        sourceWord = values["-SOURCE-"]
        targetWord = values["-TARGET-"]
        # Add source word to list

        if sourceWord not in sourceList and targetWord not in targetList:
            sourceList.append(sourceWord)
            targetList.append(targetWord)

            # window["-WORD LIST-"].update([])
            window['-WORD LIST-'].get_list_values()
            window['-WORD LIST-'].update()

    if event == "-TARGET LANG-":  # A file was chosen from the listbox
        lang_code = values["-TARGET LANG-"]
    if event == "-GO-":
        try:
            if lang_code == "" or output == r"":
                sg.popup("Please select an output location and language.", title="Warning")
                continue
            credential_path = "crucial-cycling-313504-148b7392f3ca.json"
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
            # os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:/Users/exman/Downloads/crucial-cycling-313504-148b7392f3ca.json"
            # Instantiates a client

            client = texttospeech.TextToSpeechClient()
            lang = lang_code[0]
            voice = texttospeech.VoiceSelectionParams()
            if lang == "English":
                voice = texttospeech.VoiceSelectionParams(
                    language_code='en-US',
                    name='en-US-Wavenet-J',
                    ssml_gender=texttospeech.SsmlVoiceGender.MALE)
            elif lang == "Italian":
                voice = texttospeech.VoiceSelectionParams(
                    language_code='it-IT',
                    name='it-IT-Wavenet-D',
                    ssml_gender=texttospeech.SsmlVoiceGender.MALE)
            elif lang == "German":
                voice = texttospeech.VoiceSelectionParams(
                    language_code='de-DE',
                    name='de-DE-Wavenet-D',
                    ssml_gender=texttospeech.SsmlVoiceGender.MALE)
            elif lang == "Japanese":
                voice = texttospeech.VoiceSelectionParams(
                    language_code='ja-JP',
                    name='ja-JP-Wavenet-C',
                    ssml_gender=texttospeech.SsmlVoiceGender.MALE)

            # Select the type of audio file you want returned
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3)

            for x in list:
                synthesis_input = texttospeech.SynthesisInput(text=x)
                # Perform the text-to-speech request on the text input with the selected
                # voice parameters and audio file type
                response = client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                )
                completeName = os.path.join(output, x.strip('\n') + ".mp3")
                # The response's audio_content is binary.
                with open(completeName, 'wb') as out:
                    # Write the response to the output file.
                    out.write(response.audio_content)
            sg.popup("Audio Files Created", title="Anki Audio Generator ")
        except:
            pass

window.close()
