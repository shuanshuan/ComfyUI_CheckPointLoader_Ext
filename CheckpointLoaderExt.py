import folder_paths
import comfy.sd

from aiohttp import web
from server import PromptServer
# from aiohttp import web
routes = PromptServer.instance.routes



class CheckpointLoaderExt:
    
    def __init__():
        pass

    def load_checkpoint(self, ckpt_name):
        ckpt_path = folder_paths.get_full_path("checkpoints", ckpt_name)
        out = comfy.sd.load_checkpoint_guess_config(ckpt_path, output_vae=True, output_clip=True, embedding_directory=folder_paths.get_folder_paths("embeddings"))
        return out[:3]

    @classmethod
    def INPUT_TYPES(s):
        return {"required": { "ckpt_name": (folder_paths.get_filename_list("checkpoints"), ),
                             }}
    RETURN_TYPES = ("MODEL", "CLIP", "VAE")
    FUNCTION = "load_checkpoint"

    CATEGORY = "loaders"


    

NODE_CLASS_MAPPINGS = {
    "CheckpointLoaderExt": CheckpointLoaderExt
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "CheckpointLoaderExt": "Checkpoint Loader Ext"
}