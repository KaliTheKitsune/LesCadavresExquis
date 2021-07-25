import discord
import asyncio
import json
import random
import os
import logging
from discord.ext import commands

# defining bot api permissions
intent = discord.Intents.default()
intent.members = True
intent.presences = False

bot = commands.Bot(command_prefix='ce!', intents=intent)
bot.remove_command("help")

"""
GENERAL
    ingame = {userids: "gameid"}
    quitm = {messageid: [userid, oldgameid, newgameid]}
    ready = TRUE/FALSE
GAMES
    ID
        USERS
            [userids]
        DATA
            fillable: TRUE/FALSE
            started: TRUE/FALSE
            channelid: ID
            structure: []
            waiting: "player who waiting for",
            url: "url"
"""

# Initialize logging configuration
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] {%(module)s} - %(funcName)s: %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

async def deleteQuitMessage(id):
    content = getFile()
    user = bot.get_user(content["GENERAL"]["quitm"][str(id)][0])
    if user.id == bot.user.id: pass
    content["GENERAL"]["ingame"][str(user.id)] = content["GENERAL"]["quitm"][str(id)][2]
    if user.dm_channel is None:
        await user.create_dm()
    message = await user.dm_channel.fetch_message(int(id))
    await message.delete()
    content["GENERAL"]["quitm"].pop(str(id))

async def alreadyInGame(user, newgameid):
    data = getFile()
    embed = discord.Embed(
        title= "Vous devez quitter votre partie actuelle avant d'en rejoindre une autre !",
        description= "*cliquez sur 🔁 pour rejoindre et quitter l'ancienne !*",
        url= data["GAMES"][str(data["GENERAL"]["ingame"][str(user.id)])]["DATA"]["url"]
    )
    embed.set_footer(text="Cliquez sur le titre pour accèsder à la partie actuelle.")
    message = await user.send(embed= embed)
    await message.add_reaction("🔁")
    data["GENERAL"]["quitm"][str(message.id)] = [user.id, data["GENERAL"]["ingame"][str(user.id)], newgameid]
    updateFile(data)

def updateFile(newdata):
    with open(os.path.join(".", "data.json"), "r") as f:
        content = json.load(f)
    content = newdata
    with open(os.path.join(".", "data.json"), "w") as f:
        json.dump(content, f, indent= 4)

def getFile():
    with open(os.path.join(".", "data.json"), "r") as f:
        return json.load(f)

def getWordDB():
    with open(os.path.join(".", "wordbase.json"), "r") as f:
        return json.load(f)

def deleteGameData(messageid):
    content = getFile()
    for u in content["GAMES"][str(messageid)]["USERS"]:
        if str(u) in content["GENERAL"]["ingame"]:
            content["GENERAL"]["ingame"].pop(str(u))
    content["GAMES"].pop(messageid)
    updateFile(content)

async def timeout(id):
    try:
        await asyncio.sleep(30)
        content = getFile()
        content["GAMES"][str(id)]["DATA"]["fillable"] = True
        updateFile(content)
        channel = bot.get_channel(content["GAMES"][str(id)]["DATA"]["channelid"])
        message = await channel.fetch_message(int(id))
        await message.add_reaction("♾️")
        await message.add_reaction("🤖")
        await asyncio.sleep(7080)
        for userid in content["GAMES"][str(id)]["USERS"]:
            content["GENERAL"]["ingame"].pop(str(userid))
        content["GAMES"].pop(str(id))
        updateFile(content)
    except:
        pass


    if id in content:
        deleteGameData(id)
        channel = bot.get_channel(content["GAMES"][id]["DATA"]["channelid"])
        message = await channel.fetch_message(id)
        embed = discord.Embed(
            title= "Les Cadavres Exquis",
            description=  ":x: La partie ne figure plus dans la base de donnée, merci de la recréer...",
            colour=  0xf1c40f
        )
        await message.edit(embed= embed)
        await message.clear_reactions()
    
async def deletemTimeout(id):
    await asyncio.sleep(300)
    content = getFile()
    if id in content["GENERAL"]["quitm"]:
        deleteQuitMessage(id)
        

async def updatePlayerList(messageid):
    data = getFile()
    text = ""
    u = 0
    for x in data["GAMES"][str(messageid)]["USERS"]:
        try:
            text = f"{text}- <@!{x}>\n"
            u += 1
        except:
            pass
    x = len(data["GAMES"][str(messageid)]["DATA"]["structure"])-len(data["GAMES"][str(messageid)]["USERS"])
    while x != 0:
        text = f"{text}-\n"
        x = x-1
    clearembed = discord.Embed(
        title= "Les Cadavres Exquis",
        description=  "cliquez sur 💬 pour rejoindre !",
        colour=  0xf1c40f
    )
    var= len(data["GAMES"][str(messageid)]["DATA"]["structure"])
    clearembed.add_field(name =f"players ({u}/{var})", value= text)
    channel = bot.get_channel(data["GAMES"][str(messageid)]["DATA"]["channelid"])
    message = await channel.fetch_message(messageid)
    await message.edit(embed= clearembed)
    return clearembed, u









def CCL(url):
    embed = discord.Embed(
        title= "Entrez un complément de lieu:",
        description= "Jouez franc jeu !",
        colour=  0xf1c40f,
        url= url
    )
    rdm = random.choice(getWordDB()["CCL"])
    embed.add_field(name="Exemple:", value=f"`{rdm}`", inline=False)
    embed.set_footer(text=f"Appuyez sur le titre pour voir l'avancée de la partie !")
    return embed

def pick_CCL():
    return random.choice(getWordDB()["CCL"])

def GN(url):
    embed = discord.Embed(
        title= "Entrez un Groupe nominal avec déterminant:",
        description= "Jouez franc jeu !",
        colour= 0xf1c40f,
        url= url
    )
    rdm= random.choice(getWordDB()["GN"][random.choice(list(getWordDB()["GN"]))])
    embed.add_field(name="Exemple:", value=f"`{rdm}`", inline=False)
    embed.set_footer(text=f"Appuyez sur le titre pour voir l'avancée de la partie !")
    return embed

def pick_GN():
    singulier = bool(random.getrandbits(1))
    masculin = bool(random.getrandbits(1))
    if singulier:
        if masculin:
            message = random.choice(getWordDB()["GN"]["masculin singulier"])
        else:
            message = random.choice(getWordDB()["GN"]["feminin singulier"])
    else:
        if masculin:
            message = random.choice(getWordDB()["GN"]["masculin pluriel"])
        else:
            message = random.choice(getWordDB()["GN"]["feminin pluriel"])

    return message, singulier, masculin

async def ask_GN(user, reaction, data):
    def checkm(message):
        return message.author.id != bot.user.id and message.channel == message.author.dm_channel and message.author.id == user.id
    def checke(reaction, user):
        return (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌") and user.id != bot.user.id and message.author.id == user.id and message.channel == message.author.dm_channel


    embed = GN(data["GAMES"][str(reaction.message.id)]["DATA"]["url"])
    await user.send(embed= embed)
    message = await bot.wait_for('message', check=checkm)
    qmessage = await user.send(embed= discord.Embed(title= "Votre sujet est-il singulier ?", colour=  0xf1c40f))
    await qmessage.add_reaction("✅")
    await qmessage.add_reaction("❌")
    ereaction, user = await bot.wait_for("reaction_add", check= checke)
    if ereaction.emoji == "✅":
        singulier = True
    else:
        singulier = False

    qmessage = await user.send(embed= discord.Embed(title= "Votre sujet est-il masculin ?", colour=  0xf1c40f))
    await qmessage.add_reaction("✅")
    await qmessage.add_reaction("❌")
    ereaction, user = await bot.wait_for("reaction_add", check= checke)
    if ereaction.emoji == "✅":
        masculin = True
    else:
        masculin = False

    return message, singulier, masculin

def ADJ(url, singulier, masculin):
    if masculin:
        genre= "masculin"
    else:
        genre= "feminin"
 
    if singulier:
        nombre = "singulier"
    else:
        nombre = "pluriel"
        
    embed = discord.Embed(
        title= "Entrez un ADJ qualificatif:",
        description= "Jouez franc jeu !",
        colour=  0xf1c40f,
        url= url
    )
    rdm= random.choice(getWordDB()["ADJ"][f"{genre} {nombre}"])
    embed.add_field(name="Exemple:", value=f"`{rdm}`", inline=False)
    embed.add_field(name="Note:", value=f"votre adjectif doit s'accorder avec le sujet, celui-ci est **{genre}**, **{nombre}**.", inline=False)
    embed.set_footer(text=f"Appuyez sur le titre pour voir l'avancée de la partie !")
    return embed

def pick_ADJ(singulier, masculin):
    if singulier:
        if masculin:
            message = random.choice(getWordDB()["ADJ"]["masculin singulier"])
        else:
            message = random.choice(getWordDB()["ADJ"]["feminin singulier"])
    else:
        if masculin:
            message = random.choice(getWordDB()["ADJ"]["masculin pluriel"])
        else:
            message = random.choice(getWordDB()["ADJ"]["feminin pluriel"])

    return message

def Verbe(url, singulier):
    if singulier:
        nombre = "singulier"
    else:
        nombre = "pluriel"
    embed = discord.Embed(
        title= "Entrez un verbe conjugué admettant un COD:",
        description= "Jouez franc jeu !",
        colour=  0xf1c40f,
        url= url
    )
    rdm= random.choice(getWordDB()["V"][f"{nombre}"])
    embed.add_field(name="Exemple:", value=f"`{rdm}`", inline=False)
    embed.add_field(name="Note:", value=f"votre verbe doit être conjugué à la **3ème personne** du **{nombre}**.", inline=False)
    embed.set_footer(text=f"Appuyez sur le titre pour voir l'avancée de la partie !")
    return embed

def pick_Verbe(singulier):
    if singulier:
        message = random.choice(getWordDB()["V"]["singulier"])
    else:
        message = random.choice(getWordDB()["V"]["pluriel"])

    return message

def Adverbe(url):
    embed = discord.Embed(
        title= "Entrez un adverbe:",
        description= "Jouez franc jeu !",
        colour=  0xf1c40f,
        url= url
    )
    rdm = random.choice(getWordDB()["A"])
    embed.add_field(name="Exemple:", value=f"`{rdm}`", inline=False)
    embed.set_footer(text=f"Appuyez sur le titre pour voir l'avancée de la partie !")
    return embed

def pick_Adverbe():
    return random.choice(getWordDB()["A"])





@bot.event
async def on_ready():
    content = getFile()
    try:
        content["GENERAL"]["ready"] = False
        updateFile(content)
    except:
        pass

    print(f"We have logged in as {bot.user}, with id {bot.user.id}")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("Bot is starting up !"))

    try:
        for mid in content["GAMES"]:
            channel = bot.get_channel(content["GAMES"][mid]["DATA"]["channelid"])
            message = await channel.fetch_message(mid)
            embed = discord.Embed(
                title= "Les Cadavres Exquis",
                description=  ":x: La partie ne figure plus dans la base de donnée, merci de la recréer...",
                colour=  0xf1c40f
            )
            await message.edit(embed= embed)
            await message.clear_reactions()
    except:
        pass
    try:
        for u in content["GENERAL"]["ingame"]:
            await bot.get_user(int(u)).send(":x: Désolé, le bot a redémarré et est dans l'incapacité de restaurer votre partie, veuillez nous excuser de la gêne occasionnée.")
    except:
        pass

    data = {
        "GENERAL": {
            "ingame": {},
            "ready": True,
            "quitm": {}
        },
        "GAMES": {}
    }
    updateFile(data)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("ce!help"))

@bot.command()
async def custom(ctx, *args):
    if not getFile()["GENERAL"]["ready"]:
        await ctx.message.channel.send(":x: Oops ! Le bot n'as pas encore initialisé sa base de donnée :(, veuillez patienter...")
        return

    if len(args) > 20:
        await ctx.send(":x: votre structure de phrase trop longue !")
        return

    for arg in args:
        if arg not in ["CCL","GN","ADJ", "V", "A"]:
            await ctx.send(f":x: Type de mot invalide: `{arg}`, merci de consulter la liste des types de mots supportés avec la commande ce!support")
            return

    embed = discord.Embed(
        title= "Les Cadavres Exquis",
        description=  "cliquez sur 💬 pour rejoindre !",
        colour=  0xf1c40f
    )
    text = ""
    for x in range(len(args)):
        text = f"{text}-\n"
    embed.add_field(name =f"players (0/{len(args)})", value=text, inline=False)
    join_message = await ctx.message.channel.send(embed= embed)
    await join_message.add_reaction("💬")
    content = getFile()
    content["GAMES"][join_message.id] = {
        "USERS": [],
        "DATA": {
            "fillable": False,
            "started": False,
            "finished": False,
            "channelid": join_message.channel.id,
            "structure": args,
            "waiting": None,
            "url": join_message.jump_url
        }
    }
    updateFile(content)
    bot.loop.create_task(timeout(str(join_message.id)))


@bot.event
async def on_message(message):
    try:
        if message.author == bot.user:
            return
        if message.author.dm_channel is None:
            await message.author.create_dm()
            
        if message.channel.id == message.author.dm_channel.id:
            return
    except:
        pass
    if message.content.startswith('ce!start'):
        if not getFile()["GENERAL"]["ready"]:
            await message.channel.send(":x: Oops ! Le bot n'as pas encore initialisé sa base de donnée :(, veuillez patienter...")
            return
        embed = discord.Embed(
            title= "Les Cadavres Exquis",
            description=  "cliquez sur 💬 pour rejoindre !",
            colour=  0xf1c40f
        )
        embed.add_field(name ="players (0/7)", value="-\n-\n-\n-\n-\n-\n-", inline=False)
        join_message = await message.channel.send(embed= embed)
        await join_message.add_reaction("💬")
        content = getFile()
        content["GAMES"][join_message.id] = {
            "USERS": [],
            "DATA": {
                "fillable": False,
                "started": False,
                "finished": False,
                "channelid": join_message.channel.id,
                "structure": ["CCL","GN","ADJ", "V", "A", "GN", "ADJ"],
                "waiting": None,
                "url": join_message.jump_url
            }
        }
        updateFile(content)
        bot.loop.create_task(timeout(str(join_message.id)))
    elif message.content.startswith('ce!help'):
        embed = discord.Embed(
            title= "Les Cadavres Exquis - AIDE",
            description=  "le préfix du bot est: `ce!`",
            colour=  0x3498db
        )
        embed.add_field(name="COMMANDES D'INFORMATION:",value="Toutes les commandes relatives au bot.", inline=False)
        embed.add_field(name="help", value="Affiche ce menu.", inline=False)
        embed.add_field(name="description", value= "Donne le but du jeu du cadavre exqui.")
        embed.add_field(name="credits", value="Affiche les crédits.", inline=False)
        embed.add_field(name="tos", value="Affiche les informations relatives à la collecte de données.",inline=False)
        embed.add_field(name="support", value="Affiche la liste des types de mots supportés.",inline=False)
        embed.add_field(name="invite", value="Donne le lien d'invitation du bot.",inline=False)
        embed.add_field(name="COMMANDES DE JEU:",value="Toutes les commandes relatives au jeu.", inline=False)
        embed.add_field(name="start", value="Lance une partie avec les paramètres par défaut.",inline=False)
        embed.add_field(name="custom", value="Lance une partie avec la structure de phrase de votre choix(/!\ nous ne vérifions pas votre phrase, la structure de phrase peut être invalide.).",inline=False)
        await message.channel.send(embed=embed)
    elif message.content.startswith('ce!support'):
        embed = discord.Embed(
            title= "Les Cadavres Exquis - TYPES DE MOTS SUPPOTÉS",
            description=  "La liste des différents types de mots supportés dans les cadavres exquis customs",
            colour=  0x3498db
        )
        embed.add_field(name="Complément circonstentiel de lieu",value="CCL", inline=False)
        embed.add_field(name="Groupe nominal avec déterminant",value="GN", inline=False)
        embed.add_field(name="Adjectif quallificatif",value="ADJ", inline=False)
        embed.add_field(name="Verbe conjugué admettant un COD",value="V", inline=False)
        embed.add_field(name="Adverbe",value="A", inline=False)
        await message.channel.send(embed=embed)
    elif message.content.startswith("ce!description"):
        embed = discord.Embed(
            title= "Les cadavres exquis - DESCRIPTION",
            colour=  0x3498db,
            description= "Jeu collectif qui vise à produire un texte à l’aide de fragments proposés successivement par chaque joueur, chacun ignorant les propositions de ses prédécesseurs. Pour la version textuelle, le joueur connait la nature (nominale, verbale, adjectivale, complémentaire) que doit revêtir sa proposition, afin que le texte finalement formé soit grammaticalement correct."
        )
        await message.channel.send(embed=embed)
    elif message.content.startswith('ce!invite'):
        embed = discord.Embed(
            title= "[Appuyez ici pour être redirigé vers la page d'invitation]",
            url= f"https://discord.com/api/oauth2/authorize?client_id={bot.id}&permissions=93248&scope=bot"
        )
        await message.channel.send(embed=embed)
    elif message.content.startswith('ce!credits'):
        embed = discord.Embed(
            title= "Les Cadavres Exquis - CREDITS",
            description=  "Tous ceux ayant participés de près ou de loin à la création du bot",
            colour=  0x3498db
        )
        embed.add_field(name="Développement:",value="Kalitsune", inline=False)
        embed.add_field(name="Création de la base de connaissances du bot:",value="-§ir Acolamona \n-Psycho Force \n-モンキー・Ｄ・ルフィ \n-Kalitsune \n-whitecraft299", inline=False)
        await message.channel.send(embed=embed)
    elif message.content.startswith('ce!tos'):
        embed = discord.Embed(
            title= "Les Cadavres Exquis - TOS",
            description=  "Relatif à la collecte de donnée.",
            colour=  0x3498db
        )
        embed.add_field(name="ID de chaques joueurs étant inscrits dans un cadavre exqui*",value="Pourquoi ? Nous en avons besoin pour vous retrouver, vous envoyer un message, ou vous mentionner dans l'avancement de la partie.", inline=False)
        embed.add_field(name="ID du salon*",value="Pourquoi ? Nous en avons besoin pour retrouver, mettre à jour le message indiquant le déroulement de la partie et pour stocker les données relatives à votre partie", inline=False)
        embed.add_field(name="Le contenu des messages que vous envoyez au bot*", value="Pourquoi ? Il sagit d'un morceau de la phrase qui constituera le cadavre exqui, nous en avons besoin pour le construire")
        embed.set_footer(text="* = Cette donnée est suprimée à la fin de la partie, deux heures après son début ou lors du redémarrage du bot.")
        await message.channel.send(embed=embed)
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, AttributeError):
        return
    print(error)

@bot.event
async def on_reaction_add(reaction, user):
    data = getFile()
    if str(reaction.message.id) in data["GAMES"]: 
        if user.id == bot.user.id: return
        await reaction.remove(user)
        if getFile()["GAMES"][str(reaction.message.id)]["DATA"]["started"]: 
            return
        if reaction.emoji == "🔓":
            await reaction.message.add_reaction("♾️")
            await reaction.message.add_reaction("🤖")
            data["GAMES"][str(reaction.message.id)]["DATA"]["fillable"] = True
            updateFile(data)

        elif reaction.emoji == "🤖":
            if data["GAMES"][str(reaction.message.id)]["DATA"]["fillable"]:
                foo = []
                for x in range(0, len(data["GAMES"][str(reaction.message.id)]["DATA"]["structure"])):
                    if x <= len(data["GAMES"][str(reaction.message.id)]["USERS"])-1:
                        foo.append(data["GAMES"][str(reaction.message.id)]["USERS"][x])
                        data["GENERAL"]["ingame"][user.id] = reaction.message.id
                    else:
                        foo.append(bot.user.id) 
                data["GAMES"][str(reaction.message.id)]["USERS"] = foo
        elif reaction.emoji == "♾️":
            if data["GAMES"][str(reaction.message.id)]["DATA"]["fillable"]:
                if user.id not in data["GAMES"][str(reaction.message.id)]["USERS"] or not data["GAMES"][str(reaction.message.id)]["DATA"]["fillable"]:
                    return
                foo = []
                for x in range(0, len(data["GAMES"][str(reaction.message.id)]["DATA"]["structure"])):
                    if x <= len(data["GAMES"][str(reaction.message.id)]["USERS"])-1:
                        foo.append(data["GAMES"][str(reaction.message.id)]["USERS"][x])
                        data["GENERAL"]["ingame"][user.id] = reaction.message.id
                    else:
                        i = 0
                        while True:
                            i = i+1
                            item = random.choice(data["GAMES"][str(reaction.message.id)]["USERS"]) 
                            if item != foo[x-1] or i == 10:
                                foo.append(item)
                                break
                data["GAMES"][str(reaction.message.id)]["USERS"] = foo
                    
        elif reaction.emoji == "💬":
            if user.id in data["GAMES"][str(reaction.message.id)]["USERS"]:
                data["GAMES"][str(reaction.message.id)]["USERS"].remove(user.id)
                data["GENERAL"]["ingame"].pop(str(user.id))
            else:
                if str(user.id) not in data["GENERAL"]["ingame"]:
                    if len(data["GAMES"][str(reaction.message.id)]["USERS"]) < len(data["GAMES"][str(reaction.message.id)]["DATA"]["structure"])+1:
                        data["GAMES"][str(reaction.message.id)]["USERS"].append(user.id)
                        data["GENERAL"]["ingame"][user.id] = reaction.message.id
                    else:
                        return
                else:
                    await alreadyInGame(user, reaction.message.id)
                    return
        else:
            return

        updateFile(data)
        clearembed, u = await updatePlayerList(reaction.message.id)

        if u == len(data["GAMES"][str(reaction.message.id)]["DATA"]["structure"]):
            data = getFile()
            data["GAMES"][str(reaction.message.id)]["DATA"]["started"] = True
            updateFile(data)
            await reaction.message.clear_reactions()
            rule = data["GAMES"][str(reaction.message.id)]["DATA"]["structure"]
            singulier = True
            masculin = True
            finalmessage = ""
            it = 0
            for typeobj in rule:

                def checkm(message):
                    return message.author.id != bot.user.id and message.channel == message.author.dm_channel and message.author.id == user.id

                user = bot.get_user(data["GAMES"][str(reaction.message.id)]["USERS"][it])
                
                data["GAMES"][str(reaction.message.id)]["DATA"]["waiting"] = user.id
                updateFile(data)
                text = ""
                u= 0
                for x in data["GAMES"][str(reaction.message.id)]["USERS"]:
                    if u == it:
                        text = f"{text}- <@!{x}> ←\n"
                    else:
                        text = f"{text}- <@!{x}>\n"
                    u = u+1
                embed = discord.Embed(
                    title= "Les Cadavres Exquis",
                    description=  "cliquez sur 💬 pour rejoindre !",
                    colour=  0xf1c40f
                )
                max = len(data["GAMES"][str(reaction.message.id)]["DATA"]["structure"])
                embed.add_field(name =f"players ({u}/{max})", value= text)
                await reaction.message.edit(embed= embed)

                if user.id == bot.user.id:
                    if typeobj == "CCL":
                        message = pick_CCL()
                    
                    elif typeobj == "A":
                        message = pick_Adverbe()

                    elif typeobj == "GN":
                        message, singulier, masculin = pick_GN()

                    elif typeobj == "ADJ":
                        message = pick_ADJ(singulier, masculin)

                    elif typeobj == "V":
                        message = pick_Verbe(singulier)

                else:
                    try:
                        if user.dm_channel is None:
                            await user.create_dm()
                        if typeobj == "CCL":
                            embed = CCL(data["GAMES"][str(reaction.message.id)]["DATA"]["url"])
                            await user.send(embed= embed)
                            message = await bot.wait_for('message', check=checkm, timeout=60)

                        elif typeobj == "GN":
                            message, singulier, masculin = await asyncio.wait_for(ask_GN(user, reaction, data), timeout=60)

                        elif typeobj == "ADJ":
                            embed = ADJ(data["GAMES"][str(reaction.message.id)]["DATA"]["url"], singulier, masculin)
                            await user.send(embed= embed)
                            message = await bot.wait_for('message', check=checkm, timeout=60)

                        elif typeobj == "V":
                            embed = Verbe(data["GAMES"][str(reaction.message.id)]["DATA"]["url"], singulier)
                            await user.send(embed= embed)
                            message = await bot.wait_for('message', check=checkm, timeout=60)

                        elif typeobj == "A":
                            embed = Adverbe(data["GAMES"][str(reaction.message.id)]["DATA"]["url"])
                            await user.send(embed= embed)
                            message = await bot.wait_for('message', check=checkm, timeout=60)
                        
                        message = message.content

                    except asyncio.TimeoutError:
                        await reaction.message.channel.send(f"⏱️ {user} n'a pas répondu à temps et son tour a été sauté !")
                        if typeobj == "CCL" or typeobj == "A":
                            message = pick_CCL()

                        elif typeobj == "GN":
                            message, singulier, masculin = pick_GN()

                        elif typeobj == "ADJ":
                            message = pick_ADJ(singulier, masculin)

                        elif typeobj == "V":
                            message = pick_Verbe(singulier)

                finalmessage = f"{finalmessage} {message}"
                it = it+1
            text = ""
            for x in data["GAMES"][str(reaction.message.id)]["USERS"]:
                text = f"{text}- <@!{x}>\n"
                try:
                    data["GENERAL"]["ingame"].pop(str(x))
                except:
                    pass
            print(finalmessage.strip().capitalize())
            clearembed.add_field(name= "phrase:", value= finalmessage.strip().capitalize(),inline=False)
            await reaction.message.edit(embed= clearembed)
            deleteGameData(str(reaction.message.id))
    elif str(reaction.message.id) in data["GENERAL"]["quitm"]:
        if user.id == bot.user.id: return
        if reaction.emoji == "🔁":
            data = getFile()
            if user.id != data["GAMES"][str(data["GENERAL"]["quitm"][str(reaction.message.id)][1])]["DATA"]["waiting"]:
                for x in range(len(data["GAMES"][str(data["GENERAL"]["quitm"][str(reaction.message.id)][1])]["USERS"])):
                    if user.id == data["GAMES"][str(data["GENERAL"]["quitm"][str(reaction.message.id)][1])]["USERS"][x]:
                        if len(data["GAMES"][str(data["GENERAL"]["quitm"][str(reaction.message.id)][2])]["DATA"]["structure"]) > len(data["GAMES"][str(data["GENERAL"]["quitm"][str(reaction.message.id)][2])]["USERS"]):
                            data["GAMES"][str(data["GENERAL"]["quitm"][str(reaction.message.id)][1])]["USERS"][x] = bot.user.id
                            data["GAMES"][str(data["GENERAL"]["quitm"][str(reaction.message.id)][2])]["USERS"].append(user.id)

                            for it in  [1, 2]:
                                text = ""
                                u = 0
                                for x in data["GAMES"][str(data["GENERAL"]["quitm"][str(reaction.message.id)][it])]["USERS"]:
                                    try:
                                        text = f"{text}- <@!{x}>\n"
                                        u = u+1
                                    except:
                                        pass
                                x = len(data["GAMES"][str(reaction.message.id)]["DATA"]["structure"])-len(data["GAMES"][str(data["GENERAL"]["quitm"][str(reaction.message.id)][it])]["USERS"])
                                while 0 != x:
                                    text = f"{text}-\n"
                                    x = x-1
                                clearembed = discord.Embed(
                                    title= "Les Cadavres Exquis",
                                    description=  "cliquez sur 💬 pour rejoindre !",
                                    colour=  0xf1c40f
                                )
                                var= len(data["GAMES"][str(data["GENERAL"]["quitm"][str(reaction.message.id)][it])]["DATA"]["structure"])
                                clearembed.add_field(name =f"players ({u}/{var})", value= text)
                                channel = bot.get_channel(data["GAMES"][str(data["GENERAL"]["quitm"][str(reaction.message.id)][it])]["DATA"]["channelid"])
                                message = await channel.fetch_message(data["GENERAL"]["quitm"][str(reaction.message.id)][it])
                                await message.edit(embed= clearembed)
                            await deleteQuitMessage(reaction.message.id)
                            await user.send("Vous avez correctement été déplacé :white_check_mark: !")

                            data["GENERAL"]["ingame"][str(user.id)] = data["GENERAL"]["quitm"][str(reaction.message.id)][2]
                            data["GENERAL"]["quitm"].pop(str(reaction.message.id))
                            updateFile(data)
                        else:
                            await user.send("Désolé, la partie demandée est complète...")
            else:
                await user.send("Vous ne pouvez pas quitter une partie temps que vous n'avez pas répondu...")
                return

if __name__ == '__main__':
    token = "" # type your token here
    if not token:
        print("Token not found, checking for token in environment...")
        token = os.getenv("TOKEN")
        if token:
            print("TOKEN FOUND")
            
    print("starting bot...")
    bot.run(token)
