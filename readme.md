# My Site
This is a experiment where many different projects are joined together into one website, served by a REST API to provide data to each separate app.

## Apps

### DiscordBot

This is an experiment that combines a discord bot interfacing with a REST API (using Django Rest Framework and the discord module).
Users of the channel where the bot lives can register board game match results (persisted in a sqlite DB) and also query the Boardgamegeek api to retrieve information about their favorite board games.

Run the bot like this:

> python -m bot

### Todo