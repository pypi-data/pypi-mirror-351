try:
    from emoji import replace_emoji

except ImportError:
    import re

    def replace_emoji(string: str, replacement: str):
        # this covers many, but not all Emoji.
        emoji_pattern = r"[\U00010000-\U0010ffff]"
        return re.sub(emoji_pattern, replacement, string)
