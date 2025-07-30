from blankit.utils import (
    extract_substrings,
    create_pii_mapping,
    replace_pii_values,
    redact_document,
)


def test_extract_substrings1():
    document = "barry went to see harish"
    labels = [
        {"category": "Person", "offset": 0, "length": 5},
        {"category": "Person", "offset": 18, "length": 6},
    ]

    text_segments, pii_segments = extract_substrings(document, labels)

    assert len(text_segments) == 4
    assert len(pii_segments) == 2
    assert pii_segments[0][0] == "Person"
    assert pii_segments[0][1] == "barry"
    assert pii_segments[0][2] == 0
    assert pii_segments[1][0] == "Person"
    assert pii_segments[1][1] == "harish"
    assert pii_segments[1][2] == 18
    assert text_segments[0][0] == "non_pii"
    assert text_segments[0][1] == ""
    assert text_segments[0][2] == 0
    assert text_segments[1][0] == "Person"
    assert text_segments[1][1] == "barry"
    assert text_segments[1][2] == 0
    assert text_segments[2][0] == "non_pii"
    assert text_segments[2][1] == " went to see "
    assert text_segments[2][2] == 5
    assert text_segments[3][0] == "Person"
    assert text_segments[3][1] == "harish"
    assert text_segments[3][2] == 18


def test_extract_substrings2():
    document = "buenos aires is the capital of argentina and it is a beautiful city"
    labels = [
        {"category": "Location", "offset": 0, "length": 12},
        {"category": "Location", "offset": 31, "length": 9},
    ]

    text_segments, pii_segments = extract_substrings(document, labels)

    assert len(text_segments) == 5
    assert len(pii_segments) == 2
    assert pii_segments[0][0] == "Location"
    assert pii_segments[0][1] == "buenos aires"
    assert pii_segments[0][2] == 0
    assert pii_segments[1][0] == "Location"
    assert pii_segments[1][1] == "argentina"
    assert pii_segments[1][2] == 31
    assert text_segments[0][0] == "non_pii"
    assert text_segments[0][1] == ""
    assert text_segments[0][2] == 0
    assert text_segments[1][0] == "Location"
    assert text_segments[1][1] == "buenos aires"
    assert text_segments[1][2] == 0
    assert text_segments[2][0] == "non_pii"
    assert text_segments[2][1] == " is the capital of "
    assert text_segments[2][2] == 12
    assert text_segments[3][0] == "Location"
    assert text_segments[3][1] == "argentina"
    assert text_segments[3][2] == 31
    assert text_segments[4][0] == "non_pii"
    assert text_segments[4][1] == " and it is a beautiful city"
    assert text_segments[4][2] == 40


def test_pii_mapping1():
    document = "barry went to see harish"
    labels = [
        {"category": "Person", "offset": 0, "length": 5},
        {"category": "Person", "offset": 18, "length": 6},
    ]

    _, pii_segments = extract_substrings(document, labels)
    pii_mapping = create_pii_mapping(pii_segments)

    assert isinstance(pii_mapping, dict)
    assert len(pii_mapping) == 2
    assert ("barry" in pii_mapping.keys()) and ("harish" in pii_mapping.keys())
    assert ("[Person_0]" in pii_mapping.values()) and (
        "[Person_1]" in pii_mapping.values()
    )
    assert pii_mapping["barry"] == "[Person_0]"
    assert pii_mapping["harish"] == "[Person_1]"


def test_pii_mapping2():
    document = "buenos aires is the capital of argentina and it is a beautiful city"
    labels = [
        {"category": "Location", "offset": 0, "length": 12},
        {"category": "Location", "offset": 31, "length": 9},
    ]

    _, pii_segments = extract_substrings(document, labels)
    pii_mapping = create_pii_mapping(pii_segments)

    assert isinstance(pii_mapping, dict)
    assert len(pii_mapping) == 2
    assert ("buenos aires" in pii_mapping.keys()) and (
        "argentina" in pii_mapping.keys()
    )
    assert ("[Location_0]" in pii_mapping.values()) and (
        "[Location_1]" in pii_mapping.values()
    )
    assert pii_mapping["buenos aires"] == "[Location_0]"
    assert pii_mapping["argentina"] == "[Location_1]"


def test_replace_pii_values1():
    document = "barry went to see harish"
    labels = [
        {"category": "Person", "offset": 0, "length": 5},
        {"category": "Person", "offset": 18, "length": 6},
    ]

    text_segments, pii_segments = extract_substrings(document, labels)
    pii_mapping = create_pii_mapping(pii_segments)
    new_document, new_labels = replace_pii_values(text_segments, pii_mapping)

    assert isinstance(new_document, str)
    assert isinstance(new_labels, list)
    assert len(new_document) == 33
    assert len(new_labels) == 2
    assert new_labels[0]["category"] == "Person"
    assert new_labels[0]["offset"] == 0
    assert new_labels[0]["length"] == 10
    assert new_labels[1]["category"] == "Person"
    assert new_labels[1]["offset"] == 23
    assert new_labels[1]["length"] == 10


def test_replace_pii_values2():
    document = "buenos aires is the capital of argentina and it is a beautiful city"
    labels = [
        {"category": "Location", "offset": 0, "length": 12},
        {"category": "Location", "offset": 31, "length": 9},
    ]

    text_segments, pii_segments = extract_substrings(document, labels)
    pii_mapping = create_pii_mapping(pii_segments)
    new_document, new_labels = replace_pii_values(text_segments, pii_mapping)

    assert isinstance(new_document, str)
    assert isinstance(new_labels, list)
    assert len(new_document) == 70
    assert len(new_labels) == 2
    assert new_labels[0]["category"] == "Location"
    assert new_labels[0]["offset"] == 0
    assert new_labels[0]["length"] == 12
    assert new_labels[1]["category"] == "Location"
    assert new_labels[1]["offset"] == 31
    assert new_labels[1]["length"] == 12


def test_redact_document1():
    document = "barry went to see harish"
    labels = [
        {"category": "Person", "offset": 0, "length": 5},
        {"category": "Person", "offset": 18, "length": 6},
    ]

    redacted_document, new_labels = redact_document(document, labels)
    assert len(redacted_document) == 33
    assert isinstance(redacted_document, str)
    assert len(new_labels) == 2
    assert new_labels[0]['category'] == 'Person'
    assert new_labels[0]['offset'] == 0
    assert new_labels[0]['length'] == 10
    assert new_labels[1]['category'] == 'Person'
    assert new_labels[1]['offset'] == 23
    assert new_labels[1]['length'] == 10

def test_redact_document2():
    document = "buenos aires is the capital of argentina and it is a beautiful city"
    labels = [
        {"category": "Location", "offset": 0, "length": 12},
        {"category": "Location", "offset": 31, "length": 9},
    ]

    redacted_document, new_labels = redact_document(document, labels)
    assert len(redacted_document) == 70
    assert isinstance(redacted_document, str)
    assert len(new_labels) == 2
    assert new_labels[0]['category'] == 'Location'
    assert new_labels[0]['offset'] == 0
    assert new_labels[0]['length'] == 12
    assert new_labels[1]['category'] == 'Location'
    assert new_labels[1]['offset'] == 31
    assert new_labels[1]['length'] == 12