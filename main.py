# img_viewer.py
from google.cloud import texttospeech
import PySimpleGUI as simpleGUI
import os.path

languageList = ['English', 'Italian', 'German', 'Japanese']
sourceList = []
targetList = []
input_type = None

key_output_folder = "-OUTPUT-"
key_output_field = "-OUTPUT_FIELD-"
key_source_lang = "-SRC LANG-"
key_target_lang = "-TARGET_LANG-"
key_go = "-GO-"
key_file = "-FILE-"
key_text = "-TEXT-"
key_confirm = "-CONFIRM-"
key_src_file_field = "-SRC_FILE_INPUT-"
key_target_file_field = "-TARGET_FILE_INPUT-"
key_src_file_folder = "-SRC_FILE-"
key_target_file_folder = "-TARGET_FILE-"
key_src_txt_input = '-SRC_INPUT-'
key_target_txt_input = '-TARGET_INPUT-'
key_add = "-ADD-"
key_exit = "-EXIT-"

# output = None
global output_location
# input location if input from .txt. file chosen
global src_file_location
global target_file_location

output_element = [simpleGUI.Text("Please select an output folder:"), simpleGUI.Input(key=key_output_field),
                  simpleGUI.FolderBrowse(
                      key=key_output_folder, enable_events=True)]
languagePrompt = [
    simpleGUI.Text("Please select the languages:")
]
languageSelectors = [
    simpleGUI.Text("Source language:"),
    simpleGUI.Combo(languageList,
                    enable_events=True,
                    size=(40, 4),
                    key=key_source_lang),
    simpleGUI.Text("Target language:"),
    simpleGUI.Combo(languageList,
                    enable_events=True,
                    size=(40, 4),
                    key=key_target_lang)
]
buildButton = [
    simpleGUI.Button("Build Deck", enable_events=True, key=key_go),
]

# Initial window selecting input method
selection_column = [
    [
        simpleGUI.Text("Please select input method:")
    ],
    [
        simpleGUI.Radio('File Upload', "RADIO1", default=True, key=key_file),
        simpleGUI.Radio('Text Entry', "RADIO1", key=key_text),

    ],
    [
        simpleGUI.Button('Confirm', key=key_confirm, enable_events=True)
    ]
]

# window for file entry selection
file_entry_column = [
    output_element
    ,
    # choose file with source language words
    [
        simpleGUI.Text("Please .txt file in source language:"),
        simpleGUI.Input(key=key_src_file_field),
        simpleGUI.FileBrowse(key=key_src_file_folder, enable_events=True)
    ],
    # choose file with target language words
    [
        simpleGUI.Text("Please .txt file in target language:"),
        simpleGUI.Input(key=key_target_file_field),
        simpleGUI.FileBrowse(key=key_target_file_folder, enable_events=True)
    ],
    languagePrompt,
    languageSelectors,
    buildButton,
]

# window for text entry selection
text_entry_column = [
    output_element,
    languagePrompt,
    languageSelectors,
    [
        simpleGUI.Text("Enter each word or phrase and its translation in the boxes below, then press 'add'.")
    ],
    [
        simpleGUI.Text("Source: "), simpleGUI.InputText(default_text="", key=key_src_txt_input, do_not_clear=False),
        simpleGUI.Text("Target: "), simpleGUI.InputText(default_text="", key=key_target_txt_input, do_not_clear=False)
    ],
    [
        simpleGUI.Button(key=key_add, auto_size_button=True, button_text="Add")
    ],
    buildButton
]


def main():
    global output_location
    # target language that the card audio will be created in
    global targetLangCode
    # source language that the card
    global sourceLangCode

    if (input_type == "file"):
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
        if event == key_target_lang:  # A target language was chosen
            targetLangCode = values[key_target_lang]
        if event == key_source_lang:  # A source language was chosen
            sourceLangCode = values[key_source_lang]
        if event == key_output_folder:  # An output folder was selected
            output_location = window[key_output_field].get()
        if event == key_src_file_folder:
            src_file_location = window[key_src_file_field].get()
        if event == key_target_file_folder:
            target_file_location = window[key_target_file_field].get()
        if event == key_add:
            if values[key_src_txt_input] != "" and values[key_target_txt_input] != "":
                sourceList.append(values[key_src_txt_input])
                targetList.append(values[key_target_txt_input])
            else:
                simpleGUI.popup("Please add a word to both boxes.")
        if event == key_go:  # user chooses to generate deck
            window.read()
            is_error()
                window.close()
                simpleGUI.popup("Deck generated!", title="Success")
                generate()
            else:
                is_error()


def  is_error():
    error = "Please fix the following issues before continuing:"
    if output_location is None:
        error += "\n - Select an output location."
    if targetLangCode is None:
        error += "\n - Select a target language."
    if sourceLangCode is None:
        error += "\n - Select a source language."
    if(input_type == "file"):
        if src_file_location is None:
            error += "\n - Select a file with list in source langauge."
        if target_file_location is None:
            error += "\n - Select a file with list in target language."

    if error == "Please fix the following issues before continuing:":
        return False
    else:
        simpleGUI.popup(error, title="Warning")


def generate():
    print(output_location)
    if targetLangCode == "" or output_location == r"":
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
        completeName = os.path.join(output_location, x.strip('\n') + ".mp3")
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

    if event == key_confirm:
        if values[key_file]:
            input_type = "file"
        if values[key_text]:
            input_type = "text"
        window.close()
        main()
    if event == key_exit or event == simpleGUI.WIN_CLOSED:
        window.close()
        break
