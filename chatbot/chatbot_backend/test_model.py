from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = 'distilgpt2'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Set the device
if torch.cuda.is_available():
    device = torch.device('cuda')
    print("Using CUDA")
elif torch.backends.mps.is_available():
    device = torch.device('mps')
    print("Using MPS (Apple Silicon)")
else:
    device = torch.device('cpu')
    print("Using CPU")

model.to(device)
model.eval()

prompt = "Hello, how are you?"

inputs = tokenizer(prompt, return_tensors='pt').to(device)

# Generate text
outputs = model.generate(
    **inputs,
    max_length=50,
    num_return_sequences=1,
    no_repeat_ngram_size=2,
    early_stopping=True,
    pad_token_id=tokenizer.eos_token_id,
)

generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
response_text = generated_text[len(prompt):].strip()

print("Response:", response_text)
