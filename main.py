import discord
from utilities import *
from classes import *
from games import *
from EmbedMsg import *
import os

token = ""
print(token)
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
        Takes in an embedded message object and sends it to the channel of the message.
        '''
        await embed.send(message)

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

    async def on_guild_join(self, guild: discord.Guild):
        self.guild = guild
        categ = await guild.create_category('PotterBot')
        await guild.create_voice_channel("chill", category=categ)
        await guild.create_text_channel('guide', category=categ)
        await guild.create_text_channel('general', category=categ)
        await guild.create_text_channel('newts', category=categ)
        await guild.create_text_channel('dueling-club', category=categ)
        await guild.create_text_channel('forbidden-forest', category=categ)
        await guild.create_text_channel('mini-games', category=categ)
        Gryffindor.role = await guild.create_role(name="Gryffindor", color=discord.Color.red())
        Ravenclaw.role = await guild.create_role(name="Ravenclaw", color=discord.Color.blue())
        Slytherin.role = await guild.create_role(name="Hufflepuff", color=discord.Color.gold())
        Hufflepuff.role = await guild.create_role(name="Slytherin", color=discord.Color.green())

        print("Created the channels and roles.")

        y = False
        for x in self.guild.categories:
            if x.name == 'PotterBot':
                y = True

        if not y:
            await self.on_guild_join(self.guild)

    async def on_message(self, message: discord.Message):
        """
        Does the following everytime there is a message on the server.
        """

        self.guild = message.guild

        if isinstance(message.channel, discord.DMChannel):
            pass
        elif (message.author == self.user) or (message.channel.category.name.casefold() != "potterbot") or (message.author.id in self.notFreeUser):
            return

        if message.channel.id in self.notFreeChannel:
            await message.channel.send("Please wait for the current game to finish.")
            return

        print(message.content)

        currUser = self.getUser(message)
        if message.content.casefold() == "~revelio" and message.channel.name == "general":
            self.notFreeUser.append(message.author.id)
            # adding channel to not free channel
            self.notFreeChannel.append(message.channel.id)
            currUser = await self.games.introduction(self, message)
            # if the user is playing for the first time
            if currUser and currUser.progress < 1:
                isSuccess = await self.games.plat9_3_4(self, currUser, message)
                if (isSuccess):
                    currUser.progress = 1
                # need this to wait for embed to register
                await asyncio.sleep(0.25)

            if currUser and currUser.progress == 1:
                isSuccess = await self.games.house_sort(self, currUser, message)
                if (isSuccess):
                    currUser.progress += 1
                    # need this to wait for embed to register
                    await asyncio.sleep(0.25)

            if currUser and currUser.progress == 2:
                isSuccess = await self.games.Ollivanders(self, currUser, message)
                if (isSuccess):
                    currUser.progress += 1
                    # need this to wait for embed to register
                    await asyncio.sleep(0.25)

            if currUser and currUser.progress == 3:
                isSuccess = await self.games.staircase(self, currUser, message)
                if (isSuccess):
                    currUser.progress += 1
                    # need this to wait for embed to register
                    await asyncio.sleep(0.25)

            if currUser and currUser.progress == 4:
                em = embedMessage(title="Introduction Complete!",
                                  description="***You've completed all the introduction quests, Congratulations!\n Head to different channels to explore further games!***")
                await self.create_embed(em, message)

            # freeing the channel
            self.notFreeChannel.remove(message.channel.id)

        elif currUser:
            self.notFreeUser.append(message.author.id)
            if currUser.progress >= 4:
                self.notFreeChannel.append(message.channel.id)
                # adding channel to not free channel
                if message.channel.name == "dueling-club" and message.content.find("~duel") != -1:
                    await self.games.duel(self, currUser, message)

                if message.content == "~explore" and message.channel.name == "forbidden-forest":
                    await self.games.botDuel(self, currUser, message)

                if message.channel.name == "general":
                    if message.content == "~myStats":

                        use = self.get_user(currUser.id)

                        em = embedMessage(
                            title="My Stats", author=currUser.name, thumbnail=use.display_avatar.url)
                        em.add_field(
                            name="House", value=currUser.house, inline=True)
                        em.add_field(
                            name="Points", value=currUser.points, inline=True)
                        em.add_field(
                            name="wand", value=currUser.wand, inline=True)
                        em.add_field(
                            name="Wealth", value=currUser.wealth, inline=True)
                        em.add_field(name="Potions",
                                     value=currUser.potions, inline=True)
                        em.add_field(
                            name="Spells", value=currUser.spells, inline=True)
                        em.add_field(name="Enemies Defeated",
                                     value=currUser.enemiesDefeated, inline=True)

                        await self.create_embed(em, message)

                    if message.content == "~houseStats":

                        house = eval(currUser.house)
                        em = embedMessage(title="House Stats",
                                          thumbnail=house.url, inline=True)

                        em.add_field(
                            name="points", value=house.points, inline=True)

                        try:
                            l = house.students[:]
                        except:
                            house.students = []
                        em.add_field(name="number of students",
                                     value=len(house.students), inline=True)

                        await self.create_embed(em, message)

                    if message.content == "~leaderboard":
                        houses = [Slytherin, Gryffindor,
                                  Ravenclaw, Hufflepuff]
                        houses.sort(key=lambda x: x.points, reverse=True)
                        # await bot.send(self, message, f"1){houses[0].get_points_info()}\n2){houses[1].get_points_info()}\n3){houses[2].get_points_info()}\n4){houses[3].get_points_info()}")

                        em = embedMessage(
                            title="Leaderboard", color=discord.Color.dark_blue(), inline=True, thumbnail="https://i.pinimg.com/564x/f5/12/06/f5120687c3f9c1f1f8b8d1878bd84150.jpg")

                        em.add_field(
                            name="1st", value=houses[0].get_points_info(self), inline=True)
                        em.add_field(
                            name="2nd", value=houses[1].get_points_info(self), inline=True)
                        em.add_field(
                            name="3rd", value=houses[2].get_points_info(self), inline=True)
                        em.add_field(
                            name="4th", value=houses[3].get_points_info(self), inline=True)

                        await self.create_embed(em, message)

                if message.channel.name == "mini-games":
                    if message.content == "~emoGuess":
                        await self.games.emojis(self, currUser, message)

                    if message.content == "~wordChain":
                        await self.games.WordChain(self, currUser, message)

                    if message.content == "~crossword":
                        await self.games.crossword(self, currUser, message)

                if message.channel.name == "newts":
                    if message.content == "~trivia":
                        await self.games.Trivia(self, currUser, message)

                # removing channel
                self.notFreeChannel.remove(message.channel.id)

            else:
                em = embedMessage(title="Introduction Quests",
                                  description="***Complete the introduction quests to unlock further games!***")
                await self.create_embed(em, message)

        if currUser:
            currUser.update_level()
            self.save(currUser)
            self.notFreeUser.remove(message.author.id)

        ######### moderator commands #########

        # command_prefix = ">"

        # if (message.content.startswith(command_prefix)):
        #     if (message.author.guild_permissions.administrator):
        #         command = message.content[len(command_prefix):]

        #         if (command.startswith("kick")):
        #             user = command.split(" ")[1][2:-1]
        #             user = self.get_user(int(user))
        #             reason = " ".join(command.split(" ")[2:])
        #             await self.guild.kick(user, reason=reason)
        #             await self.send(message, f"{user} has been kicked.")

        #         elif (command.startswith("ban")):
        #             user = command.split(" ")[1][2:-1]
        #             user = self.get_user(int(user))
        #             reason = " ".join(command.split(" ")[2:])
        #             await self.guild.ban(user, reason=reason)
        #             await self.send(message, f"{user} has been banned.")

        #         elif (command.startswith("softban")):
        #             user = command.split(" ")[1][2:-1]
        #             user = self.get_user(int(user))
        #             await self.guild.ban(user)
        #             await self.guild.unban(user)
        #             await self.send(message, f"{user} has been softbanned.")

        #         elif (command.startswith("unban")):
        #             user = command.split(" ")[1][2:-1]
        #             user = self.get_user(int(user))
        #             await self.guild.unban(user)
        #             await self.send(message, f"{user} has been unbanned.")

        #         elif (command.startswith("mute")):
        #             user = command.split(" ")[1][2:-1]
        #             user = self.get_user(int(user))
        #             await self.guild.mute(user)
        #             await self.send(message, f"{user} has been muted.")

        #         elif (command.startswith("unmute")):
        #             user = command.split(" ")[1][2:-1]
        #             user = self.get_user(int(user))
        #             await self.guild.unmute(user)
        #             await self.send(message, f"{user} has been unmuted.")

        #         elif (command.startswith("clear")):
        #             await message.channel.purge()

        #         elif (command.startswith("slowmode")):
        #             time = command.split(" ")[1]
        #             await message.channel.edit(slowmode_delay=time)
        #             await message.channel.send(f"Slowmode set to {time} seconds.")
        #             await self.send(message, f"Slowmode set to {time} seconds.")


potter = bot(dataHandler)
potter.run(token)
