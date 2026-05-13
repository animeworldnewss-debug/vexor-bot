import os
import asyncio
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

ROLE_CONFIG = [
    ("👑 Vexor", discord.Colour.purple(), discord.Permissions(administrator=True)),
    ("🛡️ Admin", discord.Colour.red(), discord.Permissions(
        manage_guild=True,
        manage_channels=True,
        manage_roles=True,
        manage_messages=True,
        kick_members=True,
        ban_members=True,
        moderate_members=True,
        view_audit_log=True,
    )),
    ("🔧 Moderator", discord.Colour.blue(), discord.Permissions(
        manage_messages=True,
        kick_members=True,
        moderate_members=True,
        view_audit_log=True,
    )),
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
    "tickets": "🎫 TICKETY",
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
🎭 **ROLE NA SERWERZE**

Na tym kanale możesz używać komend:

`!rola gracz` - dostajesz rolę 🎮 Gracz
`!rola widz` - dostajesz rolę 👤 Widz
`!rola aktywny` - dostajesz rolę 🔥 Aktywny

Administracja może później podpiąć tutaj reaction roles przez Carl-bota.
"""

SOCIALS_MESSAGE = """
🌐 **SOCIALE VEXOR**

🎬 YouTube: wklej tutaj link do kanału
🔴 Live: wklej tutaj link do streamów
🎵 TikTok/Shortsy: wklej tutaj link
💬 Discord: jesteś tutaj 😎
"""

TICKET_PANEL_MESSAGE = """
🎫 **TICKETY**

Masz problem, pytanie albo chcesz coś zgłosić?

Użyj komendy:

`!ticket`

Bot stworzy prywatny kanał, który zobaczysz tylko Ty i administracja.

Nie twórz ticketów dla żartu.
"""


def find_role(guild, name):
    return discord.utils.get(guild.roles, name=name)


def find_category(guild, name):
    return discord.utils.get(guild.categories, name=name)


def find_text_channel(guild, name):
    return discord.utils.get(guild.text_channels, name=name)


def find_voice_channel(guild, name):
    return discord.utils.get(guild.voice_channels, name=name)


def is_staff(member):
    staff_roles = {"👑 Vexor", "🛡️ Admin", "🔧 Moderator"}
    return member.guild_permissions.administrator or any(role.name in staff_roles for role in member.roles)


def make_embed(title, description, colour=discord.Colour.purple()):
    embed = discord.Embed(title=title, description=description, colour=colour)
    embed.set_footer(text="Vexor Bot")
    return embed


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


async def log_action(guild, text):
    log_channel = find_text_channel(guild, "📋│logi")
    if log_channel:
        await log_channel.send(text)


@bot.event
async def on_ready():
    print(f"Bot zalogowany jako: {bot.user}")


@bot.event
async def on_member_join(member):
    role = find_role(member.guild, "👤 Widz")
    if role:
        try:
            await member.add_roles(role, reason="Automatyczna rola dla nowego widza")
        except discord.Forbidden:
            pass

    welcome_channel = find_text_channel(member.guild, "👋│powitaj-sie")
    if welcome_channel:
        await welcome_channel.send(f"Siema {member.mention}, witaj na serwerze **Vexor** 💜")


@bot.command(name="pomoc")
async def pomoc(ctx):
    embed = make_embed(
        "🤖 Komendy Vexor Bota",
        """
`!setup_vexor` - tworzy strukturę serwera
`!ticket` - tworzy prywatny ticket
`!close` - zamyka ticket
`!clear 10` - usuwa wiadomości
`!ogloszenie tekst` - wysyła ogłoszenie
`!live link/tekst` - info o live
`!film link/tekst` - info o nowym filmie
`!short link/tekst` - info o shortsie
`!konkurs tekst` - ogłoszenie konkursu
`!regulamin` - wysyła regulamin
`!sociale` - pokazuje sociale
`!rola gracz/widz/aktywny` - nadaje rolę
`!ping` - sprawdza czy bot działa
""",
    )
    await ctx.reply(embed=embed)


@bot.command(name="ping")
async def ping(ctx):
    await ctx.reply(f"Pong! Bot działa. Opóźnienie: `{round(bot.latency * 1000)}ms`")


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
        everyone: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
    }

    read_only_overwrites = {
        everyone: discord.PermissionOverwrite(view_channel=True, send_messages=False, read_message_history=True),
        vexor_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        admin_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        mod_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
    }

    mod_overwrites = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        vexor_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        admin_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        mod_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
    }

    ticket_category_overwrites = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        vexor_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        admin_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        mod_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
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
        elif key == "tickets":
            categories[key] = await get_or_create_category(guild, name, ticket_category_overwrites)
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
        overwrites = recording_overwrites if voice_name == "🎥│Nagrywanie" else None
        await get_or_create_voice_channel(guild, voice_name, categories["voice"], overwrites)

    if created_text_channels.get("📜│regulamin"):
        await created_text_channels["📜│regulamin"].send(REGULAMIN)

    if created_text_channels.get("👋│powitaj-sie"):
        await created_text_channels["👋│powitaj-sie"].send(WELCOME_MESSAGE)

    if created_text_channels.get("🎭│role"):
        await created_text_channels["🎭│role"].send(ROLE_MESSAGE)

    if created_text_channels.get("📩│ticket"):
        await created_text_channels["📩│ticket"].send(TICKET_PANEL_MESSAGE)

    await ctx.reply("Gotowe! Serwer Vexor został ustawiony 💜")


@bot.command(name="ticket")
@commands.guild_only()
async def ticket(ctx):
    guild = ctx.guild
    existing = discord.utils.get(guild.text_channels, name=f"ticket-{ctx.author.id}")

    if existing:
        await ctx.reply(f"Masz już otwarty ticket: {existing.mention}")
        return

    ticket_category = find_category(guild, "🎫 TICKETY")
    if ticket_category is None:
        ticket_category = await guild.create_category("🎫 TICKETY")

    admin_role = find_role(guild, "🛡️ Admin")
    mod_role = find_role(guild, "🔧 Moderator")
    vexor_role = find_role(guild, "👑 Vexor")

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        ctx.author: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
    }

    for role in [admin_role, mod_role, vexor_role]:
        if role:
            overwrites[role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_messages=True,
            )

    channel = await guild.create_text_channel(
        name=f"ticket-{ctx.author.id}",
        category=ticket_category,
        overwrites=overwrites,
        topic=f"Ticket użytkownika {ctx.author} ({ctx.author.id})",
        reason="Nowy ticket Vexor",
    )

    embed = make_embed(
        "🎫 Ticket otwarty",
        f"{ctx.author.mention}, opisz dokładnie sprawę.\n\nAdministracja zaraz ogarnie temat.\nAby zamknąć ticket, użyj `!close`.",
    )

    await channel.send(ctx.author.mention, embed=embed)
    await ctx.reply(f"Utworzyłem ticket: {channel.mention}")
    await log_action(guild, f"🎫 Ticket utworzony przez {ctx.author.mention}: {channel.mention}")


@bot.command(name="close")
@commands.guild_only()
async def close(ctx):
    if not ctx.channel.name.startswith("ticket-"):
        await ctx.reply("Tej komendy używaj tylko w tickecie.")
        return

    if not is_staff(ctx.author) and str(ctx.author.id) not in ctx.channel.name:
        await ctx.reply("Nie możesz zamknąć tego ticketu.")
        return

    await ctx.reply("Zamykam ticket za 5 sekund...")
    await log_action(ctx.guild, f"🔒 Ticket zamknięty przez {ctx.author.mention}: `{ctx.channel.name}`")
    await asyncio.sleep(5)
    await ctx.channel.delete(reason=f"Ticket zamknięty przez {ctx.author}")


@bot.command(name="clear")
@commands.guild_only()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    amount = max(1, min(amount, 100))
    deleted = await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"Usunięto `{len(deleted) - 1}` wiadomości.")
    await asyncio.sleep(3)
    await msg.delete()


@bot.command(name="ogloszenie")
@commands.guild_only()
@commands.has_permissions(manage_messages=True)
async def ogloszenie(ctx, *, text):
    channel = find_text_channel(ctx.guild, "📢│ogłoszenia")
    if not channel:
        await ctx.reply("Nie znalazłem kanału `📢│ogłoszenia`.")
        return

    await channel.send(embed=make_embed("📢 Ogłoszenie", text, discord.Colour.purple()))
    await ctx.reply("Ogłoszenie wysłane.")


@bot.command(name="live")
@commands.guild_only()
@commands.has_permissions(manage_messages=True)
async def live(ctx, *, text):
    channel = find_text_channel(ctx.guild, "🔴│live-info")
    if not channel:
        await ctx.reply("Nie znalazłem kanału `🔴│live-info`.")
        return

    await channel.send(embed=make_embed("🔴 Vexor odpala live!", text, discord.Colour.red()))
    await ctx.reply("Info o live wysłane.")


@bot.command(name="film")
@commands.guild_only()
@commands.has_permissions(manage_messages=True)
async def film(ctx, *, text):
    channel = find_text_channel(ctx.guild, "🎬│nowe-filmy")
    if not channel:
        await ctx.reply("Nie znalazłem kanału `🎬│nowe-filmy`.")
        return

    await channel.send(embed=make_embed("🎬 Nowy film Vexora!", text, discord.Colour.blue()))
    await ctx.reply("Info o filmie wysłane.")


@bot.command(name="short")
@commands.guild_only()
@commands.has_permissions(manage_messages=True)
async def short(ctx, *, text):
    channel = find_text_channel(ctx.guild, "📺│shortsy")
    if not channel:
        await ctx.reply("Nie znalazłem kanału `📺│shortsy`.")
        return

    await channel.send(embed=make_embed("📺 Nowy shorts!", text, discord.Colour.orange()))
    await ctx.reply("Info o shortsie wysłane.")


@bot.command(name="konkurs")
@commands.guild_only()
@commands.has_permissions(manage_messages=True)
async def konkurs(ctx, *, text):
    channel = find_text_channel(ctx.guild, "🎁│konkursy")
    if not channel:
        await ctx.reply("Nie znalazłem kanału `🎁│konkursy`.")
        return

    await channel.send(embed=make_embed("🎁 Konkurs!", text, discord.Colour.gold()))
    await ctx.reply("Konkurs wysłany.")


@bot.command(name="regulamin")
@commands.guild_only()
async def regulamin(ctx):
    await ctx.reply(REGULAMIN)


@bot.command(name="sociale")
@commands.guild_only()
async def sociale(ctx):
    await ctx.reply(SOCIALS_MESSAGE)


@bot.command(name="rola")
@commands.guild_only()
async def rola(ctx, wybor=None):
    if wybor is None:
        await ctx.reply("Użyj: `!rola gracz`, `!rola widz` albo `!rola aktywny`.")
        return

    role_map = {
        "gracz": "🎮 Gracz",
        "widz": "👤 Widz",
        "aktywny": "🔥 Aktywny",
    }

    role_name = role_map.get(wybor.lower())
    if role_name is None:
        await ctx.reply("Nie znam takiej roli. Dostępne: `gracz`, `widz`, `aktywny`.")
        return

    role = find_role(ctx.guild, role_name)
    if role is None:
        await ctx.reply(f"Nie znalazłem roli `{role_name}`.")
        return

    if role in ctx.author.roles:
        await ctx.author.remove_roles(role, reason="Użytkownik zdjął rolę komendą")
        await ctx.reply(f"Zdjąłem Ci rolę {role.name}.")
    else:
        await ctx.author.add_roles(role, reason="Użytkownik wybrał rolę komendą")
        await ctx.reply(f"Dodałem Ci rolę {role.name}.")


@setup_vexor.error
@clear.error
@ogloszenie.error
@live.error
@film.error
@short.error
@konkurs.error
async def command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("Nie masz uprawnień do tej komendy.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("Brakuje tekstu/argumentu w komendzie.")
    elif isinstance(error, commands.BadArgument):
        await ctx.reply("Zły argument w komendzie.")
    elif isinstance(error, discord.Forbidden):
        await ctx.reply("Bot nie ma wystarczających uprawnień.")
    else:
        await ctx.reply(f"Wystąpił błąd: `{error}`")


if not TOKEN:
    raise RuntimeError("Brak tokenu. Dodaj DISCORD_TOKEN w Variables na Railway.")

bot.run(TOKEN)
