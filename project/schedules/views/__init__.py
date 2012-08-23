from .base import *

index = Index.as_view()
service = Service.as_view()
service_week = ServiceWeek.as_view()
search = Search.as_view()
print_schedules = Print.as_view()
now_playing = NowPlaying.as_view()