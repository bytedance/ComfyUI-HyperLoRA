import argparse
import os
import sys
from PIL import Image
from safetensors.torch import save_file

mock_path = os.path.join(os.path.dirname(__file__), 'mock')
print(f'Add mock path {mock_path} to sys.path')
sys.path.append(mock_path)

from hyperlora.common import images2tensor
from hyperlora.nodes import HyperLoRAUniLoaderNode, HyperLoRAUniGenerateIDLoRANode


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HyperLoRA testing script')
    parser.add_argument('--models_dir', type=str, required=True)
    parser.add_argument('--indir', type=str, required=True)
    parser.add_argument('--outdir', type=str, required=True)
    parser.add_argument('--image_processor', type=str, default='clip_vit_large_14_processor')
    parser.add_argument('--image_encoder', type=str, default='clip_vit_large_14')
    parser.add_argument('--encoder_types', type=str, default='clip + arcface')
    parser.add_argument('--face_analyzer', type=str, default='antelopev2')
    parser.add_argument('--model', type=str, default='sdxl_hyper_id_lora_v1_fidelity')
    parser.add_argument('--dtype', type=str, default='fp16')
    parser.add_argument('--device', type=str, default='cuda')
    args = parser.parse_args()

    import folder_paths
    from comfy import model_management
    folder_paths.models_dir = args.models_dir
    model_management.device = args.device

    HyperLoRAUniLoaderNode.INPUT_TYPES()
    HyperLoRAUniGenerateIDLoRANode.INPUT_TYPES()
    loader_node = HyperLoRAUniLoaderNode()
    gen_node = HyperLoRAUniGenerateIDLoRANode()
    hyper_lora, = loader_node.execute(args.image_processor, args.image_encoder, args.encoder_types, args.face_analyzer, args.model, args.dtype)

    image_files = [ fn for fn in os.listdir(args.indir) if os.path.splitext(fn)[1].lower() in [ '.jpg', '.jpeg', '.png' ] ]
    os.makedirs(args.outdir, exist_ok=True)
    for fn in image_files:
        try:
            lora, = gen_node.execute(hyper_lora, images2tensor([ Image.open(os.path.join(args.indir, fn)).convert('RGB') ]), False, True)
            save_file(lora, os.path.join(args.outdir, os.path.splitext(fn)[0] + '.safetensors'))
            print(f'Processed {fn}')
        except Exception as e:
            print(f'Failed to process {fn}, error: {e}')
