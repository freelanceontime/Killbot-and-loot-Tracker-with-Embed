import websocket
from discord import SyncWebhook
from websocket import create_connection
import discord
import re
import requests
import json
from bs4 import BeautifulSoup
import time

minitemprice = 50000000

# Add your Corp or Alliance ID
allianceID = 99001105
allianceName = "Seventh Sanctum."
corporationID = ""
corpName = ""
allalliancekillswebhookurl = "https://discord.com/api/webhooks/1040550494185209948/t6cmlErFvq95y61g-hClAFAADiZWMdMKtwIxQ7M1qaLPjqUM42vdAaAnG_9GYzoCm14v"
lootchannelwebhookurl = "https://discord.com/api/webhooks/1040558610406711296/8sC7atPSoXXsnEUICeyf1H6t5OHfkGlVyxYKrJS14-OH7-4tpa8bJeDKLyW7SVkAdIrP"

global toggle
toggle = False

def getkill():

    print("New Connection Established")
    ws = create_connection("wss://zkillboard.com/websocket/")

    # Comment Out Either the Alliance or Corp
    ws.send('{"action":"sub","channel":"alliance:' + str(allianceID) + '"}')
    #ws.send('{"action":"sub","channel":"corporation:' + str(corporationID) + '"}')

    while True:
        urls = []
        result =  ws.recv()
        data = json.loads(result)
        urls.append(data['url'])

        for i in range(len(urls)): 
          
            killid = (str(urls[i]))

            page = requests.get(killid)
            soup = BeautifulSoup(page.content, 'html.parser', on_duplicate_attribute='ignore')

            imageurl = soup.find("meta", attrs={'name':'og:image'}, content=True)
            image = imageurl["content"] + "?size=64"

            
            tab = soup.find("table",{"class":"table table-condensed"})
            names = tab.findAll("a")[0]
            corps = tab.findAll("a")[1]
            alliances = tab.findAll("a")[2]

            tab2 = soup.find("table",{"class":"table table-condensed table-striped table-hover"})
            row = tab2.find_all('tr')

            tab3 = soup.find("th",{"class":"hidden-md hidden-xs"})
            involved = tab3.text.strip()

            try:
                description = soup.find("meta", attrs={'name':'og:description'}, content=True)
                cleanDescription = (description["content"])
                separator = 'Final Blow by '
                result_1 = cleanDescription.split(separator, 1)[1]
                separator2 = '. Total Value'
                result_2 = result_1.split(separator2, 1)[0]
                embed.add_field(name="Final Blow by", value=result_2, inline=True)
            except:
                pass

            column1 = []
            column2 = []
            
            for row in tab2.find_all('tr'):
                columns1 = row.find_all("th")
                columns2 = row.find_all("td")
                if(columns1[0].text.strip()) != "Location:" and (columns1[0].text.strip()) != "Faction:" and (columns1[0].text.strip()) != "Related:" and (columns1[0].text.strip()) != "Time:" and (columns1[0].text.strip()) != "Points:" and (columns1[0].text.strip()) != "Damage:" and (columns1[0].text.strip()) != "Ship+Fit:" and (columns1[0].text.strip()) != "Dropped:" and (columns1[0].text.strip()) != "Destroyed:":
                    if (columns1[0].text.strip()) == "Ship:":
                        ship = columns2[0].text.split('(',1)[0]
                    elif (columns1[0].text.strip()) == "System:":
                        system = columns2[0].text.split('(',1)[0]
                    else:
                        column1.append(columns1[0].text.strip())
                        column2.append(columns2[0].text.strip())       

            for name in names:
                name = names.get('title')

            for corp in corps:
                corp = corps.get('title')

            for alliance in alliances:
                alliance = alliances.get('title')

            title = ship.strip() + " destroyed in " + system.strip()

            if alliance == allianceName:
                choosecolour = discord.Colour.red()
            else:
                choosecolour = discord.Colour.green()

            embed = discord.Embed(title=title, url=killid, colour = choosecolour)
            embed.set_thumbnail(url=image)
            embed.add_field(name="Victim", value=name, inline=True)
            embed.add_field(name="Corporation", value=corp, inline=True)
            embed.add_field(name="Alliance", value=alliance, inline=True)
            embed.add_field(name="Involved", value=involved, inline=True)
            for i in range(len(column1)):
                embed.add_field(name=column1[i], value=column2[i], inline=True)

            webhook = SyncWebhook.from_url(allalliancekillswebhookurl) 
            webhook.send(embed=embed)

            print("kill reported")

            itemname = []
            quantity = []
            price = []
            
            table1 = soup.find_all('table')[5]
            row = table1.find_all('tr')

            for row in table1.find_all('tr'):    
                columns = row.find_all("td", {"class": "item_dropped"})
                if(columns != []):
                    itemname.append(columns[0].text.strip())
                    string = str(columns[0])
                    y = re.search(r"item/([0-9.]+)/", string)
                    item = y.group(1)
                    amount = (columns[1].text.strip())
                    amount = amount.replace(',','')
                    quantity.append(amount)
                    page1 = requests.get("https://api.evemarketer.com/ec/marketstat?typeid=" + item)
                    soup1 = BeautifulSoup(page1.content, 'html.parser', on_duplicate_attribute='ignore')
                    data = str(soup1)
                    x = re.search(r"max>([0-9.]+)<", data)
                    value = x.group(1)
                    valuestrip = value[:-3]
                    priceitem = int(valuestrip) * int(amount)
                    price.append(priceitem)

            for i in range(len(price)):
                if price[i] >= minitemprice:
                    global toggle
                    toggle = True
                    valuenumber = "{:,}".format(price[i])
                    webhook = SyncWebhook.from_url(lootchannelwebhookurl)    
                    webhook.send(str(quantity[i]) + " " + itemname[i] + "\nValued at " + str(valuenumber))
                else:
                    print("Not Worth Looting")

            if toggle == True:
                webhook = SyncWebhook.from_url(lootchannelwebhookurl) 
                webhook.send(embed=embed) 
                toggle = False

while True:
    # try:
    getkill()
    # except:
    #     print("Connection Lost")
    #     pass


