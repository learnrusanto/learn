#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import shutil

# sys.path = ['./genanki'] + sys.path
import genanki
import jinja2
import mistune


def render_page(name, enhavo, vojprefikso, env):
    rendered = env.get_template(name + '.html').render(
        enhavo=enhavo,
        vojprefikso=vojprefikso,
    )

    return rendered


def write_file(filename, content):
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(filename, 'w') as f:
        f.write(content)


def aldonu_karton(deck, model, enhavo, radiko, leciono=None):
    # Ne kreu de tiuj vortspecoj.
    if enhavo['vortaro'][radiko]['vortspeco'] in ['interjekcio', 'nomo', 'vorto']:
        return deck

    esperanta_karto = radiko

    # Aldonu finaĵon.
    if radiko in enhavo['finajxoj']:
        esperanta_karto = esperanta_karto + enhavo['finajxoj'][radiko]

    # Aldonu '-' al afiksoj.
    if enhavo['vortaro'][radiko]['vortspeco'] in ['prefikso']:
        esperanta_karto = esperanta_karto + '-'
    if enhavo['vortaro'][radiko]['vortspeco'] in ['sufikso', 'finajxo']:
        esperanta_karto = '-' + esperanta_karto

    fontlingva_karto = enhavo['vortaro'][radiko]['tradukajxo']
    if isinstance(fontlingva_karto, list):
        fontlingva_karto = ', '.join(fontlingva_karto)

        # Ne kreu karton se iu de ili malplenas.
    if not esperanta_karto or not fontlingva_karto:
        return deck

    tags = [enhavo['vortaro'][radiko]['vortspeco'].replace(' ', '_')]
    if leciono:
        tags.append(leciono)

    note = genanki.Note(
        model=model,
        tags=tags,
        fields=[
            esperanta_karto,
            fontlingva_karto
        ]
    )
    deck.add_note(note)

    return deck


# Create an Anki file.
def create_anki(enhavo):
    model = genanki.Model(
        hash('Learn Esperanto') & ((1 << 31) - 1),
        'Learn Esperanto',
        fields=[
            {'name': 'eo'},
            {'name': enhavo['lingvo']},
        ],
        templates=[
            {
                'name': 'eo' + '-' + enhavo['lingvo'],
                'qfmt': '{{eo}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{' + enhavo['lingvo'] + '}}',
            },
            {
                'name': enhavo['lingvo'] + '-' + 'eo',
                'qfmt': '{{' + enhavo['lingvo'] + '}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{' + 'eo' + '}}',
            },
        ])

    deck = genanki.Deck(
        hash('Learn Esperanto: ' + enhavo['lingvo']) & ((1 << 31) - 1),
        'Learn Esperanto: ' + enhavo['lingvo']
    )

    aldonitaj = []

    # Unue aldonu laux lecionoj.
    for leciono_index_0 in range(len(enhavo['lecionoj'])):
        leciono = enhavo['lecionoj'][leciono_index_0]
        for radiko in leciono['vortoj']['teksto']:
            if radiko.lower() in enhavo['vortaro']:
                radiko = radiko.lower()
            leciono = str(leciono_index_0 + 1)
            aldonu_karton(deck, model, enhavo, radiko, leciono)
            aldonitaj.append(radiko)

    # Nun aldonu la reston.
    for radiko in enhavo['vortaro']:
        if radiko in aldonitaj:
            continue
        aldonu_karton(deck, model, enhavo, radiko)

    return deck


def generate_html(lingvo, enhavo, args):
    eligo = {}
    md = mistune.Markdown()

    env = jinja2.Environment()
    env.filters['markdown'] = lambda text: jinja2.Markup(md(text))
    env.trim_blocks = True
    env.lstrip_blocks = True
    env.loader = jinja2.FileSystemLoader('html_generiloj/templates/')

    output_path = 'html_generiloj/output/' + lingvo + '/'

    tabs = [
        ('teksto', '', enhavo['fasado']['Teksto']),
        ('vortoj', 'vortoj/', enhavo['fasado']['Novaj vortoj']),
        ('gramatiko', 'gramatiko/', enhavo['fasado']['Gramatiko']),
        ('ekzerco1', 'ekzerco1/', enhavo['fasado']['Ekzerco 1']),
        ('ekzerco2', 'ekzerco2/', enhavo['fasado']['Ekzerco 2']),
        ('ekzerco3', 'ekzerco3/', enhavo['fasado']['Ekzerco 3'])
    ]

    if args.vojprefikso:
        vojprefikso = args.vojprefikso + lingvo + '/'
    else:
        vojprefikso = '/' + lingvo + '/'

    rendered = env.get_template('index.html').render(
        enhavo=enhavo,
        vojprefikso=vojprefikso,
        tabs=tabs,
    )

    eligo[output_path + 'index.html'] = rendered

    # vortaro.js
    rendered = env.get_template('vortlisto.js').render(
        enhavo=enhavo,
    )
    eligo[output_path + 'js/vortlisto.js'] = rendered

    eligo[output_path + 'eksporto/' + enhavo['lingvo'] + '.apkg'] = create_anki(enhavo)

    for tab_page in ['tabelvortoj', 'prepozicioj', 'konjunkcioj', 'afiksoj', 'diversajxoj', 'auxtoroj', 'post']:
        eligo[output_path + tab_page + '/index.html'] = render_page(tab_page, enhavo, vojprefikso, env)

    paths = []
    for i in range(1, 13):
        for id, href, caption in tabs:
            paths.append(vojprefikso + str(i).zfill(2) + '/' + href)

    paths_index = 0

    for i in range(1, 13):
        i_padded = str(i).zfill(2)
        leciono_dir = output_path + i_padded

        for tab, href, caption in tabs:

            previous_path = None
            next_path = None

            tab_vojprefikso = vojprefikso + i_padded + '/'

            if paths_index > 0:
                previous_path = paths[paths_index - 1]
            if paths_index < len(paths) - 1:
                next_path = paths[paths_index + 1]
            paths_index += 1

            tab_rendered = env.get_template(tab + '.html').render(
                enhavo=enhavo,
                leciono=enhavo['lecionoj'][i - 1],
                leciono_index=i,
                vojprefikso=vojprefikso,
                tab_vojprefikso=tab_vojprefikso,
                previous_path=previous_path,
                next_path=next_path,
                tabs=tabs,
                active_tab=tab,
                identigilo=i_padded + '/' + href
            )

            eligo[leciono_dir + '/' + href + '/' + '/index.html'] = tab_rendered

    # Forigu nunan dosierujon.
    shutil.rmtree(output_path, ignore_errors=True)

    # Kreu novajn dosierojn
    for vojo in eligo.keys():
        if re.search(r'\.apkg$', vojo):
            write_file(vojo, '')
            genanki.Package(eligo[vojo]).write_to_file(vojo)
            continue
        write_file(vojo, eligo[vojo])
