'''
Configuration File

Setup this file according to your application Models as to map their
attributes to the equivalent atom elements.
'''

'''
gae-rest needs to import the files containing your Models since it is
unable to dynamic infer what are all the available entity kinds
(content types) in your application
Example: models = ['my_models.py', 'my_expandos.py']
'''
models = ['pool.py']

'''
which attribute on each Entity can be used as atom <author> element
Example: author = {'Entry': 'author'}
'''
author = {'Ticket':'author_email', 'Comment':'author_email'}

'''
<title>
Example: title = {'Entry': 'title'}
'''
title = {'Ticket':'summary'}

'''
<content>
Example: content = {'Entry': 'body_html'}
'''
content = {'Ticket':'description', 'Comment':'description'}

'''
<summary>
Example: summary = {'Entry': 'excerpt'}
'''
summary = {'Ticket':'description', 'Comment':'description'}

'''
<published>
Example: published = {'Entry': 'published'}
'''
published = {'Ticket':'created', 'Comment':'created'}

'''
<updated>
Example: updated = {'Entry': 'updated'}
'''
updated = {'Ticket':'updated'}