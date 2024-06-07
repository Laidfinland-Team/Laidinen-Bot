import sys, os; sys.path.insert(0, os.path.join(os.getcwd(), ''))
from __init__ import *

class disable_buttons(discord.ui.View):  # View object
    def __init__(self):
        super().__init__()
        for i in range(5):  # Add five buttons
            self.add_item(self.button_disable(str(i)))

    class button_disable(discord.ui.Button):  # Button class
        def __init__(self, label):
            super().__init__(label=label)  # set label and super init class

        async def callback(self, interaction: discord.Interaction):
            self.disabled = True  # disable button  
            await interaction.message.edit(view=self.view)  # update message
            await interaction.response.send_message("Worked!")  # respond

@bot.command()
async def button_test(interaction : discord.Interaction):  # command to add buttons to response
    await interaction.channel.send("Worked!", view=disable_buttons())  
    
    # disable_buttons is the view class to add to the message
    
bot.run(TOKEN)