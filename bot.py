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

# Vista con botones
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
            await interaction.followup.send("⚠️ No puedes disminuir más.", ephemeral=True)

    @discord.ui.button(label="➕", style=discord.ButtonStyle.primary, custom_id="increase")
    async def increase(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.count < 20:
            self.count += 1
            embed = discord.Embed(title="Mensaje Personalizado", description=self.text, color=discord.Color.blue())
            embed.set_footer(text=f"Se repetirá {self.count} veces • Por {interaction.user}")
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.followup.send("⚠️ Límite máximo alcanzado.", ephemeral=True)

    @discord.ui.button(label="✅ Enviar", style=discord.ButtonStyle.success, custom_id="send")
    async def send(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        channel = interaction.channel
        user = interaction.user
        sent = 0
        sent_via = "servidor"

        for i in range(self.count):
            try:
                # Intenta primero en el servidor
                await channel.send(self.text)
                sent += 1
                await asyncio.sleep(1.5)
            except discord.Forbidden:
                # Si falla, intenta por MD
                try:
                    await user.send(self.text)
                    sent += 1
                    sent_via = "MD"
                    await asyncio.sleep(1.5)
                except discord.Forbidden:
                    await interaction.followup.send("❌ No pude enviar mensajes.\nAbre tus MD o invita el bot al servidor.", ephemeral=True)
                    return
                except Exception as e:
                    await interaction.followup.send(f"❌ Error en MD: {e}", ephemeral=True)
                    return
            except Exception as e:
                await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)
                return

        if sent_via == "MD":
            await interaction.followup.send(f"⚠️ Bot no invitado al servidor.\n✅ Te envié {sent} mensajes por **MD**.", ephemeral=True)
        else:
            await interaction.followup.send(f"✅ Se enviaron {sent} mensajes en el canal.", ephemeral=True)
        
        self.stop()

# Comando principal
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="custommessage", description="Mensaje personalizado (intenta en servidor, sino MD)")
@app_commands.describe(texto="El texto del mensaje", veces="Cuántas veces (1-20)")
async def custommessage(interaction: discord.Interaction, texto: str, veces: int = 5):
    veces = max(1, min(20, veces))
    embed = discord.Embed(title="Mensaje Personalizado", description=texto, color=discord.Color.blue())
    embed.set_footer(text=f"Se repetirá {veces} veces • Por {interaction.user}")
    view = CustomMessageView(text=texto, count=veces, author=interaction.user)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# Comando sync
@bot.tree.command(name="sync", description="Sincroniza comandos (solo owner)")
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
        print("❌ Error: Falta DISCORD_TOKEN")
    else:
        bot.run(token)
