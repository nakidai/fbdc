FBDC
--
FBDC - Filesystem based discord client

I just wanted to make filesystem based discord client, because I haven't seen discord clients of this kind. I couldn't find time for it because of my lazyness, but now it should work.

Thanks to @UltraQbik and his [reoi](https://github.com/UltraQbik/headless-discord) for some code that I've stilled.

Usage
--
```
usage: fbdc [-h] [-r PATH] token

positional arguments:
  token                 Your token

options:
  -h, --help            show this help message and exit
  -r PATH, --root PATH  Root of the bot
```

For example, to make it work in `root` directory you can use:
```
fbdc --root root "$MY_TOKEN"
```

Then you will see folders inside of this directory and `info` file. `info` can tell you more about a guild/channel/user. Directories inside of the root are the guilds you joined, and they will have directories inside too, which are the channels that guild have. Channel has `api` directory, where you can interact with client. To do it, you should create file with the name of the event you want to do and some content in it. For example to send message you need to create file named `message_send` with the text you want to send.

Full list of commands:  
- `message_send` - contents of the file will be sent.  
