import sys
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import pickle
import os
from urllib.parse import urlparse
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QTextEdit, QLabel, QRadioButton,
                            QProgressBar, QMessageBox, QScrollArea, QFrame)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor

class MisinformationDetector:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.pipeline = None
        self.load_or_create_model()
    
    def load_or_create_model(self):
        """Load existing model or create a new one with sample training data"""
        model_file = 'misinformation_model.pkl'
        
        if os.path.exists(model_file):
            try:
                with open(model_file, 'rb') as f:
                    self.pipeline = pickle.load(f)
                print("Model loaded successfully!")
                return
            except:
                print("Error loading model, creating new one...")
        
        # Create sample training data (in real application, use larger dataset)
        # This is a simplified example - you should use real misinformation datasets
        training_texts = [
            "Scientists have confirmed that vaccines are safe and effective",
            "The earth is round as proven by centuries of scientific evidence",
            "Climate change is supported by overwhelming scientific consensus",
            "Regular exercise and healthy diet improve overall health",
            "Smoking increases risk of lung cancer according to medical studies",
            "The government is putting microchips in vaccines to track people",
            "The earth is flat and NASA is lying to everyone",
            "Climate change is a hoax created by politicians",
            "Drinking bleach can cure coronavirus",
            "5G towers are spreading deadly radiation and causing illness",
            "All mainstream media is fake news controlled by secret societies",
            "Essential oils can cure any disease including cancer",
            "The moon landing was filmed in a Hollywood studio",
            "Chemtrails are government mind control chemicals",
            "Ancient aliens built the pyramids because humans are too primitive"
        ]
        
        # Labels: 0 = reliable information, 1 = misinformation
        training_labels = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        
        # Create and train the model
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, stop_words='english')),
            ('classifier', MultinomialNB())
        ])
        
        self.pipeline.fit(training_texts, training_labels)
        
        # Save the model
        with open(model_file, 'wb') as f:
            pickle.dump(self.pipeline, f)
        
        print("New model created and saved!")
    
    def predict(self, text):
        """Predict if text is misinformation"""
        if not text.strip():
            return 0.5, "No content to analyze"
        
        # Get prediction probability
        prob = self.pipeline.predict_proba([text])[0]
        misinformation_prob = prob[1]
        
        # Determine result
        if misinformation_prob > 0.7:
            result = "HIGH RISK - Likely Misinformation"
        elif misinformation_prob > 0.4:
            result = "MODERATE RISK - Requires Verification"
        else:
            result = "LOW RISK - Appears Reliable"
        
        return misinformation_prob, result

class WebScraperThread(QThread):
    content_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
    
    def run(self):
        try:
            # Validate URL
            parsed = urlparse(self.url)
            if not parsed.scheme:
                self.url = 'http://' + self.url
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit text length for processing
            if len(text) > 5000:
                text = text[:5000] + "..."
            
            self.content_ready.emit(text)
            
        except requests.RequestException as e:
            self.error_occurred.emit(f"Error fetching URL: {str(e)}")
        except Exception as e:
            self.error_occurred.emit(f"Error processing content: {str(e)}")

class AnalysisThread(QThread):
    analysis_complete = pyqtSignal(float, str)
    
    def __init__(self, detector, content):
        super().__init__()
        self.detector = detector
        self.content = content
    
    def run(self):
        prob, result = self.detector.predict(self.content)
        self.analysis_complete.emit(prob, result)

class MisinformationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.detector = MisinformationDetector()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("AI Misinformation Detector")
        self.setGeometry(100, 100, 1000, 700)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #3c3c3c;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
            }
            QPushButton {
                background-color: #0084ff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0066cc;
            }
            QPushButton:pressed {
                background-color: #004499;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            QRadioButton {
                color: #ffffff;
                font-size: 11px;
            }
            QProgressBar {
                border: 2px solid #555555;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0084ff;
                border-radius: 3px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("AI-Powered Misinformation Detection System")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #0084ff; margin: 20px;")
        layout.addWidget(title)
        
        # Input selection
        input_frame = QFrame()
        input_frame.setStyleSheet("QFrame { border: 1px solid #555555; border-radius: 5px; padding: 10px; }")
        input_layout = QVBoxLayout(input_frame)
        
        input_label = QLabel("Choose Input Type:")
        input_label.setFont(QFont("Arial", 12, QFont.Bold))
        input_layout.addWidget(input_label)
        
        radio_layout = QHBoxLayout()
        self.url_radio = QRadioButton("URL Link")
        self.content_radio = QRadioButton("Direct Content")
        self.url_radio.setChecked(True)
        radio_layout.addWidget(self.url_radio)
        radio_layout.addWidget(self.content_radio)
        input_layout.addLayout(radio_layout)
        
        layout.addWidget(input_frame)
        
        # Input area
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Enter URL or paste content here...")
        self.input_text.setMaximumHeight(150)
        layout.addWidget(self.input_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.analyze_button = QPushButton("Analyze Content")
        self.clear_button = QPushButton("Clear All")
        
        self.analyze_button.clicked.connect(self.analyze_content)
        self.clear_button.clicked.connect(self.clear_all)
        
        button_layout.addWidget(self.analyze_button)
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Results area
        results_frame = QFrame()
        results_frame.setStyleSheet("QFrame { border: 1px solid #555555; border-radius: 5px; padding: 10px; }")
        results_layout = QVBoxLayout(results_frame)
        
        self.content_label = QLabel("Content Preview:")
        self.content_label.setFont(QFont("Arial", 12, QFont.Bold))
        results_layout.addWidget(self.content_label)
        
        # Scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        
        self.content_display = QTextEdit()
        self.content_display.setReadOnly(True)
        self.content_display.setPlaceholderText("Content will appear here after analysis...")
        scroll_area.setWidget(self.content_display)
        results_layout.addWidget(scroll_area)
        
        # Analysis result
        self.result_label = QLabel("Analysis Result:")
        self.result_label.setFont(QFont("Arial", 12, QFont.Bold))
        results_layout.addWidget(self.result_label)
        
        self.result_display = QLabel("No analysis performed yet.")
        self.result_display.setStyleSheet("""
            QLabel {
                background-color: #3c3c3c;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.result_display.setWordWrap(True)
        results_layout.addWidget(self.result_display)
        
        layout.addWidget(results_frame)
        
        # Status label
        self.status_label = QLabel("Ready to analyze content")
        self.status_label.setStyleSheet("color: #888888; font-style: italic;")
        layout.addWidget(self.status_label)
    
    def analyze_content(self):
        input_text = self.input_text.toPlainText().strip()
        if not input_text:
            QMessageBox.warning(self, "Warning", "Please enter a URL or content to analyze.")
            return
        
        self.analyze_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        if self.url_radio.isChecked():
            self.status_label.setText("Fetching content from URL...")
            self.scraper_thread = WebScraperThread(input_text)
            self.scraper_thread.content_ready.connect(self.on_content_ready)
            self.scraper_thread.error_occurred.connect(self.on_scraper_error)
            self.scraper_thread.start()
        else:
            self.on_content_ready(input_text)
    
    def on_content_ready(self, content):
        self.content_display.setPlainText(content)
        self.status_label.setText("Analyzing content for misinformation...")
        
        self.analysis_thread = AnalysisThread(self.detector, content)
        self.analysis_thread.analysis_complete.connect(self.on_analysis_complete)
        self.analysis_thread.start()
    
    def on_analysis_complete(self, probability, result):
        self.progress_bar.setVisible(False)
        self.analyze_button.setEnabled(True)
        
        # Color code the result
        if "HIGH RISK" in result:
            color = "#ff4444"  # Red
        elif "MODERATE RISK" in result:
            color = "#ffaa00"  # Orange
        else:
            color = "#44ff44"  # Green
        
        self.result_display.setStyleSheet(f"""
            QLabel {{
                background-color: #3c3c3c;
                border: 2px solid {color};
                border-radius: 5px;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                color: {color};
            }}
        """)
        
        result_text = f"{result}\n\nConfidence Score: {probability:.2%}"
        self.result_display.setText(result_text)
        self.status_label.setText("Analysis complete")
    
    def on_scraper_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.analyze_button.setEnabled(True)
        self.status_label.setText("Error occurred")
        QMessageBox.critical(self, "Error", error_msg)
    
    def clear_all(self):
        self.input_text.clear()
        self.content_display.clear()
        self.result_display.setText("No analysis performed yet.")
        self.result_display.setStyleSheet("""
            QLabel {
                background-color: #3c3c3c;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
            }
        """)
        self.status_label.setText("Ready to analyze content")

def main():
    app = QApplication(sys.argv)
    window = MisinformationApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
