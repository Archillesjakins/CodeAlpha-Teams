import tempfile
import numpy as np
import tensorflow as tf
from music21 import *
import os
import pickle
import matplotlib.pyplot as plt
from IPython.display import Audio, display
import pretty_midi


class MusicGenerator:
    def __init__(self, sequence_length=50):
        """Initialize the MusicGenerator with a sequence length."""
        self.sequence_length = sequence_length
        self.notes_to_int = {}
        self.int_to_notes = {}
        self.sequences = []
        self.next_notes = []
        self.model = None
        self.training_history = None

    def process_midi_files(self, data_path):
        """Process MIDI files from a directory or a single file."""
        notes = []

        # Handle both directory and single file paths
        if os.path.isdir(data_path):
            for file in os.listdir(data_path):
                if file.endswith(".mid"):
                    midi_path = os.path.join(data_path, file)
                    extracted_notes = self._extract_notes(midi_path)
                    if not extracted_notes:
                        print(f"No notes found in {midi_path}. Skipping file.")
                        continue
                    notes.extend(extracted_notes)
        elif os.path.isfile(data_path) and data_path.endswith(".mid"):
            extracted_notes = self._extract_notes(data_path)
            if not extracted_notes:
                print(f"No notes found in {data_path}.")
                return
            notes.extend(extracted_notes)
        else:
            raise ValueError(f"Invalid path: {data_path}. Provide a valid MIDI file or directory.")

        print(f"Total notes extracted: {len(notes)}")

        if len(notes) <= self.sequence_length:
            raise ValueError("The number of notes is too small for the given sequence length.")

        # Create vocabulary
        unique_notes = sorted(set(notes))
        print(f"Unique notes found: {len(unique_notes)}")
        self.notes_to_int = {note: number for number, note in enumerate(unique_notes)}
        self.int_to_notes = {number: note for number, note in enumerate(unique_notes)}

        # Create sequences
        network_input = []
        network_output = []

        for i in range(0, len(notes) - self.sequence_length):
            sequence_in = notes[i:i + self.sequence_length]
            sequence_out = notes[i + self.sequence_length]
            network_input.append([self.notes_to_int[char] for char in sequence_in])
            network_output.append(self.notes_to_int[sequence_out])

        if not network_output:
            raise ValueError("No sequences generated. Check the input data and sequence length.")

        self.sequences = np.reshape(network_input, (len(network_input), self.sequence_length, 1))
        self.sequences = self.sequences / float(len(self.notes_to_int))
        self.next_notes = tf.keras.utils.to_categorical(network_output, num_classes=len(self.notes_to_int))

        print(f"Generated {len(self.sequences)} input sequences and {len(self.next_notes)} output sequences.")

    def _extract_notes(self, midi_path):
        """Extract notes and chords from a MIDI file."""
        try:
            notes = []
            midi = converter.parse(midi_path)

            try:
                s2 = instrument.partitionByInstrument(midi)
                if s2 and s2.parts:  # Check if there are any instruments
                    notes_to_parse = s2.parts[0].recurse()
                else:
                    notes_to_parse = midi.flat.notes
            except:
                notes_to_parse = midi.flat.notes

            for element in notes_to_parse:
                if isinstance(element, note.Note):
                    notes.append(str(element.pitch))
                elif isinstance(element, chord.Chord):
                    notes.append('.'.join(str(n) for n in element.normalOrder))

            print(f"Extracted {len(notes)} notes from {midi_path}")
            return notes

        except Exception as e:
            print(f"Error processing {midi_path}: {str(e)}")
            return []

    def create_model(self):
        """Create the LSTM model."""
        try:
            inputs = tf.keras.layers.Input(shape=(self.sequence_length, 1))
            x = tf.keras.layers.LSTM(256, return_sequences=True)(inputs)
            x = tf.keras.layers.Dropout(0.3)(x)
            x = tf.keras.layers.LSTM(512, return_sequences=True)(x)
            x = tf.keras.layers.Dropout(0.3)(x)
            x = tf.keras.layers.LSTM(256)(x)
            x = tf.keras.layers.Dense(256, activation='relu')(x)
            outputs = tf.keras.layers.Dense(len(self.notes_to_int), activation='softmax')(x)

            self.model = tf.keras.Model(inputs, outputs)
            self.model.compile(loss='categorical_crossentropy', optimizer='rmsprop')
            print("Model created successfully")
            
        except Exception as e:
            print(f"Error creating model: {str(e)}")
            raise

    def train(self, epochs=50, batch_size=64):
        """Train the model."""
        try:
            if self.model is None:
                self.create_model()

            if len(self.sequences) == 0:
                raise ValueError("No training sequences available. Process MIDI files first.")

            self.training_history = self.model.fit(
                self.sequences, 
                self.next_notes, 
                epochs=epochs, 
                batch_size=batch_size,
                validation_split=0.2
            )
            
            print("Training completed successfully")
            return self.training_history

        except Exception as e:
            print(f"Error during training: {str(e)}")
            raise

    def generate_notes(self, start_sequence, num_notes=500, temperature=1.0):
        """Generate new music notes."""
        try:
            if len(start_sequence) != self.sequence_length:
                raise ValueError(f"Start sequence must be {self.sequence_length} notes long")

            pattern = [self.notes_to_int[char] for char in start_sequence]
            prediction_output = []

            for _ in range(num_notes):
                prediction_input = np.reshape(pattern, (1, len(pattern), 1))
                prediction_input = prediction_input / float(len(self.notes_to_int))

                prediction = self.model.predict(prediction_input, verbose=0)

                # Apply temperature sampling
                prediction = np.log(prediction) / temperature
                exp_preds = np.exp(prediction)
                prediction = exp_preds / np.sum(exp_preds)

                next_index = np.random.choice(len(prediction[0]), p=prediction[0])
                next_note = self.int_to_notes[next_index]

                prediction_output.append(next_note)
                pattern.append(next_index)
                pattern = pattern[1:]

            print(f"Generated {len(prediction_output)} notes")
            return prediction_output

        except Exception as e:
            print(f"Error generating notes: {str(e)}")
            raise

    def create_midi(self, prediction_output, filename="generated_music.mid"):
        """Convert the predicted notes into a MIDI file."""
        try:
            offset = 0
            output_notes = []

            for pattern in prediction_output:
                if ('.' in pattern) or pattern.isdigit():
                    # Handle chord
                    notes_in_chord = pattern.split('.')
                    notes = []
                    for current_note in notes_in_chord:
                        new_note = note.Note(int(current_note))
                        new_note.storedInstrument = instrument.Piano()
                        notes.append(new_note)
                    new_chord = chord.Chord(notes)
                    new_chord.offset = offset
                    output_notes.append(new_chord)
                else:
                    # Handle single note
                    new_note = note.Note(pattern)
                    new_note.offset = offset
                    new_note.storedInstrument = instrument.Piano()
                    output_notes.append(new_note)

                offset += 0.5

            midi_stream = stream.Stream(output_notes)
            midi_stream.write('midi', fp=filename)
            print(f"MIDI file created successfully: {filename}")

        except Exception as e:
            print(f"Error creating MIDI file: {str(e)}")
            raise

    def save_model(self, model_path="music_model.h5", mapping_path="note_mappings.pkl"):
        """Save the model and note mappings."""
        try:
            if self.model is None:
                raise ValueError("No model to save. Create and train a model first.")

            self.model.save(model_path)
            with open(mapping_path, 'wb') as f:
                pickle.dump((self.notes_to_int, self.int_to_notes), f)
            
            print(f"Model saved to {model_path}")
            print(f"Note mappings saved to {mapping_path}")

        except Exception as e:
            print(f"Error saving model: {str(e)}")
            raise

    def load_model(self, model_path="music_model.h5", mapping_path="note_mappings.pkl"):
        """Load a previously saved model and note mappings."""
        try:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            if not os.path.exists(mapping_path):
                raise FileNotFoundError(f"Mapping file not found: {mapping_path}")

            self.model = tf.keras.models.load_model(model_path)
            with open(mapping_path, 'rb') as f:
                self.notes_to_int, self.int_to_notes = pickle.load(f)

            print(f"Model loaded from {model_path}")
            print(f"Note mappings loaded from {mapping_path}")

        except Exception as e:
            print(f"Error loading model: {str(e)}")
            raise

    def plot_training_history(self):
        """Visualize the training history."""
        if self.training_history is None:
            raise ValueError("No training history available. Train the model first.")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

        # Plot loss
        ax1.plot(self.training_history.history['loss'], label='Training Loss')
        ax1.plot(self.training_history.history['val_loss'], label='Validation Loss')
        ax1.set_title('Model Loss Over Time')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.legend()

        if 'accuracy' in self.training_history.history:
            ax2.plot(self.training_history.history['accuracy'], label='Training Accuracy')
        if 'val_accuracy' in self.training_history.history:
            ax2.plot(self.training_history.history['val_accuracy'], label='Validation Accuracy')
            ax2.plot(self.training_history.history['val_accuracy'], label='Validation Accuracy')
        ax2.plot(self.training_history.history['val_accuracy'], label='Validation Accuracy')
        ax2.set_title('Model Accuracy Over Time')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Accuracy')
        ax2.legend()

        plt.tight_layout()
        plt.show()
        


    def play_generated_audio(self, generated_notes, sample_rate=44100):
        """Play the generated music directly in the notebook."""
        try:
            midi_stream = self.notes_to_midi_stream(generated_notes)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mid') as temp_midi:
                midi_stream.write('midi', fp=temp_midi.name)
                pm = pretty_midi.PrettyMIDI(temp_midi.name)
                audio_data = pm.synthesize(fs=sample_rate)

            print("Playing generated audio...")
            display(Audio(audio_data, rate=sample_rate))
        except Exception as e:
            print(f"Error playing audio: {str(e)}")


    