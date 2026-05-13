import os
import json
import time
import random
import asyncio
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

REACTION_PANEL_FILE = "reaction_roles_panel.json"
LEVELING_FILE = "leveling.json"

REACTION_ROLES = {
    "🎮": "🎮 Gracz",
    "👤": "👤 Widz",
    "🔥": "🔥 Aktywny",
    "🔴": "🔴 Ping Live",
    "🎬": "🎬 Ping YouTube",
    "🎁": "🎁 Ping Konkursy",
    "🕹️": "🎮 Ping Wspólne Granie",
}

XP_COOLDOWN_SECONDS = 60
XP_MIN = 10
XP_MAX = 18
xp_cooldowns = {}

ROLE_CONFIG = [
    ("👑 Vexor", discord.Colour.purple(), discord.Permissions(administrator=True)),
    ("🛡️ Admin", discord.Colour.red(), discord.Permissions(manage_guild=True, manage_channels=True, manage_roles=True, manage_messages=True, kick_members=True, ban_members=True, moderate_members=True, view_audit_log=True)),
    ("🔧 Moderator", discord.Colour.blue(), discord.Permissions(manage_messages=True, kick_members=True, moderate_members=True, view_audit_log=True)),
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

VOICE_CHANNELS = ["🔊│Poczekalnia", "🎮│Gaming 1", "🎮│Gaming 2", "🔥│Tryhard Room", "😂│Luźne gadanie", "🎥│Nagrywanie"]

READ_ONLY_CHANNELS = {"📢│ogłoszenia", "📜│regulamin", "📅│plan-streamow", "🔴│live-info", "🎬│nowe-filmy", "📺│shortsy", "⭐│polecane-klipy", "🎁│konkursy"}

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

Użyj komendy `!reaction_roles`, aby administracja wysłała profesjonalny panel ról.
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
"""


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


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


async def log_action(guild, text):
    log_channel = find_text_channel(guild, "📋│logi")
    if log_channel:
        await log_channel.send(text)


async def get_or_create_roles(guild):
    roles = {}
    for name, colour, permissions in ROLE_CONFIG:
        role = find_role(guild, name)
        if role is None:
            role = await guild.create_role(name=name, colour=colour, permissions=permissions, reason="Setup serwera Vexor")
        roles[name] = role
    return roles


async def get_or_create_category(guild, name, overwrites=None):
    category = find_category(guild, name)
    if category is None:
        category = await guild.create_category(name=name, overwrites=overwrites or {}, reason="Setup serwera Vexor")
    return category


async def get_or_create_text_channel(guild, name, category, overwrites=None, topic=None):
    channel = find_text_channel(guild, name)
    if channel is None:
        channel = await guild.create_text_channel(name=name, category=category, overwrites=overwrites or {}, topic=topic, reason="Setup serwera Vexor")
    else:
        await channel.edit(category=category, overwrites=overwrites or channel.overwrites, topic=topic or channel.topic, reason="Aktualizacja setupu Vexor")
    return channel


async def get_or_create_voice_channel(guild, name, category, overwrites=None):
    channel = find_voice_channel(guild, name)
    if channel is None:
        channel = await guild.create_voice_channel(name=name, category=category, overwrites=overwrites or {}, reason="Setup serwera Vexor")
    else:
        await channel.edit(category=category, overwrites=overwrites or channel.overwrites, reason="Aktualizacja setupu Vexor")
    return channel


async def ensure_reaction_roles(guild):
    created = []
    for role_name in REACTION_ROLES.values():
        role = find_role(guild, role_name)
        if role is None:
            await guild.create_role(name=role_name, reason="Reaction roles Vexor")
            created.append(role_name)
    return created


def save_reaction_panel(guild_id, channel_id, message_id):
    data = load_json(REACTION_PANEL_FILE, {})
    data[str(guild_id)] = {"channel_id": channel_id, "message_id": message_id}
    save_json(REACTION_PANEL_FILE, data)


def get_reaction_panel_message_id(guild_id):
    data = load_json(REACTION_PANEL_FILE, {})
    guild_data = data.get(str(guild_id))
    return guild_data.get("message_id") if guild_data else None


def xp_needed_for_level(level):
    return 100 * (level ** 2)


def calculate_level(total_xp):
    level = 0
    while total_xp >= xp_needed_for_level(level + 1):
        level += 1
    return level


def make_progress_bar(current, required, size=12):
    if required <= 0:
        return "█" * size
    filled = int((current / required) * size)
    filled = max(0, min(size, filled))
    return "█" * filled + "░" * (size - filled)


def get_user_xp_data(guild_id, user_id):
    data = load_json(LEVELING_FILE, {})
    guild_data = data.setdefault(str(guild_id), {})
    user_data = guild_data.setdefault(str(user_id), {"xp": 0})
    return data, user_data


async def handle_leveling(message):
    now = time.time()
    cooldown_key = f"{message.guild.id}:{message.author.id}"

    if now - xp_cooldowns.get(cooldown_key, 0) < XP_COOLDOWN_SECONDS:
        return

    xp_cooldowns[cooldown_key] = now
    data, user_data = get_user_xp_data(message.guild.id, message.author.id)

    old_xp = user_data.get("xp", 0)
    old_level = calculate_level(old_xp)

    gained_xp = random.randint(XP_MIN, XP_MAX)
    new_xp = old_xp + gained_xp
    new_level = calculate_level(new_xp)

    user_data["xp"] = new_xp
    save_json(LEVELING_FILE, data)

    if new_level > old_level:
        await message.channel.send(f"🔥 {message.author.mention} wbił poziom **{new_level}**!")


@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        print("Slash komendy zsynchronizowane.")
    except Exception as error:
        print(f"Błąd synchronizacji slash komend: {error}")

    print(f"Bot zalogowany jako: {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.guild is not None:
        await handle_leveling(message)

    await bot.process_commands(message)


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


@bot.event
async def on_raw_reaction_add(payload):
    if payload.guild_id is None or payload.user_id == bot.user.id:
        return

    if get_reaction_panel_message_id(payload.guild_id) != payload.message_id:
        return

    role_name = REACTION_ROLES.get(str(payload.emoji))
    if not role_name:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    member = guild.get_member(payload.user_id) or await guild.fetch_member(payload.user_id)
    role = find_role(guild, role_name)

    if role:
        try:
            await member.add_roles(role, reason="Reaction role Vexor")
        except discord.Forbidden:
            pass


@bot.event
async def on_raw_reaction_remove(payload):
    if payload.guild_id is None:
        return

    if get_reaction_panel_message_id(payload.guild_id) != payload.message_id:
        return

    role_name = REACTION_ROLES.get(str(payload.emoji))
    if not role_name:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    member = guild.get_member(payload.user_id) or await guild.fetch_member(payload.user_id)
    role = find_role(guild, role_name)

    if role:
        try:
            await member.remove_roles(role, reason="Reaction role Vexor")
        except discord.Forbidden:
            pass


@bot.command(name="reaction_roles")
@commands.guild_only()
@commands.has_permissions(administrator=True)
async def reaction_roles(ctx):
    try:
        created_roles = await ensure_reaction_roles(ctx.guild)
    except discord.Forbidden:
        await ctx.reply("Bot nie ma uprawnień do tworzenia ról. Daj mu `Manage Roles` albo `Administrator` i ustaw jego rolę wysoko.")
        return

    embed = discord.Embed(
        title="🎭 Wybierz swoje role",
        description=(
            "Kliknij odpowiednie reakcje, aby nadać lub usunąć sobie role.\n\n"
            "**Sekcja społeczności:**\n"
            "🎮 Gracz\n"
            "👤 Widz\n"
            "🔥 Aktywny\n\n"
            "**Sekcja powiadomień:**\n"
            "🔴 Ping Live\n"
            "🎬 Ping YouTube\n"
            "🎁 Ping Konkursy\n"
            "🕹️ Ping Wspólne Granie"
        ),
        colour=discord.Colour.purple()
    )
    embed.set_footer(text="Vexor Role Panel")

    message = await ctx.send(embed=embed)

    for emoji in REACTION_ROLES.keys():
        await message.add_reaction(emoji)

    save_reaction_panel(ctx.guild.id, ctx.channel.id, message.id)

    if created_roles:
        await ctx.reply(f"Panel ról wysłany. Utworzono brakujące role: `{', '.join(created_roles)}`")
    else:
        await ctx.reply("Panel ról wysłany.")


@bot.tree.command(name="rank", description="Pokazuje Twój poziom, XP i pasek postępu.")
async def rank(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message("Ta komenda działa tylko na serwerze.", ephemeral=True)
        return

    _, user_data = get_user_xp_data(interaction.guild.id, interaction.user.id)
    total_xp = user_data.get("xp", 0)
    level = calculate_level(total_xp)

    current_level_xp = xp_needed_for_level(level)
    next_level_xp = xp_needed_for_level(level + 1)
    progress_current = total_xp - current_level_xp
    progress_required = next_level_xp - current_level_xp

    embed = discord.Embed(
        title=f"🏆 Rank: {interaction.user.display_name}",
        description=(
            f"**Poziom:** {level}\n"
            f"**XP:** {total_xp}\n"
            f"**Postęp:** `{make_progress_bar(progress_current, progress_required)}` "
            f"{progress_current}/{progress_required} XP"
        ),
        colour=discord.Colour.purple()
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="leaderboard", description="Pokazuje top 10 osób z największym XP.")
async def leaderboard(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message("Ta komenda działa tylko na serwerze.", ephemeral=True)
        return

    data = load_json(LEVELING_FILE, {})
    guild_data = data.get(str(interaction.guild.id), {})

    if not guild_data:
        await interaction.response.send_message("Ranking jest jeszcze pusty.", ephemeral=True)
        return

    sorted_users = sorted(guild_data.items(), key=lambda item: item[1].get("xp", 0), reverse=True)[:10]
    lines = []

    for index, (user_id, user_data) in enumerate(sorted_users, start=1):
        member = interaction.guild.get_member(int(user_id))
        name = member.display_name if member else f"Użytkownik {user_id}"
        xp = user_data.get("xp", 0)
        level = calculate_level(xp)
        lines.append(f"**{index}.** {name} — poziom **{level}**, `{xp}` XP")

    embed = discord.Embed(title="🏆 Leaderboard Vexor", description="\n".join(lines), colour=discord.Colour.gold())
    await interaction.response.send_message(embed=embed)


@bot.command(name="pomoc")
async def pomoc(ctx):
    embed = make_embed(
        "🤖 Komendy Vexor Bota",
        """
`!setup_vexor` - tworzy strukturę serwera
`!reaction_roles` - wysyła panel reaction roles
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
`/rank` - pokazuje poziom i XP
`/leaderboard` - pokazuje top 10 osób
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

    normal_overwrites = {everyone: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)}

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

    ticket_overwrites = mod_overwrites

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
            categories[key] = await get_or_create_category(guild, name, ticket_overwrites)
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

    ticket_category = find_category(guild, "🎫 TICKETY") or await guild.create_category("🎫 TICKETY")

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        ctx.author: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
    }

    for role_name in ["👑 Vexor", "🛡️ Admin", "🔧 Moderator"]:
        role = find_role(guild, role_name)
        if role:
            overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True)

    channel = await guild.create_text_channel(
        name=f"ticket-{ctx.author.id}",
        category=ticket_category,
        overwrites=overwrites,
        topic=f"Ticket użytkownika {ctx.author} ({ctx.author.id})",
        reason="Nowy ticket Vexor",
    )

    await channel.send(ctx.author.mention, embed=make_embed("🎫 Ticket otwarty", f"{ctx.author.mention}, opisz dokładnie sprawę.\n\nAby zamknąć ticket, użyj `!close`."))
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

    role_map = {"gracz": "🎮 Gracz", "widz": "👤 Widz", "aktywny": "🔥 Aktywny"}
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
@reaction_roles.error
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
