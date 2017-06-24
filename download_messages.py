import json
import os
import urllib2
import sys

if 'SLACK_API_KEY' not in os.environ:
    with open('.env', 'r') as f:
        for line in f.read().strip().split('\n'):
            key, value = line.split('=')
            os.environ[key] = value
TOKEN = os.environ['SLACK_API_KEY']


def slack_call(method, token, **kwargs):
    '''
    use slack api to call a method
    INPUT:
        method: string; slack method to call
        token: string; slack api key token
        additional arguments for the method in question should be passed with
        kwargs
    OUTPUT:
        dictionary; response to api call
    '''
    base_url = 'https://slack.com/api/{method}?token={token}'
    call_url = base_url.format(method=method, token=token)
    for additional_option, additional_value in kwargs.iteritems():
        call_url += '&{}={}'.format(additional_option, additional_value)

    return json.load(urllib2.urlopen(call_url))


def find_id_by_name(name, private=True):
    '''
    find the slack id number of a channel based on its name
    INPUT:
        name: string; name of channel to search for
        private: boolean [optional]; whether the channel you are looking for is
        private or public
    OUTPUT:
        string; either id or message telling you id was not found
    '''
    if private:
        key = 'groups'
    else:
        key = 'channels'
    method = '{}.list'.format(key)
    groups = slack_call(method, TOKEN)
    for entry in groups[key]:
        if entry['name'] == name:
            return entry['id']
    return 'ENTRY NOT FOUND'


def get_messages(channel_name, max_messages):
    '''
    download messages from slack channel and save them to disk as
    messages_<channel_name>.json
    INPUT:
        channel_name: string; name of channel to download
        max_messages: int or None; maximum messages to download, if None then
        all messages in channel will be downloaded
    OUTPUT:
        None
    '''
    private = True
    check_1 = find_id_by_name(channel_name, private)
    check_2 = find_id_by_name(channel_name, not private)
    if check_1 == check_2 and check_1 == 'ENTRY NOT FOUND':
        message = 'either {} does not exist or you do not have access to it'
        raise ValueError(message.format(channel_name))
    elif check_1 == 'ENTRY NOT FOUND':
        private = not private
        id_num = check_2
    else:
        id_num = check_1

    if private:
        method = 'groups.history'
    else:
        method = 'channels.history'

    next = slack_call(method, TOKEN, channel=id_num)
    messages = next['messages']

    while next['has_more']:
        if max_messages and len(messages) >= max_messages:
            messages = messages[:max_messages]
            break

        next_latest = messages[-1]['ts']
        next = slack_call(method, TOKEN,
                          channel=id_num, latest=next_latest)

        messages.extend(next['messages'])

    file_name = 'messages_{}.json'.format(channel_name)

    with open(file_name, 'w') as f:
        json.dump(messages, f)


if __name__ == '__main__':
    channel = sys.argv[1]
    if len(sys.argv) > 2:
        max_downloads = int(sys.argv[2])
    else:
        max_downloads = None
    get_messages(channel, max_downloads)
