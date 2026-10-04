from apps.polling.models import PollRun
from apps.polling.serializers import PollRunSerializer
from rest_framework.generics import ListAPIView


class PollRunList(ListAPIView):
    serializer_class = PollRunSerializer
    queryset = PollRun.objects.order_by("-id")
