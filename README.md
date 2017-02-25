# Download slack messages
Script for downloading slack messages by channel

Instructions:
First get a slack api token by going [here](https://api.slack.com/docs/oauth-test-tokens) and putting it in your environment as
SLACK_API_TOKEN or create a .env file in your copy of this repo with the line:  
```bash  
SLACK_API_TOKEN=<token>  
```  
Then run `python download_messages.py <channel name> <private/public>' you can optionally add a 3rd argument specifying the number
of messages to download starting with the most recent (this was there mostly because i didn't want to download whole channels while testing).
This will create a json file with the downloaded messages, then do with that whatever you want.
