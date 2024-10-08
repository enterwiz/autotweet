import os
import sqlite3
from datetime import datetime

import gradio as gr
from openai import OpenAI

from src.appconfig import load_access_token, load_config, load_consumer_token
from src.tweet_util import post_tweet, upload_image_to_twitter

UPLOAD_FOLDER = "uploaded_images"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

conn = sqlite3.connect("tweets.db", check_same_thread=False)
c = conn.cursor()

c.execute(
    """CREATE TABLE IF NOT EXISTS tweets
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              content TEXT,
              image_path TEXT,
              created_at TIMESTAMP,
              published_at TIMESTAMP,
              status TEXT)"""
)

STATUS_PENDING = "Pending"
STATUS_PUBLISHED = "Published"
STATUS_DELETED = "Deleted"


def getOpenAIClient():
    config = load_config()
    client = OpenAI(
        api_key=config.get("openai_api_key", ""),
        base_url=config.get("openai_api_url", ""),
    )
    return client


def getOpenAIModel():
    config = load_config()
    return config.get("openai_api_model", "")


def save_tweet(tweet_content, image):
    if len(tweet_content) > 160:
        return "Tweet内容超过160字符限制!", None

    if image is not None:
        image_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
        image.save(image_path)
    else:
        image_path = None

    c.execute(
        "INSERT INTO tweets (content, image_path, created_at, status) VALUES (?, ?, ?, ?)",
        (tweet_content, image_path, datetime.now(), STATUS_PENDING),
    )
    conn.commit()

    return "Tweet已成功保存!", get_tweets()


def publish_tweet():
    c.execute(
        "SELECT id, content, image_path FROM tweets WHERE status = ? LIMIT 1",
        (STATUS_PENDING,),
    )
    tweet = c.fetchone()
    if tweet:
        id, content, image_path = tweet
        ckey, csecret = load_consumer_token()
        akey, asecret = load_access_token()
        if not (ckey and csecret and akey and asecret):
            raise Exception("请先设置OpenAI API Key和Access Token")

        if image_path:
            absolute_path = os.path.abspath(image_path)
            media_id = upload_image_to_twitter(
                ckey, csecret, akey, asecret, absolute_path
            )
            post_tweet(ckey, csecret, akey, asecret, content, media_id)
        else:
            post_tweet(ckey, csecret, akey, asecret, content)
        c.execute(
            "UPDATE tweets SET status = ?, published_at = ? WHERE id = ?",
            (STATUS_PUBLISHED, datetime.now(), id),
        )
        conn.commit()
        return f"Tweet发布成功, ID: {id}", get_tweets()
    return "当前无Tweet待发布", get_tweets()


def get_tweets():
    c.execute(
        "SELECT id, content, image_path, created_at, published_at, status FROM tweets ORDER BY created_at DESC"
    )
    tweets = c.fetchall()
    return [
        [
            tweet[0],
            tweet[1],
            tweet[2] if tweet[2] else "无图片",
            tweet[3],
            tweet[4] if tweet[4] else "",
            tweet[5],
        ]
        for tweet in tweets
    ]


def generate_tweet(idea):
    prompt = f"基于以下想法，生成一条不超过160字的Twitter Tweet内容。如果用户未指出使用的语言，则默认使用与用户输入相同的语言：{idea}"
    client = getOpenAIClient()
    response = client.chat.completions.create(
        model=getOpenAIModel(),
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
        stream=False,
    )

    return response.choices[0].message.content.strip()


def tweet_manage():
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column(scale=1):
                with gr.Row():
                    idea_input = gr.Textbox(label="输入想法")
                    generate_btn = gr.Button("自动生成")
                tweet_content = gr.Textbox(label="Tweet内容 (最多160字符)")
                image = gr.Image(type="pil", label="上传图片 (可选)")
                submit_btn = gr.Button("Submit")
                result = gr.Textbox(label="结果")

            with gr.Column(scale=2):
                publish_btn = gr.Button("按顺序发布")
                tweet_list = gr.Dataframe(
                    headers=[
                        "序号",
                        "Tweet内容",
                        "图片链接",
                        "创建时间",
                        "发布时间",
                        "状态",
                    ],
                    datatype=["number", "str", "str", "str", "str", "str"],
                    label="已提交的Tweets",
                    value=get_tweets(),
                    interactive=False,
                )
                publish_result = gr.Textbox(label="发布结果")
                publish_btn.click(
                    publish_tweet, inputs=None, outputs=[publish_result, tweet_list]
                )

        def update_tweet_content(idea):
            generated_tweet = generate_tweet(idea)
            return generated_tweet

        generate_btn.click(
            update_tweet_content, inputs=[idea_input], outputs=[tweet_content]
        )

        submit_btn.click(
            save_tweet, inputs=[tweet_content, image], outputs=[result, tweet_list]
        )

    return demo
