import torch
from tqdm.auto import trange
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline


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

    id2label = None

    def __init__(self, repo_id, dataset, task):
        self.repo_id = repo_id
        self.dataset = dataset
        self.task = task
        self.tokenizer = AutoTokenizer.from_pretrained(repo_id)
        self.configs = self.get_config(repo_id)

    def predict(self, text, batch_size=128):
        if batch_size <= 0:
            raise ValueError('batch_size must be > 0')

        folds = []
        for f in trange(self.configs['num_folds']):
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
        if len(self.id2label) == 2:
            return torch.softmax(avg_logits, dim=-1).cpu().numpy()[:, 1].tolist()
        else:
            return torch.softmax(avg_logits, dim=-1).cpu().numpy().tolist()

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
    classifier = ClassifierCV('phantomkidding/chinese-roberta-wwm-ext-large-apps', 'toxicn', 'expression_ie')
    text = ['我干他娘的', '靠腰', '我淦']
    print(classifier.predict(text))
