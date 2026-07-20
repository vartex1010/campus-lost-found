"""
Image similarity for matching lost <-> found item photos.

Phase 1 (this file): returns 0.0 if either image is missing, otherwise a
placeholder score of None so the caller knows to skip it — keeps the app
runnable with zero heavy ML dependencies until you're ready for Phase 2.

Phase 2: plug in CLIP (see bottom) for real image-to-image similarity.
"""


def image_similarity(image_path_a, image_path_b):
    """
    Returns a float 0..1, or None if not computable (e.g. missing image).
    """
    if not image_path_a or not image_path_b:
        return None
    # Phase 1 placeholder — wire up CLIP below when ready.
    return None


# ---------------------------------------------------------------------
# UPGRADE PATH — CLIP-based image similarity:
#
#   pip install open-clip-torch torch pillow
#
#   import torch, open_clip
#   from PIL import Image
#
#   device = "cuda" if torch.cuda.is_available() else "cpu"
#   model, _, preprocess = open_clip.create_model_and_transforms(
#       'ViT-B-32', pretrained='openai'
#   )
#   model.to(device).eval()
#
#   def _embed(path):
#       img = preprocess(Image.open(path).convert("RGB")).unsqueeze(0).to(device)
#       with torch.no_grad():
#           feat = model.encode_image(img)
#           feat /= feat.norm(dim=-1, keepdim=True)
#       return feat
#
#   def image_similarity(image_path_a, image_path_b):
#       if not image_path_a or not image_path_b:
#           return None
#       a, b = _embed(image_path_a), _embed(image_path_b)
#       return float((a @ b.T).item())
#
# This lets a red water bottle photo match another red water bottle photo
# even if the descriptions barely overlap in wording.
# ---------------------------------------------------------------------
