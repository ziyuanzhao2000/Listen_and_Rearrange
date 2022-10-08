import tkinter as tk
from playsound import playsound
from random import shuffle
from typing import List

# initialize program logic
button_n_rows = 6
button_n_cols = 6
n_word_slots = button_n_rows*button_n_cols
word_choices = [str(i) for i in range(n_word_slots)]
basedir = './audiobooks/alice_in_wonderland/ch1'

class ButtonsManager:
    buttons: List[tk.Button]
    capacity: int

    def __init__(self):
        self.buttons = []
        self.capacity = 0

    def bind(self, state_mgr):
        self.state_mgr = state_mgr

    def register(self, button: tk.Button):
        self.buttons.append(button)
        self.capacity += 1

    def refresh(self, sentence: str):
        tokens = sentence.split(' ')
        shuffle(tokens)
        assert(len(tokens) <= self.capacity)
        for button in self.buttons:
            button["text"] = ' '
            button["command"] = None
        self.buttons[-1]["text"] = 'effacer'
        self.buttons[-1]["command"] = self.state_mgr.txt_mgr.delete
        for button, token in zip(self.buttons, tokens):
            button["text"] = token
            button["command"] = lambda i=token: register_word(i)
        return len(tokens)

class AudioTranscriptManager:
    audio_src: str
    transcript: List[str]
    fragment_idx: int
    num_fragments: int

    def __init__(self, audio_src: str, transcript_src: str):
        self.audio_src = audio_src
        with open(transcript_src) as f:
            lines = f.readlines()
            self.transcript = [line.rstrip() for line in lines] # bad for large text, but it's ok now
        self.fragment_idx = 0
        self.num_fragments = len(self.transcript)

    def bind(self, state_mgr):
        self.state_mgr = state_mgr

    def __len__(self):
        return self.num_fragments

    def get_idx(self):
        return self.fragment_idx

    def play(self):
        return playsound(f'{self.audio_src}_{self.fragment_idx}.mp3', block=False)

    def transcribe(self):
        return self.transcript[self.fragment_idx]

    def next(self):
        self.fragment_idx+=1
        if self.fragment_idx >= len(self):
            self.fragment_idx = len(self)-1
        self.state_mgr.refresh(True)

    def prev(self):
        self.fragment_idx-=1
        if self.fragment_idx < 0:
            self.fragment_idx = 0
        self.state_mgr.refresh(True)

class TextManager():
    text_box: tk.Label
    text: str

    def __init__(self):
        self.text = ''
        self.text_box = None

    def bind(self, state_mgr):
        self.state_mgr = state_mgr

    def add(self, text_box):
        self.text_box = text_box

    def append(self, word):
        self.text += ' ' + word
        self.refresh()

    def delete(self):
        self.text = self.text.rsplit(' ', 1)[0]
        self.refresh()

    def read(self):
        return self.text

    def flush(self):
        self.text = ''
        self.refresh()

    def refresh(self, text=None):
        if text is not None:
            self.text = text
        self.text_box["text"] = self.text

class StateManager():
    btn_mgr: ButtonsManager
    ctrl: AudioTranscriptManager
    txt_mgr: TextManager
    scoreboard: tk.Label
    words_seen: List[int]
    words_correct: List[int]
    game_status: List[int]

    def __init__(self, btn_mgr, ctrl, txt_mgr):
        self.btn_mgr = btn_mgr
        self.ctrl = ctrl
        self.txt_mgr = txt_mgr
        self.btn_mgr.bind(self)
        self.ctrl.bind(self)
        self.txt_mgr.bind(self)
        self.scoreboard = None
        self.words_seen = [0] * len(self.ctrl)
        self.words_correct = [0] * len(self.ctrl)
        self.game_status = [0] * len(self.ctrl) # 0-not started, 1-incomplete, 2-finished

    def refresh(self, flush=False, text=None):
        transcript = self.ctrl.transcribe()
        num_words = self.btn_mgr.refresh(transcript) #modify the word labels
        stage = self.ctrl.get_idx()
        if not self.game_status[stage]:
            self.words_seen[stage] += num_words
            self.game_status[stage] = 1
        if flush:
            self.txt_mgr.flush()
        self.txt_mgr.refresh(text)
        if self.scoreboard:
            self.scoreboard["text"] = f'Current score: {self.words_correct[stage]}/{self.words_seen[stage]}'

    def submit(self):
        input = txt_mgr.read().strip().split(' ')
        reference = ctrl.transcribe().strip().split(' ')
        stage = self.ctrl.get_idx()
        num_correct = 0
        for i, tupl in enumerate(zip(input, reference)):
            word1, word2 = tupl
            if word1==word2:
                num_correct+=1
            else:
                input[i] = f'[{input[i]}]'
        self.words_correct[stage] = max(num_correct, self.words_correct[stage])
        if self.words_correct[stage] == self.words_seen[stage]:
            game_status[stage] = 2
        self.refresh(text=' '.join(input))

def register_word(word):
    txt_mgr.append(word)

# initialize managers
btn_mgr = ButtonsManager()
ctrl = AudioTranscriptManager(f'{basedir}/ch1', f'{basedir}/ch1_transcript.txt')
txt_mgr = TextManager()
state_mgr = StateManager(btn_mgr, ctrl, txt_mgr)

# initialize GUI
window = tk.Tk()
window_n_rows = 3
window_n_cols = 1

for r in range(window_n_rows):
    window.rowconfigure(r, weight=1, minsize=50)
for c in range(window_n_cols):
    window.columnconfigure(c, weight=1, minsize=50)

button_area_frame = tk.Frame(master=window,
                         bg="blue")
text_area_frame = tk.Frame(master=window,
                       bg="black")
button_area_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
text_area_frame.grid(row=2, column=0, rowspan=1, sticky="nsew")
button_area_control_frame = tk.Frame(master=button_area_frame, pady=5, bg='black')
button_area_control_frame.pack(fill=tk.X)
button_area_inset_frame = tk.Frame(master=button_area_frame)
button_area_inset_frame.pack(padx=100, pady=70, expand=True, fill=tk.BOTH)

# putting buttons into the top 2/3 of the window

# control buttons...
button_next = tk.Button(master=button_area_control_frame,
                        text='next', highlightbackground='black',
                        command=ctrl.next)
button_next.pack(anchor='e', side=tk.RIGHT)
button_submit = tk.Button(master=button_area_control_frame,
                        text='submit', highlightbackground='black',
                        command=state_mgr.submit)
button_submit.pack(anchor='e', side=tk.RIGHT)
button_repeat = tk.Button(master=button_area_control_frame,
                        text='audio repeat', highlightbackground='black',
                        command=ctrl.play)
button_repeat.pack(anchor='e', side=tk.RIGHT)
button_previous = tk.Button(master=button_area_control_frame,
                        text='previous', highlightbackground='black',
                        command=ctrl.prev)
button_previous.pack(anchor='e', side=tk.RIGHT)

# score panel
score_label = tk.Label(master=button_area_control_frame,
                        background='black', foreground='yellow',
                        padx=10, font=(None, 15))
score_label.pack(anchor='w', side=tk.LEFT)
state_mgr.scoreboard = score_label

# word choices buttons...
button_area_n_rows = button_n_rows
button_area_n_cols = button_n_cols
for r in range(button_area_n_rows):
    button_area_inset_frame.rowconfigure(r, weight=1)
for c in range(button_area_n_cols):
    button_area_inset_frame.columnconfigure(c, weight=1)

for r in range(button_area_n_rows):
    for c in range(button_area_n_cols):
        button_id = r*button_area_n_cols + c
        button_frame = tk.Frame(master=button_area_inset_frame)
        button_frame.grid(row=r, column=c)
        button = tk.Button(master=button_frame,
                            bg="blue", font=(None, 20),
                            text=word_choices[r*button_n_cols+c])
        button.pack()
        btn_mgr.register(button)

# text in the lower 1/3 of the window
text_area_inset_frame = tk.Frame(master=text_area_frame)
text_area_inset_frame.pack(padx=50, pady=30, expand=True, fill=tk.BOTH)
text_box = tk.Label(master=text_area_inset_frame, justify=tk.LEFT, font=(None, 20))
text_box.bind('<Configure>', lambda e: text_box.config(wraplength=text_box.winfo_width()-10))
text_box.pack(expand=True, fill=tk.X)
txt_mgr.add(text_box)

state_mgr.refresh()
window.mainloop()