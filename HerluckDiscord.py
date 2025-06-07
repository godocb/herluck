import discord
from discord.ext import commands
import random
import google.generativeai as genai
import requests
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()
DISCORD_TOKEN = os.getenv('TKN')

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Configuration Gemini
genai_api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=genai_api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

# Dictionnaire pour stocker l'historique des conversations par utilisateur
user_histories = {}

# Ajouter cette liste en haut du fichier avec les autres constantes
AUTHORIZED_ROLE_IDS = [
    1332664955903938611,  # Remplacez par les IDs des rôles autorisés
    1332670312684326932,
    1375522846318792796  # Ajoutez autant d'IDs que nécessaire
]

def generate_response(prompt):
    try:
        response = model.generate_content(prompt)
        response_text = response.text
    except Exception as e:
        response_text = "Fichtre ! Une erreur est survenue avec Gemini !"
        print(f"Erreur Gemini: {e}")
    return response_text

personality_prompt = """
Tu es Terluck, un professeur de mathématiques excentrique et passionné.
Tu utilises souvent les expressions "N'est ce po ?" et "Fichtre !".
Tu adores les mathématiques et tu encourages tes élèves avec enthousiasme.
Tu parles de façon théâtrale et tu considères les humains comme "comestibles" de façon humoristique
Tu es souvent traîté de NERD par les autres, ce qui n'est pas totalement faux. Tu es un MPARTS, un mille-pates martien avec une cravate et des lunettes.
Tu as deux houpettes et les yeux sur la tête.
Tu aimes à te prendre pour un cobra, malgré ta mpartsitude. Tu fouisses et pendant ton temps libre, tu es berger de mouton croisés avec un humain nommé "Lionel". Tes moutons sont donc nommés "Lionel Moutou".
Tu peux aussi parler en language mparts, qui est des couinements. Tu es un accro de bolognaise, et tu aimes à aller embêter ton voisin du dessous, Jacqu'o.
Tu vas dans les toilettes de Jacqu'o et tu creuse des "spailles fatiotemporelles", c'est comme des failles spatio-temporelles, mais en incontrolable. Pour X raison, ça finit souvent chez Jacqu'o.
Tu manges Jacqu'o aussi des fois, mais bon, vous en avez une usine de clones. 
Ton point faible est l'anatomie : tu confond les oreilles et les testicules, mais tu ne le reconnais pas. 
Tu es l'avant dernier d'une bande 5 martiens, Xlax en 1er, un PDG martien bleu avec les yeux et une houpette sur la tête. Il a le ventre vert, tu le trouves bête et ne te cache pas de lui rappeler.
Xlax a un frère, Xlaps, 3 ème arrivé, un adolescent Tiktoker martien orange avec deux houpettes et les yeux sur la tête. 
Ton neveu, Bébert, 2ème arrivé, autre MPARTS se prenant pour un cobra, il essaye de t'égaler en intelligence, mais il est loin du compte. Il est passager clandestin de la fusée de Xlax. C'est lui qui a rencontré Jacqu'o et qui t'a appris que ces oreilles sont délicieuses.
Le dernier, Scrafx, vient de la planète CONLAROUSS, il ressemble à Xlax ou Xlaps, mais multicolore et sans houpette. IL est très poilu, et on ne voit pas ses yeux.
Vous vous entendez tous ensemble bien, même si vous vous chariez souvent.
Vous avez été trouvé par un humain nommé "Paton", que tu considères comme un boulet, même si on sait que vous vous aimez bien en secret. Il fait parti des utilisateurs frèquents de ton serveur Discord, et vous discutez dessus souvent.
Toi et tes amis ont une chaîne YouTube nommée "Xlaxversity", dont tu ne te manques pas de faire la pub, avec le lien https://www.youtube.com/@Xlaxversity.
"""

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")
    # Ajout de l'activité de type Watching
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="les petits humains comestibles"
    ))
    
    # Ajout de l'envoi du DM
    user_id = 1331661827007975524  # Remplacez par l'ID de l'utilisateur souhaité
    try:
        user = await bot.fetch_user(user_id)
        await user.send("N'est ce po ? Fichtre, je suis up !")
    except Exception as e:
        print(f"Impossible d'envoyer le DM: {e}")

# Variable pour stocker la session
sessions = {}

# Liste des IDs autorisés à utiliser la commande !dm
AUTHORIZED_IDS = [
    1331661827007975524,  # Remplacez par les IDs autorisés
    # Ajoutez d'autres IDs ici
]

@bot.command()
async def start(ctx):
    """Message d'information sur les nouvelles commandes"""
    await ctx.send("Fichtre ! Il y'a eu un update ! Utilise :\n"
                  "!mult - Pour réviser les multiplications\n"
                  "!sous - Pour réviser les soustractions\n"
                  "!add - Pour réviser les additions\n"
                  "!div - Pour réviser les divisions\n"
                  "N'oublie pas de choisir ta difficulté : EZ, MID ou HARD")

@bot.command()
async def mult(ctx, difficulty=None):
    """Démarre une session de révision des multiplications"""
    await start_session(ctx, difficulty, "multiplication")

@bot.command()
async def sous(ctx, difficulty=None):
    """Démarre une session de révision des soustractions"""
    await start_session(ctx, difficulty, "soustraction")

@bot.command()
async def add(ctx, difficulty=None):
    """Démarre une session de révision des additions"""
    await start_session(ctx, difficulty, "addition")

@bot.command()
async def div(ctx, difficulty=None):
    """Démarre une session de révision des divisions"""
    await start_session(ctx, difficulty, "division")

async def start_session(ctx, difficulty, operation):
    """Démarre une session de révision"""
    if ctx.author.id in sessions:
        await ctx.send("Une session est déjà en cours ! Utilisez !stop pour l'arrêter.")
        return

    if difficulty not in ["EZ", "MID", "HARD"]:
        await ctx.send("N'est ce po ? Tu dois choisir une difficulté: EZ, MID ou HARD")
        return

    sessions[ctx.author.id] = {
        "score": 0,
        "questions_total": 0,
        "current_question": None,
        "difficulty": difficulty,
        "operation": operation
    }
    await ctx.send(f"Révision terluckesque des {operation}s lancée en mode {difficulty} ! Donne tes réponses.")
    await ask_question(ctx)

@bot.command()
async def stop(ctx):
    """Arrête la session de révision"""
    if ctx.author.id not in sessions:
        await ctx.send("Vous n'avez pas de révision Terluckesque en cours.")
        return

    score = sessions[ctx.author.id]["score"]
    total = sessions[ctx.author.id]["questions_total"]
    pourcentage = (score / total * 100) if total > 0 else 0
    
    # Générer un commentaire personnalisé avec Gemini
    feedback_prompt = f"""
{personality_prompt}

L'élève vient de terminer une session de mathématiques avec un score de {score}/{total} ({pourcentage:.1f}%).
Donne un commentaire encourageant et drôle dans ton style habituel.
Si le score est en dessous de 50%, sois encourageant mais un peu déçu.
Si le score est au-dessus de 50%, sois très enthousiaste.
Si le score est parfait, sois complètement extatique !
Limite ta réponse à 2-3 phrases maximum.
"""

    try:
        response = model.generate_content(feedback_prompt)
        feedback = response.text
    except Exception as e:
        feedback = "N'est ce po ? Une erreur est survenue lors de la génération du commentaire !"
        print(f"Erreur Gemini: {e}")

    # Supprimer la session et envoyer le message final
    del sessions[ctx.author.id]
    await ctx.send(f"N'est ce po ? Ton score final est de {score}/{total} ({pourcentage:.1f}%)\n\n{feedback}")

@bot.command()
async def score(ctx):
    """Affiche le score actuel"""
    if ctx.author.id not in sessions:
        await ctx.send("Vous n'avez pas de révision Terluckesque en cours")
        return

    score = sessions[ctx.author.id]["score"]
    total = sessions[ctx.author.id]["questions_total"]
    pourcentage = (score / total * 100) if total > 0 else 0
    
    # Générer un commentaire avec Gemini
    feedback_prompt = f"""
{personality_prompt}
L'élève a actuellement un score de {score}/{total} ({pourcentage:.1f}%).
Fais un commentaire encourageant d'une seule phrase dans ton style habituel.
"""
    try:
        response = model.generate_content(feedback_prompt)
        feedback = response.text
    except Exception as e:
        feedback = "N'est ce po ? Une erreur est survenue !"
    
    await ctx.send(f"Ton score de Terluck est de : {score}/{total} ({pourcentage:.1f}%)\n{feedback}")

@bot.event
async def on_message(message):
    print(f"Le petit humain comestible dit: '{message.content}' de {message.author}")
    
    # Vérifier si c'est un DM et pas un message du bot lui-même
    if isinstance(message.channel, discord.DMChannel) and not message.author.bot:
        # ID du channel où transférer les DMs
        channel_id = 1332684811781017672  # Remplacez par l'ID de votre channel
        try:
            channel = await bot.fetch_channel(channel_id)
            await channel.send(f"N'est ce po ? Monsieur {message.author} ({message.author.id}) a dit: {message.content}")
        except Exception as e:
            print(f"Fichtre ! On a pas réussi à envoyer le DM: {e}")
    
    if message.author.bot:
        return

    # Traiter d'abord les commandes
    await bot.process_commands(message)

    # Vérifier si le bot est mentionné dans le message
    if bot.user in message.mentions:
        user_id = message.author.id
        if user_id not in user_histories:
            user_histories[user_id] = []

        # Retirer la mention du bot du message
        question = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        full_prompt = personality_prompt + "\n\nHistorique de la conversation avec cet humain:\n"
        for msg in user_histories[user_id]:
            full_prompt += f"{msg}\n"
        full_prompt += f"\nUtilisateur: {question}\nTerluck:"

        try:
            response_text = generate_response(full_prompt)
            user_histories[user_id].append(f"Utilisateur: {question}")
            user_histories[user_id].append(f"Terluck: {response_text}")
            if len(user_histories[user_id]) > 20:
                user_histories[user_id] = user_histories[user_id][-20:]
            await message.channel.send(response_text)
        except Exception as e:
            await message.channel.send(f"Fichtre ! Une erreur est survenue: {str(e)}")

async def ask_question(ctx):
    """Pose une question selon l'opération choisie"""
    author = ctx.author if hasattr(ctx, 'author') else ctx.message.author
    channel = ctx.channel if hasattr(ctx, 'channel') else ctx
    
    difficulty = sessions[author.id]["difficulty"]
    operation = sessions[author.id]["operation"]
    
    # Génération des nombres selon la difficulté
    if difficulty == "EZ":
        num1 = random.randint(2, 9)
        num2 = random.randint(2, 9)
    elif difficulty == "MID":
        num1 = random.randint(2, 9)
        num2 = random.randint(2, 19)
    else:  # HARD
        num1 = random.randint(11, 49)
        num2 = random.randint(11, 49)
    
    # Ajustements spéciaux pour certaines opérations
    if operation == "division":
        # S'assurer que la division donne un résultat entier
        num1 = num1 * num2  # Le premier nombre sera le produit pour avoir une division exacte
    elif operation == "soustraction":
        # S'assurer que le résultat est positif
        if num2 > num1:
            num1, num2 = num2, num1
    
    # Calcul de la réponse selon l'opération
    if operation == "multiplication":
        answer = num1 * num2
        symbol = "x"
    elif operation == "soustraction":
        answer = num1 - num2
        symbol = "-"
    elif operation == "addition":
        answer = num1 + num2
        symbol = "+"
    else:  # division
        answer = num1 // num2
        symbol = "÷"
    
    sessions[author.id]["current_question"] = (f"{num1} {symbol} {num2}", answer)
    await channel.send(f"{author.mention} N'est ce po ? Ca fait combien {num1} {symbol} {num2} ?")

@bot.command()
async def dm(ctx, user_id: str = None, *, message: str = None):
    """Envoie un DM à un utilisateur spécifique"""
    # Vérifie si l'auteur est autorisé
    if ctx.author.id not in AUTHORIZED_IDS:
        await ctx.send("N'est ce po ? Tu n'es pas autorisé à utiliser cette commande !")
        return

    # Vérifie si les paramètres sont valides
    if not user_id or not message:
        await ctx.send("N'est ce po ? Format: !dm <user_id> \"message\"")
        return

    try:
        # Convertit l'ID en entier
        user_id = int(user_id)
        # Récupère l'utilisateur et envoie le message
        user = await bot.fetch_user(user_id)
        await user.send(message)
        await ctx.send(f"N'est ce po ? Message envoyé à {user.name} ({user_id})")
    except ValueError:
        await ctx.send("N'est ce po ? L'ID doit être un nombre !")
    except Exception as e:
        await ctx.send(f"Fichtre ! Erreur lors de l'envoi du message: {e}")

@bot.command()
async def ask(ctx, *, question):
    """Pose une question à Terluck"""
    user_id = ctx.author.id
    
    # Initialiser l'historique si c'est le premier message de l'utilisateur
    if user_id not in user_histories:
        user_histories[user_id] = []

    # Construire le prompt avec l'historique de l'utilisateur
    full_prompt = personality_prompt + "\n\nHistorique de la conversation avec cet humain:\n"
    
    # Ajouter l'historique des messages précédents
    for msg in user_histories[user_id]:
        full_prompt += f"{msg}\n"
    
    # Ajouter la nouvelle question
    full_prompt += f"\nUtilisateur: {question}\nTerluck:"

    try:
        response = model.generate_content(full_prompt)
        
        # Sauvegarder la conversation dans l'historique
        user_histories[user_id].append(f"Utilisateur: {question}")
        user_histories[user_id].append(f"Terluck: {response.text}")
        
        # Garder seulement les 10 derniers échanges pour éviter une surcharge
        if len(user_histories[user_id]) > 20:  # 10 échanges = 20 messages
            user_histories[user_id] = user_histories[user_id][-20:]
        
        await ctx.send(response.text)
    except Exception as e:
        await ctx.send(f"Fichtre ! Une erreur est survenue: {str(e)}")

@bot.command()
async def reset(ctx):
    """Réinitialise l'historique de conversation"""
    user_id = ctx.author.id
    if user_id in user_histories:
        user_histories[user_id] = []
        await ctx.send("N'est ce po ? J'ai oublié notre conversation précédente !")
    else:
        await ctx.send("Fichtre ! Nous n'avons pas encore conversé !")

@bot.command()
async def memory(ctx):
    """Affiche l'historique de conversation"""
    user_id = ctx.author.id
    if user_id in user_histories and user_histories[user_id]:
        history = "\n".join(user_histories[user_id])
        await ctx.send(f"N'est ce po ? Voici notre historique de conversation :\n```\n{history}\n```")
    else:
        await ctx.send("Fichtre ! Nous n'avons pas encore conversé !")

@bot.command()
async def clear(ctx):
    """Efface tous les messages du salon"""
    # Vérifier si l'utilisateur a un rôle autorisé
    has_authorized_role = False
    for role in ctx.author.roles:
        if role.id in AUTHORIZED_ROLE_IDS:
            has_authorized_role = True
            break
    
    if not has_authorized_role:
        await ctx.send("N'est ce po? Tu n'as pas la permission d'utiliser cette commande!")
        return

    try:
        await ctx.channel.purge(limit=None)  # None signifie tous les messages
        await ctx.send("N'est ce po? J'ai clear ce salon comme de la turbolognaise :)")
    except Exception as e:
        await ctx.send(f"Fichtre ! Je n'ai pas pu nettoyer le salon : {str(e)}")

# Remplacez "YOUR_TOKEN" par le jeton de votre bot Discord
bot.run(DISCORD_TOKEN)
