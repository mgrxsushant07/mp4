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
    if request.method == 'POST':
        video_url = request.POST.get('url')
        file_format = request.POST.get('format')
        if not video_url or not file_format:
            error = 'Please provide a valid YouTube URL and select a format.'
        else:
            try:
                import tempfile
                unique_id = str(uuid.uuid4())
                import tempfile
                tmpdir = tempfile.TemporaryDirectory()
                if file_format == 'mp3':
                    output_template = os.path.join(tmpdir.name, f'{unique_id}.%(ext)s')
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': output_template,
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                    }
                    final_ext = 'mp3'
                else:
                    output_template = os.path.join(tmpdir.name, f'{unique_id}.%(ext)s')
                    ydl_opts = {
                        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
                        'outtmpl': output_template,
                        'merge_output_format': 'mp4',
                    }
                    final_ext = 'mp4'
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.extract_info(video_url, download=True)
                filename = f"{unique_id}.{final_ext}"
                file_path = os.path.join(tmpdir.name, filename)
                import time
                for _ in range(10):  # Try for up to 5 seconds
                    try:
                        f = open(file_path, 'rb')
                        break
                    except PermissionError:
                        time.sleep(0.5)
                else:
                    tmpdir.cleanup()
                    raise Exception("File is still being used by another process.")
                response = FileResponse(f, as_attachment=True, filename=filename)
                # Attach cleanup to response so tempdir is cleaned after response is closed
                orig_close = response.close
                def cleanup_file(*args, **kwargs):
                    try:
                        f.close()
                    except Exception:
                        pass
                    tmpdir.cleanup()
                    return orig_close(*args, **kwargs)
                response.close = cleanup_file
                return response
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                error = f'Error: {str(e)}\nTraceback:\n{tb}'
    return render(request, 'converter/home.html', {'error': error})
