import gradio as gr

from src.appconfig import load_config, save_config


def openai_manage():
    with gr.Blocks() as demo:
        gr.Markdown("## OpenAI设置")
        config = load_config()
        openai_api_key = gr.Textbox(
            label="OpenAI API Key", value=config.get("openai_api_key", "")
        )
        openai_api_url = gr.Textbox(
            label="OpenAI API URL", value=config.get("openai_api_url", "")
        )
        openai_api_model = gr.Textbox(
            label="OpenAI API Model", value=config.get("openai_api_model", "")
        )
        openai_save_btn = gr.Button("保存OpenAI设置")

        def save_openai_settings(api_key, api_url, api_model):
            config["openai_api_key"] = api_key
            config["openai_api_url"] = api_url
            config["openai_api_model"] = api_model
            save_config(config)
            return "OpenAI设置已保存"

        openai_save_btn.click(
            save_openai_settings,
            inputs=[openai_api_key, openai_api_url, openai_api_model],
            outputs=gr.Textbox(),
        )

    return demo
