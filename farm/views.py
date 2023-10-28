from django.shortcuts import render
from .filters import ServiceFilter  # Import the filter

# Create your views here.
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Service
from .serializers import ServiceSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import (
    Farm,
    FarmActivity,
    Livestock,
    Crop,
    Produce,
    Service,
    Question,
    Answer,
)
from .serializers import (
    FarmSerializer,
    FarmActivitySerializer,
    LivestockSerializer,
    CropSerializer,
    ProduceSerializer,
    ServiceSerializer,
    QuestionSerializer,
    AnswerSerializer,
)


# View for listing all farms and creating a new farm
class FarmListCreateView(generics.ListCreateAPIView):
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    # permission_classes = [IsAuthenticated]


# View for retrieving, updating, and deleting a specific farm
class FarmRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    # permission_classes = [IsAuthenticated]


# View for listing all available services and creating a new service booking
class ServiceListCreateView(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Set the farmer booking the service to the current user
        serializer.save()  # farmer=self.request.user


class ServiceRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filter_class = ServiceFilter  # Specify the filter class

    def perform_update(self, serializer):
        # Custom logic for updating a service booking
        instance = serializer.save()
        if instance.status == 'Completed':
            # Implement your logic for handling completed services here
            pass

    def perform_destroy(self, instance):
        # Custom logic for canceling a service booking
        if instance.status == 'Pending':
            # Implement your logic for canceling a pending service here
            instance.status = 'Cancelled'
            instance.save()
        else:
            # Handle other cases as needed
            pass


# View for asking a question
class QuestionCreateView(generics.CreateAPIView):
    serializer_class = QuestionSerializer
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Set the farmer asking the question to the current user
        serializer.save()  # farmer=self.request.user


class QuestionListView(generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


# View for viewing and adding produce from livestock
class LivestockProduceView(generics.ListCreateAPIView):
    queryset = Livestock.objects.all()
    serializer_class = LivestockSerializer
    # permission_classes = [IsAuthenticated]


# View for viewing and adding produce from crop
class CropProduceView(generics.ListCreateAPIView):
    queryset = Crop.objects.all()
    serializer_class = CropSerializer
    # permission_classes = [IsAuthenticated]


# View for listing all farm activities and creating a new farm activity
class FarmActivityListCreateView(generics.ListCreateAPIView):
    queryset = FarmActivity.objects.all()
    serializer_class = FarmActivitySerializer
    # permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Check if a similar activity already exists
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        similar_activities = FarmActivity.objects.filter(
            activity_type=serializer.validated_data["activity_type"],
            date=serializer.validated_data["date"],
            time=serializer.validated_data["time"],
        )
        if similar_activities.exists():
            return Response(
                {"detail": "A similar activity is already planned."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            serializer.save()  # farmer=self.request.user
            return Response(serializer.data, status=status.HTTP_201_CREATED)


# View for retrieving, updating, and deleting a specific farm activity
class FarmActivityRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FarmActivity.objects.all()
    serializer_class = FarmActivitySerializer
    # permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        # Check if a similar activity already exists
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        similar_activities = FarmActivity.objects.filter(
            activity_type=serializer.validated_data["activity_type"],
            date=serializer.validated_data["date"],
            time=serializer.validated_data["time"],
        ).exclude(
            pk=instance.pk
        )  # Exclude the current activity from the check
        if similar_activities.exists():
            return Response(
                {"detail": "A similar activity is already planned."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        # You can include a message in the response
        instance.delete()
        return Response(
            {
                "detail": f"Farm activity with ID {instance.id} and name {instance.activity_type} deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT,
        )


# View for viewing and adding answers
class AnswerView(generics.ListCreateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    # permission_classes = [IsAuthenticated]
