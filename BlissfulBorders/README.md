# BlissfulBoarders

BlissfulBoarders is a web application that provides personalized location recommendations for users based on their preferences or unique user IDs. The app helps users discover suitable places for relocation by considering various factors such as economic sector, climate, and socio-political characteristics.

## Table of Contents

- [Features](#features)
- [Installation and Usage](#installation-and-usage)
- [File Structure](#file-structure)

## Features

- Display personalized location recommendations on a map
- Accept user preferences to generate tailored recommendations
- Retrieve recommendations based on user ID
- Rate My Location feature for user feedback

## Installation and Usage

1. Clone the repository or download the source code.
2. Install the required Python libraries.
3. Navigate to the directory containing `app.py` from your terminal or command prompt.
4. Run the command: `python app.py`
5. Open your web browser and visit [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

Note: The application currently uses a sample dataset to generate recommendations.

For a simple getting started tutorial, watch this video: [https://www.youtube.com/watch?v=pYY7qbSUJ-o](https://www.youtube.com/watch?v=pYY7qbSUJ-o)

## File Structure

- `results-by-userid.html`: Generates recommendations based on user ID. Users can input their user ID and the number of locations they would like to receive recommendations for.
- `preferences.html`: Displays a map with relocation recommendations, top cities, and their details.
- `add-rating.html`: Contains a form for users to provide their preferences on various factors.
- `app.py`: A Flask web application that serves the HTML files, handles form submissions, and generates recommendations based on user inputs.

With BlissfulBoarders, users can find tailored location recommendations, making their search for the perfect place to relocate more efficient and personalized.