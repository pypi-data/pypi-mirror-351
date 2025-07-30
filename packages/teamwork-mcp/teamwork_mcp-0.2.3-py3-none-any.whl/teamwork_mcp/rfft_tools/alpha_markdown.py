def clean_markdown(markdown: str):
    import regex
    # 删除网址
    pattern = regex.compile(r'\(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)\)')
    markdown2 = pattern.sub(r'()', markdown)
    # 删除删除网址之后的括号
    pattern2 = regex.compile(r'\[([^\]\[]*)\]\(\)')
    markdown2 = pattern2.sub(r'\1', markdown2)
    # 还有嵌套？再来次
    pattern3 = regex.compile(r'\[([^\]\[]*)\]\(\)')
    markdown2 = pattern3.sub(r'\1', markdown2)
    # 还有？
    pattern4 = regex.compile(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)')
    markdown2 = pattern4.sub(r'', markdown2)
    # 删除奇怪的换行
    markdown2 = markdown2.replace('\u3000', '')
    # 删除双换行
    markdown2 = '\n'.join(["" if len(line.strip()) <= 1 else line for line in markdown2.split('\n')])
    markdown2 = markdown2.replace('\n\n', '\n').replace('\n\n', '\n').replace('\n\n', '\n').replace('\n\n', '\n')
    return markdown2