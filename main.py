import discord
from utilities import *
from classes import *
from games import *
from EmbedMsg import *

intents = discord.Intents.default()
client = discord.Client(intents=intents)


class bot(discord.Client):
    def __init__(self, dataHandle: dataHandler, intents=discord.Intents.all(), **options):
        super().__init__(intents=intents, ** options)
        self.userDataHandler = dataHandle('user_data.json')
        self.houseDataHandler = dataHandle('house_data.json')
        self.games = games()
        self.categ = None
        self.userDataHandler.read(readAmajeDataUser)
        self.houseDataHandler.read(readAmajeDataHouse)
        self.notFreeUser = []
        self.notFreeChannel = []

    def check(self, m1, m2):
        '''
        Checks if author of message 1 is the same as message 2.
        '''
        return m1.author == m2.author

    def save(self, currUser: user):
        '''
        This saves the user.
        '''
        user.users[user.names.index(currUser.name)] = currUser
        self.userDataHandler.dump(
            data=user.users, func=getDumpUser, key='users')
        self.houseDataHandler.dump(
            data=[Slytherin, Gryffindor, Ravenclaw, Hufflepuff], func=getDumpHouse, key='house')

    def getUser(self, message: discord.Message):
        '''
        Gets the user object of the message author.
        '''
        try:
            return user.ids[message.author.id]
        except:
            print(f"{user.users}")
            return None

    async def send(self, message: discord.Message, content: str):
        '''
        Sends a message to the channel of the message.
        '''
        await message.channel.send(content)

    async def create_embed(self, embed: embedMessage, message: discord.Message):
        '''
        Takes in an embedded messaage object and sends it to the channel of the message.
        '''
        embed.send(message)

    async def recieve(self, message: discord.Message, check=None, timeout=None):
        '''
        Recieves a message from the channel of the message.
        '''
        try:
            return await self.wait_for('message', check=check, timeout=timeout)
        except:
            return None

    async def on_ready(self):
        """
        Does the following whenever bot starts up.
        """
        print(f'Logged in as {self.user}')
        print(self.user.id)

        # Need to save this guild id when created in the on_guild_join function.
        self.guild = self.get_guild(1217366468908290118)

        y = False
        for x in self.guild.categories:
            if x.name == 'PotterBot':
                y = True

        if not y:
            await self.on_guild_join(self.guild)

        # Getting the roles for the houses.
        Ravenclaw.get_role(self)
        Gryffindor.get_role(self)
        Slytherin.get_role(self)
        Hufflepuff.get_role(self)

    async def on_guild_join(self, guild: discord.Guild):
        categ = await guild.create_category('PotterBot')
        await guild.create_voice_channel("chill", category=categ)
        await guild.create_text_channel('general', category=categ)
        await guild.create_text_channel('newts', category=categ)
        await guild.create_text_channel('dueling-club', category=categ)
        await guild.create_text_channel('forbidden-forest', category=categ)
        await guild.create_text_channel('mini-games', category=categ)
        await guild.create_role(name="Gryffindor")
        await guild.create_role(name="Ravenclaw")
        await guild.create_role(name="Hufflepuff")
        await guild.create_role(name="Slytherin")

        print("Created the channels and roles.")

    async def on_message(self, message: discord.Message):
        """
        Does the following everytime there is a message on the server.
        """
        if isinstance(message.channel, discord.DMChannel):
            pass
        elif (message.author == self.user) or (message.channel.category.name.casefold() != "potterbot") or (message.author.id in self.notFreeUser):
            return

        if message.channel.id in self.notFreeChannel:
            await message.channel.send("Please wait for the current game to finish.")
            return

        print(message.content)

        currUser = self.getUser(message)
        self.notFreeUser.append(message.author.id)
        if message.content.casefold() == "~revelio" and message.channel.name == "general":
            # adding channel to not free channel
            self.notFreeChannel.append(message.channel.id)
            currUser = await self.games.introduction(self, message)
            # if the user is playing for the first time
            if currUser and currUser.progress < 1:
                isSuccess = await self.games.plat9_3_4(self, currUser, message)
                if (isSuccess):
                    currUser.progress = 1

            if currUser and currUser.progress == 1:
                isSuccess = await self.games.house_sort(self, currUser, message)
                if (isSuccess):
                    currUser.progress += 1

            if currUser and currUser.progress == 2:
                isSuccess = await self.games.Ollivanders(self, currUser, message)
                if (isSuccess):
                    currUser.progress += 1

            if currUser and currUser.progress == 3:
                isSuccess = await self.games.staircase(self, currUser, message)
                if (isSuccess):
                    currUser.progress += 1

            if currUser and currUser.progress == 4:
                await message.channel.send("You've completed all the introduction quests, Congratulations!\n Head to different channels to explore further games!")

            # freeing the channel
            self.notFreeChannel.append(message.channel.id)

        if currUser:
            # adding channel to not free channel
            self.notFreeChannel.append(message.channel.id)
            if message.channel.name == "dueling-club" and message.content.find("~duel") != -1:
                await self.games.duel(bot, currUser, message)

            if message.content == "~enter" and message.channel.name == "forbidden-forest":
                await self.games.botDuel(bot, currUser, message)

            if message.channel.name == "general":
                if message.content == "~myStats":
                    await bot.send(message, currUser.get_full_info())

                if message.content == "~houseStats":
                    await bot.send(message, eval(currUser.house).get_info())

            if message.channel.name == "mini-games":
                if message.content == "~crossword":
                    await self.games.crossword(bot, currUser, message)

            if message.channel.name == "newts":
                if message.content == "~trivia":
                    await self.games.Trivia(bot, currUser, message)

            # removing channel
            self.notFreeChannel.append(message.channel.id)

            currUser.update_level()
            self.save(currUser)
            self.notFreeUser.remove(message.author.id)


potter = bot(dataHandler)
potter.run(
    "MTIyMDQxOTY2OTM3OTM4MzM3Ng.Gz7ug4.AwIcTXV57TEwlfR2GPTKAOwJayghwiI2RCy3TE")
