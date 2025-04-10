import torch
import torch.cuda
import gc

import warnings
warnings.filterwarnings("ignore")

from transformers import AutoModel  # noqa

torch.inference_mode()
torch.set_default_dtype(torch.float16)


class Model:
    def __init__(self):
        self.model = AutoModel.from_pretrained(
            'jinaai/jina-embeddings-v2-base-code',
            trust_remote_code=True).cuda()

    def encode(self, text):
        free_mem, total_mem = torch.cuda.mem_get_info()

        # if free_mem < 2 * 1024 * 1024 * 1024:  # 2 gb
            # print("gc")
        # gc.collect()
        # torch.cuda.empty_cache()
        embeddings = self.model.encode(
            text, convert_to_numpy=False
        ).detach().cpu().numpy()
        return embeddings

    def get_out_feature_count(self):
        return self.model.config.hidden_size
