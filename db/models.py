from tortoise.models import Model
from tortoise import fields

class BotInfo(Model):
    id = fields.IntField(primary_key=True)
    bale_id = fields.CharField(max_length=16, unique=True)
    telegram_id = fields.CharField(max_length=16)


    owner = fields.ForeignKeyField('models.User', related_name='owned_channels')
    is_active = fields.BooleanField(default=True)

    forwards = fields.IntField(default=0)


class User(Model):
    id = fields.IntField(primary_key=True)
    bale_id = fields.CharField(max_length=16)
    username = fields.CharField(max_length=64, null=True)

    def __str__(self):
        return f"User(id={self.id}, bale_id={self.bale_id}, username={self.username})"


class Channel(Model):
    id = fields.IntField(primary_key=True)
    bale_id = fields.CharField(max_length=16)
    telegram_id = fields.CharField(max_length=16)

    bale_username = fields.CharField(max_length=64, null=True)
    telegram_username = fields.CharField(max_length=64, null=True)

    owner = fields.ForeignKeyField('models.User', related_name='channels')

    is_active = fields.BooleanField(default=True)
    is_deleted = fields.BooleanField(default=False)

    def __str__(self):
        return f"User(id={self.id}, bale_id={self.bale_id}, bale_username={self.bale_username}, " + \
                f"telegram_id={self.telegram_id}, telegram_username={self.telegram_username}, " + \
                f"is_active={self.is_active}, is_deleted={self.is_deleted})"


class RequiredJoinChats(Model):
    id = fields.IntField(primary_key=True)
    channel_name = fields.CharField(max_length=64)
    channel_id = fields.CharField(max_length=16)
    channel_username = fields.CharField(max_length=64, null=True)

    chat_link = fields.CharField(max_length=128)

    bot = fields.ForeignKeyField('models.BotInfo', related_name='required_chats')
