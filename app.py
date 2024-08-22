import gradio as gr

from src.cron_manage import cron_manage
from src.openai_manage import openai_manage
from src.token_manage import token_manage
from src.tweet_manage import tweet_manage

with gr.Blocks() as demo:
    gr.Markdown("# 定时发送Tweet工具")
    with gr.Tabs():
        with gr.TabItem("Tweet管理"):
            tweet_manage()
        with gr.TabItem("OpenAI设置"):
            openai_manage()
        with gr.TabItem("Twitter账号设置"):
            token_manage()
        with gr.TabItem("Cron任务设置"):
            cron_manage()

demo.launch()
