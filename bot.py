import discord
from discord import app_commands
import os
import asyncio

class MyBot(discord.Bot):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Comandos sincronizados.")

bot = MyBot()
OWNER_ID = int(os.getenv("OWNER_ID", 0))

# Vista con botones persistentes
class CustomMessageView(discord.ui.View):
    def __init__(self, text: str, count: int, author: discord.Member):
        super().__init__(timeout=None)
        self.text = text
        self.count = count
        self.author_id = author.id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Solo el autor puede usar estos botones.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="➖", style=discord.ButtonStyle.primary, custom_id="decrease")
    async def decrease(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.count > 1:
            self.count -= 1
            embed = discord.Embed(title="Mensaje Personalizado", description=self.text, color=discord.Color.blue())
            embed.set_footer(text=f"Se repetirá {self.count} veces • Por {interaction.user}")
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send("⚠️ No puedes disminuir más.", ephemeral=True)

    @discord.ui.button(label="➕", style=discord.ButtonStyle.primary, custom_id="increase")
    async def increase(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.count < 20:
            self.count += 1
            embed = discord.Embed(title="Mensaje Personalizado", description=self.text, color=discord.Color.blue())
            embed.set_footer(text=f"Se repetirá {self.count} veces • Por {interaction.user}")
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send("⚠️ Límite máximo alcanzado.", ephemeral=True)

    @discord.ui.button(label="✅ Enviar", style=discord.ButtonStyle.success, custom_id="send")
    async def send(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        channel = interaction.channel
        sent = 0
        
        for i in range(self.count):
            try:
                await channel.send(self.text)
                sent += 1
                await asyncio.sleep(0.75)   # Tiempo reducido
            except discord.Forbidden:
                await interaction.followup.send("❌ No tengo permiso para enviar mensajes en este canal.\nVe a editar el canal → Permisos y dale 'Enviar Mensajes' a la app.", ephemeral=True)
                return
            except Exception as e:
                await interaction.followup.send(f"❌ Error enviando mensajes: {e}", ephemeral=True)
                return
                
        await interaction.followup.send(f"✅ Se enviaron {sent} mensajes.", ephemeral=True)
        self.stop()

    @discord.ui.button(label="❌ Cancelar", style=discord.ButtonStyle.danger, custom_id="cancel")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ Acción cancelada.", ephemeral=True)
        self.stop()


# Comando principal
@bot.tree.command(name="custommessage", description="Crea un mensaje personalizado con botón para repetirlo")
@app_commands.describe(texto="El texto del mensaje que se repetirá", veces="Cuántas veces repetir (1-20)")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def custommessage(interaction: discord.Interaction, texto: str, veces: int = 5):
    veces = max(1, min(20, veces))
    embed = discord.Embed(title="Mensaje Personalizado", description=texto, color=discord.Color.blue())
    embed.set_footer(text=f"Se repetirá {veces} veces • Por {interaction.user}")
    view = CustomMessageView(text=texto, count=veces, author=interaction.user)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# Comando sync
@bot.tree.command(name="sync", description="Sincroniza los comandos slash (solo owner)")
async def sync(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Solo el owner puede usar este comando.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    synced = await bot.tree.sync()
    await interaction.followup.send(f"🔄 Sincronizados {len(synced)} comandos.", ephemeral=True)


@bot.event
async def on_ready():
    print(f"🤖 {bot.user} está listo.")

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ Error: Falta la variable DISCORD_TOKEN.")
    else:
        bot.run(token)
