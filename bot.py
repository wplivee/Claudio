import discord
from discord import app_commands
import os
import asyncio

intents = discord.Intents.default()

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.add_view(RepeatView())
    await self.tree.sync()   # ← agregá esta línea
    print("Bot listo y vistas registradas.")

bot = MyBot()


# ====================== VISTA CON BOTÓN ======================
class RepeatView(discord.ui.View):
    def __init__(self, message_content: str = "¡Mensaje por defecto!", repeat_count: int = 5):
        super().__init__(timeout=None)  # Persistente
        self.message_content = message_content
        self.repeat_count = repeat_count

    @discord.ui.button(label="Repetir Mensaje", style=discord.ButtonStyle.primary, custom_id="repeat_button")
    async def repeat_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        channel = interaction.channel
        for i in range(self.repeat_count):
            try:
                await channel.send(self.message_content)
                await asyncio.sleep(1.5)  # Pausa anti-spam
            except Exception as e:
                print(f"Error enviando mensaje: {e}")
                break

        await interaction.followup.send(f"✅ Se enviaron **{self.repeat_count}** mensajes.", ephemeral=True)


# ====================== COMANDO SLASH ======================
@bot.tree.command(name="custommessage", description="Crea un mensaje personalizado con botón para repetirlo")
@app_commands.describe(
    texto="El texto del mensaje que se repetirá",
    veces="Cuántas veces repetir el mensaje (1-20)"
)
async def custommessage(interaction: discord.Interaction, texto: str, veces: int = 5):
    veces = max(1, min(20, veces))  # Limitar entre 1 y 20

    embed = discord.Embed(
        title="Mensaje Personalizado",
        description=texto,
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Se repetirá {veces} veces • Por {interaction.user}")

    view = RepeatView(message_content=texto, repeat_count=veces)

    await interaction.response.send_message(
        embed=embed,
        view=view,
        ephemeral=True
    )


# ====================== SINCRONIZACIÓN ======================
@bot.tree.command(name="sync", description="Sincroniza los comandos slash (solo owner)")
async def sync(interaction: discord.Interaction):
    owner_id = int(os.getenv("OWNER_ID", 0))
    if interaction.user.id != owner_id:
        await interaction.response.send_message("❌ Solo el owner puede usar este comando.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    try:
        synced = await bot.tree.sync()
        await interaction.followup.send(f"✅ ¡{len(synced)} comandos sincronizados!", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)


@bot.event
async def on_ready():
    print(f'✅ {bot.user} está conectado y listo!')


if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ Error: DISCORD_TOKEN no encontrado en variables de entorno de Railway.")
    else:
        bot.run(token)
