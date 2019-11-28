import discord
from discord.utils import get
from redbot.core import commands, Config, checks
from redbot.core.utils.chat_formatting import escape, info, error

class VisualRolesCog(commands.Cog):
    """Adds or removes roles for a user based on reactions."""

    def __init__(self, bot):

        default_guild = {
            "role_request_channel": None,
            "role_request_message": None,
            "role_reactions": {},
        }

        self.bot = bot
        self.config = Config.get_conf(self, identifier=3287368723648263)
        self.config.register_guild(**default_guild)

    @commands.group()
    @checks.admin()
    async def visualroles(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            pass

    @visualroles.command(name="channel")
    async def set_channel(self, ctx, channel_id: int):
        """Enter a channel id to set the roles request channel."""

        channel = ctx.guild.get_channel(channel_id)

        if channel is None:
            await ctx.send(error("Channel not found."))
            return
        elif channel.guild != ctx.guild:
            await ctx.send(error("Channel not found on this server."))
            return
        else:
            channel_id = channel.id

        await self.config.guild(ctx.guild).role_request_channel.set(channel_id)
        await self.config.guild(ctx.guild).role_request_message.set(None)

        if channel_id != None:
            await ctx.send(info("{channel} will now be used for users to select roles.".format(channel=channel.mention)))
            await ctx.send(info("NOTE: updating the channel has cleared the message setting. You will need to set a new message id using the visualroles message command."))
        else:
            await ctx.send(info("No channel is configured for users to select roles."))

    @visualroles.command(name="message")
    async def set_message(self, ctx, message_id: int):
        """Enter a message id to add roles to."""

        channel_id = await self.config.guild(ctx.guild).role_request_channel()

        if channel_id is None:
            await ctx.send(error("You must first set a channel."))
            return
        else:
            channel = ctx.guild.get_channel(channel_id)

        if message_id is None:
            await ctx.send(error("You must specify a message id."))
            return
        else:
            msg = await channel.fetch_message(message_id)
            message_id = msg.id

        await self.config.guild(ctx.guild).role_request_message.set(message_id)

        if message_id != None:
            await ctx.send(info("The message id {message} will be used for users to select roles.".format(message=msg.id)))
        else:
            await ctx.send(info("No message is configured for user to select roles."))

    @visualroles.command(name="list")
    async def list_linked_roles(self, ctx):
        """List all roles that are linked to reactions/emoji."""

        roledict = await self.config.guild(ctx.guild).role_reactions()

        role_embed = discord.Embed()
        role_embed.title = "Linked Roles"
        role_embed.description = "**Roles that have been linked with reactions/emojis.\n\n**"

        if not roledict:
            role_embed.add_field(name = "No roles have been linked with emojis yet. Use the link command to add one:", value = "```{p}visualroles link some_role some_emoji```".format(p=ctx.prefix))
        else:
            # get the valid emojis and list them along with valid roles
            role_embed.add_field(name = "__**Valid Links**__", value = "*Both the role and the custom emoji exist on the server.*\n\u200b", inline = False)
            for key in roledict:
                valid_emoji = discord.utils.get(ctx.guild.emojis, name=roledict[key])
                valid_role = get(ctx.guild.roles, name=key)
                if valid_emoji and valid_role:
                    role_embed.add_field(name = valid_emoji, value = "The role **" + str(key) + "** is linked to the emoji **" + str(roledict[key]) + "**.", inline = True)
                else: role_embed.add_field(name = "None Found", value = "No valid links found. Add some!", inline = True)

            role_embed.add_field(name = "\u200b", value = "\u200b", inline = False)

            # get the invalid emojis and list them along with valid roles
            role_embed.add_field(name = "__**Invalid Links**__", value = "*The role or emoji does not exist on the server.*\n\u200b", inline = False)
            for key in roledict:
                valid_emoji = discord.utils.get(ctx.guild.emojis, name=roledict[key])
                valid_role = get(ctx.guild.roles, name=key)
                if not valid_emoji or not valid_role:
                    role_embed.add_field(name = key, value = roledict[key], inline = True)
                else:
                    role_embed.add_field(name = "None Found", value = "No invalid links found. Yay!", inline = False)

            # TODO: instructions on how to clean them up

        await ctx.send(embed = role_embed)

    @visualroles.command(name="link")
    async def link_role_to_reaction(self, ctx, role, emoji):
        """Link a role to a reaction/emoji."""

        if role is None:
            await ctx.send(error("You must specify a role name."))
            return

        valid_role = discord.utils.find(lambda m: m.name.lower() == role.lower(), ctx.guild.roles)

        if not valid_role:
            await ctx.send("Couldn't find a valid role called {role}".format(role=role))
            return

        if emoji is None:
            await ctx.send(error("You must specify an emoji."))
            return

        valid_emoji = discord.utils.get(ctx.guild.emojis, name=emoji)

        if valid_emoji:
            roledict = await self.config.guild(ctx.guild).role_reactions()
            roledict.update({role : emoji})
            await self.config.guild(ctx.guild).role_reactions.set(roledict)
            await ctx.send(info("Role and reaction linked successfully!"))
        else:
            await ctx.send(error("No valid emoji found with that name."))


    # TODO: command to unlink a role and reaction; just specify the role

    #     message = await self.safe_get_message(channel, message_id)
    #     if message is None:
    #         await ctx.send(error("Message not found."))
    #         return
    #     else:
    #         msg_conf = self.get_message_config(server.id, channel.id, message.id)
    #         emoji_id = discord.utils.get(guild.emojis, name=emoji)
    #         if emoji_id:
    #             # do stuff
    #         else:
    #             await ctx.send(error("Emoji or reaction not found."))
    #             return


    # TODO: command to clear all settings (channel id, message id, all role and reaction links)

    # Events

    # async def on_raw_reaction_add(payload):
    #     if payload.guild_id is None:
    #         return # Reaction is on a private message
    #
    #     guild = client.get_guild(payload.guild_id)
    #
    #     role = discord.utils.get(guild.roles, name="testrole")
    #
    #     member = guild.get_member(payload.user_id)
    #
    #     role_assignment_channel = ["396366214420758529"]
    #
    #     if str(payload.channel_id) in role_assignment_channel:
    #         await member.add_roles(role, reason="testrole")
