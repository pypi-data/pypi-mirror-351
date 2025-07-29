import logging
import pandas as pd
import torch
from tqdm.auto import trange
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class Classifier:
    """
    A wrapper for loading multiple fold-based Hugging Face models and performing
    ensemble prediction by averaging logits.

    Attributes:
        model_name (str): The Hugging Face model repository path.
        device (torch.device): The selected computation device (CUDA, MPS, or CPU).
        tokenizer: The tokenizer associated with the model.
        configs (dict): Configuration dictionary with number of folds and max_length.
        models (List[AutoModelForSequenceClassification]): Loaded model instances.
    """

    def __init__(self, model_name, sub_model=None):
        if torch.cuda.is_available() and torch.cuda.device_count() > 0:
            self.device = torch.device('cuda')
            logging.info('Using CUDA backend')
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available() and torch.backends.mps.is_built():
            self.device = torch.device("mps")
            logging.info('Using MPS backend')
        else:
            self.device = torch.device('cpu')
            logging.info('No GPU detected; using CPU.')

        self.model_name = model_name
        self.sub_model = sub_model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.configs = self.get_config(model_name)
        self.models = self.load_models()

    def load_models(self):
        models = []
        for fold in range(self.configs['num_folds']):
            path = str(fold) if self.sub_model is None else f'{self.sub_model}/{fold}'
            model = (AutoModelForSequenceClassification
                     .from_pretrained(self.model_name, subfolder=path)
                     .to(self.device))
            model.eval()
            models.append(model)
        return models

    def predict(self, text, batch_size=32):
        """
        Perform batch-wise ensemble prediction over input texts.

        Args:
            text (iterable of str): Input strings to classify.
            batch_size (int): Number of texts to process at once.

        Returns:
            list of float: Probability scores for the positive class.
        """
        if batch_size <= 0:
            raise ValueError('batch_size must be > 0')

        if isinstance(text, pd.Series):
            text = text.tolist()

        probs = []
        num_batches = (len(text) + batch_size - 1) // batch_size

        for i in trange(num_batches, desc=self.model_name.split('/', 1)[-1]):
            batch_texts = text[i * batch_size:(i + 1) * batch_size]
            inputs = self.tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                return_tensors='pt',
                max_length=self.configs['max_length']
            ).to(self.device)

            with torch.no_grad():
                logits_list = [model(**inputs).logits for model in self.models]
                avg_logits = torch.mean(torch.stack(logits_list), dim=0)
                probs += torch.softmax(avg_logits, dim=-1).cpu().numpy()[:, 1].tolist()

        return probs

    @staticmethod
    def get_config(model_name):
        match model_name:
            case _ if model_name in {
                'phantomkidding/bertweet-large-bragging',
                'phantomkidding/bertweet-large-disclosure',
            }:
                return {'num_folds': 5, 'max_length': 128}
            case _:
                return {'num_folds': 1, 'max_length': 128}


class Bragging(Classifier):
    """ Jin et al. 2022, Automatic Identification and Classification of Bragging in Social Media """
    def __init__(self):
        super().__init__('phantomkidding/bertweet-large-bragging')


if __name__ == '__main__':
    import pandas as pd
    classifier = Classifier('phantomkidding/bertweet-large-bragging')
    df = pd.read_csv('bragging/bragging_data.csv', dtype=str, usecols=['text'], nrows=512)
    df['bragging'] = classifier.predict(df['text'].tolist(), batch_size=64)
