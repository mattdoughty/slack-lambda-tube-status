import http
import json


LINE_COLOURS = {
    'bakerloo': '894e24',
    'central': 'dc241f',
    'circle': 'ffce00',
    'district': '007229',
    'dlr': '00afad',
    'hammersmith-city': 'd799af',
    'jubilee': '6a7278',
    'london-overground': 'e86a10',
    'metropolitan': '751056',
    'northern': '000',
    'piccadilly': '0019a8',
    'tfl-rail': '0019a8',
    'victoria': '00a0e2',
    'waterloo-city': '76d0bd',
}

STATUS_EMOJI = {
    2: ':no_entry:',  # Suspended
    3: ':no_entry:',  # Part Suspended
    6: ':bangbang:',  # Severe Delays
    9: ':warning:',  # Minor Delays
    11: ':no_entry:',  # Part Closed
    20: ':no_entry:',  # Service Closed
}


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def lambda_handler(event, context):
    conn = http.client.HTTPSConnection('api.tfl.gov.uk')
    conn.request('GET', '/Line/Mode/tube%2Cdlr%2Ctflrail%2Coverground/Status')
    response = conn.getresponse()
    content = json.loads(response.read())
    
    statuses = []
    for line in content:
        line_disruptions = []
        for status in line['lineStatuses']:
            status_code = status['statusSeverity']
            description = status['statusSeverityDescription']
            line_disruptions.append('{} {}'.format(
                STATUS_EMOJI.get(status_code, ''),
                description
            ))
        
        statuses.append({
            'color': LINE_COLOURS[line['id']],
            'text': '{}: {}'.format(line['name'], ', '.join(line_disruptions))
        })
    
    return respond(None, {
        'response_type': 'in_channel',
        'attachments': statuses
    })
