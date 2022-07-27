from decimal import Decimal
from tortoise.models import Model
from tortoise import fields, run_async
from tortoise import Tortoise
from tortoise.exceptions import NoValuesFetched, DoesNotExist
import hashlib
import os


class User(Model):
    id = fields.IntField(pk=True)
    chat_id = fields.BigIntField(unique=True)
    refcode = fields.CharField(unique=True, null=True, max_length=16)
    refered_by = fields.CharField(null=True, max_length=16)
    username = fields.CharField(max_length=32)
    count_refs = fields.IntField(default=0)
    count_refs_2nd = fields.IntField(default=0)
    lang = fields.CharField(max_length=2, default='en')
    balance = fields.DecimalField(default=0, max_digits=32, decimal_places=3)
    wallet = fields.CharField(max_length=50, null=True)
    messages: fields.ReverseRelation["Message"]
    coupons: fields.ReverseRelation["Coupon"]
    history: fields.ReverseRelation["History"]

    class Meta:
        table = 'users'

    def __str__(self):
        return self.username

    async def generate_refcode(self):
        strs = str(self.chat_id)
        result = hashlib.sha1(strs.encode())
        refcode = result.hexdigest()[:8]
        self.refcode = refcode
        await self.save()

    async def add_to_refs(self, refcode):
        self.refered_by = refcode
        await self.save()
        try:
            user1 = await User.get(refcode=refcode)
            user1.count_refs += 1
            await user1.save()
        except Exception as e:
            print(e)
        try:
            user2 = await User.get(refcode=user1.refered_by)
            user2.count_refs_2nd += 1
            await user2.save()
        except Exception as e:
            print(e)


class Message(Model):
    id = fields.IntField(pk=True)
    text = fields.CharField(max_length=500)
    date = fields.DatetimeField(auto_now_add=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name='messages')

    class Meta:
        table = 'messages'


class Coupon(Model):
    id = fields.IntField(pk=True)
    arr = fields.JSONField(default={'coupon': []})
    is_loaded = fields.BooleanField(default=False)
    date = fields.DatetimeField(auto_now=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name='coupons')

    class Meta:
        table = 'coupons'

    async def pay_to_refs(self):
        try:
            user1 = await User.get(refcode=self.user.refered_by)
            amount = await Setting.get(label = 'Стоимость').values()
            user1.balance += Decimal(amount['value']['coupon']) * Decimal('0.1')
            hs = History(type = 'ref', amount = Decimal(amount['value']['coupon']) * Decimal('0.1'), user = user1)
            await hs.save()
            await user1.save()
        except Exception as e:
            print(e)
        try:
            amount = await Setting.get(label = 'Стоимость').values()
            user2 = await User.get(refcode=user1.refered_by)
            user2.balance += Decimal(amount['value']['coupon']) * Decimal('0.05')
            hs = History(type = 'ref', amount = Decimal(amount['value']['coupon']) * Decimal('0.05'), user = user2)
            await hs.save()            
            await user2.save()
        except Exception as e:
            print(e)


class Setting(Model):
    id = fields.IntField(pk=True)
    label = fields.CharField(max_length=200)
    value = fields.JSONField()
    image: fields.ReverseRelation["Image"]
    class Meta:
        table = 'settings'


class Transaction(Model):
    id = fields.IntField(pk=True)
    hash = fields.CharField(max_length=300)

    class Meta:
        table = 'transactions'


class History(Model):
    id = fields.IntField(pk=True)
    type = fields.CharField(max_length=4)
    amount = fields.DecimalField(max_digits=32, decimal_places=3, default=0)
    date = fields.DatetimeField(auto_now=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name='history')

    class Meta:
        table = 'history'


class Image(Model):
    id = fields.IntField(pk=True)
    file_id = fields.CharField(max_length=100)
    filename = fields.CharField(max_length=100)
    message: fields.ForeignKeyRelation[Setting] = fields.ForeignKeyField(
        "models.Setting", related_name='image')

    class Meta:
        table = 'images'


async def run():
    await Tortoise.init(db_url="asyncpg://postgres:{}@coupon.localhost:5432".format(os.environ['PASSWORD_DB']), modules={"models": ["__main__"]})
    await Tortoise.generate_schemas()
if __name__ == '__main__':
    run_async(run())
