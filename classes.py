import asyncio
import discord
import random
from assets.constants import *


class house():
    def __init__(self, name):
        self.name = name
        self.points = 0
        self.students = []

    def __str__(self):
        return self.name

    def add_points(self, points):
        self.points += points

    def add_student(self, student):
        self.students.append(student)

    def get_points(self):
        return self.points

    def get_students(self):
        return self.students

    def get_name(self):
        return self.name

    def get_info(self):
        return self.name + f" has {self.points} points. The following students are in {self.name}:\n" + "\n".join([x.name for x in self.students])

    def get_student_info(self):
        return self.name + " has the following students:\n" + "\n".join(self.students)

    def get_points_info(self):
        return self.name + f" has {self.points} points."


Hufflepuff = house("Hufflepuff")
Ravenclaw = house("Ravenclaw")
Gryffindor = house("Gryffindor")
Slytherin = house("Slytherin")

class user():
    users = []
    names = []
    ids = {}

    def __init__(self, name, id, house=None, wand=None, points=0, wealth=0, potions=[], spells=['stupefy', 'expelliarmus', 'protego'], items=[], progress=0, enemiesDefeated=0, health=150):
        self.name = name
        self.id = id
        self.house = house
        self.health = health
        self.max_health = health
        self.enemiesDefeated = enemiesDefeated
        self.wand = wand
        self.spells = spells
        self.points = points
        self.level = self.points//30
        self.wealth = wealth
        self.potions = potions
        self.items = items
        self.progress = progress
        user.users.append(self)
        user.names.append(self.name)
        user.ids[self.id] = self
        self.revealed = False

    def add_points(self, points):
        self.points += points

    def add_spell(self, spell):
        self.spells.append(spell)

    def add_potion(self, potion):
        self.potions.append(potion)

    def add_item(self, item):
        self.items.append(item)

    def set_house(self, house):
        self.house = house

    def get_info(self):
        return self.name + " is in " + self.house + f" and has {self.points} points."

    def get_full_info(self):
        return self.name + " is in " + self.house + f" and has {self.points} points. You have the following spells: " + ",".join(self.spells) + "\nYou have the following wand: " + self.wand + "\nYour level is: " + str(self.level) + "\nYour max health is: " + str(self.max_health) + "\nNumber of enemies defeated: " + str(self.enemiesDefeated)

    def get_spell_info(self):
        return self.name + " has the following spells:\n" + "\n".join(self.spells)

    def get_potion_info(self):
        return self.name + " has the following potions:\n" + "\n".join(self.potions)

    def get_item_info(self):
        return self.name + " has the following items:\n" + "\n".join(self.items)

    def get_house_info(self):
        return self.name + " is in " + self.house + "."

    def get_points_info(self):
        return self.name + " has " + self.points + " points."

class games:
    async def introduction(self, bot, message):
        '''
        This function is used whenever the user wants to login and use the bot.
        '''
        await bot.send(message, "Greetings! Welcome to the whimsical world of PotterBot, where the whispers of ancient spells and the flicker of wands weave tales of wonder reminiscent of Dumbledore's office. Here, amid the hallowed halls of Hogwarts, where portraits come to life and enchanted creatures roam, embark on a journey beyond the pages of the Marauder's Map, where mischief and magic await your command!")
        await bot.send(message, "If you wish to leave at any point in the game, just type 'exit'.")

        if message.author.id in user.ids:
            await bot.send(message, "Welcome back to Hogwarts, " + user.ids[message.author.id].name + "!")
            return user.ids[message.author.id]

        currUser = await self.new_user(bot, message)

        return currUser

    async def new_user(self, bot, message):
        '''
        Function to initiate a new user.
        '''
        await bot.send(message, "Welcome, new user! Please choose your username.")
        response = await bot.recieve(message, check=lambda message1: bot.check(message1, message))
        if response.content == "exit":
            await bot.send(response, "Goodbye.")
            return None

        if response.content in user.names:
            await bot.send(response, "I'm sorry, that username is already taken. Please try again.")
            return await bot.new_user(message)

        u = user(response.content, response.author.id)
        await bot.send(response, "Welcome to Hogwarts, " + response.content + "!")

        return u

    async def staircase(self, client, currUser, message):
        total_stairs = 20
        moves_left = total_stairs//2
        stairs_left = total_stairs
        cap_steps = total_stairs//3

        await message.channel.send(f"You're running late to class and you've just stepped onto the moving staircases. You now get {moves_left} moves to climb up {total_stairs} stairs to make it to your Transfiguration lesson on time. \nHere's what you have to do: \nType in the number of stairs you wanna climb at a time and then play a game of 7 up 7 down to see if you were successful. Mind your step! You don't wanna step onto a trick stair which will cause you to get stuck on that stair for the next move.\nConsecuently that move will be skipped (total moves reduces by 2)")
        await message.channel.send(f"Max steps that can be crossed per move is {cap_steps}. All the best!")
        await message.channel.send("If you don't know how 7 Up 7 Down works, enter '7' to learn now. Otherwise, type 'play' to start the game.")

        while True:
            response = await client.wait_for('message', check=lambda message1: client.check(message, message1))
            if response.content == "exit":
                await response.channel.send("Farewell for now, come back again soon!")
                return False

            elif response.content == "play":
                break

            elif response.content == "7":
                await message.channel.send("The random number generator generates a number between 1 to 12. You have to guess if the number is >=7 or <7 (Enter a number >=7 or <7 to guess respectively). If your guess is correct, you move up your chosen number of steps; but if your guess is wrong, you fall down the chosen number of steps.")
                await message.channel.send("Now that the rules are , type 'play' to proceed to the game.")
                break

            else:
                await response.channel.send("I'm sorry, I didn't catch that. Please try again.")

        trick = False

        while moves_left > 0 and stairs_left > 0:
            trick = random.choice([True, False, False, False, False, False])

            while True:
                await message.channel.send("How many steps do you wanna take at a time?")
                response = await client.wait_for('message', check=lambda message1: client.check(message1, message))
                n = response.content
                if n.isdigit() and int(n) > 0 and int(n) <= cap_steps:
                    break
                else:
                    await message.channel.send(f"Please enter a valid number from 1-{cap_steps}.")

            while True:
                await message.channel.send("Let's see if the odds are in your favour! Pick a number between 1 to 12 (both included).")
                response = await client.wait_for('message', check=lambda message1: client.check(message1, message))
                guess = response.content

                if response.content == "exit":
                    await response.channel.send("Farewell for now, come back again soon!")
                    return False

                elif guess.isdigit():
                    if int(guess) >= 1 and int(guess) <= 12:
                        break
                    else:
                        await message.channel.send("Please enter a valid guess from 1-12.")

                else:
                    await message.channel.send("Please enter a valid guess.")

            random_no = random.randint(1, 12)

            if trick == True:
                increment_steps = random.randint(1, int(n))
                await message.channel.send(f"Oh no! You stepped on a trick step on the {increment_steps} step.")
                stairs_left = min(stairs_left + increment_steps, total_stairs)
                moves_left -= 1

            if not trick and ((random_no >= 7 and int(guess) >= 7) or (random_no < 7 and int(guess) < 7)):
                await message.channel.send(f"Congrats! You have climbed {n} steps.")
                stairs_left = max(0, stairs_left - int(n))

            elif not trick:
                await message.channel.send(f"Alas! You have fallen down {n} steps. Better luck next time.")
                stairs_left = min(stairs_left + int(n), total_stairs)

            moves_left -= 1
            await message.channel.send(f"You now have to climb {stairs_left} stairs in {moves_left} moves.")

            if (moves_left*cap_steps < stairs_left):
                await message.channel.send(f"Oh no, you don't have enough moves!")
                break

        if stairs_left == 0:
            await message.channel.send(f"Phew! You've managed to maneuver the magical staircases to reach class on time. Now Professor McGonagall won't transfigure you into a pocket watch!")
            return True

        else:
            await message.channel.send(f"L! You couldn't maneuver the staircases on time and now you're late to class. Your excuse was lame and Professor McGonagall has deducted 5 house points from {currUser.house.get_name()}.")
            currUser.house.add_points(-5)
            return True

    async def Trivia(self, client, currUser, message):
        ques_done = []
        s = 0
        while True:
            while True:
                ques, ans = random.choice(list(trivia.items()))
                if ques not in ques_done:
                    ques_done.append(ques)
                    break
                else:
                    continue
            await message.channel.send(ques)
            response = await client.wait_for('message', check=lambda message1: client.check(message1, message))
            if response.content == "exit" and response.channel.name == "potterbot-newts":
                await response.channel.send("Farewell for now, come back again soon!")
                return False
            elif response.channel.name == "potterbot-newts":
                if response.content.title() in ans:
                    await response.channel.send("You're correct!")
                    s += 1

                else:
                    await response.channel.send(f"That's not right. The correct answer is {ans[0]}")
                    break
            else:
                await response.channel.send("A game is already in progress. Do you want to exit trivia? (yes/no)")
                response = await client.wait_for('message', check=lambda message1: client.check(message1, message))
                if response.content == "yes":
                    await response.channel.send("Farewell for now, come back again soon!")
                    return False
                continue

        await response.channel.send(f"You were right {s} times!")
        await message.channel.send(f"You've earned {s} points for your house!")
        currUser.house.points += s
        return True

    async def crossword(self, client, currUser, message):

        cross = {
            'cross1.png': {'1': 'Caldron', '2': 'Glasses', '3': 'Wand', '4': 'Owl', '5': 'Potion', '6': 'Sortinghat',
                           '7': 'Cloak', '8': 'Goldensnitch', '9': 'Broomstick', '10': 'Scar', '11': 'Cupboard'},
            'cross2.png': {'1': 'Voldemort', '2': 'Dumbledore', '3': 'Ron', '4': 'Broom', '5': 'Draco',
                           '6': 'Slytherin', '7': 'Hagrid', '8': 'Hedwig', '9': 'Scabbers', '10': 'Fluffy',
                           '11': 'Dudley'},
            'cross3.png': {'1': 'Muggle', '2a': 'Hogwarts', '2d': 'Hogsmeade', '3': 'Sirius', '4': 'Scabbers',
                           '5': 'Hedwig', '6': 'Honeydukes', '7': 'Alohomora', '8': 'Azkaban', '9': 'Always',
                           '10a': 'Dumbledore', '10d': 'Dobby', '11': 'Quidditch', '12': 'Fluffy', '13': 'Voldemort'},
            'cross4.png': {'1': 'Hedwig', '2': 'Weasley', '3': 'Hermione', '4': 'Neville', '5': 'Scabbers',
                           '6': 'Hagrid', '7': 'Dudley', '8': 'Draco', '9': 'Dumbledore'},
            'cross5.png': {'1': 'Hogwartsexpress', '2': 'Hufflepuff', '3': 'Ravenclaw', '4': 'Owls', '5': 'Boats',
                           '6': 'Diagonalley', '7': 'Toads', '8': 'Slytherin', '9': 'Sortinghat', '10': 'Hogwarts'},
            'cross6.png': {'1': 'Expelliarmus', '2': 'Lumos', '3': 'Dumbledoresarmy', '4': 'Darkmark',
                           '5': 'Goldensnitch', '6': 'Hufflepuff', '7': 'Hagrid', '8': 'Tomriddle', '9': 'Hogwarts',
                           '10': 'Basilisk', '11': 'Hermionegranger', '12': 'Hedwig'},
            'cross7.png': {'1': 'Voldemort', '2': 'Theburrow', '3': 'Crookshanks', '4': 'Dobby', '5': 'Snape',
                           '6': 'Privetdrive', '7': 'Diagon', '8': 'Scared', '9a': 'Every', '9d': 'Errol'},
            'cross8.png': {'1': 'Riddikulus', '2': 'Hedwig', '3': 'Hufflepuff', '4': 'Slytherin', '5': 'Ravenclaw',
                           '6': 'Fluffy', '7': 'Trolls', '8': 'Muggle', '9': 'Opens', '10': 'Tea', '11': 'Die',
                           '12': 'Hogwarts'},
            'cross9.png': {'1': 'Deluminator', '2': 'Howler', '3': 'Wand', '4': 'Invisibilitycloak', '5': 'Voldemort',
                           '6': 'Rubeushagrid', '7': 'AvadaKedavra', '8': 'Gryffindor', '9': 'Hufflepuff',
                           '10': 'Quidditch'}
            }

        chosen_one = random.choice(list(cross.keys()))
        await message.channel.send("Here's your crossword!\n Please don't put a space between 2 words in your answer.",
                                   file=discord.File(chosen_one))
        await message.channel.send(
            "You can type your answers in any order, but the format must be 'question_number answer'. For example, if the answer to the first question is Harry Potter, type '1 HarryPotter'. The answers are not case sensitive.")
        await message.channel.send(
            "For the crosswords that have both across and down on the same number, follow the following format: For example, if the answer for 1 across is HarryPotter, type '1a HarryPotter'. And '1d Hermione' if the answer for 1 down is Hermione.")
        await message.channel.send("Type 'I'm done' when you wish to end the game and reveal the answers.")

        user_answers = {}
        for i in cross[chosen_one]:
            user_answers[i] = ''

        while True:
            response = await client.wait_for('message', check=lambda message1: client.check(message1, message))
            if user_answers == cross[chosen_one]:
                await message.channel.send("Congrats! You've successfully solved the crossword.")
                await message.channel.send(f"You've earned {user_answers} points for your house!")
                currUser.house.add_points(len(user_answers))
                return True
            elif response.channel.name == "potterbot-mini-games":
                if response.content == "exit":
                    await response.channel.send("Farewell for now, come back again soon!")
                    return False

                elif response.content.lower() == "i'm done":
                    for i in cross[chosen_one]:
                        await response.channel.send(f"{i} : {cross[chosen_one][i]}")
                    await message.channel.send(f"You've earned {user_answers} points for your house!")
                    currUser.house.add_points(len(user_answers))
                    return True

                n = response.content.find(' ')

                try:
                    if response.content[n + 1:].title() == cross[chosen_one][response.content[0:n]]:
                        await response.channel.send("You're right, of course!")
                        user_answers[response.content[0:n]
                        ] = response.content[n + 1:].title()
                    else:
                        await response.channel.send(f"That's not right. Try again.")
                        user_answers[response.content[0:n]
                        ] = response.content[n + 1:].title()

                except KeyError:
                    if (n == -1):
                        await response.channel.send(f"There is no {response.content}")

                    elif (response.content[n - 1].isdigit()):
                        await response.channel.send(
                            f"{response.content[0:n]} has both across and down. Please specify which one you're answering.")

                    else:
                        await response.channel.send(f"There is no {response.content[0:n]}")
            else:
                await response.channel.send("A game is already in progress. Do you want to exit crossword? (yes/no)")
                response = await client.wait_for('message', check=lambda message1: client.check(message1, message))
                if response.content == "yes":
                    await response.channel.send("Farewell for now, come back again soon!")
                    return False