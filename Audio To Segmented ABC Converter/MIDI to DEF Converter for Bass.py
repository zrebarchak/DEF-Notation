import tkinter as tk
from tkinter import filedialog, messagebox
from mido import MidiFile

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("MIDI files", "*.mid")])
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

def midi_note_to_def(note):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (note // 12) - 2  # Subtracting 2 to get the correct octave
    note_name = notes[note % 12]
    return f"{note_name}{octave}"

def convert_bass_to_def():
    midi_path = file_entry.get()
    if not midi_path:
        messagebox.showerror("Error", "Please select a MIDI file.")
        return

    try:
        midi_file = MidiFile(midi_path)
        
        ticks_per_sixteenth = midi_file.ticks_per_beat // 4
        total_ticks = sum(msg.time for track in midi_file.tracks for msg in track)
        total_sixteenths = (total_ticks + ticks_per_sixteenth - 1) // ticks_per_sixteenth

        pattern = ['.' for _ in range(total_sixteenths)]
        current_tick = 0
        active_notes = {}

        for track in midi_file.tracks:
            for msg in track:
                current_tick += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    note = midi_note_to_def(msg.note)
                    start_index = current_tick // ticks_per_sixteenth
                    if start_index < total_sixteenths:
                        pattern[start_index] = note
                        active_notes[msg.note] = start_index
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if msg.note in active_notes:
                        start_index = active_notes[msg.note]
                        end_index = current_tick // ticks_per_sixteenth
                        for i in range(start_index + 1, end_index):
                            if i < total_sixteenths:
                                pattern[i] = '-'
                        del active_notes[msg.note]

        # Handle any notes that are still active at the end
        for start_index in active_notes.values():
            for i in range(start_index + 1, total_sixteenths):
                pattern[i] = '-'

        def_notation = ''
        for i, symbol in enumerate(pattern):
            def_notation += symbol + ' '
            if (i + 1) % 16 == 0:
                def_notation += '| '

        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, def_notation.strip())

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Create main window
root = tk.Tk()
root.title("MIDI to DEF Converter (Bass)")

# File selection
file_frame = tk.Frame(root)
file_frame.pack(padx=10, pady=10)

file_label = tk.Label(file_frame, text="Select Bass MIDI file:")
file_label.pack(side=tk.LEFT)

file_entry = tk.Entry(file_frame, width=50)
file_entry.pack(side=tk.LEFT)

file_button = tk.Button(file_frame, text="Browse", command=select_file)
file_button.pack(side=tk.LEFT)

# Convert button
convert_button = tk.Button(root, text="Convert to DEF", command=convert_bass_to_def)
convert_button.pack(pady=10)

# Result output
result_text = tk.Text(root, height=20, width=80)
result_text.pack(padx=10, pady=10)

# Run the application
root.mainloop()