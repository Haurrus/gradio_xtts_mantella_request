import argparse
import gradio as gr
import requests
import os
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(description='Text-to-Speech Conversion')
    parser.add_argument('--ip', default='127.0.0.1', help='IP address of the server.')
    parser.add_argument('--port', default=8020, type=int, help='Port of the server.')
    parser.add_argument('--text', required=True, help='Text to convert to speech.')
    parser.add_argument('--language', default='en', help='Language code of the text (e.g., "en" for English).')
    parser.add_argument('--file_path', default='.', help='Path where the output file will be saved.')
    parser.add_argument('--model', default=None, help='Model to switch to. If blank, no model switch is attempted.')
    parser.add_argument('--speaker_wav', required=True, help='Identifier for the speaker WAV file.')
    parser.add_argument('--temperature', type=float, default=0.75, help='TTS temperature setting.')
    parser.add_argument('--length_penalty', type=float, default=1.0, help='TTS length penalty setting.')
    parser.add_argument('--repetition_penalty', type=float, default=5.0, help='TTS repetition penalty setting.')
    parser.add_argument('--top_k', type=int, default=50, help='TTS top_k setting.')
    parser.add_argument('--top_p', type=float, default=0.85, help='TTS top_p setting.')
    parser.add_argument('--speed', type=float, default=1.0, help='TTS speed setting.')
    parser.add_argument('--enable_text_splitting', type=bool, default=True, help='Flag to enable or disable text splitting.')
    parser.add_argument('--stream_chunk_size', type=int, default=100, help='Stream chunk size for TTS.')
    return parser.parse_args()



last_settings = None
last_model = None

def send_model_switch_request(ip, port, model_name):
    switch_model_url = f'http://{ip}:{port}/switch_model'
    requests.post(switch_model_url, json={"model_name": model_name})
    print("Model switched to:", model_name)

def send_tts_request(ip, port, text, language, speaker_wav):
    tts_url = f'http://{ip}:{port}/tts_to_audio/'
    data = {
        "text": text,
        "language": language,
        "speaker_wav": speaker_wav
    }
    response = requests.post(tts_url, json=data)
    return response.content

def send_tts_settings_request(ip, port, settings):
    settings_url = f'http://{ip}:{port}/set_tts_settings'
    response = requests.post(settings_url, json=settings)
    return response.json()

def tts_convert(ip, port, text, language, file_path, speaker_wav, model,
                temperature=0.75, length_penalty=1.0, repetition_penalty=5.0, top_k=50, top_p=0.85,
                speed=1.0, enable_text_splitting=True, stream_chunk_size=100):
    global last_model
    global last_settings
    settings = {
        "temperature": temperature,
        "length_penalty": length_penalty,
        "repetition_penalty": repetition_penalty,
        "top_k": top_k,
        "top_p": top_p,
        "speed": speed,
        "enable_text_splitting": enable_text_splitting,
        "stream_chunk_size": stream_chunk_size
    }

    if model != last_model and model != None:
        send_model_switch_request(ip, port, model)
        last_model = model
    if settings != last_settings and settings != None:
        send_tts_settings_request(ip, port, settings)
        last_settings = settings

    content = send_tts_request(ip, port, text, language, speaker_wav)
    file_saved_path = save_to_file(content, file_path)
    return file_saved_path, content  # Return both the path and the content

def save_to_file(content, file_path, file_name="output.wav"):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    full_file_path = os.path.join(file_path, file_name)
    with open(full_file_path, 'wb') as file_output:
        file_output.write(content)
    return full_file_path

def get_models(ip, port):
    url = f'http://{ip}:{port}/get_models_list'
    response = requests.get(url)
    return response.json() if response.status_code == 200 else []

def get_speakers(ip, port):
    url = f'http://{ip}:{port}/speakers_list'
    response = requests.get(url)
    speakers_json = response.json() if response.status_code == 200 else {}
    # Create a simple dictionary with language keys and list of speaker names as values
    return {lang: details['speakers'] for lang, details in speakers_json.items()}


def create_gradio_interface():
    default_ip = '127.0.0.1'
    default_port = 8020

    with gr.Blocks() as interface:
        ip = gr.Textbox(label="IP Address", value=default_ip)
        port = gr.Number(label="Port", value=default_port)
        load_button = gr.Button("Load Models and Speakers")
        text = gr.TextArea(label="Text to Convert")
        language = gr.Dropdown(label="Language", choices=[], interactive=False)
        speaker = gr.Dropdown(label="Speaker", choices=[], interactive=False, allow_custom_value=True)
        model = gr.Dropdown(label="Model (optional)", choices=[], interactive=False)
        file_path = gr.Textbox(label="Directory to Save Output", value=".")
        
        # TTS Settings Sliders
        temperature = gr.Slider(minimum=0.0, maximum=1.0, value=0.75, label="Temperature")
        length_penalty = gr.Slider(minimum=0.0, maximum=2.0, value=1.0, label="Length Penalty")
        repetition_penalty = gr.Slider(minimum=1.0, maximum=10.0, value=5.0, label="Repetition Penalty")
        top_k = gr.Slider(minimum=0, maximum=100, value=50, label="Top K")
        top_p = gr.Slider(minimum=0.0, maximum=1.0, value=0.85, label="Top P")
        speed = gr.Slider(minimum=0.5, maximum=2.0, value=1.0, label="Speed")
        enable_text_splitting = gr.Checkbox(value=True, label="Enable Text Splitting")
        stream_chunk_size = gr.Number(value=100, label="Stream Chunk Size")
        
        submit_button = gr.Button("Convert", interactive=False)
           
        def load_model(ip, port):
            models = get_models(ip, port)
            model.choices = models
            model.interactive = True
            return gr.Dropdown(choices=models, interactive=True)
            
        def load_language(ip, port):
            global speakers_data
            speakers_data = get_speakers(ip, port)
            language_choices = list(speakers_data.keys())
            return gr.Dropdown(choices=language_choices, value=language_choices[0] if language_choices else None, interactive=True)
            
        def make_interactive():
            return gr.Dropdown(interactive=True)

        def update_speakers(language, speakers_data):
            # Fetch speakers based on selected language
            new_speakers = speakers_data.get(language, [])
            # Update the speaker Dropdown directly
            return gr.Dropdown(choices=new_speakers, value=None, interactive=True)

        load_button.click(
            fn=load_model,
            inputs=[ip, port],
            outputs=[model]
        )
        
        load_button.click(
            fn=load_language,
            inputs=[ip, port],
            outputs=[language]
        )
        
        load_button.click(
            fn=make_interactive,
            inputs=[],
            outputs=[submit_button]
        )
        
        load_button.click(
            fn=make_interactive,
            inputs=[],
            outputs=[temperature]
        )        
        
        load_button.click(
            fn=make_interactive,
            inputs=[],
            outputs=[length_penalty]
        )

        load_button.click(
            fn=make_interactive,
            inputs=[],
            outputs=[repetition_penalty]
        )

        load_button.click(
            fn=make_interactive,
            inputs=[],
            outputs=[top_k]
        )

        load_button.click(
            fn=make_interactive,
            inputs=[],
            outputs=[top_p]
        )

        load_button.click(
            fn=make_interactive,
            inputs=[],
            outputs=[speed]
        )

        load_button.click(
            fn=make_interactive,
            inputs=[],
            outputs=[enable_text_splitting]
        )

        load_button.click(
            fn=make_interactive,
            inputs=[],
            outputs=[stream_chunk_size]
        )


        # And the event handler for the language change
        language.change(fn=lambda x: update_speakers(x, speakers_data), inputs=[language], outputs=[speaker])
        
        submit_button.click(
            fn=lambda ip, port, text, language, model, speaker, file_path, temperature=None, length_penalty=None, repetition_penalty=None, top_k=None, top_p=None, speed=None, enable_text_splitting=None, stream_chunk_size=None: tts_convert(
                ip, port, text, language, file_path, speaker, model,
                temperature=temperature, length_penalty=length_penalty, repetition_penalty=repetition_penalty,
                top_k=top_k, top_p=top_p, speed=speed,
                enable_text_splitting=enable_text_splitting, stream_chunk_size=stream_chunk_size
            ),
            inputs=[ip, port, text, language, model, speaker, file_path,
                    temperature, length_penalty, repetition_penalty, top_k, top_p, speed, enable_text_splitting, stream_chunk_size],
            outputs=[gr.Textbox(label="Path where the file is saved"), gr.Audio(label="Audio Output", type="filepath")]
        )

    return interface

if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = parse_arguments()
        # Call tts_convert with all necessary arguments
        result_path, content = tts_convert(
            args.ip, args.port, args.text, args.language, args.file_path, args.speaker_wav, args.model,
            args.temperature, args.length_penalty, args.repetition_penalty, args.top_k, args.top_p,
            args.speed, args.enable_text_splitting, args.stream_chunk_size
        )
        print(f"Audio file saved to: {result_path}")
    else:
        gradio_ui = create_gradio_interface()
        gradio_ui.launch(inbrowser=True)
