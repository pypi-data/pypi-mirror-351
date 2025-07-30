# img_db.py

def img(name):
    image_dict = {
        "neptune":"https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Neptune_like_planet_or_mini_neptune_2_1_1_1.png/960px-Neptune_like_planet_or_mini_neptune_2_1_1_1.png?20230920134641",
        "uranus":"https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Uranus_and_Neptune.jpg/960px-Uranus_and_Neptune.jpg?20230622181218",
        "saturn":"https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Saturn_square_crop.jpg/960px-Saturn_square_crop.jpg?20220813182013",
        "jupiter":"https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupiter_%28January_2023%29_%28heic2303e%29.jpg/960px-Jupiter_%28January_2023%29_%28heic2303e%29.jpg?20230416215004",
        "mars":"https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/MARS_THE_RED_PLANET.jpg/960px-MARS_THE_RED_PLANET.jpg?20210319054849",
        "earth":"https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Artistic_depiction_of_planet_Earth.jpg/960px-Artistic_depiction_of_planet_Earth.jpg?20201109194112",
        "dog": "https://upload.wikimedia.org/wikipedia/commons/6/6e/Golde33443.jpg",
        "cat": "https://upload.wikimedia.org/wikipedia/commons/3/3a/Cat03.jpg",
        "mercury": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Mercury_render_with_Blender_01.png/800px-Mercury_render_with_Blender_01.png",
        "venus":"https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Venus_-_December_23_2016.png/960px-Venus_-_December_23_2016.png?20201026180121"
    }
    return image_dict.get(name.lower(), None)

def image_source(name):
    image_desc_dict = {
        "uranus":"https://commons.wikimedia.org/wiki/File:Uranus_and_Neptune.jpg",
        "satrun":"https://commons.wikimedia.org/wiki/File:Saturn_square_crop.jpg",
        "jupiter":"https://commons.wikimedia.org/wiki/File:Jupiter_%28January_2023%29_%28heic2303e%29.jpg",
        "mars":"https://commons.wikimedia.org/wiki/File:MARS_THE_RED_PLANET.jpg",
        "earth":"https://commons.wikimedia.org/wiki/File:Artistic_depiction_of_planet_Earth.jpg",
        "mercury": "https://commons.wikimedia.org/wiki/File:Mercury_render_with_Blender_01.png",
        "dog": "https://commons.wikimedia.org/wiki/File:Golde33443.jpg",
        "cat": "https://commons.wikimedia.org/wiki/File:Cat03.jpg",
        "venus":"https://commons.wikimedia.org/wiki/File:Venus_-_December_23_2016.png",
        "neptune":"https://commons.wikimedia.org/wiki/File:Neptune_like_planet_or_mini_neptune_2_1_1_1.png"
    }
    return image_desc_dict.get(name.lower(), None)
