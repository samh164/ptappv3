# PT App - AI Fitness Plan Generator

A Streamlit web application that generates personalized fitness plans using AI, integrating with OpenAI's GPT models and ExerciseDB API.

## Features

- 🏋️ Create personalized workout plans based on user profiles
- 🥗 Generate customized meal plans that respect dietary preferences and restrictions
- 📊 Track fitness progress through an interactive journal
- 📈 Visualize progress metrics over time
- 📱 Accessible through any web browser

## Tech Stack

- **Frontend/Backend**: Streamlit
- **AI Integration**: OpenAI API
- **Exercise Data**: ExerciseDB API (via RapidAPI)
- **Database**: SQLite with SQLAlchemy ORM
- **Language**: Python 3.11+

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/samh164/ptappv3.git
   cd ptappv3
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your API keys:
   - Create a `.env` file in the root directory
   - Add your API keys:
     ```
    OPENAI_API_KEY=your_openai_api_key
    EXERCISEDB_API_KEY=your_exercisedb_api_key
     ```

## Usage

1. Start the application:
   ```
   streamlit run PTApp.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8501
   ```

3. Create a user profile and follow the guided workflow to generate your fitness plan.

## Project Structure

- `PTApp.py`: Main application file
- `database/`: Database models and connection management
- `services/`: Core business logic services
- `pages/`: UI components for different sections
- `utils/`: Utility functions and helpers
- `config/`: Configuration settings

## License

MIT

## Acknowledgements

- Exercise data provided by [ExerciseDB](https://rapidapi.com/justin-WFnsXH_t6/api/exercisedb)
- AI text generation powered by [OpenAI](https://openai.com/)
- UI built with [Streamlit](https://streamlit.io/) 