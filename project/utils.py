from user.models import Writer


def get_writer_for_user(user):
    return Writer.objects.get(user=user)
