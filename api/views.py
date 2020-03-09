from rest_framework.parsers import FileUploadParser, MultiPartParser
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from attendance.models import Parent
from rest_framework.permissions import IsAdminUser, IsAuthenticated
import face_recognition
import mimetypes
from django.core.mail import EmailMultiAlternatives
from attendance.views import verify_requests_redo
from django.shortcuts import get_object_or_404
from django.utils import timezone


class ParentRecordView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, format=None):
        parents = Parent.objects.all()
        serializer = ParentSerializer(parents, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ParentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=ValueError):
            serializer.create(validated_data=request.data)
            return Response({'message': 'created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


class LostKidRegistrationView(APIView):
    parser_class = (FileUploadParser,)
    permission_classes = [IsAdminUser]

    def get(self, format=None):
        lost_kids = LostKid.objects.all()
        serializer = LostKidSerializer(lost_kids, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LostKidSerializer(data=request.data)
        if serializer.is_valid(raise_exception=ValueError):
            instance = serializer.save()
            verify_requests_redo(instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


class VerifyKidView(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = VerifyKidSerializer(data=request.data)
        print(serializer)
        found = False
        if serializer.is_valid(raise_exception=ValueError):
            vf = serializer.save()
            lost_kids = LostKid.objects.filter(found=False)
            image = face_recognition.load_image_file(vf.photo)
            file = vf.photo.open().read()
            name = vf.photo.name
            format_file = mimetypes.guess_type(vf.photo.name)[0]
            unknown_encoding = face_recognition.face_encodings(image)
            if unknown_encoding:
                unknown_encoding = unknown_encoding[0]
                for i in lost_kids:
                    image_known = face_recognition.load_image_file(i.photo)
                    biden_encoding = face_recognition.face_encodings(image_known)[0]
                    results = face_recognition.compare_faces([biden_encoding], unknown_encoding, tolerance=0.51)
                    if results[0]:
                        i.found = True
                        i.found_location = vf.location
                        i.save()
                        message = EmailMultiAlternatives("Congratulations !! Your kid {} is found".format(i.name),
                                                         "Your kid {} was found at the location {}".format(i.name,
                                                                                                           i.found_location),
                                                         "admin@ohuru.tech",
                                                         [i.email],
                                                         )
                        message.attach(name, file, format_file)
                        message.send()
                        found = True
                        vf.delete()
                        name = i.name
                        contact = i.email + ' ' + i.phone_number
                        break
            if found:
                context = {
                    'found_name': name,
                    'contact': contact
                }
                return Response(context, status=status.HTTP_202_ACCEPTED)
            else:
                lost_kids = LostKid.objects.filter(found=True)
                not_save = False
                for i in lost_kids:
                    image_known = face_recognition.load_image_file(i.photo)
                    biden_encoding = face_recognition.face_encodings(image_known)[0]
                    results = face_recognition.compare_faces([biden_encoding], unknown_encoding)
                    if results[0]:
                        not_save = True
                        pass
                if not_save:
                    vf.delete()
                    context = {
                        'message': 'The Kid is already found',
                    }
                else:
                    context = {
                        'message': 'The verification request has been saved'
                    }
                return Response(context, status=status.HTTP_201_CREATED)

        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


class KidView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser,)

    def get(self, request, format=None):
        parent = get_object_or_404(Parent, user=request.user)
        children = Kid.objects.filter(parent=parent)
        serializer = KidSerializer(children, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = KidSerializer(data=request.data)
        if serializer.is_valid(raise_exception=ValueError):
            child = Kid()
            child.name = serializer.validated_data['name']
            child.description = serializer.validated_data['description']
            child.photo_id = request.data['photo_id']
            child.state = serializer.validated_data['state']
            parent = get_object_or_404(Parent, user=request.user)
            child.parent = parent
            child.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class MakeLostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = KidSerializer(data=request.data)
        if serializer.is_valid(raise_exception=ValueError):
            if not serializer.validated_data['flag']:
                lost = LostKid()
                lost.email = request.user.email
                child = get_object_or_404(Kid, name=serializer.validated_data['name'])
                lost.name = child.name
                lost.state = child.state
                lost.photo = child.photo_id
                lost.date = timezone.now()
                lost.description = child.description
                lost.phone_number = child.parent.phone_number
                lost.save()
                child.lost_instance = lost
                child.lost = True
                child.save()
                verify_requests_redo(lost)
                return Response({'message': 'Done'}, status=status.HTTP_202_ACCEPTED)
            else:
                child = get_object_or_404(Kid, name=serializer.validated_data['name'])
                child.lost = False
                child.lost_instance.delete()
                child.lost_instance = None
                child.save()
                return Response({'message': 'Done'}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)
