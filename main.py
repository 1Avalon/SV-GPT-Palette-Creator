import openai
from api_key import API_KEY
import colorsys
from PIL import Image
import requests
import PyPDF2
from io import BytesIO

def get_sundrop_guide():
    url = 'https://sundrop.kvdk.net/files/SundropArtGuide.pdf'
    response = requests.get(url)
    pdf_bytes = BytesIO(response.content)

    pdf_reader = PyPDF2.PdfReader(pdf_bytes)

    guide = ''
    for page in pdf_reader.pages:
        guide += page.extract_text()
    
    return guide

def get_color_list(gpt_response):
    colors = ''
    start = False
    for letter in gpt_response:
        if letter == '[' and not start:
            start = True
        
        if start:
            colors += letter #starts to add the characters to an empty string after the list begins

    return colors

def convert_color_list(color_list):
    color_list = color_list.strip('[]')
    tuples = color_list.split('), (')

    convertedList = []


    for str_tuple in tuples:
        str_tuple = str_tuple.strip('()') 
        splitted_tuple = tuple(map(lambda x: x.strip(), str_tuple.split(','))) #getting rid of unwanted characters
        converted_tuple = tuple(map(int, splitted_tuple)) #converting the elements of the tuple into integers
        convertedList.append(converted_tuple)

    convertedList.sort(key=lambda rgb: colorsys.rgb_to_hls(*rgb), reverse=True) #sorting colors by hue
    return convertedList

def create_palette(colors, scale, name):
    palette = Image.new('RGB', (len(colors) * scale, scale))

    pixel_pos = 0
    for y in range(scale):
        for color in colors:
            for length in range(scale):
                palette.putpixel((pixel_pos, y), color)
                pixel_pos += 1                    
        pixel_pos = 0

    palette.save(f"{name}.png")
    print("Palette saved.")

openai.api_key = API_KEY
prompt = input("Please describe your palette: ")
scale = int(input("Please enter the scale of each color of the palette: "))

palette_name = prompt.replace(" ", "_")
guide = get_sundrop_guide()

while True:
    completion = openai.Completion.create(max_tokens=800, 
                                        engine="text-davinci-003", 
                                        prompt= "Please read the following guide:\n" + guide + 
                                        ". Make sure you apply the rules, especially hue shifting and high saturation. Now, by following the guide, create a pixel art palette which can be used to draw this: " + prompt 
                                        + ". Don't give me a different color when I ask for a specific one. Please give me the result as a python list with rgb values as tuples. Please don't add any comments.") # CHANGING THE PROMPT CAN RESULT IN AN INFINITE LOOP !
    response = completion.choices[0].text

    colors = get_color_list(response)

    try:
        color_list = convert_color_list(colors)

    except Exception:
        continue # sometimes the AI adds comments to the output, resulting in raising errors. We will just skip this and create a new palette

    
    create_palette(color_list, scale, palette_name)

    input('Hit enter to recreate the palette')
    