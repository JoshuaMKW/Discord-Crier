import asyncio
import atexit
import random

import os
import sys

from io import BytesIO

import discord
from discord.ext import commands
from dotenv import load_dotenv

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 


PRONOUNS = ["I", "You", "They", "He", "She", "It", "My"]
VERBS = ["like", "likes", "want", "wants", "hate", "hates", "love", "loves", "become", "became", "was", "were", "am", "are", "is", "will"] # incomplete
NOUNS = ["body", "phone", "drugs", "pet", "food", "car", "job", "family", "money", "dreams", "fears", "destiny", "stuff", "things", "status", "problem", "problems", "solution", "solutions"]
COMMON_ADJECTIVES = ["much", "little", "extravagent", "extreme", "cool", "bad", "dope", "thicc", "terrible", "awesome", "great", "out of this world", "radical", "crazy", "perfect"]

MARKOV_LIST = {"__START__": ["If", "I", "You", "They", "He", "She", "It", "My"],

               # --- CONDITIONAL CONNECTIONS --- #
               "If": ["I", "you", "he", "she", "they", "it", "my"],

               # --- PRONOUNS ---#
               "I": ["like", "want", "hate", "love", "became", "was", "am", "will", "lose", "lost", "won", "win", "eat", "ate", "drop", "dropped", "pick", "picked", "tie", "tied"],
               "You": ["like", "want", "hate", "love", "became", "were", "are", "will", "lose", "lost", "won", "win", "eat", "ate", "drop", "dropped", "pick", "picked", "tie", "tied"],
               "They": ["like", "want", "hate", "love", "became", "were", "are", "will", "lose", "lost", "won", "win", "eat", "ate", "drop", "dropped", "pick", "picked", "tie", "tied"],
               "He": ["likes", "wants", "hates", "loves", "became", "was", "is", "will", "loses", "lost", "won", "wins", "eats", "ate", "drops", "dropped", "picks", "picked", "ties", "tied"],
               "She": ["likes", "wants", "hates", "loves", "became", "was", "is", "will", "loses", "lost", "won", "wins", "eats", "ate", "drops", "dropped", "picks", "picked", "ties", "tied"],
               "It": ["likes", "wants", "hates", "loves", "became", "was", "is", "will", "loses", "lost", "won", "wins", "eats", "ate", "drops", "dropped", "picks", "picked", "ties", "tied"],
               "My": ["body", "phone", "drugs", "pet", "food", "car", "job", "family", "money", "dreams", "fears", "destiny"],

               "you": ["like", "want", "hate", "love", "became", "were", "are", "will", "lose", "lost", "won", "win", "eat", "ate", "drop", "dropped", "pick", "picked", "tie", "tied"],
               "they": ["like", "want", "hate", "love", "became", "were", "are", "will", "lose", "lost", "won", "win", "eat", "ate", "drop", "dropped", "pick", "picked", "tie", "tied"],
               "he": ["likes", "wants", "hates", "loves", "became", "was", "is", "will", "loses", "lost", "won", "wins", "eats", "ate", "drops", "dropped", "picks", "picked", "ties", "tied"],
               "she": ["likes", "wants", "hates", "loves", "became", "was", "is", "will", "loses", "lost", "won", "wins", "eats", "ate", "drops", "dropped", "picks", "picked", "ties", "tied"],
               "it": ["likes", "wants", "hates", "loves", "became", "was", "is", "will", "loses", "lost", "won", "wins", "eats", "ate", "drops", "dropped", "picks", "picked", "ties", "tied"],
               "my": ["body", "phone", "drugs", "pet", "food", "car", "job", "family", "money", "dreams", "fears", "destiny"],

               # --- VERBS --- #
               "like": ["my", "his", "her", "their", "its", "to", "too", "food", "drugs", "money", "games", "life", "people", "having", "going", "bringing", "taking"],
               "likes": ["my", "his", "her", "their", "its", "to", "too", "food", "drugs", "money", "games", "life", "people", "having", "going", "bringing", "taking"],
               "want": ["my", "his", "her", "their", "its", "to", "too", "food", "drugs", "money", "games", "life", "people", "having", "going", "bringing", "taking"],
               "wants": ["my", "his", "her", "their", "its", "to", "too", "food", "drugs", "money", "games", "life", "people", "having", "going", "bringing", "taking"],
               "hate": ["my", "his", "her", "their", "its", "to", "too", "food", "drugs", "money", "games", "life", "people", "having", "going", "bringing", "taking"],
               "hates": ["my", "his", "her", "their", "its", "to", "too", "food", "drugs", "money", "games", "life", "people", "having", "going", "bringing", "taking"],
               "love": ["my", "his", "her", "their", "its", "to", "too", "food", "drugs", "money", "games", "life", "people", "having", "going", "bringing", "taking"],
               "loves": ["my", "his", "her", "their", "its", "to", "too", "food", "drugs", "money", "games", "life", "people", "having", "going", "bringing", "taking"],
               "become": ["my", "his", "her", "their", "its", "too", "food", "drugs", "money", "games", "life", "people"],
               "became": ["my", "his", "her", "their", "its", "to", "too", "food", "drugs", "money", "games", "life", "people", "having", "going", "bringing", "taking"],
               "were": ["my", "his", "her", "their", "its", "too", "having", "going", "bringing", "taking"],
               "am": ["my", "his", "her", "their", "its", "too", "having", "going", "bringing", "taking"],
               "are": ["my", "his", "her", "their", "its", "too", "having", "going", "bringing", "taking"],
               "will": ["have", "go", "bring", "take"],
               "lose": ["my", "his", "her", "their", "its", "too", "to", "food", "drugs", "money", "games", "life", "people", "having", "going", "bringing", "taking"],
               "loses": ["my", "his", "her", "their", "its", "too", "to", "food", "drugs", "money", "games", "life", "people", "having", "going", "bringing", "taking"],
               "lost": ["my", "his", "her", "their", "its", "too", "to", "food", "drugs", "money", "games", "life", "people", "having", "going", "bringing", "taking"],
               "won": ["my", "his", "her", "their", "its", "too", "to", "food", "drugs", "money", "games", "life", "people", "having", "going", "bringing", "taking"],
               "win": ["my", "his", "her", "their", "its", "too", "food", "drugs", "money", "games", "life", "people", "having", "going", "bringing", "taking"],
               "wins": ["my", "his", "her", "their", "its", "too", "food", "drugs", "money", "games", "life", "people", "having", "going", "bringing", "taking"],
               "eat": ["my", "his", "her", "their", "its", "too", "food", "drugs", "money", "games", "life", "people"],
               "eats": ["my", "his", "her", "their", "its", "too", "food", "drugs", "money", "games", "life", "people"],
               "ate": ["my", "his", "her", "their", "its", "too", "food", "drugs", "money", "games", "life", "people"],
               "drop": ["my", "his", "her", "their", "its", "too", "food", "drugs", "money", "games", "life", "people", "having", "going", "bringing", "taking"],
               "drops": ["my", "his", "her", "their", "its", "too", "food", "drugs", "money", "games", "life", "people", "having", "going", "bringing", "taking"],
               "dropped": ["my", "his", "her", "their", "its", "too", "food", "drugs", "money", "games", "life", "people", "having", "going", "bringing", "taking"],
               "pick": ["my", "his", "her", "their", "its", "too", "food", "drugs", "money", "games", "life", "people", "having", "going", "bringing", "taking"],
               "picks": ["my", "his", "her", "their", "its", "too", "food", "drugs", "money", "games", "life", "people", "having", "going", "bringing", "taking"],
               "picked": ["my", "his", "her", "their", "its", "too", "food", "drugs", "money", "games", "life", "people", "having", "going", "bringing", "taking"],
               "tie": ["my", "his", "her", "their", "its", "too", "people"],
               "ties": ["my", "his", "her", "their", "its", "too", "people"],
               "tied": ["my", "his", "her", "their", "its", "too", "people"],

               # --- NOUN CONNECTIONS --- #
               "with": ["my", "his", "her", "their", "its", "too", "food", "drugs", "money", "games", "life", "people"],
               "while": ["my", "his", "her", "their", "its", "too", "food", "drugs", "money", "games", "life", "people"],

               # --- POSSESSION --- #
               "his": ["body", "phone", "drugs", "pet", "food", "car", "job", "family", "money", "dreams", "fears", "destiny", "stuff", "things", "status", "problem", "problems", "solution", "solutions"],
               "her": ["body", "phone", "drugs", "pet", "food", "car", "job", "family", "money", "dreams", "fears", "destiny", "stuff", "things", "status", "problem", "problems", "solution", "solutions"],
               "their": ["body", "phone", "drugs", "pet", "food", "car", "job", "family", "money", "dreams", "fears", "destiny", "stuff", "things", "status", "problem", "problems", "solution", "solutions"],
               "its": ["body", "phone", "drugs", "pet", "food", "car", "job", "family", "money", "dreams", "fears", "destiny", "stuff", "things", "status", "problem", "problems", "solution", "solutions"],

               # --- SPECIAL VERBS --- #
               "have": ["my", "his", "her", "their", "its", "too", "food", "drugs", "money", "games", "life", "people", "a job", "a pet", "a family", "a destiny"],
               "go": ["too", "to"],
               "bring": ["my", "his", "her", "their", "its", "too", "food", "drugs", "money", "games", "life", "people"],
               "having": ["my", "his", "her", "their", "its", "too", "food", "drugs", "money", "games", "life", "people", "a job", "a pet", "a family", "a destiny"],
               "going": ["too", "to"],
               "bringing": ["my", "his", "her", "their", "its", "too", "food", "drugs", "money", "games", "life", "people"],
               "take": ["my", "his", "her", "their", "its", "too", "food", "drugs", "money", "games", "life", "people"],
               "taking": ["my", "his", "her", "their", "its", "too", "food", "drugs", "money", "games", "life", "people"],

               # --- VERBAL CONNECTIONS --- #
               "to": ["like", "want", "hate", "love", "become", "lose", "win", "eat", "drop", "pick", "tie", "go", "have", "bring", "take"],

               # --- NOUNS --- #
               "body": ["is", "was", "will be", "too", "though", "although", "but"],
               "phone": ["is", "was", "will be", "too", "though", "although", "but"],
               "drugs": ["are", "were", "will be", "too", "though", "although", "but"],
               "pet": ["is", "was", "will be", "too", "though", "although", "but"],
               "food": ["is", "was", "will be", "too", "though", "although", "but"],
               "car": ["is", "was", "will be", "too", "though", "although", "but"],
               "job": ["is", "was", "will be", "too", "though", "although", "but"],
               "family": ["is", "was", "will be", "too", "though", "although", "but"],
               "money": ["is", "was", "will be", "too", "though", "although", "but"],
               "games": ["are", "were", "will be", "too", "though", "although", "but"],
               "life": ["is", "was", "will be", "too", "though", "although", "but"],
               "people": ["are", "were", "will be", "too", "though", "although", "but"],
               "dreams": ["are", "were", "will be", "too", "though", "although", "but"],
               "fears": ["are", "were", "will be", "too", "though", "although", "but"],
               "destiny": ["is", "was", "will be", "too", "though", "although", "but"],
               "a pet": ["is", "was", "will be", "too", "though", "although", "but"],
               "a job": ["is", "was", "will be", "too", "though", "although", "but"],
               "a family": ["is", "was", "will be", "too", "though", "although", "but"],
               "a destiny": ["is", "was", "will be", "too", "though", "although", "but"],
               "stuff": ["is", "was", "will be", "too", "though", "although", "but"],
               "things": ["are", "were", "will be", "too", "though", "although", "but"],
               "status": ["is", "was", "will be", "too", "though", "although", "but"],
               "problem": ["is", "was", "will be", "too", "though", "although", "but"],
               "problems": ["are", "were", "will be", "too", "though", "although", "but"],
               "solution": ["is", "was", "will be", "too", "though", "although", "but"],
               "solutions": ["are", "were", "will be"],



               # --- DESCRIPTIVE CONNECTIONS --- #
               "is": COMMON_ADJECTIVES,
               "was": COMMON_ADJECTIVES,
               "will be": COMMON_ADJECTIVES,
               "too": COMMON_ADJECTIVES,
               "though": ["I", "you", "he", "she", "they", "it", "my", "when", "if", "only when", "and", "or", "only if", "even if", "even when", "even though",
                          "food", "family", "money", "games", "life", "people", "dreams", "fears", "destiny", "a pet", "a job", "a family", "a destiny", "stuff", "things", "status", "problems", "solutions"],
               "although": ["I", "you", "he", "she", "they", "it", "my", "when", "if", "only when", "and", "or", "only if", "even if", "even when", "even though",
                            "food", "family", "money", "games", "life", "people", "dreams", "fears", "destiny", "a pet", "a job", "a family", "a destiny", "stuff", "things", "status", "problems", "solutions"],
               "but": ["I", "you", "he", "she", "they", "it", "my", "when", "if", "only when", "and", "or", "only if", "even if", "even when", "even though",
                       "food", "family", "money", "games", "life", "people", "dreams", "fears", "destiny", "a pet", "a job", "a family", "a destiny", "stuff", "things", "status", "problems", "solutions"],

               # --- ADJECTIVES --- #
               COMMON_ADJECTIVES[0]: ["when", "if", "only when", "and", "or", "only if", "even if", "even when", "even though"],
               COMMON_ADJECTIVES[1]: ["when", "if", "only when", "and", "or", "only if", "even if", "even when", "even though"],
               COMMON_ADJECTIVES[2]: ["when", "if", "only when", "and", "or", "only if", "even if", "even when", "even though"],
               COMMON_ADJECTIVES[3]: ["when", "if", "only when", "and", "or", "only if", "even if", "even when", "even though"],
               COMMON_ADJECTIVES[4]: ["when", "if", "only when", "and", "or", "only if", "even if", "even when", "even though"],
               COMMON_ADJECTIVES[5]: ["when", "if", "only when", "and", "or", "only if", "even if", "even when", "even though"],
               COMMON_ADJECTIVES[6]: ["when", "if", "only when", "and", "or", "only if", "even if", "even when", "even though"],
               COMMON_ADJECTIVES[7]: ["when", "if", "only when", "and", "or", "only if", "even if", "even when", "even though"],
               COMMON_ADJECTIVES[8]: ["when", "if", "only when", "and", "or", "only if", "even if", "even when", "even though"],
               COMMON_ADJECTIVES[9]: ["when", "if", "only when", "and", "or", "only if", "even if", "even when", "even though"],
               COMMON_ADJECTIVES[10]: ["when", "if", "only when", "and", "or", "only if", "even if", "even when", "even though"],
               COMMON_ADJECTIVES[11]: ["when", "if", "only when", "and", "or", "only if", "even if", "even when", "even though"],
               COMMON_ADJECTIVES[12]: ["when", "if", "only when", "and", "or", "only if", "even if", "even when", "even though"],
               COMMON_ADJECTIVES[13]: ["when", "if", "only when", "and", "or", "only if", "even if", "even when", "even though"],
               COMMON_ADJECTIVES[14]: ["when", "if", "only when", "and", "or", "only if", "even if", "even when", "even though"],

               # --- LOOPERS --- #
               "when": ["I", "you", "he", "she", "they", "it", "my"],
               "if": ["I", "you", "he", "she", "they", "it", "my"],
               "only when": ["I", "you", "he", "she", "they", "it", "my"],
               "and": ["I", "you", "he", "she", "they", "it", "my"],
               "or": ["I", "you", "he", "she", "they", "it", "my"],
               "only if": ["I", "you", "he", "she", "they", "it", "my"],
               "even if": ["I", "you", "he", "she", "they", "it", "my"],
               "even when": ["I", "you", "he", "she", "they", "it", "my"],
               "even though": ["I", "you", "he", "she", "they", "it", "my"],

               # --- END WORDS --- #
               "__END__": ["you", "him", "her", "them", "loses", "wins", "lose", "win", "likes", "hates", "become", "body", "phone", "drugs", "pet", "food", "car", "job", "family", "money", "games", "life", "people", "dreams", "fears", "destiny", "a pet", "a job", "a family", "a destiny"]
}

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
#GUILD = os.getenv("DISCORD_GUILD")
#CHANNEL = os.getenv("DISCORD_CHANNEL")
GUILD = "JoshuaMK's server"
CHANNEL = 783486609924292681

class TextWrapper(object):
    """ Helper class to wrap text in lines, based on given text, font
        and max allowed line width.
    """

    def __init__(self, text, font, max_width):
        self.text = text
        self.text_lines = [
            ' '.join([w.strip() for w in l.split(' ') if w])
            for l in text.split('\n')
            if l
        ]
        self.font = font
        self.max_width = max_width

        self.draw = ImageDraw.Draw(
            Image.new(
                mode='RGB',
                size=(100, 100)
            )
        )

        self.space_width = self.draw.textsize(
            text=' ',
            font=self.font
        )[0]

    def get_text_width(self, text):
        return self.draw.textsize(
            text=text,
            font=self.font
        )[0]

    def wrapped_text(self):
        wrapped_lines = []
        buf = []
        buf_width = 0

        for line in self.text_lines:
            for word in line.split(' '):
                word_width = self.get_text_width(word)

                expected_width = word_width if not buf else \
                    buf_width + self.space_width + word_width

                if expected_width <= self.max_width:
                    # word fits in line
                    buf_width = expected_width
                    buf.append(word)
                else:
                    # word doesn't fit in line
                    wrapped_lines.append(' '.join(buf))
                    buf = [word]
                    buf_width = word_width

            if buf:
                wrapped_lines.append(' '.join(buf))
                buf = []
                buf_width = 0

        return '\n'.join(wrapped_lines)

class QuoteHandler():
    class CryTypes:
        TEXT = 0
        IMAGE = 1

    def __init__(self, vocabulary: dict, imageFolder: str, markovWordChain={}):
        self.cryType = QuoteHandler.CryTypes.IMAGE
        self.quoteLog = []
        self.startswith = None
        self._markovWords = vocabulary
        self._templateImages = [os.path.join(imageFolder, image) for image in os.listdir(imageFolder) if os.path.isfile(os.path.join(imageFolder, image))]
        self._isIfContext = False
        self._forceContinue = False


    @property
    def lastQuote(self) -> str:
        if len(self.quoteLog) == 0:
            return None
        else:
            return self.quoteLog[-1]

    @property
    def firstQuote(self) -> str:
        if len(self.quoteLog) == 0:
            return None
        else:
            return self.quoteLog[0]

    @property
    def msgCount(self):
        return len(self.quoteLog)

    def grab_random_quote(self) -> str:
        quote = self._imagine_quote()
        self.quoteLog.append(quote)
        return quote

    def grab_complying_quote(self, _startswith: str = None, max_trys: int = 1000000) -> str:
        quote = self.grab_random_quote()
        i = 0
        while i < max_trys:
            if _startswith is not None:
                starts = quote.startswith(_startswith)
            else:
                starts = True

            if starts:
                return quote

            self.quoteLog.pop()
            quote = self.grab_random_quote()
            i += 1

        return self.grab_random_quote()

    def generate_image(self, _startswith: str = None, max_trys: int = 1000000) -> Image:
        quote = self.grab_complying_quote(_startswith=_startswith, max_trys=max_trys)

        img = Image.open(random.choice(self._templateImages))
        draw = ImageDraw.Draw(img)
        
        strokeWidth = 2 if img.size[0] > 500 else 1
        
        font = ImageFont.truetype(random.choice(["arial.ttf", os.path.join("fonts", "calig_pen.ttf")]), int(img.size[0] / 14) - int(len(quote) / 4))
        
        w, h = draw.textsize(TextWrapper(quote, font, img.size[0] - 100).wrapped_text(), font=font)
        draw.text(((img.size[0] - w) / 2, (img.size[1] - h) / 5), TextWrapper(quote, font, 600).wrapped_text(), (255, 255, 255), font=font, stroke_width=strokeWidth, stroke_fill=(0, 0, 0))
        return img

    def _random_rgb(self) -> tuple:
        return (random.randrange(0, 256), random.randrange(0, 256), random.randrange(0, 256))

    def _imagine_quote(self) -> str:
        generated = []
        minlen = random.randrange(4, 14)
        while True:
            if not generated:
                words = self._markovWords['__START__']
                generated.append(random.choice(words))
                continue

            elif len(generated) > 1:
                if generated[-1] in self._markovWords['__END__'] and len(generated) > minlen and not self._forceContinue:
                    break

            words = self._markovWords[generated[-1]]
            
                 
            #if len(generated) > 2 and len(words) == 2:
            #    if not isinstance(words[0], str):
            #        words = words[0] if generated[-2] in NOUNS else words[1]

            thisWord = random.choice(words)

            if thisWord in ("when", "while", "if", "only when", "and", "or", "only if", "even if", "even when", "even though"):
                self._isIfContext = True
                self._forceContinue = True
            elif thisWord in (*NOUNS, *PRONOUNS) and generated[-1] not in ("when", "if", "only when", "and", "or", "only if", "even if", "even when", "even though"):
                self._isIfContext = False
                self._forceContinue = False
                
            generated.append(thisWord)

        return " ".join(generated)

class TownCrier(commands.Bot):
    def __init__(self, command_prefix="!", case_insensitive=True):
        super().__init__(command_prefix, case_insensitive=case_insensitive)

        self.guild = None
        self.channel = None
        self.waitTime = 60
        self.quoter = QuoteHandler(vocabulary=MARKOV_LIST, imageFolder="images")
        self.back_end_task = self.loop.create_task(self.cry_message())

    async def on_ready(self):
        _boxwidth = 24
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!tHelp"))
        print("-"*_boxwidth)
        print("::Logged in as::".center(_boxwidth))
        print(self.user.name.center(_boxwidth))
        print(("id=" + str(self.user.id)).center(_boxwidth))
        print("-"*_boxwidth)

    async def cry_message(self):
        await self.wait_until_ready()
        self.guild = discord.utils.get(self.guilds, name=GUILD)
        self.channel = self.get_channel(CHANNEL)
        while not self.is_closed():
            if self.quoter.cryType == QuoteHandler.CryTypes.IMAGE:
                with BytesIO() as image_binary:
                    try:
                        self.quoter.generate_image().save(image_binary, "PNG")
                        image_binary.seek(0)
                        await self.channel.send(file=discord.File(fp=image_binary, filename="{}.png".format(random.randrange(0, 10000000000000))))
                    except Exception as e:
                        print(e)
            else:
                await self.channel.send(self.quoter.grab_complying_quote(_startswith=self.quoter.startswith))
            await asyncio.sleep(self.waitTime)

    @atexit.register
    def __set_offline(self):
        self.logout()

try:
    bot = TownCrier()
except Exception as e:
    print(e)

@bot.event
@commands.has_permissions(manage_roles=True)
async def on_message(message):
    if message.channel.id == bot.channel.id:
        if message.content.startswith("!tDelay".lower()):
            try:
                bot.waitTime = int(float(message.content.strip().split()[1]))
            except IndexError:
                await message.channel.send(f"Alright sir, but please tell me how long to wait after the command! I don't know what to do...")
            else:
                if bot.waitTime == 1:
                    await message.channel.send("Alright sir, I will cry out every second!")
                elif bot.waitTime <= 0:
                    await message.channel.send("Sorry sir, I won't spam the channel!")
                else:
                    await message.channel.send(f"Alright sir, I will cry out every {bot.waitTime} seconds!")
        elif message.content.lower() == "!tCryImages".lower():
            bot.quoter.cryType = QuoteHandler.CryTypes.IMAGE
            await message.channel.send("Alright! I shall cry out with my beautiful artwork!")
        elif message.content.lower() == "!tCryWords".lower():
            bot.quoter.cryType = QuoteHandler.CryTypes.TEXT
            await message.channel.send("Alright! I shall cry out with my words!")

bot.run(TOKEN)
