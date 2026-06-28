import discord
from discord import app_commands
import os
import asyncio

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Comandos sincronizados.")

bot = MyBot()
OWNER_ID = int(os.getenv("OWNER_ID", 0))

class CustomMessageView(discord.ui.View):
    def __init__(self, text: str, count: int, author: discord.Member):
        super().__init__(timeout=None)
        self.text = text
        self.count = count
        self.author_id = author.id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Solo el autor.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="✅ Enviar", style=discord.ButtonStyle.success, custom_id="send")
    async def send(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        sent = 0
        for i in range(self.count):
            try:
                # Usamos followup en vez de channel.send directo
                await interaction.followup.send(self.text, ephemeral=False)
                sent += 1
                await asyncio.sleep(0.75)
            except Exception as e:
                await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)
                return

        await interaction.followup.send(f"✅ Enviados {sent} mensajes.", ephemeral=True)
        self.stop()

# Comando
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="custommessage", description="Repite mensaje (app externa)")
@app_commands.describe(texto="Texto", veces="Veces (1-20)")
async def custommessage(interaction: discord.Interaction, texto: str, veces: int = 5):
    veces = max(1, min(20, veces))
    embed = discord.Embed(title="Mensaje Personalizado", description=texto, color=discord.Color.blue())
    embed.set_footer(text=f"Se repetirá {veces} veces")
    view = CustomMessageView(text=texto, count=veces, author=interaction.user)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.event
async def on_ready():
    print(f"🤖 {bot.user} listo.")

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    bot.run(token)
