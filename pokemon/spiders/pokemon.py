import scrapy


class PokemonScraper(scrapy.Spider):
    name = 'pokemon_scraper'
    start_urls = ["https://pokemondb.net/pokedex/all"]

    def parse(self, response):
        pokemons = response.css('#pokedex > tbody > tr')
        for pokemon in pokemons:
            number = pokemon.css(
                'td.cell-num span.infocard-cell-data::text').get()
            name = pokemon.css('td.cell-name a.ent-name::text').get()
            link = pokemon.css('td.cell-name a.ent-name::attr(href)').get()
            pokemon_url = response.urljoin(link)

            types = pokemon.css('td.cell-icon a.type-icon::text').getall()

            # Navegar até a página do Pokémon
            yield response.follow(pokemon_url, self.parse_pokemon, meta={
                'number': number,
                'name': name,
                'url': pokemon_url,
                'types': types,
            })

    def parse_pokemon(self, response):
        number = response.meta['number']
        name = response.meta['name']
        pokemon_url = response.meta['url']
        types = response.meta['types']

        height = response.css(
            '.vitals-table tr:contains("Height") td::text').get().strip()
        weight = response.css(
            '.vitals-table tr:contains("Weight") td::text').get().strip()

        evolutions = []
        for evo in response.css('.infocard-list-evo .infocard'):
            evo_number = evo.css('.text-muted small::text').get()
            evo_name = evo.css('.ent-name::text').get()
            evo_link = response.urljoin(evo.css('a::attr(href)').get())
            if evo_name and evo_number:
                evolutions.append(f"{evo_number} - {evo_name} - {evo_link}")

        evolutions_str = "; ".join(evolutions)

        abilities = []
        for ability in response.css('.vitals-table tr:contains("Abilities") td a'):
            ability_name = ability.css('::text').get()
            ability_url = response.urljoin(ability.css('::attr(href)').get())
            if ability_name:
                abilities.append(
                    {'name': ability_name, 'url': ability_url, 'description': None})

        # Navegar até a página de cada habilidade e capturar a descrição
        for i, ability in enumerate(abilities):
            yield response.follow(ability['url'], self.parse_ability_description, meta={
                'number': number,
                'name': name,
                'url': pokemon_url,
                'types': ", ".join(types),
                'height_cm': height,
                'weight_kg': weight,
                'next_evolutions': evolutions_str if evolutions else "",
                'abilities': abilities,
                'ability_index': i,
                'ability_name': ability['name'],
                'ability_url': ability['url']
            })

    def parse_ability_description(self, response):
        number = response.meta['number']
        name = response.meta['name']
        pokemon_url = response.meta['url']
        types = response.meta['types']
        height = response.meta['height_cm']
        weight = response.meta['weight_kg']
        evolutions_str = response.meta['next_evolutions']
        abilities = response.meta['abilities']
        ability_index = response.meta['ability_index']
        ability_name = response.meta['ability_name']
        ability_url = response.meta['ability_url']

        # Captura a descrição da habilidade
        ability_description = response.css(
            'main > div > div > div > .vitals-table > tbody > tr:nth-Child(1) > td::text').get()

        # Verifica se a descrição foi capturada
        if ability_description:
            ability_description = ability_description.strip()
            self.log(f"Descrição capturada para {
                     ability_name}: {ability_description}")
        else:
            ability_description = "No description available"
            self.log(f"Descrição não encontrada para {
                     ability_name} na URL {ability_url}.")

        # Atualiza a habilidade com a descrição na posição correta da lista
        abilities[ability_index]['description'] = ability_description

        # Verifica se todas as descrições foram capturadas antes de retornar o Pokémon completo
        if all(ability.get('description') is not None for ability in abilities):
            yield {
                'number': number,
                'name': name,
                'url': pokemon_url,
                'types': types,
                'height_cm': height,
                'weight_kg': weight,
                'next_evolutions': evolutions_str,
                'abilities': abilities,
            }
