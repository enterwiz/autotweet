import gradio as gr
from src.appconfig import load_config, save_config
from src.twitter_util import validate_cron_expression


def cron_manage():
    with gr.Blocks() as demo:
        gr.Markdown("## 自动化任务设置")
        config = load_config()
        cron_expression = gr.Textbox(
            label="任务调度Cron表达式", value=config.get("cron_expression", "")
        )
        gr.Markdown(
            "Cron表达式帮助：[点击查看Cron表达式指南](https://crontab.guru/)",
            visible=True,
        )
        submit_cron_btn = gr.Button("提交")

        def save_cron_expression(expression):
            if not expression.strip():
                return "错误：Cron表达式不能为空"
            try:
                validate_cron_expression(expression)
            except ValueError as e:
                return f"错误：无效的Cron表达式 - {str(e)}"

            config["cron_expression"] = expression
            save_config(config)
            return "Cron表达式已保存"

        submit_cron_btn.click(
            save_cron_expression, inputs=cron_expression, outputs=gr.Textbox()
        )

    return demo
