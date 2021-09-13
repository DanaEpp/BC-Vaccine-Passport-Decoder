#!/bin/env python3

import sys
import re
import base64
import zlib
import json

SMALLEST_B64_CHAR_CODE = ord('-')
SMART_HEALTH_CARD_PREFIX = 'shc:/'

def decode(data):
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)

    return base64.urlsafe_b64decode(data)

def decode_shc(shc):
    if not shc.startswith(SMART_HEALTH_CARD_PREFIX):
        print( "Invalid SMART Health Card. Aborting." )
        sys.exit()

    # Strip "shc:/" header and break into numeric parts
    parts = re.findall( '..', shc[5:] )

    jws = ""

    # Convert to a proper base64 encoded string we can decode
    for p in parts:
        jws += chr(int(p) + SMALLEST_B64_CHAR_CODE )

    jws_parts = list(map(decode, jws.split(".")))

    # Decompress the data. Since Python doesn't support raw deflate, 
    # we use the wbits to emulate it
    passport_data = zlib.decompress(jws_parts[1], wbits=-15)

    return jws_parts[0], passport_data, jws_parts[2]

def pp_json(data):
    pretty_data = json.loads(data)
    print(json.dumps(pretty_data, indent=4, sort_keys=True))

with open( "passport.txt", "r" ) as passport:
    shc = passport.read()

passport_header, passport_data, passport_sig = decode_shc(shc)

print( "Header: ", passport_header )
pp_json(passport_data)

