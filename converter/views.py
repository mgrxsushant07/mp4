from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
import yt_dlp
import uuid

MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'media')
os.makedirs(MEDIA_ROOT, exist_ok=True)

def home(request):
    return render(request, 'converter/home.html')

@csrf_exempt
def download(request):
    error = None
    file_url = None
    if request.method == 'POST':
        video_url = request.POST.get('url')
        file_format = request.POST.get('format')
        if not video_url or not file_format:
            error = 'Please provide a valid YouTube URL and select a format.'
        else:
            try:
                unique_id = str(uuid.uuid4())
                if file_format == 'mp3':
                    output_template = os.path.join(MEDIA_ROOT, f'{unique_id}.%(ext)s')
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': output_template,
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                    }
                else:  # mp4
                    output_template = os.path.join(MEDIA_ROOT, f'{unique_id}.%(ext)s')
                    ydl_opts = {
                        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
                        'outtmpl': output_template,
                        'merge_output_format': 'mp4',
                    }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    if file_format == 'mp3':
                        filename = f"{unique_id}.mp3"
                    else:
                        filename = f"{unique_id}.mp4"
                file_url = f"/media/{filename}"
                context = {'file_url': file_url}
                return render(request, 'converter/home.html', context)
            except Exception as e:
                error = f'Error: {str(e)}'
    return render(request, 'converter/home.html', {'error': error})
