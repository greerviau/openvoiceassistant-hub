def init(config):
    pass

def hello(context):
    command = context['command']
    addr = context['addr'] if 'addr' in context else ''

    response = ''
    if 'morning' in command:
        response = f'Good morning {addr}'
    elif 'afternoon' in command:
        response = f'Good afternoon {addr}'
    elif 'evening' in command:
        response = f'Good evening {addr}'
    elif 'night' in command:
        response = f'Good night {addr}'
    else:
        response = f'Hello {addr}'
    context['response'] = response

def how_are_you(context):
    command = context['command']
    addr = context['addr'] if 'addr' in context else ''

    response = f'Doing well {addr}'
    context['response'] = response

def whats_up(context):
    command = context['command']
    addr = context['addr'] if 'addr' in context else ''

    response = f'Not much {addr}'
    context['response'] = response

def goodbye(context):
    command = context['command']
    addr = context['addr'] if 'addr' in context else ''

    response = f'Goodbye {addr}'
    context['response'] = response