import re
from urllib.parse import urlparse, parse_qs, unquote
from pathlib import PurePosixPath
import csv

## Install this library
from fuzzywuzzy import fuzz

def url_brands(domain, url):
    #BRANDS
    with open('brands.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        is_typosquatting = False
        brand_found = False
        number_of_brands_found = 0
        brand_in_domain = False
        brand_in_domain_exactly = False

        for row in csv_reader:
            brand = row["Brands"].strip().lower()
            index_for_brand_in_loop = fuzz.ratio(brand, domain)
            if index_for_brand_in_loop >= 90 and index_for_brand_in_loop != 100:
                is_typosquatting = True
            else:
                is_typosquatting = False
            if url.find(brand) != -1:
                brand_found = True
                number_of_brands_found = number_of_brands_found + 1
                if domain.find(brand) != -1:
                    brand_in_domain = True
                    if domain == brand:
                        brand_in_domain_exactly = True

    return (
        brand_found, 
        number_of_brands_found, 
        brand_in_domain, 
        brand_in_domain_exactly, 
        is_typosquatting,
    )

def url_hostname(hostname):
    #HOSTNAME
    hostname_length = len(hostname)
    number_of_digits = len(re.findall(r"\d", hostname, re.MULTILINE))
    special_characters = len(re.findall(r"[\-\_\!\`\'\#\%\&\,\;\<\>\=\@\{\}\~\$\(\)\*\+\?\[\]\^\|]", hostname, re.MULTILINE))

    return (hostname_length, number_of_digits, special_characters)

def url_subdomain(hostname):
    #SUBDOMAINS AND DOMAIN
    subdomains_and_domain = re.findall(r"[^.]+(?=\.)", hostname, re.MULTILINE)
    domain = subdomains_and_domain.pop()
    subdomains = subdomains_and_domain
    #---FEATURES---#
    subdomain_length = len(''.join(subdomains))
    domain_length = len(domain)
    number_of_subdomains = len(subdomains)
    
    return (domain, subdomain_length, domain_length, number_of_subdomains)

def url_queries(parsed_url):
    #QUERY AND DIRECTORIES
    queries = parse_qs(parsed_url.query)
    #---FEATURES---#
    number_of_parameters = len(queries.keys())
    length_of_parameters = 0
    length_of_values = 0
    query_special_characters = 0
    for key in queries:
        length_of_parameters = length_of_parameters + len(key)
        length_of_values = length_of_values + len(queries[key][0])
        query_special_characters = query_special_characters + len(re.findall(r"[\!\`\'\#\%\&\,\;\<\>\=\@\{\}\~\$\(\)\*\+\?\[\]\^\|\\\/\.]", key, re.MULTILINE))
    
    return (number_of_parameters, length_of_parameters, length_of_values, query_special_characters)

def url_directories(parsed_url):
    #DIRECTORIES OR FILE PATHS
    paths = parsed_url.path
    [path, match, filename] = paths.rpartition('/')
    #---FEATURES---#
    number_of_directories = 0
    length_of_directories = 0
    directories_special_characters = 0
    directories = list()
    if match != '': # returns the rpartition separator if found
        directories = list(PurePosixPath(unquote(path)).parts)
        number_of_directories = 0
        for directory in directories:
            if directory == '/':
                continue
            length_of_directories = length_of_directories + len(directory)
            directories_special_characters = directories_special_characters + len(re.findall(r"[\!\`\'\#\%\&\,\;\<\>\=\@\{\}\~\$\(\)\*\+\?\[\]\^\|\\\/\.]", directory, re.MULTILINE))
            number_of_directories = number_of_directories + 1
    
    return (number_of_directories, length_of_directories, directories_special_characters)

def url_fragments(parsed_url):
    #FRAGMENTS
    fragments = parse_qs(parsed_url.fragment)
    #---FEATURES---#
    number_of_fragments = len(fragments.keys())
    length_of_fragments = 0
    length_of_fragment_values = 0
    fragment_special_characters = 0
    for fragment in fragments:
        length_of_fragments = length_of_fragments + len(fragment)
        length_of_fragment_values = length_of_fragment_values + len(fragments[fragment][0])
        fragment_special_characters = fragment_special_characters + len(re.findall(r"[\!\`\'\#\%\&\,\;\<\>\=\@\{\}\~\$\(\)\*\+\?\[\]\^\|\\\/\.]", fragment, re.MULTILINE))

    return (number_of_fragments, length_of_fragments, length_of_fragment_values, fragment_special_characters)

def url_breakdown(url):
    if(len(re.findall(r"(?<=\:\/\/).*", url, re.MULTILINE)) == 0):
        hostname = re.findall(r"[^\/]*", url, re.MULTILINE)[0]
    else:
        hostname = re.findall(r"[^\/]*", (re.findall(r"(?<=\:\/\/).*", url, re.MULTILINE)[0]), re.MULTILINE)[0]

    ip = re.findall(r"[a-zA-Z]", hostname, re.MULTILINE)
    if len(ip) == 0:
        raise ValueError('IP Found')
    
    if re.search(r"\/(.*)$", url, re.MULTILINE) == None:
        url = url + '/'
    url_rest = re.search(r"\/(.*)$", url, re.MULTILINE)
    parsed_url = urlparse(url_rest.group())

    [
        domain, 
        subdomain_length, 
        domain_length, 
        number_of_subdomains
    ] = url_subdomain(hostname)

    if(subdomain_length == 0):
        hostname = 'www.' + hostname

        [
            domain, 
            subdomain_length, 
            domain_length, 
            number_of_subdomains
        ] = url_subdomain(hostname)

    [
        hostname_length, 
        number_of_digits, 
        special_characters
    ] = url_hostname(hostname)

    [
        number_of_parameters, 
        length_of_parameters, 
        length_of_values, 
        query_special_characters
    ] = url_queries(parsed_url)

    [
        number_of_directories, 
        length_of_directories, 
        directories_special_characters
    ] = url_directories(parsed_url)

    [
        number_of_fragments, 
        length_of_fragments, 
        length_of_fragment_values, 
        fragment_special_characters
    ] = url_fragments(parsed_url)

    [
        brand_found, 
        number_of_brands_found, 
        brand_in_domain, 
        brand_in_domain_exactly, 
        is_typosquatting
    ] = url_brands(domain, url)
        
    return [
        hostname_length,
        number_of_digits,
        special_characters,
        subdomain_length,
        domain_length,
        number_of_subdomains,
        number_of_parameters,
        length_of_parameters,
        length_of_values,
        query_special_characters,
        number_of_directories,
        length_of_directories,
        directories_special_characters,
        number_of_fragments,
        length_of_fragments,
        length_of_fragment_values,
        fragment_special_characters,
        brand_found,
        number_of_brands_found,
        brand_in_domain,
        brand_in_domain_exactly,
        is_typosquatting
    ]

def convertToDictionary(arrayOfVals, header):
    finalDict = {}
    count = 0

    for key in header:
        finalDict[key] = arrayOfVals[count]
        count = count + 1

    return finalDict

## Uncomment the below code and add the URL as a parameter.
# breakdown = url_breakdown("URL")