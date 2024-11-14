import folium
import requests
from playwright.sync_api import sync_playwright


def html_to_png(html_str: str):
    with sync_playwright() as p:
        browser_type = p.chromium
        browser = browser_type.launch()
        page = browser.new_page(viewport={"width": 512, "height": 512})
        page.set_content(html_str, wait_until="load")
        png = page.screenshot()
        browser.close()

    return png


def test_a_map_of_gainesville():
    m = folium.Map(location=[29.6520, -82.3250], zoom_start=18, name="map")
    folium.TileLayer(
        "https://b.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="Test"
    ).add_to(m)

    html_str: str = m.get_root().render()
    png = html_to_png(html_str)

    with open("test.png", "wb") as f:
        f.write(png)


def test_map_of_occurrences():
    m = folium.Map(location=[0, 0], zoom_start=1, name="the_map", zoom_control=False,
                   fade_animation=False)

    folium.TileLayer(
        "https://b.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="Test",
        transition={
            "duration": 0,
            "delay": 0
        }
    ).add_to(m)

    d = requests.post("https://search.idigbio.org/v2/mapping/", json={
        "rq": {
            "class": "aves"
        },
        "style": {
            "styleOn": "kingdom"
        },
        "type": "points"
    })
    tiles_url = d.json()["tiles"]
    folium.TileLayer(
        tiles_url,
        attr="iDigBio Portal",
        transition={
            "duration": 0,
            "delay": 0
        }
    ).add_to(m)

    html_str = str(m.get_root().render())
    png = html_to_png(html_str)

    with open("test_idb.png", "wb") as f:
        f.write(png)


def test_pw():
    with sync_playwright() as p:
        browser_type = p.chromium
        browser = browser_type.launch()
        page = browser.new_page()
        page.set_content("<h1>This is a test</h1>")
        page.screenshot(path=f'test.png')
        browser.close()
