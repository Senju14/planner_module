import torch

def test_gpu_diagnostics():
    """
    Diagnoses PyTorch CUDA GPU availability and prints hardware details.
    """
    print("\n=== GPU Diagnostics Test ===")
    print(f"PyTorch Version: {torch.__version__}")
    
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_available}")
    
    if cuda_available:
        device_count = torch.cuda.device_count()
        print(f"Device Count: {device_count}")
        for i in range(device_count):
            print(f"  Device {i}: {torch.cuda.get_device_name(i)}")
        print(f"Active Device Index: {torch.cuda.current_device()}")
    else:
        print("Warning: CUDA GPU is not available. Local model inference will fall back to CPU (slower).")
    print("============================\n")

if __name__ == "__main__":
    test_gpu_diagnostics()
