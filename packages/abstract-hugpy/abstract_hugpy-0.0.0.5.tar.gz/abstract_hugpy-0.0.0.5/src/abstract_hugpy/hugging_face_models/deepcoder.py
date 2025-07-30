import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
from transformers import BitsAndBytesConfig
from .config import DEFAULT_PATHS

DEFAULT_PATH = DEFAULT_PATHS["deepcoder"]

class DeepCoder:
    def __init__(
        self,
        model_dir: str = None,
        device: str = None,
        torch_dtype=torch.float16,
        use_quantization: bool = True
    ):
        self.model_dir = model_dir or DEFAULT_PATH
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.torch_dtype = torch_dtype
        self.use_quantization = use_quantization
        self._load_model()
        self._load_tokenizer()
        self._load_generation_config()

    def _load_model(self):
        kwargs = {"torch_dtype": self.torch_dtype}
        if self.use_quantization and self.device == "cuda":
            try:
                kwargs["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True)
            except ImportError:
                self.use_quantization = False
        self.model = AutoModelForCausalLM.from_pretrained(self.model_dir, **kwargs).to(self.device)

    def _load_tokenizer(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir, trust_remote_code=True)
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

    def _load_generation_config(self):
        try:
            self.generation_config = GenerationConfig.from_pretrained(self.model_dir)
        except Exception:
            self.generation_config = GenerationConfig(do_sample=True, temperature=0.6, top_p=0.95, max_new_tokens=64000)

    def generate(
        self,
        prompt,
        max_new_tokens: int = 1000,
        temperature: float = 0.6,
        top_p: float = 0.95,
        use_chat_template: bool = False,
        messages=None,
        do_sample: bool = False
    ) -> str:
        if use_chat_template and messages:
            inputs = self.tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors="pt")
        else:
            inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        max_tokens = min(max_new_tokens, getattr(self.generation_config, 'max_new_tokens', max_new_tokens))
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=do_sample,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

def get_deep_coder(
    module_path: str = None,
    torch_dtype=None,
    use_quantization: bool = None
) -> DeepCoder:
    return DeepCoder(
        model_dir=module_path or DEFAULT_PATH,
        torch_dtype=torch_dtype or torch.float16,
        use_quantization=use_quantization if use_quantization is not None else True
    )