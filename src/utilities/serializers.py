from bson import ObjectId

def serialize_mongo_doc(doc):
    """
    Recursively converts ObjectId and nested structures into JSON-serializable values.
    """
    if isinstance(doc, list):
        return [serialize_mongo_doc(d) for d in doc]
    elif isinstance(doc, dict):
        new_doc = {}
        for k, v in doc.items():
            if isinstance(v, ObjectId):
                new_doc[k] = str(v)
            elif isinstance(v, (dict, list)):
                new_doc[k] = serialize_mongo_doc(v)
            else:
                new_doc[k] = v
        return new_doc
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc
