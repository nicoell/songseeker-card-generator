# SongSeeker Card Generator

## Introduction
The SongSeeker Card Generator is a Python script designed to create visual playing cards based on song data. This tool is part of the [SongSeeker project](https://github.com/andygruber/songseeker), a music guessing game.

## Features
- Generate visual cards for songs with QR codes.
- PDF output optimized for double-sided printing.
- Input data in CSV format generated from Spotify playlists.

## Prerequisites
Before you start using the SongSeeker Card Generator, ensure you have Python installed on your system. The script is tested with Python 3.11 and above. You can download and install Python from [here](https://www.python.org/downloads/).

## Installation
Clone the repository to your local machine using the following command:

```bash
git clone https://github.com/andygruber/songseeker-card-generator.git
```

Navigate to the cloned directory:

```bash
cd songseeker-card-generator
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

To run the script, use the following command:

```bash
python card_generator.py <input_csv_path> <output_pdf_path>
```

### Example

```bash
python card_generator.py data/example-spotify-songs.csv example.pdf
```

You can also add an icon to the card by using the `--icon` flag:

```bash
# Add icon from a URL
python card_generator.py data/example-spotify-songs.csv example.pdf --icon https://github.com/andygruber/songseeker/blob/main/icons/icon-96x96.png?raw=true

# Add icon from a local file
python card_generator.py data/example-spotify-songs.csv example.pdf --icon ../songseeker/icons/icon-96x96.png
```

## Printing Instructions

1. **Double-Sided Printing**: Print the generated PDF double-sided.
2. **Flipping on Long Edge**: Ensure that the pages are flipped on the long edge to align the QR codes and text correctly.

## CSV Input Format

### Generating CSV Data

1. **Exportify**: Use [Exportify.net](https://exportify.net/) to export your Spotify playlist data into a CSV file. This tool allows you to download your playlist's song information easily.

### Required CSV Columns

Ensure your CSV file contains the following headers:

- **Track ID**: The unique Spotify track identifier.
- **Track Name**: The title of the song.
- **Artist Name(s)**: The artist or artists performing the song.
- **Release Date**: The release date of the song (format: YYYY-MM-DD).

### Example CSV Structure

```csv
Track ID,Track Name,Album Name,Artist Name(s),Release Date,Duration (ms),Popularity,Added By,Added At,Genres,Record Label,Danceability,Energy,Key,Loudness,Mode,Speechiness,Acousticness,Instrumentalness,Liveness,Valence,Tempo,Time Signature
5Phy3qS90Q5I8DGcTxmSIL,"What's a Woman","Night Owls","Vaya Con Dios",1990-04-10,233493,56,,2024-11-16T08:36:48Z,"classic belgian pop","Ariola",0.294,0.329,7,-12.571,1,0.0338,0.625,0.00032,0.154,0.267,82.865,3
```

**Note**: The script utilizes the following columns from the CSV:

- `Track ID`
- `Track Name`
- `Artist Name(s)`
- `Release Date`

Ensure these columns are present and correctly named in your CSV file. Additional columns will be ignored.

## Contributing

Contributions to the SongSeeker Card Generator are welcome. Please ensure to update tests as appropriate and follow best practices for code quality and documentation.

## License

This project is licensed under the AGPL-3.0 license - see the [LICENSE](LICENSE) file for details.

---

## Additional Notes

- **Icon Requirements**: If you choose to add an icon to the QR codes, ensure the icon image does not exceed 300x300 pixels and uses a transparent background for optimal appearance.
- **PDF Layout**: The generated PDF is designed for cutting into individual cards. Ensure your printer settings match the recommended printing instructions to maintain alignment.
- **Error Handling**: The script dynamically adjusts font sizes to prevent text from clipping. However, extremely long titles or artist names may still require manual adjustment in the CSV data for optimal results.

Feel free to reach out via the repository's [issues page](https://github.com/andygruber/songseeker-card-generator/issues) for any questions or support.