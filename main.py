# img_viewer.py
from google.cloud import texttospeech
import PySimpleGUI as simpleGUI
import os.path

languageList = ['English', 'Italian', 'German', 'Japanese']
sourceList = []
targetList = []
input_type = None
# output = None
output_element = [simpleGUI.Text("Please select an output folder:"), simpleGUI.Input(key="-OUTPUT_FIELD-"), simpleGUI.FolderBrowse(
    key="-OUTPUT-", enable_events=True)]
languageSelectors = [
        simpleGUI.Combo(languageList,
                        enable_events=True,
                        size=(40, 4),
                        key="-SRC LANG-"),

        simpleGUI.Combo(languageList,
                        enable_events=True,
                        size=(40, 4),
                        key="-TARGET LANG-")
    ]
languagePrompt = [
        simpleGUI.Text("Please select the source and target language:")
    ]
buildButton = [
        simpleGUI.Button("Build Deck", enable_events=True, key="-GO-"),
    ]


# Initial window selecting input method
selection_column = [
    [
        simpleGUI.Text("Please select input method:")
    ],
    [
        simpleGUI.Radio('File Upload', "RADIO1", default=True, key="-FILE-"),
        simpleGUI.Radio('Text Entry', "RADIO1", key="-TEXT-"),

    ],
    [
        simpleGUI.Button('Confirm', key="-CONFIRM-", enable_events=True)
    ]
]

#
file_entry_column = [
    output_element
    ,
    [
        simpleGUI.Text("Please select a .txt file:"), simpleGUI.Input(key="-FILE_INPUT-"),
        simpleGUI.FileBrowse(key="-TEXT_OUTPUT-", enable_events=True)
    ],
    languagePrompt,
    languageSelectors,
    buildButton,
]
text_entry_column = [
    output_element,
    [
        simpleGUI.InputText(key='-TEXT_INPUT')
    ],
    languageSelectors,
    [
        simpleGUI.Text("Enter the word or phrase and its translation in the boxes below, then press add.")
    ],
    [
        simpleGUI.Text("Source:"),
        simpleGUI.In(size=(25, 1), enable_events=True, key="-SOURCE-")
    ],

    [
        simpleGUI.Text("Target:"),
        simpleGUI.In(size=(25, 1), enable_events=True, key="-TARGET-")
    ],
    [
        simpleGUI.Text("", key="-ERROR-")
    ],
    [
        simpleGUI.Button(key="-ADD-", auto_size_button=True, button_text="Add"),

        simpleGUI.Button("Build Deck", enable_events=True, key="-GO-"),

    ]
]


def main():
    global output
    # target language that the card audio will be created in
    global targetLangCode
    # source language that the card
    global sourceLangCode

    # output location

    # input location if input from .txt. file chosen
    text_file_location = r""

    if(input_type == "file"):
        layout = [
            [
                simpleGUI.Column(file_entry_column)
            ]
        ]
    else:
        layout = [
            [
                simpleGUI.Column(text_entry_column)
            ]
        ]
    window = simpleGUI.Window("Anki Language Learning Deck Builder", layout)
    while True:
        event, values = window.read()
        if event == "Exit" or event == simpleGUI.WIN_CLOSED:
            break
        if event == "-TARGET LANG-":  # A target language was chosen
            targetLangCode = values["-TARGET LANG-"]
        if event == "-SRC LANG-":  # A source language was chosen
            sourceLangCode = values["-SRC LANG-"]
        if event == "-OUTPUT-": # An output folder was selected
            output = window["OUTPUT_FIELD"].get()
        if event == "-TEXT_OUTPUT":
            text_file_location = window["-FILE_INPUT"].get()
        if event == "-GO-":  # user chooses to generate deck
            window.read()
            if output is None and targetLangCode is None and sourceLangCode is None:
                window.close()
                simpleGUI.popup("Deck generated!", title="Success")
                generate()
            else:
                error()


def error():
    error = "Please fix the following issues before continuing:"
    if output == "":
        error += "\n - Output location empty."
    if targetLangCode == "":
        error += "\n - Select a target language."
    if sourceLangCode == "":
        error += "\n - Select a source language."
    simpleGUI.popup(error, title="Warning")


def generate():
    print(output)
    if targetLangCode == "" or output == r"":
        simpleGUI.popup("Please select an output location and language.", title="Warning")
        return
    credential_path = "crucial-cycling-313504-148b7392f3ca.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:/Users/exman/Downloads/crucial-cycling-313504-148b7392f3ca.json"
    # Instantiates a client

    client = texttospeech.TextToSpeechClient()
    lang = targetLangCode[0]
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
    simpleGUI.popup("Audio Files Created", title="Anki Audio Generator ")


layout = [
    [
        simpleGUI.Column(selection_column)
    ]
]
window = simpleGUI.Window("Anki Language Learning Deck Builder", layout)


while True:
    event, values = window.read()
    """
    if event == "-MANUAL-":
        window.close()
        manual()
    """
    if values['-FILE-']:
        input_type = "file"
    if values['-TEXT-']:
        input_type = "text"
    if event == "-CONFIRM-":
        window.close()
        main()
    if event == "-EXIT-" or event == simpleGUI.WIN_CLOSED:
        window.close()
        break

"""
def manual():
    layout = [
        [
            sg.Column(manual_entry_column)
        ]
    ]
    window = sg.Window("Anki Language Learning Deck Builder", layout)
    # Run the Event Loop
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        # Word added to list, display words in window
        if event == "-ADD-" and values["-SOURCE-"] != "" and values["-TARGET-"] != "":
            sourceWord = values["-SOURCE-"]
            targetWord = values["-TARGET-"]

            # check for uniqueness
            if sourceWord not in sourceList and targetWord not in targetList:
                # Add source and target words to list
                sourceList.append(sourceWord)
                targetList.append(targetWord)
                window['-ERROR-'].update("Word/phrase pair added!")
                window['-SOURCE-'].update("")
                window['-TARGET-'].update("")
            else:
                window['-ERROR-'].update("Please check your entries. Each word/phrase pair must be unique.")

        if event == "-TARGET LANG-":  # A target language was chosen
            targetLangCode = values["-TARGET LANG-"]
        if event == "-SRC LANG-":  # A source language was chosen
            sourceLangCode = values["-SRC LANG-"]
        if event == "-OUTPUT-":
            output = window["-INPUT-"].get()
        if event == "-GO-":  # user chooses to generate deck
            window.read()
            if output == "" and targetLangCode != "":
                sg.popup("Please select an output location.", title="Warning")
            if output != "" and targetLangCode == "":
                sg.popup("Please select a a target language.", title="Warning")
            if output == "" and targetLangCode == "":
                sg.popup("Please select an output location and a target language.", title="Warning")
            else:
                go()
"""
