# coding=utf-8
import re
from types import SimpleNamespace

import logging

tagRE = re.compile(r'(.*?)<(/?\w+)[^>]*?>(?:([^<]*)(<.*?>)?)?')
#                    1     2               3      4
keyRE = re.compile(r'key="(\d*)"')

options = SimpleNamespace(
    ##
    # Defined in <siteinfo>
    # We include as default Template, when loading external template file.
    knownNamespaces={'Template': 10},

    ##
    # The namespace used for template definitions
    # It is the name associated with namespace key=10 in the siteinfo header.
    templateNamespace='',
    templatePrefix='',

    ##
    # The namespace used for module definitions
    # It is the name associated with namespace key=828 in the siteinfo header.
    moduleNamespace='',

    ##
    # Recognize only these namespaces in links
    # w: Internal links to the Wikipedia
    # wiktionary: Wiki dictionary
    # wikt: shortcut for Wiktionary
    #
    acceptedNamespaces=['w', 'wiktionary', 'wikt'],

    # This is obtained from <siteinfo>
    urlbase='',

    ##
    # Filter disambiguation pages
    filter_disambig_pages=False,

    ##
    # Drop tables from the article
    keep_tables=False,

    ##
    # Whether to preserve links in output
    keepLinks=False,

    ##
    # Whether to preserve section titles
    keepSections=True,

    ##
    # Whether to preserve lists
    keepLists=False,

    ##
    # Whether to output HTML instead of text
    toHTML=False,

    ##
    # Whether to write json instead of the xml-like default output format
    write_json=False,

    ##
    # Whether to expand templates
    expand_templates=True,

    ##
    ## Whether to escape doc content
    escape_doc=False,

    ##
    # Print the wikipedia article revision
    print_revision=False,

    ##
    # Minimum expanded text length required to print document
    min_text_length=0,

    # Shared objects holding templates, redirects and cache
    templates={},
    redirects={},
    # cache of parser templates
    # FIXME: sharing this with a Manager slows down.
    templateCache={},

    # Elements to ignore/discard

    ignored_tag_patterns=[],

    discardElements=[
        'gallery', 'timeline', 'noinclude', 'pre',
        'table', 'tr', 'td', 'th', 'caption', 'div',
        'form', 'input', 'select', 'option', 'textarea',
        'ul', 'li', 'ol', 'dl', 'dt', 'dd', 'menu', 'dir',
        'ref', 'references', 'img', 'imagemap', 'source', 'small',
        'sub', 'sup', 'indicator'
    ],
)


def load_siteinfo(source):
    with open(source) as f:
        # collect siteinfo
        for line in f:
            m = tagRE.search(line)
            if not m:
                continue
            tag = m.group(2)
            if tag == 'base':
                # discover urlbase from the xml dump file
                # /mediawiki/siteinfo/base
                base = m.group(3)
                options.urlbase = base[:base.rfind("/")]
            elif tag == 'namespace':
                mk = keyRE.search(line)
                if mk:
                    nsid = mk.group(1)
                else:
                    nsid = ''
                options.knownNamespaces[m.group(3)] = nsid
                if re.search('key="10"', line):
                    options.templateNamespace = m.group(3)
                    options.templatePrefix = options.templateNamespace + ':'
                elif re.search('key="828"', line):
                    options.moduleNamespace = m.group(3)
                    options.modulePrefix = options.moduleNamespace + ':'
            elif tag == '/siteinfo':
                break


def pages(input):
    """
    Scans input extracting pages.
    """
    page = []
    in_page = False
    for line in input:
        if not in_page:
            striped = line.strip()
            if striped == '<page>':
                in_page = True
                page.append(line)
            else:
                continue
        else:
            page.append(line)
            striped = line.strip()
            if striped == '</page>':
                yield page
                page = []
                in_page = False


def extract_wiki_item(page_text):
    page_xml = etree.fromstring(page_text)
    ns = page_xml.find('ns').text
    if ns not in ns_list:
        return None

    title = page_xml.find('title').text
    if ns == NS_CAT:
        title = extract_cat_title(title)
    pid = page_xml.find('id').text
    redirect = page_xml.find('redirect')
    redirect_to = None
    if redirect is not None:
        redirect_to = clean_title(redirect.attrib['title'])

    rev = page_xml.find('revision')
    text = rev.find('text').text
    if text is None:
        return None

    cats = RE_CAT.findall(text)
    cats = [c.split('|')[0].strip() for label, c in cats]
    is_disam = any(disam in text for disam in DISAM)

    page_xml.clear()

    page = Page(ns, int(pid), title, redirect_to, cats, is_disam)
    return page


def load_templates(source, output_file):
    """
    Load templates from :param file:.
    :param output_file: file where to save templates and modules.
    """
    options.templatePrefix = options.templateNamespace + ':'
    options.modulePrefix = options.moduleNamespace + ':'

    with open(source) as f, open(output_file, 'w') as output:
        for page_count, page_lines in enumerate(pages(f)):
            page_text = ''.join(page_lines)
            item = extract_wiki_item(page_text)
            page = page_text
            if ns in templateKeys:
                text = ''.join(page)
                define_template(title, text)
                # save templates and modules to file
                if output_file:
                    output.write('<page>\n')
                    output.write('   <title>%s</title>\n' % title)
                    output.write('   <ns>%s</ns>\n' % ns)
                    output.write('   <id>%s</id>\n' % id)
                    output.write('   <text>')
                    for line in page:
                        output.write(line)
                    output.write('   </text>\n')
                    output.write('</page>\n')
            if page_count and page_count % 100000 == 0:
                logging.info("Preprocessed %d pages", page_count)
        if output_file:
            output.close()
            logging.info("Saved %d templates to '%s'", len(options.templates), output_file)


if __name__ == '__main__':
    wiki_source = 'zh_classicalwiki-20170520.xml'
    print(options.templateNamespace)
    print(options.templatePrefix)
    print(options.moduleNamespace)
    # print(options.modulePrefix)

    load_siteinfo(wiki_source)
    print(options.templateNamespace)
    print(options.templatePrefix)
    print(options.moduleNamespace)
    # print(options.modulePrefix)
