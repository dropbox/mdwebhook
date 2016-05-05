# Markdown Webhook

This simple example app uses webhooks to get notified of new Markdown files in Dropbox. It then converts all Markdown files it sees to HTML.

Read more about webhooks and this example on [the Dropbox developers site](https://www.dropbox.com/developers/webhooks/tutorial).

You can try the example yourself by visiting [mdwebhook.herokuapp.com](https://mdwebhook.herokuapp.com).

## Running the sample yourself

This sample was built with Heroku in mind as a target, so the simplest way to run the sample is via `foreman`:

1. Copy `.env_sample` to `.env` and fill in the values.
2. Run `pip install -r requirements.txt` to install the necessary modules.
3. Launch the app via `foreman start` or deploy to Heroku.

You can also just set the required environment variables (using `.env_sample` as a guide) and run the app directly with `python app.py`.

## Deploy on Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)
=======
You can deploy directly to Heroku with the button below. First you'll need to create an API app via the [App Console](https://www.dropbox.com/developers/apps). Make sure your app has access to files (not just datastores), and answer "Yes - My app only needs access to files it creates" to ensure your app gets created with "App folder" permissions.

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

Once you've deployed, you can easily clone the app and make modifications:

```
$ heroku clone -a new-app-name
...
$ vim index.js
$ git add .
$ git commit -m "update index.js"
$ git push heroku master
...
```
