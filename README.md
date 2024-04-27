# Text-to-Speech Conversion Service

This Python script provides a comprehensive Text-to-Speech (TTS) conversion service, allowing users to convert text into speech with customizable settings. It is designed to work with a server that processes the TTS requests.

## Features

- Convert text to speech using specific language and speaker characteristics.
- Customizable speech settings such as temperature, speed, repetition penalty, and more.
- Ability to switch between different TTS models.
- Save output as WAV files.
- Interactive web interface using Gradio for easy use.

## Requirements

- Python 3.6 or higher
- Gradio
- Requests

## Installation

To set up the TTS service, you'll need to install the required Python libraries. You can install these libraries using pip:

```bash
pip install gradio requests
```

## Usage

### Command Line Interface

You can run the script from the command line with the following arguments:

```bash
python tts_script.py --ip <server-ip> --port <server-port> --text "Your text here" --language en --file_path <path-to-save-output> --speaker_wav <speaker-file-identifier>
```

### Using Gradio Interface

To use the interactive Gradio interface:

1. Run the script without any arguments:
   ```bash
   python tts_script.py
   ```
2. Open the displayed URL in a web browser to access the GUI.

### Arguments

- `--ip`: IP address of the TTS server (default: `127.0.0.1`).
- `--port`: Port of the TTS server (default: `8020`).
- `--text`: Text to convert to speech.
- `--language`: Language code (default: `en` for English).
- `--file_path`: Directory path where the output file will be saved (default: current directory).
- `--model`: Optional model switch.
- `--speaker_wav`: Identifier for the speaker WAV file.
- Additional TTS settings like `--temperature`, `--speed`, and more.

## Contributing

Contributions to the project are welcome. Please fork the repository and submit a pull request.


## Contact

For issues, questions, or contributions, please feel free to ask
