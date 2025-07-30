def extract_substrings(document, labels):
    """
    Replace the text in the document with generic pii labels

    Parameters
    ----------
    document : str
        the original document containing pii
    labels : list of dict
        each dict contains keys 'category', 'offset' and 'length' of the pii

    Returns
    -------
    document_new : str
        the document with pii replaced by generic labels
    labels_new: list of dict
        updated labels for the generic pii labels
    """
    text_segments = []
    offset = 0

    for label in labels:
        start = label["offset"]
        end = label["length"] + start
        category = label["category"]
        pii_text = document[start:end]
        non_pii_text = document[offset:start]
        text_segments += [
            ("non_pii", non_pii_text, offset),
            (category, pii_text, start),
        ]
        offset = end

    # add the final substring (if there is one)
    if document[end:]:
        text_segments.append(("non_pii", document[end:], end))

    pii_segments = [
        text_segment for text_segment in text_segments if text_segment[0] != "non_pii"
    ]
    pii_segments = sorted(list(set(pii_segments)), key=lambda x: (x[0], x[2]))

    return text_segments, pii_segments


def create_pii_mapping(pii_segments):
    """
    Replace pii segments with generic pii labels

    Parameters
    ----------
    pii_segments : list of tuples
        original pii to map to new values
    synthetic_data : bool
        whether or not to create synthetic pii to replace existing pii

    Returns
    -------
    pii_mapping : dict
        maps old pii values to new, generic pii values
    """
    pii_mapping = {}

    counter = 0
    category, pii_value, _ = pii_segments[0]
    new_pii_value = f"[{category}_0]"
    pii_mapping[pii_value] = new_pii_value

    for pii_segment in pii_segments[1:]:
        new_category, pii_value, _ = pii_segment
        if new_category != category:
            counter = 0
            new_pii_value = f"[{new_category}_0]"
            category = new_category
            pii_mapping[pii_value] = new_pii_value
        else:
            counter += 1
            new_pii_value = f"[{new_category}_{counter}]"
            pii_mapping[pii_value] = new_pii_value

    return pii_mapping


def replace_pii_values(text_segments, pii_mapping):
    """
    Replace all instances of pii in the document with generic pii labels

    Parameters
    ----------
    text_segments : list of tuples
        list of text segments in document (either pii or not pii)
    pii_mapping : dict
        mapping of old pii values to new ones

    Returns
    -------
    document_new : str
        the document with pii replaced
    new_labels : list of dict
        list with the offsets and length of the labels in the new document
    """
    new_document_segments = []
    new_labels = []
    offset = 0

    for text_segment in text_segments:
        if text_segment[0] == "non_pii":
            offset += len(text_segment[1])
            new_document_segments.append(text_segment[1])
        else:
            new_pii_value = pii_mapping[text_segment[1]]
            new_labels.append(
                {
                    "category": text_segment[0],
                    "offset": offset,
                    "length": len(new_pii_value),
                }
            )
            offset += len(new_pii_value)
            new_document_segments.append(new_pii_value)

    new_document = "".join(new_document_segments)

    return new_document, new_labels


def redact_document(document, labels):
    """
    Replace all instances of pii in a document with a generic pii label

    Parameters
    ----------
    document : str
        the original document containing pii
    labels : list of dict
        labels containing category, offset and length keys that defin the pii

    Returns
    -------
    redacted_document : str
        the document with all pii removed
    new_labels : list of dict
        locations of all the generic pii labels
    """
    # extract all the substrings defined by the pii boundaries
    text_segments, pii_segments = extract_substrings(document, labels)

    # map pii to generic category types
    pii_mapping = create_pii_mapping(pii_segments)

    # replace all pii in the original document with the generic pii type values and create the redacted document
    redacted_document, new_labels = replace_pii_values(
        text_segments, pii_mapping
    )

    return redacted_document, new_labels


def detect_pii(model, document, entities):
    """
    Detect all instances of pii in a document, based on a specified list of entities

    Parameters
    ----------
    model : GliNER model
        the NLP model used to detect the pii
    document : str
        the document to redact
    entities : list of str
        types of pii to detect

    Returns
    -------
    labels : list of dict
        list of all the instances of pii
    """
    labels = [
        {
            "category": label["label"],
            "offset": label["start"],
            "length": label["end"] - label["start"],
        }
        for label in model.predict_entities(document, entities, threshold=0.5)
    ]

    return labels
