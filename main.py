from google.cloud import texttospeech
import PySimpleGUI as simpleGUI
import os.path
import genanki
import random

languageList = ['English', 'Italian', 'German']  # list of supported target language types
sourceList = list()  # holds words in source language
targetList = list()  # holds words in target language
fileList = list()  # holds filenames
input_type = None  # determines GUI type
deck_name = 'My Deck'  # name of deck and package
model_id = random.randrange(1 << 30, 1 << 31)  # unique id for anki note model
model_reverse_id = random.randrange(1 << 30, 1 << 31)  # unique id for reversed note model

# TODO: make it so card name is unique and changed per card creation
model = genanki.Model(
    model_id,
    'Simple Model',
    fields=[
        {'name': 'Question'},
        {'name': 'Answer'},
        {'name': 'Media'}
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{Question}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}<br>{{Media}}',
        },
    ])

# TODO: see note above 'model'
model_reverse = genanki.Model(
    model_reverse_id,
    'Simple Model',
    fields=[
        {'name': 'Question'},
        {'name': 'Answer'},
        {'name': 'Media'}
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{Question}}<br>{{Media}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
        },
    ])

error = "Please fix the following issues before continuing:"  # default error message

# keys for reading values from GUI elements
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
key_deck_name = "-DECK_NAME-"


def clean_list(file):
    """Is passed an open text file and returns a 'cleaned' list with blank lines removed"""
    lines = (line.rstrip() for line in file)  # All lines including the blank ones
    lines = list(line for line in lines if line)
    return lines


# the folder where the deck will be created
global output_location
# location of the txt file for source list
src_file_location = None
# location of the txt file for target list
target_file_location = None
# target language
targetLangCode = None
# source language
sourceLangCode = None

# GUI element that asks user to choose a language
languagePrompt = [
    simpleGUI.Text("Please select the languages:")
]

# GUI element that lets the user choose a language
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

# GUI button that prompts the building of the deck
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

# Deck name element

deck_name_element = \
    [
        simpleGUI.Text("Deck name:"),
        simpleGUI.Input(key=key_deck_name, enable_events=True),
    ]

# GUI element that lets the user select an output folder for the finished deck
output_element = \
    [
        simpleGUI.Text("Please select an output folder:"),
        simpleGUI.Input(key=key_output_field, enable_events=True),
        simpleGUI.FolderBrowse(key=key_output_folder, enable_events=True)
    ]

# window for file entry selection
file_entry_column = [
    output_element
    ,
    # choose file with source language words
    [
        simpleGUI.Text("Please .txt file in source language:"),
        simpleGUI.Input(key=key_src_file_field, enable_events=True),
        simpleGUI.FileBrowse(key=key_src_file_folder, enable_events=True)
    ],
    # choose file with target language words
    [
        simpleGUI.Text("Please .txt file in target language:"),
        simpleGUI.Input(key=key_target_file_field, enable_events=True),
        simpleGUI.FileBrowse(key=key_target_file_folder, enable_events=True)
    ],
    languagePrompt,
    languageSelectors,
    deck_name_element,
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
    deck_name_element,
    buildButton
]

# GUI element that contains the other elements
layout = [
    [
        simpleGUI.Column(selection_column)
    ]
]
window = simpleGUI.Window("Anki Language Learning Deck Builder", layout)


def main():
    """Reads user input, displays GUI based on chosen input type, handles GUI events"""

    # global redeclarations
    global output_location
    global src_file_location
    global target_file_location
    global targetLangCode
    global sourceLangCode
    global sourceList
    global targetList
    global layout
    global window
    global event, values
    global deck_name

    # checks chosen input type, constructs layout accordingly
    if input_type == "file":
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

    # main loop, where GUI elements are read. Calls error handling function
    while True:

        # read values from GUI elements
        event, values = window.read()

        # close window
        if event == "Exit" or event == simpleGUI.WIN_CLOSED:
            break
        if event == key_deck_name:
            deck_name = values[key_deck_name]
        if event == key_target_lang:  # A target language was chosen
            targetLangCode = values[key_target_lang]
        if event == key_source_lang:  # A source language was chosen
            sourceLangCode = values[key_source_lang]
        if event == key_output_field:  # An output folder was selected
            output_location = values[key_output_field]
        if event == key_src_file_field:  # A file for the source words was provided
            src_file_location = values[key_src_file_field]  # read file path
            file = open(src_file_location, encoding='utf-8')  # open file
            sourceList = clean_list(file)  # save lines to list with blank lines removed
        if event == key_target_file_field:  # a file for the target words was provided
            target_file_location = values[key_target_file_field]  # read file path
            file = open(target_file_location, encoding='utf-8')  # open file
            targetList = clean_list(file)  # save lines to list with blank lines removed
        if event == key_add:  # the user pressed the 'add' button
            if values[key_src_txt_input] != "" and values[key_target_txt_input] != "":  # verify both boxes have values
                sourceList.append(values[key_src_txt_input])  # add source word
                targetList.append(values[key_target_txt_input])  # add target word
            else:
                simpleGUI.popup("Please add a word to both boxes.")  # display an error to the user
        if event == key_go:  # user chooses to generate deck
            if not is_error():  # call error handling method
                # TODO: popup blocks creation of deck, stop that
                simpleGUI.popup("Please do not close this window, your deck is being generated.", title="Generating Deck...")
                create_mp3()
                create_deck()
                window.close()
                simpleGUI.popup("Deck generated!", title="Success")


def test():
    global output_location
    # input location if input from .txt. file chosen
    global src_file_location
    global target_file_location
    # target language that the card audio will be created in
    global targetLangCode
    # source language that the card
    global sourceLangCode
    global sourceList
    global targetList
    targetLangCode = 'Italian'
    sourceLangCode = 'English'
    output_location = 'C:/Users/exman/Desktop/Mp3s'
    src_file_location = 'C:/Users/exman/Desktop/source.txt'
    file = open(src_file_location, encoding='utf-8')
    sourceList = clean_list(file)
    target_file_location = 'C:/Users/exman/Desktop/target.txt'
    file = open(target_file_location, encoding='utf-8')
    targetList = clean_list(file)

    create_mp3()
    create_deck()


def is_error():
    """Verifies all necessary values are knows, or displays error popups asking the user to fix problems"""
    global src_file_location
    global target_file_location
    global targetLangCode
    global sourceLangCode
    global error

    if output_location is None:  # if an output location isn't chosen
        error += "\n - Select an output location."
    if targetLangCode is None:  # if a target language isn't selected
        error += "\n - Select a target language."
    if sourceLangCode is None:  # if a source language isn't selected
        error += "\n - Select a source language."
    if input_type == "file":  # if a source/target file isn't selected
        if src_file_location is None:
            error += "\n - Select a file with list in source langauge."
        if target_file_location is None:
            error += "\n - Select a file with list in target language."
    if error == "Please fix the following issues before continuing:":  # if no issues
        return False
    else:  # display error popup
        simpleGUI.popup(error, title="Warning")
        return True


def create_mp3():
    """Generates mp3s from list of target words using TTS"""

    # strip newline characters
    for (a, b) in zip(targetList, sourceList):
        a.strip('\n')
        a.strip()
        b.strip('\n')
        b.strip()

    # defining client for TTS
    credential_path = "crucial-cycling-313504-68e61ab8fbee.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    client = texttospeech.TextToSpeechClient()

    # creating voice variable based on target language
    if targetLangCode == "English":
        voice = texttospeech.VoiceSelectionParams(
            language_code='en-US',
            name='en-US-Wavenet-J',
            ssml_gender=texttospeech.SsmlVoiceGender.MALE)
    elif targetLangCode == "Italian":
        voice = texttospeech.VoiceSelectionParams(
            language_code='it-IT',
            name='it-IT-Wavenet-D',
            ssml_gender=texttospeech.SsmlVoiceGender.MALE)
    elif targetLangCode == "German":
        voice = texttospeech.VoiceSelectionParams(
            language_code='de-DE',
            name='de-DE-Wavenet-D',
            ssml_gender=texttospeech.SsmlVoiceGender.MALE)
    elif targetLangCode == "Japanese":
        voice = texttospeech.VoiceSelectionParams(
            language_code='ja-JP',
            name='ja-JP-Wavenet-C',
            ssml_gender=texttospeech.SsmlVoiceGender.MALE)

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    # write an mp3 for each word in target list
    for x in targetList:
        synthesis_input = texttospeech.SynthesisInput(text=x)
        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        # get path of mp3
        complete_name = (output_location + '/' + x.strip('\n').replace('/', '_').replace('?', '') + '.mp3')
        fileList.append(complete_name)  # save filenames to list

        with open(complete_name, 'wb') as out:  # write mp3s
            out.write(response.audio_content)

def create_deck():
    """Create an Anki deck with a card and a reverse card for each source/target word pair, with added mp3s"""

    # define deck with random deck_id
    deck = genanki.Deck(
        random.randrange(1 << 30, 1 << 31),
        deck_name)

    # define package which stores deck and anki files
    package = genanki.Package(deck)

    for (source, target, name) in zip(sourceList, targetList, fileList):
        package.media_files.append(name)  # add filenames of target TTS mp3s to package 'media_files' list
        media = '[sound:' + name.replace(output_location + '/', '') + ']'  # strip path from filename

        # create note according to model, with source & target words and filename for target TTS mp3
        note = genanki.Note(
            model=model,
            fields=[source, target, media]
        )

        # add note to deck
        deck.add_note(note)

    # TODO: add GUI option for letting the user choose to generate reverse cards
    # repeat previous process with reverse versions of cards
    for (source, target, name) in zip(sourceList, targetList, fileList):
        media = '[sound:' + name.replace(output_location + '/', '') + ']'
        note = genanki.Note(
            model=model_reverse,
            fields=[target, source, media]
        )
        deck.add_note(note)

    package.write_to_file(output_location + '\\' + deck_name + '.apkg')
    for file in fileList:
        os.remove(file)


# loop for first, input type prompt, GUI popup
while True:
    event, values = window.read()
    window.close()

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
