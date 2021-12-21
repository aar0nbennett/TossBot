import discord, os, asyncio, csv, pandas as pd, json, random, datetime
from tabulate import tabulate

intents = discord.Intents.all()
from discord.ext import commands, tasks

# from keep_alive import keep_alive

'''
      Once winter break tasks are complete add it to UNCC Roommates
      Update Version string 
'''

# Global Variables
verStr = 'Version Alpha 1.0'
commandsPrefix = '~'  # In the server settings make it so server admin can change prefix
profanityToggle = True
swearwords = []
with open('swearwords.txt', 'r') as f:  # Creating swearwords list
    words = f.read()
    swearwords = words.split()
currName = 'coin'
botChannelToggle = False  # If set to true commands can only be run in defined channel
botChannelID = ''  # Will need to be defined for guilds that hae botChannelToggle set to True
bannedWords = []
csv_fieldnames = ['id', 'coins']
guilds_id = [713444498331533314]  # Add UNCC Roommates into here when ready
channels_id = [713755841282441257]  # Add 614672777240379409 when UNCC Roommates is in
default_gs_dict = {
    "profanityToggle": "True",
    "coinName": "coin",
    "commandPrefix": "tb!",
    "botChannelToggle": "False",
    "botChannelName": "None",
    "bannedWords": ["ass", "bastard", "bitch", "cunt", "dick", "fuck"]
}

# Client Setup
activity = discord.Activity(name=verStr, type=discord.ActivityType.streaming)
client = commands.Bot(command_prefix=commandsPrefix, intents=intents, activity=activity)
client.remove_command('help')

''' 
/////////////////////////////////////////////
---------------------------------------------
Discord Events
---------------------------------------------
/////////////////////////////////////////////
'''


@client.event
async def on_ready():
    print('Running ' + verStr)
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_guild_join(guild):
    """
                 Coin Database CSV
    1. Create a list of rows, and fill a row for each member
    2. Fill each CSV row with users id, and coin amount
        - Keys = id, coins
        - coins start at 200
    3. Write rows to CSV file, with guild.id as name
    """
    csv_rows = [{'id': 'swearjar', 'coins': 0}]
    for mem in guild.members:
        if not mem.bot:
            csv_rows.append({'id': mem.id, 'coins': 200})

    csv_name = str(guild.id) + '_coins.csv'
    with open(csv_name, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    # Create bot channel category
    '''
    Update later to make so that only TossBot can add messages to the channels
    Use something like this:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }
    Just make it so its everyone can read messages but cant send
    '''
    category = guild.create_category_channel('TossBot Channels')
    # Create bot audit log channel
    guild.create_text_channel('audit-log', category=category)
    # Create bet log channel
    guild.create_text_channel('bet-log', category=category)

    '''
                Guilds Setting JSON
    1. Pull dictionary from Guilds Setting JSON
    2. Add guild to dictionary
    3. Dump dictionary into Guilds Setting JSON
    
    with open("guilds_setting.json") as json_file:
        gs_dict = json.load(json_file)
    gs_dict[str(guild.id)] = default_gs_dict
    with open("guilds_setting.json", "w") as outfile:
        json.dump(gs_dict, outfile)
    '''


@client.event
async def on_member_join(member):
    # Add new member to coin database
    # Add them to the csv file dataframe
    csv_name = str(member.guild.id) + '_coins.csv'
    new_row = [member.id, 200]
    with open(csv_name, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(new_row)


@client.event
async def on_message(message):
    await profanityCheck(message)

    # Always have this at the end so commands can be processed
    await client.process_commands(message)


@client.event
async def on_member_remove(member):
    # Do need to remove member from coin csv? Up for debate
    print('on_member_remove does nothing atm')


''' 
/////////////////////////////////////////////
---------------------------------------------
Helper Methods
---------------------------------------------
/////////////////////////////////////////////
'''


async def profanityCheck(message):
    '''
    Not used atm as guild settings is a later integration

    # Grab profanity toggle from guild settings
    with open("guilds_setting.json") as json_file:
        gs_dict = json.load(json_file)
        '''
    if profanityToggle:  # If profanity check is on (True)
        # Check for swearwords
        for word in swearwords:
            if word in message.content:
                # Possibly switch to DM and deleting message
                # Make so it only sends once per message

                await message.channel.send('Bad discord user, shame on you for your profanity.'
                                           '\nYou have been fined 5 coins.'
                                           '\n5 coins have been added to the swear jar also.')
                # Add removeFunds from user
                print(message.author)
                print(message.author.id)
                await removeFunds(message.guild.id, message.author, 5)
                # Add money to swear jar
                await addtoSwearJar(message.guild.id)


async def addFunds(guild_id: int, user: discord.User, amount: int):
    print('Running add funds')
    csv_name = str(guild_id) + '_coins.csv'
    df = pd.read_csv(csv_name)
    coin_val = df.loc[df["id"] == str(user.id), "coins"]
    coin_val = coin_val + amount
    df.loc[df["id"] == str(user.id), "coins"] = coin_val
    df.to_csv(csv_name, index=False)


async def removeFunds(guild_id: int, user: discord.User, amount: int):
    print('Running remove funds')
    csv_name = str(guild_id) + '_coins.csv'
    df = pd.read_csv(csv_name)
    coin_val = df.loc[df["id"] == str(user.id), "coins"]
    coin_val = coin_val - amount
    df.loc[df["id"] == str(user.id), "coins"] = coin_val
    df.to_csv(csv_name, index=False)


# When profanity check is activated add x amount coins to swear jar
async def addtoSwearJar(guild_id):
    print('Running add to swear jar')
    csv_name = str(guild_id) + '_coins.csv'
    df = pd.read_csv(csv_name)
    coin_val = df.loc[df["id"] == "swearjar", "coins"]
    coin_val = coin_val + 5
    df.loc[df["id"] == 'swearjar', "coins"] = coin_val
    df.to_csv(csv_name, index=False)


# Not used atm but could be in the future
async def getGSValue(guild_id: int, key: str):
    with open("guilds_setting.json") as json_file:
        gs_dict = json.load(json_file)
    guild_dict = gs_dict.get(str(guild_id))
    return guild_dict.get(key)


# Figure out how to make it async and only grab the List[List[str]] and not the whole courtine
def getCSVList(guild_id: int):
    csv_list = list()
    csv_name = str(guild_id) + '_coins.csv'
    reader = csv.reader(open(csv_name))
    for row in reader:
        csv_list.append(row)
    return csv_list


# Could make helper method to find user csv row and return it

''' 
/////////////////////////////////////////////
---------------------------------------------
Display Commands
---------------------------------------------
/////////////////////////////////////////////
'''


# Self Created Help Command
@client.command(pass_context=True)
async def help(ctx):
    # Create embed with help information needed
    embed = discord.Embed(
        title="Help File Hyperlink",
        description="Click on link to travel to Help file in GitHub.",
        colour=discord.Colour.purple(),
        url='https://github.com/aar0nbennett/TossBot/blob/master/HELP.md'
    )
    await ctx.send(embed=embed)


# Self Created Help Command
@client.command(pass_context=True)
async def gitHub(ctx):
    # Create embed with help information needed
    embed = discord.Embed(
        title="GitHub Hyperlink",
        description="Click on link to travel to repo in GitHub for TossBot.",
        colour=discord.Colour.purple(),
        url='https://github.com/aar0nbennett/TossBot'
    )
    await ctx.send(embed=embed)


# Swear Jar display command
@client.command(pass_context=True)
async def swearJar(ctx):
    # Create embed with amount in swear jar and time before next raffle
    embed = discord.Embed(
        title="Swear Jar",
        colour=discord.Colour.purple()
    )
    csv_list = getCSVList(ctx.message.guild.id)
    swear_jar = csv_list.pop(1)
    embed.add_field(name='Amount in Swear Jar', value=swear_jar[1], inline=False)

    # Add Field for what time swear jar will raffle off

    await ctx.send(embed=embed)


# Coins leaderboard display command
@client.command(pass_context=True)
async def leaderboard(ctx):
    # Create embed with top 10 guild members based on amount of coins
    # Initialize embed for leader board
    embed = discord.Embed(
        title="Leaderboard",
        description="Top 10 members of guild in funds.",
        colour=discord.Colour.purple()
    )

    # Grab list of from CSV file
    csv_list = getCSVList(ctx.message.guild.id)
    # Remove first row, as it is the keys
    csv_list.pop(0)
    # Remove second row as it is the swear jar
    csv_list.pop(0)
    # Order list in greatest to least amount of coins
    sorted_rows = sorted(csv_list, key=lambda x: x[1], reverse=True)
    # Add top 10 members to a string or all members if less than 10
    member_string = ''
    if len(sorted_rows) > 10:
        for i in range(0, 10):
            member_string = member_string + str(i + 1) + '. @' + str(sorted_rows[i][0]) + ': ' + str(
                sorted_rows[i][1]) + '\n'
    else:
        for i in range(0, len(sorted_rows)):
            member_string = member_string + str(i + 1) + '. <@' + str(sorted_rows[i][0]) + '>: ' + str(
                sorted_rows[i][1]) + '\n'
    # Add the sting to a field
    embed.add_field(name='Members', value=member_string, inline=False)

    await ctx.send(embed=embed)
    # Check comments of leader board task in Todoist to see possible updates to be made


# Coin balance display command
@client.command(pass_context=True)
async def balance(ctx):
    # Create embed with coin amount of user
    # Grab list of from CSV file
    csv_list = getCSVList(ctx.message.guild.id)
    # Remove first row, as it is the keys
    csv_list.pop(0)
    # Remove second row as it is the swear jar
    csv_list.pop(0)
    # Find row with author
    author_row = []
    for row in csv_list:
        if row[0] == str(ctx.message.author.id):
            author_row = row
            break
    # Create embed showcasing their funds
    embed = discord.Embed(
        title="Balance",
        colour=discord.Colour.purple()
    )
    embed.add_field(name='Your Funds: ', value=str(author_row[1]), inline=False)

    await ctx.send(embed=embed)


# Coin balance display command
@client.command(pass_context=True)
async def balanceOf(ctx, user: discord.User):
    await ctx.send('Balance of command is not implemented as of now. Come back soon!')
    # Create embed with coin amount of specified user
    # Grab list of from CSV file
    csv_list = getCSVList(ctx.message.guild.id)
    # Remove first row, as it is the keys
    csv_list.pop(0)
    # Remove second row as it is the swear jar
    csv_list.pop(0)
    # Find row with user
    user_row = []
    for row in csv_list:
        if row[0] == str(user.id):
            user_row = row
            break
    # Create embed showcasing their funds
    embed = discord.Embed(
        title="BalanceOf",
        colour=discord.Colour.purple()
    )
    embed.add_field(name=user.name + ' Funds: ', value=str(user_row[1]), inline=False)

    await ctx.send(embed=embed)


''' 
/////////////////////////////////////////////
---------------------------------------------
Economy Commands
---------------------------------------------
/////////////////////////////////////////////
'''


# Fine command
@client.command(pass_context=True)
async def fine(ctx, user: discord.User, amount: int):
    # Make sure they are an admin
    if ctx.message.author.guild_permissions.administrator:
        # Make sure amount is a positive number
        if amount > 0:
            # Call remove funds helper method
            await removeFunds(ctx.message.guild, user, amount)
        else:
            await ctx.send("You must enter a positive number.")
    else:
        await ctx.send("You must be an Admin to use this command.")


# Gift command
@client.command(pass_context=True)
async def gift(ctx, user: discord.User, amount: int):
    # Make sure they are an admin
    if ctx.message.author.guild_permissions.administrator:
        # Make sure amount is a positive number
        if amount > 0:
            # Call add funds helper method
            await addFunds(ctx.message.guild, user, amount)
        else:
            await ctx.send("You must enter a positive number.")
    else:
        await ctx.send("You must be an Admin to use this command.")


# Bet command on an honor system that you react if you won or not
@client.command(pass_context=True)
async def bet(ctx, amount: int):
    # Check to make sure they entered a positive number
    if amount <= 0:
        await ctx.send('Bid must be a positive integer')
        return
    # Check to make sure they have the funds to make the bet
    csv_list = getCSVList(ctx.message.guild.id)
    csv_list.pop(0)
    csv_list.pop(0)
    max_bid = None
    for row in csv_list:
        if row[0] == str(ctx.message.author.id):
            max_bid = row[1]
            break
    # If they don't send message with their max bet possible and return
    if amount > int(max_bid):
        await ctx.send('Bid cannot be larger than amount in account\n'
                       'Your max bid is %s' % max_bid)
        return
    # Create embed of bet
    better = ctx.message.author
    today = datetime.datetime.now()
    won = False
    bet_channel = None
    embed = discord.Embed(
        title="Bet",
        timestamp=today,
        colour=discord.Colour.purple()
        # Add footer on what emoji to press
    )
    embed.add_field(name='Amount Bet', value=str(amount), inline=False)
    embed.set_footer(text='Click Green check if won, Red cross if loss')
    # Send embed to user PM with push reactions W and L
    embed_msg = await better.send(embed=embed)
    await embed_msg.add_reaction('✅')
    await embed_msg.add_reaction('❌')

    # Wait for them to push
    def check(reaction, user):
        return user == better and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌')

    reaction, user = await client.wait_for('reaction_add', check=check)
    # See which reaction better clicked
    cache_msg = discord.utils.get(client.cached_messages, id=embed_msg.id)
    print(cache_msg.reactions)
    for reaction in cache_msg.reactions:
        if reaction.count == 2:  # If the user reacted with this emoji
            print(reaction.emoji)
            if reaction.emoji == '✅': won = True
    # Once pushed either reward or remove coins from them
    if won:
        await addFunds(ctx.message.guild.id, better, amount)
    else:
        await removeFunds(ctx.message.guild.id, better, amount)
    # Once pushed create outcome embed and send to user PM and bet-log
    outcome_embed = discord.Embed(
        title="Bet Outcome",
        timestamp=today,
        colour=discord.Colour.purple()
    )
    outcome_embed.add_field(name='Amount Bet by ' + better.name, value=str(amount), inline=False)
    if won:
        outcome_embed.add_field(name='Outcome of bet', value='Won ' + str(amount), inline=False)
    elif not won:
        outcome_embed.add_field(name='Outcome of bet', value='Lost ' + str(amount), inline=False)
    await better.send(embed=outcome_embed)
    for channel in ctx.message.guild.text_channels:
        if channel.name == 'bet-log':
            bet_channel = channel
    await bet_channel.send(embed=outcome_embed)


# Raffle method, called when the weekly raffle timer is up
async def raffle(guild_id: int):
    # Grab amount of coins in swear jar
    csv_list = getCSVList(guild_id)
    sj = csv_list.pop(1)
    sj_amount = sj[1]

    # Randomly select one member
    csv_list.pop(0)
    winner = random.choice(csv_list)
    winner_id = winner[0]

    # Update coin csv
    csv_name = str(guild_id) + '_coins.csv'
    df = pd.read_csv(csv_name)
    # Give winning user sj_amount
    coin_val = df.loc[df["id"] == str(winner_id), "coins"]
    coin_val = coin_val + sj_amount
    df.loc[df["id"] == str(winner_id), "coins"] = coin_val
    # Set Swear Jar to zero
    df.loc[df["id"] == 'swearjar', "coins"] = 0
    df.to_csv(csv_name, index=False)

    return winner_id, sj_amount  # Return both id and amount to be put in the congratulations message


# Task for raffle called every week
@tasks.loop(hours=168)
async def called_once_a_week():
    for i in range(len(guilds_id) - 1):
        message_channel = client.get_channel(channels_id[i])
        print(f"Got channel {message_channel}")
        winner_id, winnings = raffle(guilds_id[i])
        winner_mentionable = '<@' + winner_id + '>'
        await message_channel.send('Congrats %s you have won this weeks raffle!\n'
                                   'You have won %d' % (winner_mentionable, int(winnings)))


@called_once_a_week.before_loop
async def before():
    await client.wait_until_ready()
    print("Finished waiting")


# Uncomment when ready to do raffle, make sure to implement for UNCC Roommates discord also
# called_once_a_week.start()
client.run(os.getenv('TOKEN'))
