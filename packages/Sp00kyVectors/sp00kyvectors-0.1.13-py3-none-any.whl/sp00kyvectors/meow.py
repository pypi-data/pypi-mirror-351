import os
import torch
from  cnn import Convoultion_NN  
import tempfile
import shutil

dataset_path = os.path.abspath(os.path.join(os.getcwd(), '..', 'imgs', 'test_imgs'))

print("Using dataset path:", dataset_path)
def test_model_initialization():
    """
    Test if the model initializes without error and builds the correct architecture.
    """
    
    try:
        model = Convoultion_NN(dataset_path=dataset_path)
        assert isinstance(model.model, torch.nn.Module)
        print("✅ Model initialized and architecture built.")
    except Exception as e:
        print("❌ Model initialization failed:", e)

def test_forward_pass():
    """
    Test a forward pass with a single image tensor.
    """
    try:
        model = Convoultion_NN(dataset_path=dataset_path)
        dummy_input = torch.randn(1, *model.input).to(model.device)  # Shape: (1, C, H, W)
        output = model.forward(dummy_input)
        assert output.shape[-1] == model.number_of_labels
        print("✅ Forward pass successful. Output shape:", output.shape)
    except Exception as e:
        print("❌ Forward pass failed:", e)

def test_train_step():
    """
    Test if the training loop runs one epoch without crashing.
    """
    try:
        model = Convoultion_NN(dataset_path=dataset_path, batch_size=4)
        model.train_model(epochs=1)
        print("✅ Training loop ran successfully for 1 epoch.")
    except Exception as e:
        print("❌ Training loop failed:", e)

def test_process_image():
    try:
        model = Convoultion_NN(dataset_path=dataset_path)
        # get first image path, not the array
        sample_image_path = model.image_paths[0][1]
        prediction = model.process_image(sample_image_path)
        assert isinstance(prediction, str)
        print("✅ Prediction successful. Predicted label:", prediction)
    except Exception as e:
        import traceback
        print("❌ Prediction failed:", e)
        traceback.print_exc()





if __name__ == "__main__":
    print("🔬 Running Convoultion_NN tests...")
    test_model_initialization()
    test_forward_pass()
    test_train_step()
    test_process_image()
