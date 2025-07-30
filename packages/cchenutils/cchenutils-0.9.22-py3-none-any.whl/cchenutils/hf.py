import pandas as pd
from datasets import Dataset
from transformers import pipeline as ppl


def pipeline(text, /, batch_size=None, **kwargs):
    """
    Analyze a list, Series, or single string using a HuggingFace pipeline with batching.

    Args:
        text (str | list[str] | pd.Series): Input text(s).
        *args, **kwargs: Arguments for the transformers.pipeline function.
        batch_size (int): Number of items per batch.

    Returns:
        pd.DataFrame: Prediction scores.
    """

    if not isinstance(batch_size, int) or batch_size <= 0:
        raise ValueError('batch_size must be > 0')

    match text:
        case str():
            text = [text]
        case pd.Series():
            text = text.tolist()
    ds = Dataset.from_dict({'text': text})

    clf = ppl(**kwargs)
    ds_out = ds.map(
        lambda x: {
            'pred': [{pred['label']: pred['score'] for pred in r} for r in clf(x['text'])]
        },
        batched=True,
        batch_size=batch_size,
        desc=kwargs.get('model')
    )
    return pd.DataFrame(ds_out['pred'])
