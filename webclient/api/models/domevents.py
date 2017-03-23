import json

DOM_EVENTS = {
    'mouse_events': [
        'click',
        'mousedown',
        'mouseup',
        'mouseover',
        'mousemove',
        'mouseout'
    ],
    'html_events': [
        'load',
        'unload',
        'abort',
        'error',
        'select',
        'change',
        'submit',
        'reset',
        'focus',
        'blur',
        'resize',
        'scroll'
    ],
    'storage_events': [
        'storage',
    ],
    'ui_events': [
        'DOMFocusIn',
        'DOMFocusOut',
        'DOMActivate'
    ]
}


def get_dom_events():
    """
    Returns list with supported DOM events
    """
    return json.dumps(DOM_EVENTS)
