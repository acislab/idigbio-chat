import pandas as pd
import requests
import unstructured.partition.html


def get_glossary():
    res = requests.get("https://www.idigbio.org/wiki/index.php/Glossary_of_Terms")
    return res.text


def chunk():
    unstructured.partition.auto.partition()


def test_pandas():
    table = pd.read_html("resources/external/idigbio_org_Glossary_of_Terms.html")[0]
    row = table.iloc[0]
    name = f"{row['Long Name']} ({row['Short Name']})" if row['Short Name'] != row['Long Name'] else row['Short Name']
    doc = f"{name} [{row['Tag']}]. Homepage: {row['URL']}. Description: {row['Definition']}"
    pass


def test_unstructured():
    with open("resources/external/idigbio_org_Glossary_of_Terms.html", "w+") as f:
        gloss = get_glossary()
        f.write(gloss)

    parts = unstructured.partition.html.partition.partition_html(
        "resources/external/idigbio_org_Glossary_of_Terms.html",
        infer_table_structure=True
    )
    parts

    pass
