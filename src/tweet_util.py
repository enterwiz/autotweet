import json

from requests_oauthlib import OAuth1Session


def get_request_token(consumer_key, consumer_secret):
    request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)
    fetch_response = oauth.fetch_request_token(request_token_url)
    resource_owner_key = fetch_response.get("oauth_token")
    resource_owner_secret = fetch_response.get("oauth_token_secret")
    return resource_owner_key, resource_owner_secret


def get_authorization_url(
    consumer_key, consumer_secret, resource_owner_key, resource_owner_secret
):
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
    )
    base_authorization_url = "https://api.twitter.com/oauth/authorize"
    authorization_url = oauth.authorization_url(base_authorization_url)
    return authorization_url


def get_access_token(
    consumer_key, consumer_secret, resource_owner_key, resource_owner_secret, verifier
):

    access_token_url = "https://api.twitter.com/oauth/access_token"
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier,
    )
    oauth_tokens = oauth.fetch_access_token(access_token_url)
    access_token = oauth_tokens["oauth_token"]
    access_token_secret = oauth_tokens["oauth_token_secret"]
    return access_token, access_token_secret


def upload_image_to_twitter(ckey, csecret, akey, asecret, image_path):
    twitter = OAuth1Session(
        ckey,
        client_secret=csecret,
        resource_owner_key=akey,
        resource_owner_secret=asecret,
    )

    url = "https://upload.twitter.com/1.1/media/upload.json"

    with open(image_path, "rb") as image_file:
        files = {"media": image_file}
        response = twitter.post(url, files=files)

    if response.status_code != 200:
        err = f"Failed to upload media. Status code: {response.status_code}, Response: {response.text}"
        print(err)
        raise Exception(err)

    media_id = response.json()["media_id_string"]
    print(f"Media uploaded successfully. Media ID: {media_id}")
    return media_id


def post_tweet(
    consumer_key, consumer_secret, access_token, access_token_secret, tweet, media_id=""
):
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )
    if media_id and media_id != "":
        payload = {"text": tweet, "media": {"media_ids": [media_id]}}
    else:
        payload = {"text": tweet}

    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json=payload,
    )

    if response.status_code != 201:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )

    print("Response code: {}".format(response.status_code))

    # Saving the response as JSON
    json_response = response.json()
    print(json.dumps(json_response, indent=4, sort_keys=True))
