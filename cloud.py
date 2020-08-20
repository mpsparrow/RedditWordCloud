import argparse
import csv
import re
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from stop_words import safe_get_stop_words
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

parser = argparse.ArgumentParser(description="Turns a text file into a word cloud")
parser.add_argument("file", type=str,
                    help="The text file")
parser.add_argument("-l", nargs="+",
                    help="The languages to add stopwords for")
parser.add_argument("-o", metavar="out", type=str,
                    help="Output file")
parser.add_argument("-s", metavar="scale", type=int,
                    help="The scale of the wordcloud")
parser.add_argument("-m", metavar="mask", type=str,
                    help="The mask that is applied to the wordcloud")
parser.add_argument("-b", metavar="background", type=str,
                    help="Background color of the wordcloud")
parser.add_argument("-c", metavar=("cw", "cc"), type=str, nargs=2,
                    help="Width and color of contour")
parser.add_argument("--color", action="store_true",
                    help="Use mask as color mask")
parser.add_argument("-N", metavar="max_words", type=int,
                    help="Maximum number of words in WordCloud (Default 200)")
parser.add_argument("-w", metavar="wordlist", type=str,
                    help="The wordlist to use for weighting (Default english)")
parser.add_argument("-min", metavar="min_freq", type=float,
                    help="The minimum frequency a word needs to have to be counted in percent (Default 0)")
parser.add_argument("-boost", metavar="freq_boost", type=float,
                    help="The boost a word that isn't in the wordlist gets (Default 1)")
parser.add_argument("-blow", metavar="freq_blow", type=float,
                    help="The \"anti-boost\" a word that is in the wordlist gets (Default 1)")

args = parser.parse_args()

if args.b is None:
    args.b = "black"

if args.N is None:
    args.N = 200

if args.w is None:
    args.w = "english"

if args.min is None:
    args.min = 0

if args.boost is None:
    args.boost = 1

if args.blow is None:
    args.blow = 1

stopwords = set(STOPWORDS)
if args.l is not None:
    for language in args.l:
        stopwords.update(safe_get_stop_words(language.lower()))

mask = None
colors = None
if args.m is not None:
    print("Creating mask...", end=" ", flush=True)
    mask = np.array(Image.open(args.m).convert("RGB"))
    colors = ImageColorGenerator(mask)
    print("Done!")

cw = 0
cc = None
if args.c is not None:
    cw = int(args.c[0])
    cc = args.c[1]

wc_obj = WordCloud(font_path="ARIALUNI.TTF",
                   max_words=args.N,
                   collocations=False,
                   scale=args.s,
                   stopwords=stopwords,
                   mask=mask,
                   background_color=args.b,
                   mode="RGB",
                   contour_width=cw,
                   contour_color=cc
                   )

with open(args.file, encoding="utf-8") as file:
    text = file.read()
    text = re.sub(r'[\[\(]?https?:\/\/[0-9A-Za-z\/\?#\[\]\)@\.!$\&%\-+,;=]+', '', text)

    words = wc_obj.process_text(text)


with open(f"wordlists/{args.w}.csv") as list:
    lookup = csv.reader(list, delimiter=";")
    lookup_dict = {}
    for row in lookup:
        lookup_dict[row[1]] = int(row[2].replace(" ", ""))

out_dict = {}
words_total = 0
max_freq = 0
for (word, freq) in words.items():
    words_total += freq
    if freq > max_freq:
        max_freq = freq

for (word, freq) in words.items():
    if freq / words_total >= args.min:
        out_freq = freq
        if word in lookup_dict:
            out_freq *= (max_freq / lookup_dict[word]) / args.blow
        else:
            out_freq *= args.boost

        out_dict[word] = out_freq

wordcloud = wc_obj.generate_from_frequencies(out_dict)

if args.color is True:
    wordcloud.recolor(color_func=colors)

if args.o is not None:
    wordcloud.to_file(args.o)

plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")

plt.show()
