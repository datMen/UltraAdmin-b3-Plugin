-===··> UltraAdmin Plugin <··===-
-·> Plugin for B3 (www.bigbrotherbot.com)
-·> Author: LouK(8thelouk8@gmail.com) from the Sni:{Per}:Jum Clan: http://sniperjum.wix.com/clan

-===··> Installation of UltraAdmin for B3 <··===-

* Place ultraadmin.py in /extplugins/ and ultraadmin.xml in /extplugins/conf/
* In your b3.xml config, add this line:

<plugin name="ultraadmin" config="@b3/extplugins/conf/ultraadmin.xml"/>

* Change command levels & messages layout(do not change the %s order) in the ultraadmin.xml

---·> Requirements <·---

In order to use this plugin, you need to have some other's in your b3:
note: These plugins doesn't belong to me, if you have questions about them, please contact with the owner.

Follow Plugin: http://forum.bigbrotherbot.net/releases/follow-users-plugin
Geowelcome Plugin: http://forum.bigbrotherbot.net/releases/geowelcome-plugin

---·> Commands <·---

-·> !ultrauserinfo or !uui: Display information about the selected player:
- 1: Server id: playerlist number
- 2: Exact player's name
- 3: b3 @id
- 4: b3 group & level
- 5: Player's connections number
- 6: Player's IP
- 7: Player's location(see http://forum.bigbrotherbot.net/releases/geowelcome-plugin geowelcome plugin)
- 8: Watchlist: If the player is in the watchlist(displayed only if the player is in watchlist)(see http://forum.bigbrotherbot.net/releases/follow-users-plugin follow plugin) 
- 9: Aliases: 5 aliases(displayed only if the player has aliases)
- 10: Active warns(displayed only if the player has active warns)
- 11: Past bans(displayed only if the player has past bans)

-·> !ultralist or !ul: Display information(less than uui) about connected players:
- 1: Server id: playerlist number
- 2: Exact player's name
- 3: b3 @id
- 4: b3 level
- 5: Player's connections number
- 6: Player's IP
- 7: Active warns(number)
- 8: Past bans(number)
