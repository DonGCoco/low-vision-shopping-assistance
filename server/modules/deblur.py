from torchvision.transforms.functional import to_pil_image
import torch
from torchvision import transforms
from PIL import Image
import model.model as module_arch


def init_model(ckpt_path, device):
    checkpoint = torch.load(ckpt_path)
    config = checkpoint['config']
    # build model architecture
    generator_class = getattr(module_arch, config['generator']['type'])
    generator = generator_class(**config['generator']['args'])
    # prepare model for deblurring
    # device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    generator.to(device)
    generator.load_state_dict(checkpoint['generator'])
    generator.eval()
    return generator


generator = None


def image_preprocess(image_path, device):
    infer_transform = transforms.Compose([
        transforms.ToTensor(),  # convert to tensor
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))  # normalize
    ])
    # image_path = 'server_cache/input_image/input.jpg'
    blurred = Image.open(image_path).convert('RGB')
    h = blurred.size[1]
    w = blurred.size[0]
    new_h = h - h % 4 + 4 if h % 4 != 0 else h
    new_w = w - w % 4 + 4 if w % 4 != 0 else w
    blurred = transforms.Resize([new_h, new_w])(blurred)
    blurred = infer_transform(blurred).unsqueeze(0).to(device)
    return blurred  # (1, 3, w, h) tensor


def denormalize(image_tensor):
    # denormalize the normalized image tensor(N,C,H,W) with mean=0.5 and std=0.5 for each channel
    return (image_tensor + 1) / 2.0


def image_deblur(image_file, device):
    input_tensor = image_preprocess(image_file, device)
    with torch.no_grad():
        # for batch_idx, sample in enumerate(data_loader, ascii=True):
        deblurred = generator(input_tensor)
        deblurred_img = to_pil_image(denormalize(deblurred).squeeze().cpu())
        # deblurred_img.save(os.path.join(deblurred_dir, 'deblurred ' + image_name))\
    return deblurred_img


if __name__ == '__main__':
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    deblur_model_path = "../model_zoo/deblurGAN.pth"
    generator = init_model(deblur_model_path, device)
    res = image_deblur("../server_cache/input_image/input.jpg", "cuda")
    res.show()
