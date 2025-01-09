import sys
import cv2
import os
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
from zipfile import ZipFile
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QMessageBox

# Configuration for Gmail SMTP
email_sender = 'kshetty200319@gmail.com'  # Sender's email
email_password = 'kdpo givc nwoi mnhl'  # App-specific password
email_receivers = ['kshetty200319@gmail.com', 'kshetty2003@gmail.com', 'krrish.shetty@ggsf.edu.in', 'amanyadav16544@gmail.com']  # List of receiver emails
smtp_server = 'smtp.gmail.com'
smtp_port = 587

# Paths
image_folder = 'captured_images/'
video_avi_path = 'captured_video.avi'
video_mp4_path = 'captured_video.mp4'
compressed_images_path = 'compressed_images.zip'

# Create directory for images
os.makedirs(image_folder, exist_ok=True)

class DesktopApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('ABB Dispatch Automata')
        self.setGeometry(100, 100, 400, 400)
        
        layout = QVBoxLayout()
        
        # User Inputs
        self.label_sr_no = QLabel('Enter Sr. No:')
        layout.addWidget(self.label_sr_no)
        self.sr_no_input = QLineEdit()
        layout.addWidget(self.sr_no_input)
        
        self.label_sales_order = QLabel('Enter Sales Order Number:')
        layout.addWidget(self.label_sales_order)
        self.sales_order_input = QLineEdit()
        layout.addWidget(self.sales_order_input)
        
        self.image_count_label = QLabel('Enter Number of Images to Capture:')
        layout.addWidget(self.image_count_label)
        self.image_count_input = QLineEdit()
        layout.addWidget(self.image_count_input)
        
        # Start Button
        self.btn = QPushButton('Start Capture')
        self.btn.clicked.connect(self.startAutomation)
        layout.addWidget(self.btn)
        
        self.setLayout(layout)
        
    def capture_images_and_video(self):
        try:
            num_images = int(self.image_count_input.text())
        except ValueError:
            self.show_message("Error", "Please enter a valid number of images.")
            return

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.show_message("Error", "Could not open video capture.")
            return

        cv2.namedWindow('Camera Feed', cv2.WINDOW_NORMAL)
        image_counter = 0

        # Capture images manually by pressing the spacebar
        while image_counter < num_images:
            ret, frame = cap.read()
            if not ret:
                self.show_message("Error", "Could not read frame.")
                break

            cv2.imshow('Camera Feed', frame)

            key = cv2.waitKey(1)
            if key == ord(' '):  # Spacebar key
                image_path = f'{image_folder}image_{image_counter}.jpg'
                cv2.imwrite(image_path, frame)
                self.show_message("Success", f"Image {image_counter + 1} saved.")
                image_counter += 1

        # Start recording video after capturing images
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(video_avi_path, fourcc, 20.0, (640, 480))
        start_time = time.time()
        video_duration = 15  # Duration of the video in seconds

        while (time.time() - start_time) < video_duration:
            ret, frame = cap.read()
            if not ret:
                self.show_message("Error", "Could not read frame.")
                break
            out.write(frame)
            cv2.imshow('Camera Feed', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):  # Quit video recording early
                break

        cap.release()
        out.release()
        cv2.destroyAllWindows()

        # Convert the .avi file to .mp4
        self.convert_avi_to_mp4()

    def convert_avi_to_mp4(self):
        cap = cv2.VideoCapture(video_avi_path)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_mp4_path, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)

        cap.release()
        out.release()

    def compress_files(self):
        with ZipFile(compressed_images_path, 'w') as zipf:
            for root, dirs, files in os.walk(image_folder):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), image_folder))

    def send_email(self):
        sr_no = self.sr_no_input.text()
        sales_order = self.sales_order_input.text()

        msg = MIMEMultipart()
        msg['From'] = email_sender
        msg['To'] = ', '.join(email_receivers)  # Join multiple email addresses with a comma
        msg['Subject'] = f'Captured files of Dispatch for Sr. No {sr_no} - Sales Order #{sales_order}'

        body = (
            f"Dear Sir,\n\n"
            f"Please find the captured images and video attached for the following details:\n\n"
            f"Sr. No: {sr_no}\n"
            f"Sales Order Number: {sales_order}\n\n"
            f"Thank you.\n\n"
            f"Regards,\n"
            f"Automation Team"
        )
        msg.attach(MIMEText(body, 'plain'))

        with open(compressed_images_path, 'rb') as file:
            part = MIMEBase('application', 'zip')
            part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={compressed_images_path}')
            msg.attach(part)

        with open(video_mp4_path, 'rb') as file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={video_mp4_path}')
            msg.attach(part)

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(email_sender, email_password)
                server.send_message(msg)
                self.show_message("Success", "Email sent successfully!")
        except Exception as e:
            self.show_message("Failed", f'Failed to send email: {e}')

    def clean_up(self):
        if os.path.exists(video_avi_path):
            os.remove(video_avi_path)
        if os.path.exists(video_mp4_path):
            os.remove(video_mp4_path)
        if os.path.exists(compressed_images_path):
            os.remove(compressed_images_path)
        if os.path.exists(image_folder):
            for file in os.listdir(image_folder):
                os.remove(os.path.join(image_folder, file))
            os.rmdir(image_folder)

    def startAutomation(self):
        if not self.sr_no_input.text():
            self.show_message("Error", "Please enter a Sr. No.")
            return
        if not self.sales_order_input.text():
            self.show_message("Error", "Please enter a Sales Order Number.")
            return
        self.capture_images_and_video()
        self.compress_files()
        self.send_email()
        self.clean_up()
        self.show_message("Completed", "Automation process completed successfully!")

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DesktopApp()
    ex.show()
    sys.exit(app.exec_())