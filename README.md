# i-want-project v1
work in progress: a static version to show what it does, eventually it will have a small interactive frontend.
to run the code right now, it's necessary to set up a reddit account with api access to fill in the credentials.ini file.
drop everything in the same folder.
the filepaths for the resulting pdf and the backup input need to be changed (folder_path).
i've added an example output file, but i'm aiming at an easily usable dynamic version (via web service).

This program requests data from Reddit and puts it together in a pdf.
It's a reflection on navigating the internet as a woman.


Concept:

Subreddits such as TrollXChromosomes, where most posters are FLINTAs and content is curated for our eyes, can be uplifting spaces for us to express ourselves, share experiences and laugh together.

Apart from those tightly moderated communities however, sexism is still widespread in even the most popular Subreddits, e.g. AskReddit. This reddit flavour of gendered hate uses specific language and dogwhistles that flood our feeds with toxic content by default, unless we actively avoid them and decide not to participate.

In the last couple of years, thanks to misogynistic internet stars like Andrew Tate, "women" have become "females", and we're being talked about as if we were a non-human species, alien and inferior. When called out, those posters usually pretend that their use of the word is neutral.

By collecting comments starting with "females should" (and variations)  from the largest text-based subreddit AskReddit, the pattern becomes apparent. Sure, some of the comments talk about literal animals - but those fit right into the mix. due to the absurd nature of that lingo, ironic use of the phrase isn't always clear.

With a simple substitution algorithm, the peaceful, if somewhat typically "terminally online" chatter on TrollXChromosomes gets disturbed, then entirely consumed. FLINTAs expressing what we want, wish, hope for get overwritten by commenters speculating on our evil desires and telling us what we must do.


Details on the code:

The program tries to request data via pushshift API. If that's down, it uses a backup csv with automatically generated data. It usually loops once per subreddit, looking at 1000 comments and submissions, until it has 2x100 sentences. then it makes a list of strings, each representing a page. On page 2, 100 random starting points for substituting characters are chosen. On each following page, one more character (following the last substitution) gets changed. If the algo reaches already changed characters, it looks for a new starting point.

Most comments and about half of the code written by ChatGPT.

This program has been tested on my pc and nowhere else and does mostly what it should. Still, it needs a proper cleanup and some details aren't quite right. It can probably be optimized.

to do on this version:
- fix transition algo so that is keeps searching for starting points at the beginning, looping around
- wrangle the pdf maker function into maintaining the emoticons instead of deleting them, maybe by switching to another font for smileys
- possibly make substituted characters italic for easier spotting of the transition

to do on next version:
- make a simple web interface so that people can interact with the program, requesting new data each time.
- make cool animation to make it seem like people are typing, at first chatting with each other, then characters or sentences getting corrupted / glitched into the "females... " content.

