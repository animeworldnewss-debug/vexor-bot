import discord

from discord.ext import commands

TOKEN = "MTUwMzg5NDA0MTc3NzkzNDM1Ng.GQtr-c.trpMWuechccI-xbNhrLz0IkCcinpppQtC4GZRE"

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

ROLE_CONFIG = [
    ("👑 Vexor", discord.Colour.purple(), discord.Permissions(administrator=True)),
    ("🛡️ Admin", discord.Colour.red(), discord.Permissions(manage_channels=True, manage_roles=True, manage_messages=True, kick_members=True, ban_members=True, moderate_members=True)),
    ("🔧 Moderator", discord.Colour.blue(), discord.Permissions(manage_messages=True, kick_members=True, moderate_members=True)),
    ("⭐ VIP", discord.Colour.gold(), discord.Permissions.none()),
    ("🔥 Aktywny", discord.Colour.orange(), discord.Permissions.none()),
    ("🎮 Gracz", discord.Colour.green(), discord.Permissions.none()),
    ("👤 Widz", discord.Colour.light_grey(), discord.Permissions.none()),
    ("🤖 Bot", discord.Colour.blurple(), discord.Permissions.none()),
]

CATEGORY_NAMES = {
    "start": "📌 START",
    "community": "💬 SPOŁECZNOŚĆ",
    "youtube": "🎥 VEXOR YOUTUBE",
    "gaming": "🎮 GRANIE Z WIDZAMI",
    "voice": "🔊 KANAŁY GŁOSOWE",
    "mod": "🛡️ MODERACJA",
}

TEXT_CHANNELS = {
    "start": ["📢│ogłoszenia", "👋│powitaj-sie", "📜│regulamin", "🎭│role", "📅│plan-streamow"],
    "community": ["💬│czat", "😂│memy", "🎮│gaming", "📸│screeny-klipy", "💡│pomysly-na-filmy"],
    "youtube": ["🔴│live-info", "🎬│nowe-filmy", "📺│shortsy", "⭐│polecane-klipy", "🎁│konkursy"],
    "gaming": ["🧍│szukam-ekipy", "🎯│turnieje", "🕹️│wspolne-granie", "📨│zapisy-do-gry-z-vexorem"],
    "mod": ["🚨│zgloszenia", "📩│ticket", "🔨│mod-chat", "📋│logi"],
}

VOICE_CHANNELS = [
    "🔊│Poczekalnia",
    "🎮│Gaming 1",
    "🎮│Gaming 2",
    "🔥│Tryhard Room",
    "😂│Luźne gadanie",
    "🎥│Nagrywanie",
]

READ_ONLY_CHANNELS = {
    "📢│ogłoszenia",
    "📜│regulamin",
    "📅│plan-streamow",
    "🔴│live-info",
    "🎬│nowe-filmy",
    "📺│shortsy",
    "⭐│polecane-klipy",
    "🎁│konkursy",
}

REGULAMIN = """
📜 **REGULAMIN SERWERA VEXOR**

1. Szanuj innych. Bez wyzywania, prowokowania i robienia dram.
2. Nie spamuj wiadomościami, emoji, linkami ani pingami.
3. Zakaz reklam bez zgody administracji.
4. Nie pinguj Vexora, Adminów i Moderatorów bez powodu.
5. NSFW, gore, scam i dziwne linki są zakazane.
6. Nie oszukuj w grach. Cheaty i exploity = kara.
7. Kanały mają swoje tematy. Memy na memy, klipy na klipy.
8. Na voice zachowuj się normalnie. Bez krzyków, puszczania muzyki i trollowania.
9. Słuchaj administracji.
10. Obowiązuje regulamin Discorda.

Miłego siedzenia na serwerze i widzimy się na graniu 💜🎮
"""

WELCOME_MESSAGE = """
👋 **Siema! Witaj na serwerze Vexor!**

To miejsce dla ekipy z YouTube, live’ów i wspólnego grania.

Na start:
📜 przeczytaj regulamin
🎭 wybierz role
💬 wbij na czat
🎮 sprawdź wspólne granie
🔴 obserwuj info o live’ach

Miłego siedzenia z ekipą Vexor 💜
"""

ROLE_MESSAGE = """
🎭 **WYBIERZ SWOJE ROLE**

Na tym kanale możesz później dodać reaction role albo button role przez bota typu Carl-bot.

Propozycje ról:
🎮 Gracz
👤 Widz
⭐ VIP
🔥 Aktywny

Pingi, które możesz dodać później:
🔴 Ping Live
🎬 Ping YouTube
🎁 Ping Konkursy
🎮 Ping Wspólne Granie
"""


def find_role(guild, name):
    return discord.utils.get(guild.roles, name=name)


def find_category(guild, name):
    return discord.utils.get(guild.categories, name=name)


def find_text_channel(guild, name):
    return discord.utils.get(guild.text_channels, name=name)


def find_voice_channel(guild, name):
    return discord.utils.get(guild.voice_channels, name=name)


async def get_or_create_roles(guild):
    roles = {}

    for name, colour, permissions in ROLE_CONFIG:
        role = find_role(guild, name)

        if role is None:
            role = await guild.create_role(
                name=name,
                colour=colour,
                permissions=permissions,
                reason="Setup serwera Vexor",
            )

        roles[name] = role

    return roles


async def get_or_create_category(guild, name, overwrites=None):
    category = find_category(guild, name)

    if category is None:
        category = await guild.create_category(
            name=name,
            overwrites=overwrites or {},
            reason="Setup serwera Vexor",
        )

    return category


async def get_or_create_text_channel(guild, name, category, overwrites=None, topic=None):
    channel = find_text_channel(guild, name)

    if channel is None:
        channel = await guild.create_text_channel(
            name=name,
            category=category,
            overwrites=overwrites or {},
            topic=topic,
            reason="Setup serwera Vexor",
        )
    else:
        await channel.edit(
            category=category,
            overwrites=overwrites or channel.overwrites,
            topic=topic or channel.topic,
            reason="Aktualizacja setupu serwera Vexor",
        )

    return channel


async def get_or_create_voice_channel(guild, name, category, overwrites=None):
    channel = find_voice_channel(guild, name)

    if channel is None:
        channel = await guild.create_voice_channel(
            name=name,
            category=category,
            overwrites=overwrites or {},
            reason="Setup serwera Vexor",
        )
    else:
        await channel.edit(
            category=category,
            overwrites=overwrites or channel.overwrites,
            reason="Aktualizacja setupu serwera Vexor",
        )

    return channel


@bot.event
async def on_ready():
    print(f"Bot zalogowany jako: {bot.user}")


@bot.command(name="setup_vexor")
@commands.guild_only()
@commands.has_permissions(administrator=True)
async def setup_vexor(ctx):
    guild = ctx.guild
    await ctx.reply("Startuję setup serwera Vexor... chwilka 🎮")

    roles = await get_or_create_roles(guild)

    everyone = guild.default_role
    vexor_role = roles["👑 Vexor"]
    admin_role = roles["🛡️ Admin"]
    mod_role = roles["🔧 Moderator"]

    normal_overwrites = {
        everyone: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
        )
    }

    read_only_overwrites = {
        everyone: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=False,
            read_message_history=True,
        ),
        vexor_role: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
        ),
        admin_role: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
        ),
        mod_role: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
        ),
    }

    mod_overwrites = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        vexor_role: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
        ),
        admin_role: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
        ),
        mod_role: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
        ),
    }

    recording_overwrites = {
        everyone: discord.PermissionOverwrite(view_channel=False, connect=False),
        vexor_role: discord.PermissionOverwrite(view_channel=True, connect=True, speak=True),
        admin_role: discord.PermissionOverwrite(view_channel=True, connect=True, speak=True),
        mod_role: discord.PermissionOverwrite(view_channel=True, connect=True, speak=True),
    }

    categories = {}

    for key, name in CATEGORY_NAMES.items():
        if key == "mod":
            categories[key] = await get_or_create_category(guild, name, mod_overwrites)
        else:
            categories[key] = await get_or_create_category(guild, name)

    created_text_channels = {}

    for category_key, channel_names in TEXT_CHANNELS.items():
        for channel_name in channel_names:
            if category_key == "mod":
                overwrites = mod_overwrites
            elif channel_name in READ_ONLY_CHANNELS:
                overwrites = read_only_overwrites
            else:
                overwrites = normal_overwrites

            channel = await get_or_create_text_channel(
                guild=guild,
                name=channel_name,
                category=categories[category_key],
                overwrites=overwrites,
                topic=f"Kanał serwera Vexor: {channel_name}",
            )

            created_text_channels[channel_name] = channel

    for voice_name in VOICE_CHANNELS:
        if voice_name == "🎥│Nagrywanie":
            overwrites = recording_overwrites
        else:
            overwrites = None

        await get_or_create_voice_channel(
            guild=guild,
            name=voice_name,
            category=categories["voice"],
            overwrites=overwrites,
        )

    regulamin_channel = created_text_channels.get("📜│regulamin")
    welcome_channel = created_text_channels.get("👋│powitaj-sie")
    role_channel = created_text_channels.get("🎭│role")

    if regulamin_channel:
        await regulamin_channel.send(REGULAMIN)

    if welcome_channel:
        await welcome_channel.send(WELCOME_MESSAGE)

    if role_channel:
        await role_channel.send(ROLE_MESSAGE)

    await ctx.reply("Gotowe! Serwer Vexor został ustawiony 💜")


@setup_vexor.error
async def setup_vexor_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("Musisz mieć Administratora, żeby użyć tej komendy.")
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.reply("Tej komendy można użyć tylko na serwerze.")
    elif isinstance(error, discord.Forbidden):
        await ctx.reply("Bot nie ma wystarczających uprawnień. Daj mu Administratora i ustaw jego rolę wysoko.")
    else:
        await ctx.reply(f"Wystąpił błąd: `{error}`")


bot.run(TOKEN)
