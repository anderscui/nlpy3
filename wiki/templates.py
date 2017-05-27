# coding=utf-8
import re
from types import SimpleNamespace
import xml.etree.ElementTree as etree
from html.entities import name2codepoint


import logging


NS_CAT = '14'
NS_PAGE = '0'
NS_TEMPLATE = '10'
NS_MODULE = '828'
ns_list = [NS_PAGE, NS_CAT]
# Keys for Template and Module namespaces
templateKeys = {'10', '828'}

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


class Page(object):
    def __init__(self, ns, pid, title, redirect_to=None, text=None):
        self.ns = ns
        self.pid = pid
        self.title = title
        self.redirect_to = redirect_to
        self.text = text

    def is_page(self):
        return self.ns == NS_PAGE

    def is_category(self):
        return self.ns == NS_CAT

    def redirected(self):
        return self.redirect_to is not None


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
    # if ns == NS_CAT:
    #     title = extract_cat_title(title)
    pid = page_xml.find('id').text
    redirect = page_xml.find('redirect')
    redirect_to = None
    if redirect is not None:
        # redirect_to = clean_title(redirect.attrib['title'])
        redirect_to = redirect.attrib['title']

    rev = page_xml.find('revision')
    text = rev.find('text').text
    # if text is None:
    #     return None

    # cats = RE_CAT.findall(text)
    # cats = [c.split('|')[0].strip() for label, c in cats]
    # is_disam = any(disam in text for disam in DISAM)

    page_xml.clear()

    page = Page(ns, int(pid), title, redirect_to, text)
    return page


def unescape(text):
    """
    Removes HTML or XML character references and entities from a text string.

    :param text The HTML (or XML) source text.
    :return The plain text, as a Unicode string, if necessary.
    """

    def fixup(m):
        text = m.group(0)
        code = m.group(1)
        try:
            if text[1] == "#":  # character reference
                if text[2] == "x":
                    return chr(int(code[1:], 16))
                else:
                    return chr(int(code))
            else:  # named entity
                return chr(name2codepoint[code])
        except:
            return text  # leave as is

    return re.sub("&#?(\w+);", fixup, text)


# Match HTML comments
# The buggy template {{Template:T}} has a comment terminating with just "->"
comment = re.compile(r'<!--.*?-->', re.DOTALL)

# Extract Template definition
reNoinclude = re.compile(r'<noinclude>(?:.*?)</noinclude>', re.DOTALL)
reIncludeonly = re.compile(r'<includeonly>|</includeonly>', re.DOTALL)


def define_template(title, page):
    """
    Adds a template defined in the :param page:.
    @see https://en.wikipedia.org/wiki/Help:Template#Noinclude.2C_includeonly.2C_and_onlyinclude
    """
    # title = normalizeTitle(title)

    # sanity check (empty template, e.g. Template:Crude Oil Prices))
    if not page:
        return

    # check for redirects
    m = re.match('#REDIRECT.*?\[\[([^\]]*)]]', page[0], re.IGNORECASE)
    if m:
        options.redirects[title] = m.group(1)  # normalizeTitle(m.group(1))
        return

    text = unescape(''.join(page))

    # We're storing template text for future inclusion, therefore,
    # remove all <noinclude> text and keep all <includeonly> text
    # (but eliminate <includeonly> tags per se).
    # However, if <onlyinclude> ... </onlyinclude> parts are present,
    # then only keep them and discard the rest of the template body.
    # This is because using <onlyinclude> on a text fragment is
    # equivalent to enclosing it in <includeonly> tags **AND**
    # enclosing all the rest of the template body in <noinclude> tags.

    # remove comments
    text = comment.sub('', text)

    # eliminate <noinclude> fragments
    text = reNoinclude.sub('', text)
    # eliminate unterminated <noinclude> elements
    text = re.sub(r'<noinclude\s*>.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'<noinclude/>', '', text)

    onlyincludeAccumulator = ''
    for m in re.finditer('<onlyinclude>(.*?)</onlyinclude>', text, re.DOTALL):
        onlyincludeAccumulator += m.group(1)
    if onlyincludeAccumulator:
        text = onlyincludeAccumulator
    else:
        text = reIncludeonly.sub('', text)

    if text:
        if title in options.templates:
            logging.warn('Redefining: %s', title)
        options.templates[title] = text


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
            # page = item.text
            if item.ns in templateKeys:
                # text = ''.join(page)
                define_template(item.title, item.text)
                # save templates and modules to file
                output.write('<page>\n')
                output.write('   <title>%s</title>\n' % item.title)
                output.write('   <ns>%s</ns>\n' % item.ns)
                output.write('   <id>%s</id>\n' % id)
                output.write('   <text>')
                output.write(item.text)
                output.write('   </text>\n')
                output.write('</page>\n')
            if page_count and page_count % 100000 == 0:
                logging.info("Preprocessed %d pages", page_count)
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
