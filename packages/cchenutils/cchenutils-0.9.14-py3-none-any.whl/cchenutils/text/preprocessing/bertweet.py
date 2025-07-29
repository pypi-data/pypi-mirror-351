import html
import re

from nltk import TweetTokenizer

from .emojis import UNICODE_EMOJI

try:
    import emoji
    from emoji import demojize  # 0.6.0

    if emoji.__version__ != '0.6.0':
        raise ImportError(f'The emoji library version must be 0.6.0, but found {emoji.__version__}')
except ImportError:
    demojize = lambda x: x

tokenizer = TweetTokenizer()


def bertweet_normalize(txt, keep_emoji=True, reduce_repeat=True):
    txt = html.unescape(txt)
    txt = re.sub(r'^RT @\w+:\s*', '', txt)
    txt = re.sub(r'\b(?:ha|ah){2,}\b', 'haha', txt, flags=re.IGNORECASE)
    txt = re.sub(r'@\w+', '@user', txt)
    txt = re.sub(r'http\S+|www\S+|https\S+', 'http', txt)
    txt = re.sub(r'^(?:@user\s+){1,}', '', txt.strip())
    txt = re.sub(r'(?:\s+@user){2,}$', '', txt)
    if reduce_repeat:
        txt = re.sub(r'([^\w\s])\1{3,}', r'\1\1\1', txt)
        txt = re.sub(r'(.)\1{4,}', r'\1\1\1', txt)
    txt = _normalizeTweet(txt, keep_emoji)
    if keep_emoji:
        txt = re.sub(r'(:[^\s:]+:)(\s*\1){3,}', lambda m: ' '.join([m.group(1)] * 3), txt)
    return re.sub(r'\s+', ' ', txt).strip()


def _normalizeToken(token, keep_emoji=True):
    lowercased_token = token.lower()
    if token.startswith("@"):
        return "@USER"
    elif lowercased_token.startswith("http") or lowercased_token.startswith("www"):
        return "HTTPURL"
    elif any(char in UNICODE_EMOJI for char in token):
        return demojize(token) if keep_emoji else ''

    else:
        if token == "’":
            return "'"
        elif token == "…":
            return "..."
        else:
            return token


def _normalizeTweet(tweet, keep_emoji=True):
    tokens = tokenizer.tokenize(tweet.replace("’", "'").replace("…", "..."))
    normTweet = " ".join(_normalizeToken(token, keep_emoji) for token in tokens)

    normTweet = (
        normTweet.replace("cannot ", "can not ")
        .replace("n't ", " n't ")
        .replace("n 't ", " n't ")
        .replace("ca n't", "can't")
        .replace("ai n't", "ain't")
    )
    normTweet = (
        normTweet.replace("'m ", " 'm ")
        .replace("'re ", " 're ")
        .replace("'s ", " 's ")
        .replace("'ll ", " 'll ")
        .replace("'d ", " 'd ")
        .replace("'ve ", " 've ")
    )
    normTweet = (
        normTweet.replace(" p . m .", " p.m.")
        .replace(" p . m ", " p.m ")
        .replace(" a . m .", " a.m.")
        .replace(" a . m ", " a.m ")
    )

    return " ".join(normTweet.split())
