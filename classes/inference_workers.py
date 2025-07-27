# classes/inference_workers.py
import torch
from PyQt6.QtCore import QThread, pyqtSignal
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

class ModelLoaderThread(QThread):
    finished = pyqtSignal(object, object)
    error = pyqtSignal(str)
    def __init__(self, model_id, adapter_path=None):
        super().__init__()
        self.model_id = model_id
        self.adapter_path = adapter_path
    def run(self):
        try:
            bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=False)
            base_model = AutoModelForCausalLM.from_pretrained(self.model_id, quantization_config=bnb_config, device_map={"": 0})
            tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            tokenizer.pad_token = tokenizer.eos_token
            model = PeftModel.from_pretrained(base_model, self.adapter_path) if self.adapter_path else base_model
            self.finished.emit(model, tokenizer)
        except Exception as e:
            self.error.emit(str(e))

class InferenceThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    def __init__(self, model, tokenizer, chat_history):
        super().__init__()
        self.model = model
        self.tokenizer = tokenizer
        self.chat_history = chat_history
    def run(self):
        try:
            prompt = self.tokenizer.apply_chat_template(self.chat_history, tokenize=False, add_generation_prompt=True)
            inputs = self.tokenizer.encode(prompt, add_special_tokens=False, return_tensors="pt").to("cuda")
            outputs = self.model.generate(
                input_ids=inputs, 
                max_new_tokens=1536, 
                do_sample=True, 
                temperature=0.8,
                top_k=50, 
                top_p=0.95,
                repetition_penalty=1.15
            )
            response_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            newly_generated_text = response_text[len(prompt.replace("<bos>", "")):]
            self.finished.emit(newly_generated_text.strip())
        except Exception as e:
            self.error.emit(str(e))
