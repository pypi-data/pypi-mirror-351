import logging

import torch
import pandas as pd
from tqdm.auto import trange
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class Classifier:
    """
    A wrapper for loading multiple fold-based Hugging Face models and performing
    ensemble prediction by averaging logits.

    Attributes:
        repo_id (str): The Hugging Face model repository path.
        device (torch.device): The selected computation device (CUDA, MPS, or CPU).
        tokenizer: The tokenizer associated with the model.
        configs (dict): Configuration dictionary with number of folds and max_length.
        models (List[AutoModelForSequenceClassification]): Loaded model instances.
    """

    def __init__(self, repo_id, dataset, task):
        if torch.cuda.is_available() and torch.cuda.device_count() > 0:
            self.device = torch.device('cuda')
            logging.info('Using CUDA backend')
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available() and torch.backends.mps.is_built():
            self.device = torch.device("mps")
            logging.info('Using MPS backend')
        else:
            self.device = torch.device('cpu')
            logging.info('No GPU detected; using CPU.')

        self.repo_id = repo_id
        self.dataset = dataset
        self.task = task
        self.tokenizer = AutoTokenizer.from_pretrained(repo_id)
        self.configs = self.get_config(repo_id)
        self.models = self.load_models()

    def load_models(self):
        models = []
        for fold in range(self.configs['num_folds']):
            model = AutoModelForSequenceClassification.from_pretrained(
                self.repo_id,
                subfolder=f'{self.dataset}/{self.task}/{fold}').to(self.device)
            model.eval()
            models.append(model)
            self.id2label = model.config.id2label
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

        for i in trange(num_batches, desc=f'{self.dataset}/{self.task}'):
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
                if len(self.id2label) == 2:
                    probs += torch.softmax(avg_logits, dim=-1).cpu().numpy()[:, 1].tolist()
                else:
                    probs += torch.softmax(avg_logits, dim=-1).cpu().numpy().tolist()

        return probs

    @staticmethod
    def get_config(model_name):
        match model_name:
            case _ if model_name in {
                'phantomkidding/bertweet-large-bragging',
                'phantomkidding/bertweet-large-disclosure',
            }:
                return {'num_folds': 5, 'max_length': 128}
            case 'phantomkidding/chinese-roberta-wwm-ext-large-apps':
                return {'num_folds': 5, 'max_length': 512}
            case _:
                return {'num_folds': 1, 'max_length': 128}


if __name__ == '__main__':
    import pandas as pd
    classifier = Classifier('phantomkidding/chinese-roberta-wwm-ext-large-apps', 'toxicn', 'toxic')
    df = pd.read_csv('bragging/bragging_data.csv', dtype=str, usecols=['text'], nrows=512)
    df['bragging'] = classifier.predict(df['text'].tolist(), batch_size=64)
