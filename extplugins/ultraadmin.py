#
# UltraAdmin Plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA	   02110-1301	 USA

__version__ = '2.0'
__author__  = 'LouK'

import b3, thread, time
import b3.plugin

from b3.translator import translate
from b3 import geoip
from b3 import functions
#--------------------------------------------------------------------------------------------------
class UltraadminPlugin(b3.plugin.Plugin):
    _adminPlugin = None

    _SELECT_QUERY = "SELECT client_id, reason, admin_id FROM following WHERE client_id = %s"
    _DEFAULT_REASON = "cheating"

    def startup(self):
      """\
      Initialize plugin settings
      """

   # get the admin plugin so we can register commands
      self._adminPlugin = self.console.getPlugin('admin')
      if not self._adminPlugin:
      # something is wrong, can't start without admin plugin
        self.error('Could not find admin plugin')
        return False
    
    # register our commands (you can ignore this bit)
      if 'commands' in self.config.sections():
        for cmd in self.config.options('commands'):
          level = self.config.get('commands', cmd)
          sp = cmd.split('-')
          alias = None
          if len(sp) == 2:
            cmd, alias = sp

          func = self.getCmd(cmd)
          if func:
            self._adminPlugin.registerCommand(self, cmd, level, func, alias)

      self.debug('Started')
            
    def get_all_player_bans(self,  client):
        cursor = self.console.storage.query(
        """SELECT COALESCE((SELECT DISTINCT clients.name FROM clients
        WHERE clients.id =  penalties.admin_id),'^2Auto-Ban^7' )AS name, reason, time_expire FROM  penalties 
        INNER JOIN clients ON client_id = clients.id
        WHERE (type =  "Ban" OR  type =  "Tempban") AND clients.id = %s """ %(client.id))
        bans = []
        if cursor.rowcount > 0:
            while not cursor.EOF:
                r = cursor.getRow()
                bans.append("by %s, reason: ^1%s ^7until ^3%s" %(r['name'],  r['reason'],  self.console.formatTime(r['time_expire'])))
                cursor.moveNext()
        cursor.close()
        return bans

    def get_client_location(self, client):
        if client.isvar(self,'localization'):
            return client.var(self, 'localization').value    
        else:
            # lets find the country
            try:
                ret = geoip.geo_ip_lookup(client.ip)
                if ret:
                    client.setvar(self, 'localization', ret)
                return ret
            except Exception, e:
                self.error(e)
                return False
 

    def getCmd(self, cmd):
      cmd = 'cmd_%s' % cmd
      if hasattr(self, cmd):
        func = getattr(self, cmd)
        return func

      return None
#--------Commands-----------------------------------------------------

    def cmd_ultrauserinfo(self, data, client=None, cmd=None):
        """\
        <name> - display player's ultra information.
        """

        if not self.console.storage.status():
            cmd.sayLoudOrPM(client, '^7Cannot lookup, database apears to be ^1DOWN')
            return False		
        input = self._adminPlugin.parseUserCmd(data)
        input = data.split(' ',1)
        if not input:
            client.message('^7correct syntax is ^2!ultrauserinfo ^7<name>')
            return False
        
        cid = input[0]
        sclient = self._adminPlugin.findClientPrompt(cid, client)
        if not sclient:
            client.message('^7correct syntax is ^2!ultrauserinfo ^7<name>')
            return

        self._country_format = '^1%(city)s ^7[^3%(country_name)s^7]'
        bans = self.get_all_player_bans(sclient)
        location = self.get_client_location(sclient)
        clients = self.console.clients.getClientsByLevel()
        cursor = self.console.storage.query(self._SELECT_QUERY % sclient.id)
        if location:
            country = translate(self._country_format % location)
            cmd.sayLoudOrPM(client, self.getMessage('general_info', sclient.cid, sclient.exactName, sclient.id, sclient.maxGroup.name, sclient.maxLevel, sclient.connections, sclient.ip, country))
        else:
            cmd.sayLoudOrPM(client, '^7%s: %s^7 [^2@%s^7] is a  ^2%s^7 [^1%s^7], connected: ^6%s ^7times. ^4%s ^7from: %s' % (sclient.cid, sclient.exactName, sclient.id, sclient.maxGroup.name, sclient.maxLevel, sclient.connections, sclient.ip))
    
        if sclient not in clients:
            cmd.sayLoudOrPM(client, 'Last seen: %s' % self.console.formatTime(sclient.timeEdit))

        if cursor.rowcount > 0:
            r = cursor.getRow()
            admin = self._adminPlugin.findClientPrompt("@%s" % r['admin_id'], client)
            if admin:
                admin_name = admin.name
            else:
                admin_name = 'B3'
            if r['reason'] and r['reason'] != '' and r['reason'] != 'None':
                reason = r['reason']
            else:
                reason = self._DEFAULT_REASON
            cmd.sayLoudOrPM(client, self.getMessage('watchlist_info', admin_name, reason))
        else:
            cmd.sayLoudOrPM(client, "")

        if sclient:
            warns = sclient.numWarnings
            myaliases = []
            for a in sclient.aliases:
                myaliases.append('%s' % a.alias)
                if len(myaliases) > 4:
                    myaliases.append('^7[^2more^7]')
                    break

            if len(myaliases):
                cmd.sayLoudOrPM(client, "^3Aliases^7: %s" % (', '.join(myaliases)))
            else:
                cmd.sayLoudOrPM(client, '')
 
            if warns:
                msg = ''
                warn = sclient.firstWarning
                if warn:
                    expire = functions.minutesStr((warn.timeExpire - (self.console.time())) / 60)
                    msg = '^7. expires in ^5%s' % expire
                warn = sclient.lastWarning
                if warn:
                    msg += '^7: ^3%s' % warn.reason
                message = '^1Warnings^7: ^4%s %s' % (warns, msg)
            else:
                message = ''
                
            cmd.sayLoudOrPM(client, message)

        if len(bans) == 0:
            return True

        cmd.sayLoudOrPM(client, "^1Past Bans^7: ^4%s"  % len(bans))
        for b in bans:
            cmd.sayLoudOrPM(client,  b)

    def cmd_ultralist(self, data, client, cmd=None):
        """\
        - list ultra information for all players in the server.
        """
        thread.start_new_thread(self.doUltraList, (client, cmd))

    def doUltraList(self, client, cmd):
        names = []
        for c in self.console.clients.getClientsByLevel():
            pastbans = self.console.storage.query("""SELECT id FROM penalties WHERE (type = "tempban" OR type = "ban") AND client_id = "%s" """ % c.id)
            names.append(self.getMessage('ultra_list', c.cid, c.name, c.id, c.maxLevel, c.connections, c.numWarnings, pastbans.rowcount))
                         
        for b in names:
            cmd.sayLoudOrPM(client,  b)
        return True
        
    def cmd_ultraserverinfo(self, data, client=None, cmd=None):
        """\
        or <variable> - list ultra information about the server.
        """
            
        #Get server information
        gametype = self.console.getCvar('g_gametype').getInt()
        
        if gametype==0:
            gametype='Free For All'
        if gametype==1:
            gametype='Last Man Standing'
        if gametype==3:
            gametype='Team Death Match'
        if gametype==4:
            gametype='Team Survivor'
        if gametype==7:
            gametype='Capture The Flag'
        if gametype==8:
            gametype='Bomb'
        if gametype==9:
            gametype='Jump'

        if  data is None or data=='':
            cmd.sayLoudOrPM(client, "^7Server: %s" % self.console.getCvar('sv_hostname').getString())
            cmd.sayLoudOrPM(client, "^7IP: ^2%s^7:^5%s" % (self.console._publicIp, self.console._port))
            cmd.sayLoudOrPM(client, "^7Version: ^5%s" % self.console.getCvar('version').getString())
            cmd.sayLoudOrPM(client, "^7Public Slots: ^2%s" % self.console.getCvar('sv_maxclients').getString())
            cmd.sayLoudOrPM(client, "^7Private Slots: ^2%s" % self.console.getCvar('sv_privateClients').getString())
            cmd.sayLoudOrPM(client, "^7Gametype: ^5%s" % gametype)
            cmd.sayLoudOrPM(client, "^7Timelimit: ^2%s" % self.console.getCvar('timelimit').getString())
            cmd.sayLoudOrPM(client, "^7Fraglimit: ^2%s" % self.console.getCvar('fraglimit').getString())
            cmd.sayLoudOrPM(client, "^7Current map: ^2%s" % self.console.getCvar('mapname').getString())
            cmd.sayLoudOrPM(client, "^7Next Map: ^2%s" % self.console.getNextMap())
            return False
        else:
            input = self._adminPlugin.parseUserCmd(data)
            variable = input[0]
            if (variable == "servername") or (variable == "server"):
                cmd.sayLoudOrPM(client, "^7Server: %s" % self.console.getCvar('sv_hostname').getString())
            elif (variable == "serverip") or (variable == "ip"):
                cmd.sayLoudOrPM(client, "^7IP: ^2%s^7:^5%s" % (self.console._publicIp, self.console._port))
            elif (variable == "serverversion") or (variable == "version"):
                cmd.sayLoudOrPM(client, "^7Version: ^5%s" % self.console.getCvar('version').getString())
            elif (variable == "publicslots") or (variable == "pubslots"):
                cmd.sayLoudOrPM(client, "^7Public Slots: ^2%s" % self.console.getCvar('sv_maxclients').getString())
            elif (variable == "privateslots") or (variable == "privslots"):
                cmd.sayLoudOrPM(client, "^7Private Slots: ^2%s" % self.console.getCvar('sv_privateClients').getString())
            elif (variable == "gametype") or (variable == "gt"):
                cmd.sayLoudOrPM(client, "^7Gametype: ^5%s" % gametype)
            elif (variable == "timelimit") or (variable == "tlimit"):
                cmd.sayLoudOrPM(client, "^7Timelimit: ^2%s" % self.console.getCvar('timelimit').getString())
            elif (variable == "fraglimit") or (variable == "flimit"):
                cmd.sayLoudOrPM(client, "^7Fraglimit: ^2%s" % self.console.getCvar('fraglimit').getString())
            elif (variable == "currentmap") or (variable == "map"):
                cmd.sayLoudOrPM(client, "^7Current map: ^2%s" % self.console.getCvar('mapname').getString())
            elif (variable == "nextmap") or (variable == "nm"):
                cmd.sayLoudOrPM(client, "^7Next Map: ^2%s" % self.console.getNextMap())
            else:
                client.message("Couldn't find your request")
        
    def cmd_ultrab3(self, data, client=None, cmd=None):
        """\
        or <variable> - list ultra information about the server.
        """
        
        
        if not self.console.storage.status():
            cmd.sayLoudOrPM(client, '^7Cannot lookup, database apears to be ^1DOWN')
            return False
            
        #Get SQL information
        players = self.console.storage.query("""SELECT * FROM clients """)
        total_admins = self.console.storage.query("""SELECT id FROM clients WHERE (group_bits='32' OR group_bits='256' OR group_bits='4096' OR group_bits='65536' OR group_bits='2097152') """)
        total_regulars = self.console.storage.query("""SELECT id FROM clients WHERE group_bits='2' """)
        follow = self.console.storage.query("""SELECT id FROM following """)
        totalbans = self.console.storage.query("""SELECT id FROM penalties WHERE (type = "tempban" OR type = "ban") """)
        permbans = self.console.storage.query("""SELECT id FROM penalties WHERE type= 'ban' AND time_expire = '-1' """)
        warns = self.console.storage.query("""SELECT c.id, c.name, p.time_expire FROM penalties p, clients c  WHERE p.client_id = c.id AND p.inactive = 0 AND  type='Warning' AND p.time_expire >= UNIX_TIMESTAMP() """)
        tempbans = self.console.storage.query("""SELECT id FROM penalties WHERE type= 'tempban' AND inactive = 0 AND time_expire >= UNIX_TIMESTAMP() """)
        uptime = functions.minutesStr(self.console.upTime() / 60.0)
        
        if data is None or data=='':
            cmd.sayLoudOrPM(client, '^7Version: ^1%s' % b3.version)
            cmd.sayLoudOrPM(client, '^7Uptime: [^2%s^7]' % uptime)
            cmd.sayLoudOrPM(client, "^7Total Players: ^5%s" % players.rowcount)
            cmd.sayLoudOrPM(client, "^7Admins: ^5%s" % total_admins.rowcount)
            cmd.sayLoudOrPM(client, "^7Regulars: ^5%s" % total_regulars.rowcount)
            cmd.sayLoudOrPM(client, "^7Players in Watchlist: ^5%s" % follow.rowcount)
            cmd.sayLoudOrPM(client, "^7Permbans: ^5%s" % permbans.rowcount)
            cmd.sayLoudOrPM(client, "^7Active Tempbans: ^5%s" % tempbans.rowcount)
            cmd.sayLoudOrPM(client, "^7Active Warnings: ^5%s" % warns.rowcount)
            return False
        else:
            input = self._adminPlugin.parseUserCmd(data)
            variable = input[0]
            if (variable == "b3version") or (variable == "version"):
                cmd.sayLoudOrPM(client, '^7Version: ^1%s' % b3.version)
            elif (variable == "b3uptime") or (variable == "uptime"):
                cmd.sayLoudOrPM(client, '^7Uptime: [^2%s^7]' % uptime)
            elif (variable == "b3players") or (variable == "players") or (variable == "allplayers") or (variable == "totalplayers"):
                cmd.sayLoudOrPM(client, "^7Total Players: ^5%s" % players.rowcount)
            elif (variable == "b3admins") or (variable == "admins"):
                cmd.sayLoudOrPM(client, "^7Admins: ^5%s" % total_admins.rowcount)
            elif (variable == "b3regulars") or (variable == "regulars") or (variable == "regs"):
                cmd.sayLoudOrPM(client, "^7Regulars: ^5%s" % total_regulars.rowcount)
            elif (variable == "watchlist") or (variable == "follow") or (variable == "following") or (variable == "b3watchlist"):
                cmd.sayLoudOrPM(client, "^7Players in Watchlist: ^5%s" % follow.rowcount)
            elif (variable == "permbans") or (variable == "totalbans") or (variable == "bans") or (variable == "pbans"):
                cmd.sayLoudOrPM(client, "^7Permbans: ^5%s" % permbans.rowcount)
            elif (variable == "tempbans") or (variable == "tbans") or (variable == "totaltempbans"):
                cmd.sayLoudOrPM(client, "^7Active Tempbans: ^5%s" % tempbans.rowcount)
            elif (variable == "currentmap") or (variable == "map"):
                cmd.sayLoudOrPM(client, "^7Current map: ^2%s" % self.console.getCvar('mapname').getString())
            elif (variable == "warns") or (variable == "warnings")  or (variable == "activewarnings"):
                cmd.sayLoudOrPM(client, "^7Active Warnings: ^5%s" % warns.rowcount)
            else:
                client.message("Couldn't find your request")

    def cmd_ultraadmins(self, data, client=None, cmd=None):
        """\
        or <level> - list all online/offline admins in the server.
        """
        input = self._adminPlugin.parseUserCmd(data)
        
        if not data:
            level = 20
            cursor = self.console.storage.query("""SELECT clients.id, COALESCE((SELECT DISTINCT aliases.alias FROM aliases WHERE aliases.client_id =  clients.id ORDER BY aliases.num_used DESC LIMIT 1), clients.name ) AS admin, level FROM clients, groups WHERE clients.group_bits = groups.id AND level >= %s ORDER BY group_bits DESC """ % level)
        else:
            variable = input[0]
            if (variable == "100") or (variable == "superadmin") or (variable == "superadmins"):
                level = 100
            elif (variable == "90") or (variable == "cofounders") or (variable == "headadmins"):
                level = 90
            elif (variable == "80") or (variable == "senioradmin") or (variable == "senioradmins"):
                level = 80
            elif (variable == "60") or (variable == "fulladmin") or (variable == "fulladmins"):
                level = 60
            elif (variable == "40") or (variable == "admins") or (variable == "admin"):
                level = 40
            elif (variable == "20") or (variable == "mod") or (variable == "moderators"):
                level = 20
            elif (variable == "15") or (variable == "member") or (variable == "members"):
                level = 15
            elif (variable == "10") or (variable == "recruit") or (variable == "recruits"):
                level = 10
            elif (variable == "5") or (variable == "premium") or (variable == "premiums"):
                level = 5
            elif (variable == "2") or (variable == "reg") or (variable == "regulars"):
                level = 2
            elif (variable == "1") or (variable == "user") or (variable == "users"):
                if client.maxLevel < 100:
                    client.message('Only superadmins can see all users')
                    return False
                else:
                    level = 1
            elif (variable == "0") or (variable == "guest") or (variable == "guests"):
                if client.maxLevel < 100:
                    client.message('Only superadmins can see all guests')
                    return False
                else:
                    level = 0
            else:
                client.message("Couldn't find your request")
                return False
            
            cursor = self.console.storage.query("""SELECT clients.id, COALESCE((SELECT DISTINCT aliases.alias FROM aliases WHERE aliases.client_id =  clients.id ORDER BY aliases.num_used DESC LIMIT 1), clients.name ) AS admin, level FROM clients, groups WHERE clients.group_bits = groups.id AND level = %s ORDER BY group_bits DESC """ % level)
        
        admins = []
        if cursor.rowcount > 0:
            while not cursor.EOF:
                r = cursor.getRow()
                admin = r['admin']
                id = r['id']
                level = r['level']
                admins.append(self.getMessage('ultra_admins', r['admin'], r['id'], r['level']))
                cursor.moveNext()
        cursor.close()
        
        for b in admins:
            cmd.sayLoudOrPM(client,  b)
        return False
    
    def cmd_listplugins(self, data, client=None, cmd=None):
        """\
        - list all installed plugins.
        """
        plugins = []
        for pname in self.console._pluginOrder:
            plugins.append("^2%s ^7%s" % (pname, getattr(getModule(self.console.getPlugin(pname).__module__), '__version__', '__name__')))
        
        for b in plugins:
            cmd.sayLoudOrPM(client, b)
        return True
    
    def cmd_unmaskall(self, data, client=None, cmd=None):
        """\
        - unmask all players in the server.
        """
        for c in self.console.clients.getClientsByLevel():
            if c.maskLevel > 0:
                c.maskLevel = 0
                c._maskGroup = None
                c.save()
        
        client.message('You unmasked all clients in the server')
        
    def cmd_checkmasked(self, data, client, cmd=None):
        """\
        - check masked players in the server.
        """
        thread.start_new_thread(self.doCheckMaskList, (client, cmd))

    def doCheckMaskList(self, client, cmd):
        names = []
        for c in self.console.clients.getClientsByLevel():
            if c.maskLevel > 0:
                names.append('%s Mask level: ^2%s' % (c.exactName, c.maskGroup.name))
         
        if len(names) == 0:
            client.message('There are no masked players in the server') 
        else:
            for b in names:
                cmd.sayLoudOrPM(client,  b)
            return True
