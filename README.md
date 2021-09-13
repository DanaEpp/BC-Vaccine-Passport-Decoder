# BC Vaccine Passport Decoder

## Introduction

The province of British Columbia is launching a new Vaccine Passport on September 13th, 2021. This research is a personal project to see if I can reverse engineer the passport and figure out what information it provides. The notes in this README are only rough notes as I review this. 

Feel free to use it however you like. *But don't be evil.*

Suggestions, feedback and corrections on anything I have gotten wrong are always welcome. Open an issue anytime or submit a pull request. 

## Reverse Engineering the Passport
The passport is really nothing more than a QR code. The first step is to figure out what the QR code represents. A simple QR code scanner shows us it pops up some data that starts with *shc:/*.

A simple search on DuckDuckGo points me to the fact that **shc:/** is a protocol spec for the [SMART Health Cards Framework](https://smarthealth.cards/). It ends up they have link right on the home page to their [specs here](https://spec.smarthealth.cards/).

Looking at it, the framework is based on [W3C Verifiable Credentials](https://w3c.github.io/vc-data-model/). That's an open standard I am more familiar with, which is a good sign.

Looking around, I found a [great article](https://www.eff.org/deeplinks/2021/06/decoding-californias-new-digital-vaccine-records-and-potential-dangers) by the EFF on digital vaccine records with QR codes, and their risks as seen by the use of SHC in California.

Reading the EFF article and referencing the [SHC protocol details](https://spec.smarthealth.cards/#protocol-details), we know that the SHC is nothing more than a JWS encoded payload (via base64URL encoding) that is minified (white space removed), compressed, and signed according to specifications by a health authority.

I wrote a function called `decode_shc()` that does all that work. If you feed it a raw SHC it should spit out a clean Health Card JWS. I've included the example SHC passport from the specs to use as a base line for testing. I've tested it against several real BC Vaccine Passport QR codes with the same success.

The decoded data allows us to see:
- Date when the Vaccine Passport was issued
- Date of Birth
- Family (Last) Name
- Given (First) Name(s)
- Where a vaccine was given from
- What vaccine was given
- What lot number the vaccine was from
- When the vaccine was given

The data payload also includes information about the issuer. This is always from *https://smarthealthcard.phsa.ca/v1/issuer*. From the specs, this means we fetch the signing key data for JWKS at *https://smarthealthcard.phsa.ca/v1/issuer/.well-known/jwks.json*. Sure enough, it's there:

```json
{
  "keys": [
    {
      "kty": "EC",
      "kid": "XCqxdhhS7SWlPqihaUXovM_FjU65WeoBFGc_ppent0Q",
      "use": "sig",
      "alg": "ES256",
      "crv": "P-256",
      "x": "xscSbZemoTx1qFzFo-j9VSnvAXdv9K-3DchzJvNnwrY",
      "y": "jA5uS5bz8R2nxf_TU-0ZmXq6CKWZhAG1Y4icAx8a9CA"
    }
  ]
}
```

This is how their app is able to verify the passports offline. By knowing the public key information they can verify the digital signature of the SMART Health Card JWS. 

## TODO
- Need to convert the JSON pretty print to human readable extractor
- Need to build a lookup table of the vaccine codes and make that human readable using the data from the Canadian Vaccine Catalog
- Need to work out the JWS signatures
- Need to test if the app BC issued in the app store properly looks at signatures. Example vulns in JWS like NULL signature keys may make it possible to bypass validation and allow forged credentials. I doubt it considering the SHC specs, but it all depends on the implementation.

## Resources
- [SMART Health Cards Framework Home Page](https://smarthealth.cards/)
- [SMART Health Cards Framework Specs](https://spec.smarthealth.cards/)
- [W3 Verifiable Credentials](https://w3c.github.io/vc-data-model/)
- [Decoding California's New Digital Vaccine Records and Potential Dangers](https://www.eff.org/deeplinks/2021/06/decoding-californias-new-digital-vaccine-records-and-potential-dangers)
- [SHC Python Sample Scripts](https://github.com/the-commons-project/healthcards_python_sample_scripts)
- [Flaw in the Quebec vaccine passport: analysis](https://www.welivesecurity.com/2021/08/31/flaw-quebec-vaccine-passport-vaxicode-verif-analysis/)
- [Canadian Vaccine Catalogue releases critical standardized terminology for COVID-19 vaccines](https://www.newswire.ca/news-releases/canadian-vaccine-catalogue-releases-critical-standardized-terminology-for-covid-19-vaccines-861079024.html)
