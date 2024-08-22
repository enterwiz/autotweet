import gradio as gr

from src.appconfig import load_config, save_config
from src.twitter_util import authorization_url, fetch_access_token, fetch_request_token


def token_manage():
    with gr.Blocks() as demo:
        gr.Markdown("## Twitter账号设置")
        config = load_config()
        consumer_key = gr.Textbox(
            label="Consumer Key", value=config.get("consumer_key", "")
        )
        consumer_secret = gr.Textbox(
            label="Consumer Secret", value=config.get("consumer_secret", "")
        )
        twitter_save_btn = gr.Button("保存Twitter设置")
        get_auth_link_btn = gr.Button("获取认证链接")
        auth_url = gr.Textbox(label="认证链接", interactive=False)
        copy_link_btn = gr.Button("复制链接")
        pin_code = gr.Textbox(label="PIN码")
        get_token_btn = gr.Button("获取Token")

    # Twitter设置保存函数
    def save_twitter_settings(c_key, c_secret):
        config["consumer_key"] = c_key
        config["consumer_secret"] = c_secret
        save_config(config)
        return "Twitter设置已保存"

    # 获取认证链接函数
    def get_auth_link():
        try:
            response = fetch_request_token()
            oauth_token = response["oauth_token"]
            oauth_token_secret = response["oauth_token_secret"]
            config["oauth_token"] = oauth_token
            config["oauth_token_secret"] = oauth_token_secret
            save_config(config)
            url = authorization_url(oauth_token)
            return url
        except Exception as e:
            return f"错误：{str(e)}"

    # 获取Token函数
    def get_token(pin):
        try:
            oauth_token = config.get("oauth_token")
            oauth_token_secret = config.get("oauth_token_secret")
            if not oauth_token or not oauth_token_secret:
                return "错误：请先获取认证链接"
            response = fetch_access_token(oauth_token, oauth_token_secret, pin)
            access_token = response["oauth_token"]
            access_token_secret = response["oauth_token_secret"]
            config["access_token"] = access_token
            config["access_token_secret"] = access_token_secret
            save_config(config)
            return "获取Token成功"
        except Exception as e:
            return f"错误：{str(e)}"

    twitter_save_btn.click(
        save_twitter_settings,
        inputs=[consumer_key, consumer_secret],
        outputs=gr.Textbox(),
    )
    get_auth_link_btn.click(get_auth_link, outputs=auth_url)
    copy_link_btn.click(lambda x: x, inputs=auth_url, outputs=gr.Textbox())
    get_token_btn.click(get_token, inputs=pin_code, outputs=gr.Textbox())

    return demo
