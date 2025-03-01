from typing import List, Tuple


TAG_LIST = [
        {"tag_typ": "category", "id": "lebensmittel", "name": "Lebensmittel"},
        {"tag_typ": "category", "id": "tanken", "name": "Tanken"},
        {"tag_typ": "category", "id": "sonstiges", "name": "Sonstiges"},
        {"tag_typ": "category", "id": "urlaub", "name": "Urlaub"},

        {"tag_typ": "person", "id": "cordula", "name": "Cordula"},
        {"tag_typ": "person", "id": "bruno", "name": "Bruno"},
        {"tag_typ": "person", "id": "oscar", "name": "Oscar"},
        {"tag_typ": "person", "id": "dirk", "name": "Dirk"},

        {"tag_typ": "location", "id": "waldaschaff", "name": "Waldaschaff"},
        {"tag_typ": "location", "id": "potsdam", "name": "Potsdam"},
        {"tag_typ": "location", "id": "torrevieja", "name": "Torrevija"},

        {"tag_typ": "tag", "id": "sport", "name": "Sport"},
        {"tag_typ": "tag", "id": "versicherung", "name": "Versicherung"},
        {"tag_typ": "tag", "id": "auto", "name": "Auto"},
        {"tag_typ": "tag", "id": "gastronomie", "name": "Gastronomie"},
        {"tag_typ": "tag", "id": "gesundheit", "name": "Gesundheit"},
        {"tag_typ": "tag", "id": "bildung", "name": "Bildung"},
        {"tag_typ": "tag", "id": "freizeit", "name": "Freizeit"},
        {"tag_typ": "tag", "id": "technologie", "name": "Technologie"},
        {"tag_typ": "tag", "id": "haushalt", "name": "Haushalt"},
        {"tag_typ": "tag", "id": "geschenke", "name": "Geschenke"},
    ]


_category_limits = {
    "lebensmittel": 200,
    "tanken": 100,
    "sonstiges": 100
}


def tags_get_categories() -> Tuple[List[str], List[str]]:
    """Returns two lists: category IDs and category names from TAG_LIST."""
    categories = [tag for tag in TAG_LIST if tag["tag_typ"] == "category"]
    return [tag["id"] for tag in categories], [tag["name"] for tag in categories]


def tags_get_limits(category_names: List[str]) -> List[float]:
    # Create the list of limits in the same order as the category_names
    return [_category_limits.get(category, 0.0) for category in category_names]