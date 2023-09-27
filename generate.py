#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
from yaml.resolver import Resolver
import glob
import re
import os
import argparse
import html_generiloj
import leo_markdown

# remove resolver entries for On/Off/Yes/No
# https://stackoverflow.com/a/36470466/52023
for ch in "OoYyNn":
    if len(Resolver.yaml_implicit_resolvers[ch]) == 1:
        del Resolver.yaml_implicit_resolvers[ch]
    else:
        Resolver.yaml_implicit_resolvers[ch] = [x for x in
                                                Resolver.yaml_implicit_resolvers[ch] if
                                                x[0] != 'tag:yaml.org,2002:bool']


def transpose_headlines(markdown, level):
    prefix = ''
    for i in range(level):
        prefix += '#'
    markdown = re.sub(r'^#', '#' + prefix, markdown)
    markdown = re.sub(r'\n#', '\n#' + prefix, markdown)
    return markdown


def get_markdown_headlines(s):
    headlines = []
    for match in re.finditer(r'(^|\n)# (.+)\n', s):
        headlines.append(match.group(2).strip())

    return headlines


def load(language, gramatiko_transpose_headlines=2):
    enhavo = {'lingvo': language, 'vortaro': {}}

    paths = glob.glob('enhavo/tradukenda/' + language + '/vortaro/*.yml')
    # Provo solvi
    # https://github.com/Esperanto/kurso-zagreba-metodo/issues/36
    # sed kauzas aliajn problemojn.
    # paths.append('enhavo/tradukenda/en/vortaro/vorto.yml')
    # print(paths)
    for path in paths:
        dirs, filename = os.path.split(path)
        root, extension = os.path.splitext(filename)
        vortspeco = root.replace('_', ' ')
        vortlisto = yaml.load(open(path).read(), yaml.Loader)
        for esperante in vortlisto:
            fontlingve = vortlisto[esperante]
            vortlisto[esperante] = {
                'tradukajxo': fontlingve,
                'vortspeco': vortspeco
            }
        enhavo['vortaro'].update(vortlisto)

    enhavo['finajxoj'] = yaml.load(open('enhavo/netradukenda/radikaj_finajxoj.yml').read(), yaml.Loader)

    enhavo['ordoj'] = {}
    enhavo['ordoj']['cifero'] = yaml.load(open('enhavo/netradukenda/ordoj/cifero.yml'), yaml.Loader)
    enhavo['ordoj']['monato'] = yaml.load(open('enhavo/netradukenda/ordoj/monato.yml'), yaml.Loader)
    enhavo['ordoj']['sezono'] = yaml.load(open('enhavo/netradukenda/ordoj/sezono.yml'), yaml.Loader)
    enhavo['ordoj']['tago_en_la_semajno'] = yaml.load(open('enhavo/netradukenda/ordoj/tago_en_la_semajno.yml'),
                                                      yaml.Loader)

    enhavo['fasado'] = {}
    paths = glob.glob('enhavo/tradukenda/' + language + '/fasado/*.yml')
    for path in paths:
        tradukajxoj = yaml.load(open(path).read(), yaml.Loader)
        enhavo['fasado'].update(tradukajxoj)

    path = 'enhavo/tradukenda/' + language + '/enkonduko.md'
    enkonduko = open(path).read()
    # enkonduko = transpose_headlines(enkonduko, 1)
    enhavo['enkonduko'] = enkonduko

    path = 'enhavo/tradukenda/' + language + '/post.md'
    enhavo['post'] = open(path).read()
    enhavo['post'] = transpose_headlines(enhavo['post'], 2)

    lecionoj = []
    vortoj = {}

    for i in range(1, 13):
        leciono = {
            'teksto': None,
            'gramatiko': None,
            'ekzercoj': None,
        }
        i_padded = str(i).zfill(2)

        leciono['indekso'] = {
            'cifre': i,
            'cxene': i_padded
        }

        path = 'enhavo/netradukenda/tekstoj/' + i_padded + '.yml'
        leciono['teksto'] = yaml.load(open(path).read(), yaml.Loader)

        # Create a string of the lesson titles.
        titolo_string = ''
        for radikoj in leciono['teksto']['titolo']:
            if radikoj:
                titolo_string += ''.join(radikoj)
            else:
                titolo_string += ' '

        leciono['teksto']['titolo_string'] = titolo_string

        leciono['vortoj'] = {}
        leciono['vortoj']['teksto'] = []
        leciono['vortoj']['pliaj'] = []

        path = 'enhavo/netradukenda/vortoj/' + i_padded + '.yml'
        leciono['vortoj']['pliaj'] = yaml.load(open(path).read(), yaml.Loader)

        for paragrafo in leciono['teksto']['paragrafoj']:
            for vorto in paragrafo:
                if type(vorto) is list:
                    for radiko in vorto:
                        if not radiko.lower() in vortoj:
                            leciono['vortoj']['teksto'].append(radiko)
                            vortoj[radiko.lower()] = True

        path = 'enhavo/tradukenda/' + language + '/gramatiko/' + i_padded + '.md'

        gramatiko_teksto = open(path).read()
        gramatiko_titoloj = get_markdown_headlines(gramatiko_teksto)
        gramatiko_teksto = transpose_headlines(gramatiko_teksto, gramatiko_transpose_headlines)

        gramatiko = {
            'teksto': gramatiko_teksto,
            'titoloj': gramatiko_titoloj,
        }
        leciono['gramatiko'] = gramatiko

        ekzercoj = {}

        path = 'enhavo/tradukenda/' + language + '/ekzercoj/traduku/' + i_padded + '.yml'
        ekzercoj['Traduku'] = yaml.load(open(path), yaml.Loader)

        path = 'enhavo/tradukenda/' + language + '/ekzercoj/traduku-kaj-respondu/' + i_padded + '.yml'
        ekzercoj['Traduku kaj respondu'] = yaml.load(open(path), yaml.Loader)

        path = 'enhavo/netradukenda/ekzercoj/kompletigu-la-frazojn/' + i_padded + '.yml'
        ekzercoj['Kompletigu la frazojn'] = yaml.load(open(path), yaml.Loader)

        # Covert from dict to list.
        leciono['ekzercoj'] = ekzercoj

        lecionoj.append(leciono)

    enhavo['lecionoj'] = lecionoj

    return enhavo


def get_cmdline_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-l",
        "--lingvo",
        help="Kreu eligon por tiu lingvo.",
        type=str,
        required=True
    )
    ap.add_argument(
        "-ef",
        "--eligformo",
        help="La eligoformo",
        type=str,
        choices=['html', 'md'],
        default='html'
    )
    ap.add_argument(
        "-pp",
        "--printendaj-partoj",
        help="Printendaj partoj",
        type=str,
        choices=['teksto', 'vortoj', 'gramatiko', 'ekzerco1', 'ekzerco2', 'ekzerco3', 'solvo1', 'solvo2', 'solvo3'],
        default=['teksto', 'vortoj', 'gramatiko', 'ekzerco1', 'ekzerco2', 'ekzerco3', 'solvo1', 'solvo2', 'solvo3'],
        nargs='*'
    )
    ap.add_argument(
        "-pl",
        "--printendaj-lecionoj",
        help="Printendaj lecionoj",
        type=int,
        choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        default=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        nargs='*'
    )
    ap.add_argument(
        "-vp",
        "--vojprefikso",
        help="La vojprefikso por ĉiuj ligiloj en la eligo. Norme: /[lingvokodo]/",
        type=str
    )
    args = ap.parse_args()

    return args


def main():
    args = get_cmdline_arguments()
    lingvoj = yaml.load(open('agordoj/lingvoj.yml').read(), yaml.Loader)
    if args.eligformo == 'html':
        # if args.lingvo not in lingvoj.keys():
        #    sys.exit("'" + args.lingvo + "' ne estas havebla lingvokodo.")
        enhavo = load(args.lingvo)
        enhavo['lingvoj'] = lingvoj
        enhavo['tekstodirekto'] = lingvoj[args.lingvo].get('tekstodirekto', 'ltr')
        html_generiloj.generi.generate_html(args.lingvo, enhavo, args)
    if args.eligformo == 'md':
        enhavo = load(args.lingvo, 3)
        enhavo['lingvoj'] = lingvoj
        enhavo['tekstodirekto'] = lingvoj[args.lingvo].get('tekstodirekto', 'ltr')
        leo_markdown.package.kreu_md(enhavo, printendaj={'partoj': args.printendaj_partoj,
                                                         'lecionoj': args.printendaj_lecionoj})


main()
