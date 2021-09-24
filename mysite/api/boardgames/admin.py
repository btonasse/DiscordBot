from django.contrib import admin
import api.boardgames.models as md

admin.site.register(md.BoardGame)
admin.site.register(md.Match)
admin.site.register(md.Player)
admin.site.register(md.Result)
