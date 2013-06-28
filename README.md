# UltraAdmin Plugin
##### Plugin for B3 (www.bigbrotherbot.com)
##### Author: LouK(8thelouk8@gmail.com) from the Sni:{Per}:Jum Clan: http://sniperjum.wix.com/clan
=
### Installation -

* Place ultraadmin.py in /extplugins/ and ultraadmin.xml in /extplugins/conf/
* In your b3.xml config, add this line: <plugin name="ultraadmin" config="@b3/extplugins/conf/ultraadmin.xml"/>
* Change command levels & messages layout(do not change the %s order) in the ultraadmin.xml

-
### Requirements -

In order to use this plugin, you need to have some other's in your b3:
> Note: These plugins doesn't belong to me, if you have questions about them, please contact with the owner.

* Follow Plugin: http://forum.bigbrotherbot.net/releases/follow-users-plugin
* Geowelcome Plugin: http://forum.bigbrotherbot.net/releases/geowelcome-plugin

-
### Commands -

#### !ultrauserinfo (!uui)
> Display information about the selected player.

- Server id: playerlist number
- Exact player's name
- b3 @id
- b3 group & level
- Player's connections number
- Player's IP
- Player'slocation(see http://forum.bigbrotherbot.net/releases/geowelcome-plugin geowelcome plugin)
- Watchlist: If the player is in the watchlist(displayed only if the player is in watchlist)(see http://forum.bigbrotherbot.net/releases/follow-users-plugin follow plugin) 
- Aliases: 5 aliases(displayed only if the player has aliases)
- Active warns(displayed only if the player has active warns)
- Past bans(displayed only if the player has past bans)

#### !ultralist (!ul)
> Display information(less than uui) about connected players.

- Server id: playerlist number
- Exact player's name
- b3 @id
- b3 level
- Player's connections number
- Player's IP
- Active warns(number)
- Past bans(number)

#### !ultraserverinfo (!usi)
> Display advanced info about the server.
> Note: This command may take some time to be processed, it has to find a lot of information

- Server name
- Download maps URL
- Maxclients / Privateclients
- Gametype / Timelimit / Fraglimit
- All Active Permbans number
- All Active Tempbans number
- All Active Warnings number
- All Admins number
- Players in the watchlist number
- Total Players number
