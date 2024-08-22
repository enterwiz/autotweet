import gradio as gr

from src.tweet_util import get_access_token, get_authorization_url, get_request_token
from src.appconfig import (
    load_consumer_token,
    load_request_token,
    save_access_token,
    save_consumer_token,
    save_request_token,
)


def token_manage():
    with gr.Blocks() as demo:
        gr.Markdown("## Twitter账号设置")
        ckey, csecret = load_consumer_token()
        consumer_key = gr.Textbox(label="Consumer Key", value=ckey)
        consumer_secret = gr.Textbox(label="Consumer Secret", value=csecret)
        twitter_save_btn = gr.Button("保存Consumer Token")

        def save_twitter_settings(c_key, c_secret):
            save_consumer_token(c_key, c_secret)
            return "Consumer Token已保存"

        twitter_save_btn.click(
            save_twitter_settings,
            inputs=[consumer_key, consumer_secret],
            outputs=gr.Textbox(),
        )

        get_auth_link_btn = gr.Button("获取认证链接")

        def get_auth_link():
            try:
                ckey, csecret = load_consumer_token()
                rkey, rsecret = get_request_token(ckey, csecret)
                save_request_token(rkey, rsecret)
                url = get_authorization_url(
                    consumer_key, consumer_secret, rkey, rsecret
                )
                return url
            except Exception as e:
                return f"错误：{str(e)}"

        auth_url = gr.Textbox(label="认证链接", interactive=False)
        get_auth_link_btn.click(get_auth_link, outputs=auth_url)

        pin_code = gr.Textbox(label="PIN码")
        get_token_btn = gr.Button("获取Token")

        def get_token(pin):
            try:
                ckey, csecret = load_consumer_token()
                rkey, rsecret = load_request_token()
                if not rkey or not rsecret:
                    return "错误：请先获取认证链接"
                akey, asecret = get_access_token(ckey, csecret, rkey, rsecret, pin)
                save_access_token(akey, asecret)
                return "获取Access Token成功"
            except Exception as e:
                return f"错误：{str(e)}"

        get_token_btn.click(get_token, inputs=pin_code, outputs=gr.Textbox())

    return demo
