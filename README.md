# image-tagger

An image tagger using [Groq](https://groq.com/). Use GroqChat to help tag your images into a json file.

<a href="https://groq.com" target="_blank" rel="noopener noreferrer">
  <img
    src="https://groq.com/wp-content/uploads/2024/03/PBG-mark1-color.svg"
    alt="Powered by Groq for fast inference."
  />
</a>

## Prerequisites

Go to [Groq](https://groq.com/). Go to the dev console and make an API Key.
Create a .env file in the root of the repository like so, replacing the XXXXX with your value.

```env
GROQ_API_KEY=XXXXX
```

Run the following from the root of the repository to get a functional conda environment.

```sh
conda env create -f environment.yaml
```

## Usage

Please note that this is not perfect. Groq sometimes returns invalid data.


```sh
python main.py -i "./tests/images/800px-Another_Day_in_NYC_(2539547867).jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Interior_Galeria_Arte_Nacional_%28Caracas%29.jpg/800px-Interior_Galeria_Arte_Nacional_%28Caracas%29.jpg?20071010223618"
```

```sh
python main.py -i ./tests/images
```

## Images

All images were source from Wikimedia commons.

## Tests

Run the following from the root

```sh
tox
```