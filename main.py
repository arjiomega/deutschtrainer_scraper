import os

import requests
from bs4 import BeautifulSoup

import genanki

class Scraper:
    def __init__(self,url=None):
        self.url = url
        self.page = None
        self.soup = None
        self.url_list = []
        self.vocab = {}

    def add_url(self,url):
        if url not in self.url_list:
            self.url_list.append(url)
        else:
            print("url already exists")

    def scrape_content(self):
        self.page = requests.get(self.url)
        self.soup = BeautifulSoup(self.page.content, "html.parser")

    def get_title(self):
        title = self.soup.find_all("div",class_="lesson-title-button-container-wrapper")
        return(title[0].find('h1').text.strip())

    def get_vocab(self):

        contents = self.soup.find_all("div",class_="knowledge-wrapper")
        vocabs = contents[0].find_all("div",class_="sc-dRGAjo kiDMro")

        for vocab in vocabs:
            vocab_row = vocab.find_all("div")

            vocab_de = vocab_row[0].text.strip()
            vocab_en = vocab_row[2].text.strip()
            vocab_audio_url = vocab_row[0].find('source')['src']

            self.vocab[vocab_en] = {
                "de":   vocab_de,
                "audio":vocab_audio_url
            }

    def download_audio(self):

        if not os.path.exists("audio"):
             os.makedirs("audio")

        folder_name = self.get_title()
        self.folder_path = os.path.join("audio",folder_name)

        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

        for i,(key,val) in enumerate(self.vocab.items()):
            response = requests.get(val['audio'])

            with open(os.path.join(self.folder_path, f"audio_{i}.mp3"),"wb") as file:
                file.write(response.content)

    def view_vocab(self):
        for i,(key,val) in enumerate(self.vocab.items()):
            print("id: ",i)
            print("en: ",key)
            print("de: ",val['de'])
            print("audio url: ",val['audio'])
            print()

def generate_package(model_id = 1652641442, deck_id = 1319323011):
    model_id = model_id # random.randrange(1 << 30, 1 << 31)

    model = genanki.Model(
        model_id,
        'Deutsch Trainer',
        fields= [
            {'name': 'Question'},
            {'name': 'Answer'},
            {'name': 'MyMedia'},
        ],
        templates= [
            {
                'name': 'Card 1',
                'qfmt': '{{Question}}<br>{{MyMedia}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ]
    )

    deck_id = deck_id # random.randrange(1 << 30, 1 << 31)
    deck = genanki.Deck(deck_id,'Deutsch Trainer')

    for i,(key,val) in enumerate(scraper.vocab.items()):
        note = genanki.Note(model=model, fields=[key,val['de'],f'[sound:{os.path.join(scraper.folder_path,f"audio_{i}.mp3")}]'])
        deck.add_note(note)

    # Save the deck
    package = genanki.Package(deck)#.write_to_file('DeutschTrainer.apkg')
    package.media_files = []
if __name__ == "__main__":
    URL = 'https://learngerman.dw.com/en/1-introducing-yourself/l-57107614/lv'

    scraper = Scraper(URL)
    #scraper.add_url(URL)
    scraper.scrape_content()
    scraper.get_vocab()
    scraper.view_vocab()
    scraper.download_audio()
    
    generate_package()
