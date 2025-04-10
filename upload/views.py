from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decouple import config
import cloudinary
import cloudinary.uploader

# Configure Cloudinary explicitly with your API details
cloudinary.config(
    cloud_name= config('CLOUDINARY_CLOUD_NAME'),
    api_key= config('CLOUDINARY_API_KEY'),
    api_secret= config('CLOUDINARY_API_SECRET')
)

class ImageUploadAPIView(APIView):
    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({'error': 'No image file provided.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = cloudinary.uploader.upload(image_file, folder='djangoshop')
        except Exception as e:
            return Response({'error': f'Upload failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        image_url = result.get('secure_url')
        if not image_url:
            return Response({'error': 'No URL returned from Cloudinary.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'url': image_url}, status=status.HTTP_201_CREATED)
