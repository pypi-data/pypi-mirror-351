import torch
from datasets import Dataset
from transformers import (AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline,
                          Trainer, TrainingArguments)


class TextClassificationPipelineLogits(TextClassificationPipeline):
    def postprocess(self, model_outputs, *args):
        logits = model_outputs["logits"][0]
        return logits.float().detach().cpu()


class ClassifierCV:
    """
    A wrapper for loading multiple fold-based Hugging Face models and performing
    ensemble prediction by averaging logits.

    Attributes:
        repo_id (str): The Hugging Face model repository id.
        dataset (str): The dataset name used to locate model subfolders (dataset pre-trained).
        task (str): The classification task name, part of the subfolder structure.
        tokenizer: The tokenizer associated with the model.
        configs (dict): Configuration dictionary with number of folds and max_length.
        id2label (dict): Mapping from label IDs to human-readable labels (populated after loading model).
    """

    def __init__(self, repo_id, dataset, task, usefolds=None):
        self.repo_id = repo_id
        self.dataset = dataset
        self.task = task
        self.configs = self.get_config(repo_id)
        self.tokenizer = AutoTokenizer.from_pretrained(repo_id)
        self.num_folds = self.configs['num_folds'] if usefolds is None else usefolds
        self.models = [AutoModelForSequenceClassification.from_pretrained(repo_id, subfolder=f'{dataset}/{task}/{f}')
                       for f in range(self.num_folds)]
        self.id2label = self.models[0].config.id2label

    def predict(self, text, batch_size=128, ):
        def tokenize(batch):
            return self.tokenizer(batch['text'], padding=True, truncation=True, max_length=self.configs['max_length'])
        text = Dataset.from_dict({'text': text}).map(tokenize, batched=True)

        all_logits = []
        for f, model in enumerate(self.models):
            print(f'{self.dataset}/{self.task}/{f}')
            trainer = Trainer(
                model=model,
                tokenizer=self.tokenizer,
                args=TrainingArguments(per_device_eval_batch_size=batch_size),
            )
            logits = trainer.predict(text).predictions
            all_logits.append(torch.tensor(logits))
        avg_logits = torch.mean(torch.stack(all_logits), dim=0)
        return torch.softmax(avg_logits, dim=-1).cpu().numpy()[:, 1:].tolist()

    def predict_pipe(self, text, batch_size=128):
        if batch_size <= 0:
            raise ValueError('batch_size must be > 0')

        folds = []
        for f in range(self.configs['num_folds']):
            print(f'{self.dataset}/{self.task}/{f}')
            model = AutoModelForSequenceClassification.from_pretrained(
                self.repo_id,
                subfolder=f'{self.dataset}/{self.task}/{f}'
            )
            self.id2label = model.config.id2label
            pipe = TextClassificationPipelineLogits(model=model, tokenizer=self.tokenizer)
            fold = pipe(text, batch_size=batch_size)
            folds.append(fold)
        logits_list = list(zip(*folds))
        avg_logits = torch.stack([torch.mean(torch.stack(logits_folds), dim=0) for logits_folds in logits_list])
        return torch.softmax(avg_logits, dim=-1).cpu().numpy()[:, 1:].tolist()

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

    @property
    def labels(self):
        return [self.id2label[i] for i in sorted(self.id2label) if i != 0]


if __name__ == '__main__':
    classifier = ClassifierCV('phantomkidding/chinese-roberta-wwm-ext-large-apps', 'toxicn', 'expression_ie')
    text = ['干他娘的', '卧槽']
    probs = classifier.predict(text)
    id2label = classifier.id2label
    columns = [id2label[k] for k in sorted(id2label) if k != 0]
    print(columns)
    print(probs)
