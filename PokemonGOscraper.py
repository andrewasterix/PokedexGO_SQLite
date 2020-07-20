import requests
import sqlite3
from sqlite3 import Error
from bs4 import BeautifulSoup
from tqdm import tqdm

# Check Data
DEBUG = False

# Statement for DB
create_table_1 = "CREATE TABLE IF NOT EXISTS Pokemon (Number INTEGER NOT NULL PRIMARY KEY, Name TEXT, Type_1 TEXT, Type_2 TEXT, Hp INTEGER, Attack INTEGER, "
create_table_2 = "Defence INTEGER, SpAttack INTEGER, SpDefence INTEGER, Speed INTEGER, Total INTEGER, Normal NUMERIC, Fire NUMERIC, "
create_table_3 = "Water NUMERIC, Electric NUMERIC, Grass NUMERIC, Ice NUMERIC, Fighting NUMERIC, Poison NUMERIC, Ground NUMERIC, "
create_table_4 = "Flying NUMERIC, Psychic NUMERIC, Bug NUMERIC, Rock NUMERIC, Ghost NUMERIC, Dragon NUMERIC, Dark NUMERIC, "
create_table_5 = "Steel NUMERIC, Fairy NUMERIC);"

statement_create = create_table_1 + create_table_2 + create_table_3 + create_table_4 + create_table_5

insert_table_1 = "INSERT INTO Pokemon (Number, Name, Type_1, Type_2, Hp, Attack, "
insert_table_2 = "Defence, SpAttack, SpDefence, Speed, Total, Normal, Fire, Water, Electric, Grass, Ice, Fighting, "
insert_table_3 = "Poison, Ground, Flying, Psychic, Bug, Rock, Ghost, Dragon, Dark, Steel, Fairy) VALUES (?, ?, ?, ?, ?, ?, ?, ?,"
insert_table_4 = " ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"

statement_insert = insert_table_1 + insert_table_2 + insert_table_3 + insert_table_4

# Multiplier function
# This function will take a string that indicate a multiplier in the HTML file and 
# return the respective multiplier
def replace_multiplier(string):
    if string == 'type-fx-25':
        return 0.25
    elif string == 'type-fx-50':
        return 0.50
    elif string == 'type-fx-200':
        return 2
    elif string == 'type-fx-400':
        return 4
    else:
        return 1

# Dowload  Web Page
print("Connecting To pokemondb.net....")
URL = 'https://pokemondb.net'
page = requests.get(URL+'/pokedex/national')

# Parsing HTML with BeautifulSoup package
soup = BeautifulSoup(page.content, 'html.parser')
results = soup.find_all("div", {"class": "infocard"})

imageCheck = input("Do you also want to download the images? [y/n] ")

if(imageCheck == 'y' or imageCheck == 'Y'):
    # Creating a sub-folder for the images
    import os
    os.mkdir('images')

    # Scraping all images into sub-folder 'images'
    from PIL import Image

    print("Downloading Images....")
    for result in tqdm(results):
        
        # Exclusion of pokemon not present in Pokémon go
        pokeNo = result.find_all("small")[0].text
        if(pokeNo == "#647" or pokeNo == "#648" or (pokeNo >= "#650" and pokeNo <= "#807") 
            or (pokeNo >= "#810" and pokeNo <= "#861") or pokeNo >= "#864"):
           continue

        pokeNo = pokeNo.replace("#", "")
        # ImageName == Pokemon Number in Pokedex
        imageURL = result.find("span",{"class": "img-fixed img-sprite"})["data-src"]
        img = Image.open(requests.get(imageURL, stream = True).raw)
        img.save(os.path.join("images", pokeNo + ".png"))

    """ 
        # ImageName == PokemonName
        imageName = result.find("a", {"class": "ent-name"}).text
        imageName = imageName.replace("\'", "")
        imageName = imageName.replace(":", "")
        imageName = imageName.replace(" ", "")
        imageName = imageName.replace("♀", "F")
        imageName = imageName.replace("♂", "M")
        imageURL = result.find("span",{"class": "img-fixed img-sprite"})["data-src"]
        img = Image.open(requests.get(imageURL, stream = True).raw)
        img.save(os.path.join("images", imageName + ".png"))
    """


# Connecting to existing DB or create it
con = sqlite3.connect("PokedexGO.db")
cursor = con.cursor()
cursor.execute(statement_create)

print("Downloading Pokemon Information....")

for result in tqdm(results):
    # Extract national number
    pokeNo = result.find_all("small")[0].text

    # Exclusion of pokemon not present in Pokémon go
    if(pokeNo == "#647" or pokeNo == "#648" or (pokeNo >= "#650" and pokeNo <= "#807") 
            or (pokeNo >= "#810" and pokeNo <= "#861") or pokeNo >= "#864"):
           continue
    
    pokeNo = pokeNo.replace("#", "")
    
    # Extract name
    pokeName = result.find("a", {"class": "ent-name"}).text
    pokeName = pokeName.replace("\'", "")
    pokeName = pokeName.replace(":", "")
    pokeName = pokeName.replace(" ", "")
    pokeName = pokeName.replace("♀", "F")
    pokeName = pokeName.replace("♂", "M")

    # Extract Type
    pokeType1 = result.find_all("small")[1].find_all("a")[0].text
    try:
        pokeType2 = result.find_all("small")[1].find_all("a")[1].text
    except IndexError:
        pokeType2 = ""

    # Extract Type Weaknesses
    subURL = result.find("a", {"class": "ent-name"})["href"]
    pokePage = requests.get(URL+subURL)
    pokeSoup = BeautifulSoup(pokePage.content, 'html.parser')

    typeResults = pokeSoup.find_all("table", {"class": "type-table type-table-pokedex"})
    nor = replace_multiplier(typeResults[0].find_all("tr")[1].find_all("td")[0]["class"][1])
    fir = replace_multiplier(typeResults[0].find_all("tr")[1].find_all("td")[1]["class"][1])
    wat = replace_multiplier(typeResults[0].find_all("tr")[1].find_all("td")[2]["class"][1])
    ele = replace_multiplier(typeResults[0].find_all("tr")[1].find_all("td")[3]["class"][1])
    gra = replace_multiplier(typeResults[0].find_all("tr")[1].find_all("td")[4]["class"][1])
    ice = replace_multiplier(typeResults[0].find_all("tr")[1].find_all("td")[5]["class"][1])
    fig = replace_multiplier(typeResults[0].find_all("tr")[1].find_all("td")[6]["class"][1])
    poi = replace_multiplier(typeResults[0].find_all("tr")[1].find_all("td")[7]["class"][1])
    gro = replace_multiplier(typeResults[0].find_all("tr")[1].find_all("td")[8]["class"][1])
    fly = replace_multiplier(typeResults[1].find_all("tr")[1].find_all("td")[0]["class"][1])
    psy = replace_multiplier(typeResults[1].find_all("tr")[1].find_all("td")[1]["class"][1])
    bug = replace_multiplier(typeResults[1].find_all("tr")[1].find_all("td")[2]["class"][1])
    roc = replace_multiplier(typeResults[1].find_all("tr")[1].find_all("td")[3]["class"][1])
    gho = replace_multiplier(typeResults[1].find_all("tr")[1].find_all("td")[4]["class"][1])
    dra = replace_multiplier(typeResults[1].find_all("tr")[1].find_all("td")[5]["class"][1])
    dar = replace_multiplier(typeResults[1].find_all("tr")[1].find_all("td")[6]["class"][1])
    ste = replace_multiplier(typeResults[1].find_all("tr")[1].find_all("td")[7]["class"][1])
    fai = replace_multiplier(typeResults[1].find_all("tr")[1].find_all("td")[8]["class"][1])

    # Extract Base Stats
    stasResults = pokeSoup.find_all("table", {"class": "vitals-table"})
    hp = stasResults[3].find_all("tr")[0].find_all("td", {"class": "cell-num"})[0].text
    atk = stasResults[3].find_all("tr")[1].find_all("td", {"class": "cell-num"})[0].text
    defe = stasResults[3].find_all("tr")[2].find_all("td", {"class": "cell-num"})[0].text
    spAtk = stasResults[3].find_all("tr")[3].find_all("td", {"class": "cell-num"})[0].text
    spDef = stasResults[3].find_all("tr")[4].find_all("td", {"class": "cell-num"})[0].text
    speed = stasResults[3].find_all("tr")[5].find_all("td", {"class": "cell-num"})[0].text
    total = stasResults[3].find_all("tr")[6].find_all("td", {"class": "cell-total"})[0].text

    if(DEBUG):
        print(pokeNo +" "+ pokeName +" "+ pokeType1 +" "+ pokeType2)
    
    to_db = [(pokeNo, pokeName, pokeType1, pokeType2, hp, atk, defe, spAtk, spDef, speed, total, nor, 
        fir, wat, ele, gra, ice, fig, poi, gro, fly, psy, bug, roc, gho, dra, dar, ste, fai)]
    
    # Insert in Db
    try:
        cursor.executemany(statement_insert, to_db)
        con.commit()
    except Error as error:
        print("Failed to INSERT record", error)

if (con):
        cursor.close()
        con.close()
print("Done!")