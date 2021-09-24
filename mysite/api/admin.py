from django.contrib import admin
import api.models.boardgames as bg

admin.site.register(bg.BoardGame)
admin.site.register(bg.Match)
admin.site.register(bg.Player)
admin.site.register(bg.Result)
