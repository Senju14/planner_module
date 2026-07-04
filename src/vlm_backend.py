import os
import json
import torch
from transformers import AutoProcessor, AutoModelForImageTextToText
from src.config import MODEL_PATH, DEVICE, MAX_NEW_TOKENS, TEMPERATURE

# Cached model resources
_model = None
_processor = None
_device = None

def load_model():
    """
    Loads and caches the local SmolVLM model and processor.
    Uses GPU/float16 as requested. Downloads the model if not present locally.
    """
    global _model, _processor, _device
    if _model is not None:
        return _model, _processor, _device

    # Automated downloader if model path is empty
    if not os.path.exists(MODEL_PATH) or not os.listdir(MODEL_PATH):
        print(f"[VLM] Local path '{MODEL_PATH}' is empty. Downloading SmolVLM-256M-Instruct from Hugging Face Hub...")
        from huggingface_hub import snapshot_download
        snapshot_download(repo_id="HuggingFaceTB/SmolVLM-256M-Instruct", local_dir=MODEL_PATH)

    device_target = DEVICE.lower()

    if device_target == "cpu":
        _device = "cpu"
        torch_dtype = torch.float32
        device_map = {"": "cpu"}
        print("[VLM] Loading model on CPU using float32...")
    elif device_target == "cuda":
        _device = "cuda"
        torch_dtype = torch.float16  # Load in Float16 as requested
        device_map = {"": "cuda"}
        print(f"[VLM] Loading model on GPU ({_device}) using float16...")
    else:  # "auto"
        if torch.cuda.is_available():
            _device = "cuda"
            torch_dtype = torch.float16
            device_map = "auto"
            print("[VLM] Loading model in 'auto' mode: GPU CUDA active with float16 offloading...")
        else:
            _device = "cpu"
            torch_dtype = torch.float32
            device_map = {"": "cpu"}
            print("[VLM] Loading model in 'auto' mode: GPU CUDA inactive, falling back to CPU float32...")

    _model = AutoModelForImageTextToText.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch_dtype,
        device_map=device_map
    )
    _processor = AutoProcessor.from_pretrained(MODEL_PATH)
    return _model, _processor, _device

def generate_action(system_prompt: str, prompt: str, image_path: str = "screenshots/current.png") -> str:
    """
    Runs inference on the local SmolVLM model using HMI screenshot and text prompt.
    """
    model, processor, device = load_model()

    # Manually downsample screenshot to 512x288 to prevent VRAM memory spike
    from PIL import Image
    small_image_path = "screenshots/current_small.png"
    
    with Image.open(image_path) as img:
        resized_img = img.resize((512, 288), Image.Resampling.LANCZOS)
        resized_img.save(small_image_path)

    # Prepend system prompt to user prompt for chat template compatibility
    combined_prompt = f"{system_prompt}\n\n{prompt}"

    # Construct SmolVLM conversation messages
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": combined_prompt}
            ]
        }
    ]

    # Clear cache before input processing to free up maximum fragmented memory
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # Apply chat template and load image using PIL
    text_prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
    pil_image = Image.open(small_image_path)

    # Preprocess inputs
    inputs = processor(
        text=text_prompt,
        images=[pil_image],
        return_tensors="pt",
        do_resize=True,
        size={"longest_edge": 384}
    )
    inputs = inputs.to(device)

    # Build generation keyword arguments
    gen_kwargs = {
        "max_new_tokens": MAX_NEW_TOKENS,
    }
    if TEMPERATURE == 0.0:
        gen_kwargs["do_sample"] = False
    else:
        gen_kwargs["do_sample"] = True
        gen_kwargs["temperature"] = TEMPERATURE

    # Perform inference
    with torch.no_grad():
        generated_ids = model.generate(**inputs, **gen_kwargs)
        # Decode only the generated text tokens
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )

    response = output_text[0].strip()

    # Clear cache after inference
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return response

class FakeVLM:
    """
    A wrapper class matching the VLM generate interface.
    """
    def generate(self, system_prompt: str, prompt: str) -> str:
        return generate_action(system_prompt, prompt)
