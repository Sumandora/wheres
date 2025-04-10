import torch

import warnings
warnings.filterwarnings("ignore")

from transformers import AutoModel  # noqa

torch.inference_mode()
torch.set_default_dtype(torch.float16)

_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch.set_default_device(_DEVICE)


class Model:
    def __init__(self):
        self.model = AutoModel.from_pretrained(
            'jinaai/jina-embeddings-v2-base-code',
            trust_remote_code=True).to(_DEVICE)

    def encode(self, text):
        embeddings = self.model.encode(
            text, convert_to_numpy=False
        ).detach().cpu().numpy()
        return embeddings

    def get_out_feature_count(self):
        return self.model.config.hidden_size
