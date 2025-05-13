import json
import threading
import time
import pyaudio
from vosk import Model, KaldiRecognizer
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import queue


class ContinuousSpeechGloss:
    """
    Class for continuous speech recognition and gloss translation.
    Runs in the background and processes speech without auto-stopping.
    """

    def __init__(self, model_path="C:\\Users\\DELL\\PycharmProjects\\ASR\\vosk-model-small-en-us-0.15", callback=None):
        """
        Initialize continuous speech recognition.

        Args:
            model_path (str): Path to the Vosk model
            callback (function): Optional callback function that receives (transcript, gloss) tuples
        """
        # Ensure NLTK resources are downloaded
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)

        # Setup NLP resources
        self.stop_words = set(stopwords.words('english')) - {
            'i', 'you', 'we', 'he', 'she', 'they', 'me', 'my', 'your', 'our', 'his', 'her', 'their'
        }

        # Gloss mapping for sign language
        self.gloss_map = {
            "i": "ME", "you": "YOU", "we": "US", "he": "HE", "she": "SHE", "they": "THEY",
            "am": "", "is": "", "are": "", "was": "", "were": "",
            "going": "GO", "go": "GO", "want": "WANT", "have": "HAVE", "had": "HAVE",
            "don't": "NOT", "not": "NOT", "no": "NOT", "won't": "NOT WILL",
            "store": "STORE", "because": "WHY", "milk": "MILK", "to": "",
            "the": "", "a": "", "an": "", "and": "PLUS", "but": "BUT",
            "this": "THIS", "that": "THAT", "there": "THERE", "here": "HERE",
            "what": "WHAT", "who": "WHO", "where": "WHERE", "when": "WHEN", "why": "WHY", "how": "HOW",
            "need": "NEED", "can": "CAN", "will": "WILL", "should": "SHOULD", "must": "MUST",
            "good": "GOOD", "bad": "BAD", "happy": "HAPPY", "sad": "SAD",
            "yes": "YES", "okay": "OK", "like": "LIKE", "help": "HELP"
        }

        self.model_path = model_path
        self.callback = callback
        self.running = False
        self.thread = None
        self.results = queue.Queue()  # Store results if no callback is provided

    def convert_to_sign_gloss(self, text):
        """Convert normal text to sign language gloss notation"""
        words = word_tokenize(text.lower())
        words = [word for word in words if word not in string.punctuation]
        filtered = [word for word in words if word not in self.stop_words or word.lower() in self.gloss_map]

        gloss_sequence = []
        for word in filtered:
            gloss_word = self.gloss_map.get(word.lower(), word.upper())
            if gloss_word:  # Only add non-empty strings
                gloss_sequence.append(gloss_word)

        gloss_string = " ".join(gloss_sequence)
        return gloss_string

    def start(self):
        """Start continuous speech recognition"""
        if self.running:
            return False

        self.running = True
        self.thread = threading.Thread(target=self._listen_continuously)
        self.thread.daemon = True
        self.thread.start()
        return True

    def stop(self):
        """Stop continuous speech recognition"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        return True

    def get_latest_result(self):
        """Get the latest result from the queue (if no callback was provided)"""
        if not self.results.empty():
            return self.results.get()
        return None

    def _listen_continuously(self):
        """Background thread that listens for speech continuously"""
        try:
            # Setup Vosk model
            model = Model(self.model_path)
            recognizer = KaldiRecognizer(model, 16000)

            # Setup audio stream
            mic = pyaudio.PyAudio()
            stream = mic.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8192
            )
            stream.start_stream()

            print("Continuous speech recognition started...")

            while self.running:
                data = stream.read(4096, exception_on_overflow=False)

                if recognizer.AcceptWaveform(data):
                    # Process final results
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").strip()

                    if text:
                        # Convert to gloss
                        gloss = self.convert_to_sign_gloss(text)

                        # Process result
                        if self.callback:
                            self.callback(text, gloss)
                        else:
                            self.results.put((text, gloss))

                time.sleep(0.01)  # Small sleep to prevent CPU hogging

            # Clean up resources
            stream.stop_stream()
            stream.close()
            mic.terminate()
            print("Continuous speech recognition stopped.")

        except Exception as e:
            error_msg = f"Error in speech recognition: {str(e)}"
            print(error_msg)
            if self.callback:
                self.callback(error_msg, "")
            else:
                self.results.put((error_msg, ""))
            self.running = False


# Example usage with callback function
def process_result(transcript, gloss):
    print(f"Transcript: {transcript}")
    print(f"Sign Gloss: {gloss}")
    print("-" * 40)


# Example usage:
if __name__ == "__main__":
    # With callback
    speech_processor = ContinuousSpeechGloss(callback=process_result)
    speech_processor.start()

    try:
        # Keep the main thread alive
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        speech_processor.stop()
        print("Program terminated by user.")