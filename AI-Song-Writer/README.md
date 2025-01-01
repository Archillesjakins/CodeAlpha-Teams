# AI Music Generator

The **AI Music Generator** application is a deep learning-based tool for generating music using Long Short-Term Memory (LSTM) networks. It processes MIDI files, trains a neural network model to learn musical patterns, and generates new sequences of music. This application also includes features for analyzing generated music, visualizing training history, and playing generated audio.

---

## Features

1. **Process MIDI Files**:
   - Extracts notes and chords from MIDI files for training.

2. **Train a Neural Network Model**:
   - Uses an LSTM-based model to learn patterns from the extracted musical sequences.

3. **Generate Music**:
   - Creates new sequences of music based on trained data.

4. **Analyze Music**:
   - Provides statistical insights into generated music, including note distribution and most common notes.

5. **Visualizations**:
   - Plots training history (loss and accuracy).

6. **Audio Playback**:
   - Plays generated music directly within a Jupyter Notebook.

---

## Requirements

- Python 3.7 or higher
- TensorFlow
- NumPy
- music21
- pretty_midi
- matplotlib
- seaborn
- pandas
- IPython

Install the dependencies using:

```bash
pip install tensorflow numpy music21 pretty_midi matplotlib seaborn pandas ipython
```

---

## Architecture

The application uses a deep learning model based on **LSTM** (Long Short-Term Memory) networks. The architecture is as follows:

1. **Input Layer**:
   - Accepts sequences of shape `(sequence_length, 1)` where each sequence represents a normalized vector of musical notes.

2. **Hidden Layers**:
   - Three LSTM layers:
     - LSTM with 256 units and return sequences enabled.
     - LSTM with 512 units and return sequences enabled.
     - LSTM with 256 units without returning sequences.
   - Dropout layers (0.3 dropout rate) after each LSTM layer for regularization.

3. **Dense Layers**:
   - A dense layer with 256 neurons and ReLU activation.
   - An output dense layer with softmax activation for multiclass classification (each note/chord as a class).

4. **Output**:
   - Predicts the probability distribution over all possible notes for the next note in the sequence.

---

## Usage

### 1. Clone the Repository

```bash
git clone https://github.com/Archillesjakins/AI-SONG-WRITER.git
cd app
```

### 2. Prepare MIDI Data

Place your MIDI files in a directory (e.g., `data/midi_files`) for processing.

### 3. Run the Application

```python
from music_generator import MusicGenerator

# Initialize the generator
generator = MusicGenerator(sequence_length=50)

# Process MIDI files
midi_path = "data/midi_files"  # Replace with your MIDI directory
generator.process_midi_files(midi_path)

# Create and train the model
generator.create_model()
generator.train(epochs=50, batch_size=64)

# Generate music
start_sequence = ["C4", "D4", "E4", "F4", "G4"] * 10  # Example starting sequence
generated_notes = generator.generate_notes(start_sequence, num_notes=100)

# Save generated music as MIDI
generator.create_midi(generated_notes, filename="generated_music.mid")

# Play generated audio
generator.play_generated_audio(generated_notes)
```

### 4. Analyze and Visualize

- Analyze generated music:

  ```python
  analysis = generator.analyze_generated_music(generated_notes)
  print(analysis)
  ```

- Visualize training history:

  ```python
  generator.plot_training_history()
  ```

---

## Example Workflow

1. Process MIDI files:
   - Input: A directory of MIDI files.
   - Output: Extracted notes and chords used for training.

2. Train the model:
   - Input: Sequences of notes and corresponding next notes.
   - Output: Trained LSTM model.

3. Generate music:
   - Input: Starting sequence of notes.
   - Output: New sequence of generated notes.

4. Save and play generated music:
   - Converts generated notes into a playable MIDI file.
   - Plays the music directly in the notebook.

---

## Model Details

- **Type**: LSTM (Long Short-Term Memory) Neural Network
- **Framework**: TensorFlow/Keras
- **Training Data**: MIDI files
- **Loss Function**: Categorical Crossentropy
- **Optimizer**: RMSprop
- **Metrics**: Accuracy
- **Dropout**: Used for regularization to prevent overfitting.
- **Sequence Length**: Configurable (default: 50).

---

## File Structure

```
app/
│
├── model.py       # Main class containing all functionalities
├── README.md                # This file
├── midi_files/                    # Directory for storing MIDI files
├── generated_music.mid      # Example output file (generated music)
└── requirements.txt         # List of dependencies
```

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Acknowledgments

- **TensorFlow**: For providing the framework for deep learning.
- **music21**: For MIDI data extraction and manipulation.
- **pretty_midi**: For MIDI-to-audio conversion.
- **Matplotlib**: For visualization tools.
