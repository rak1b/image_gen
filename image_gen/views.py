from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from diffusers import StableDiffusionPipeline
import torch
from io import BytesIO
from PIL import Image

from transformers import StableDiffusionPipeline

model = StableDiffusionPipeline.from_pretrained(
    "CompVis/stable-diffusion-v1-4", 
    torch_dtype=torch.float16, 
    low_cpu_mem_usage=True
)
# Load the Stable Diffusion model
# model = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4", torch_dtype=torch.float16)
model = model.to("cpu")  # Use "cpu" to limit memory usage; for GPU use, change to "cuda"

# Limit the prompt complexity by restricting the length of the prompt
MAX_PROMPT_LENGTH = 50  # Maximum number of characters in the prompt

@csrf_exempt
def generate_image(request):
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '')
        
        # Check if the prompt is too long
        if len(prompt) > MAX_PROMPT_LENGTH:
            return JsonResponse({'error': 'Prompt too long. Limit is {} characters.'.format(MAX_PROMPT_LENGTH)}, status=400)

        # Restrict the prompt to prevent overly complex images
        if not prompt or len(prompt.split()) < 3:
            return JsonResponse({'error': 'Prompt must be at least 3 words long.'}, status=400)

        try:
            # Generate the image using the model
            with torch.no_grad():
                image = model(prompt).images[0]

            # Save the image to a byte buffer
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            buffer.seek(0)

            # Return the image in the response
            return HttpResponse(buffer, content_type="image/png")
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def health_check(request):
    return JsonResponse({'status': "OK"}, status=200)
