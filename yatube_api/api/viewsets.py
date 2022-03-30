from rest_framework import mixins, viewsets


class CreateListModelViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    pass
