import cv2
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


class ImageToPDFMailer:
    def __init__(self, root):
        self.root = root
        self.root.title("Automata RTC")
        self.root.geometry("400x400")

        self.image_files = []  # List to store multiple image file names
        self.pdf_file = "output.pdf"
        self.so_number = None  # Placeholder for SO number
        self.sr_number = None  # Placeholder for Sr.No

        # UI Elements
        tk.Label(root, text="ABB RTC Automata", font=("Helvetica", 16)).pack(pady=10)
        
        # Add a text field for SO number input
        tk.Label(root, text="Enter SO Number:").pack(pady=5)
        self.so_entry = tk.Entry(root, font=("Helvetica", 14))
        self.so_entry.pack(pady=5)

        # Add a text field for Sr.No input
        tk.Label(root, text="Enter Sr.No:").pack(pady=5)
        self.sr_entry = tk.Entry(root, font=("Helvetica", 14))
        self.sr_entry.pack(pady=5)

        tk.Button(root, text="Capture Images", command=self.capture_images).pack(pady=10)
        tk.Button(root, text="Convert to PDF", command=self.convert_to_pdf).pack(pady=10)
        tk.Button(root, text="Send Email", command=self.send_email).pack(pady=10)

    def capture_images(self):
        """Opens the camera and captures multiple images."""
        camera = cv2.VideoCapture(0)
        count = 0
        while True:
            ret, frame = camera.read()
            if not ret:
                break
            cv2.imshow("Press 'Space' to Capture, 'Esc' to Exit", frame)

            key = cv2.waitKey(1)
            if key == 27:  # Esc to exit
                break
            elif key == 32:  # Space to capture
                image_file = f"captured_image_{count}.jpg"
                cv2.imwrite(image_file, frame)
                self.image_files.append(image_file)
                messagebox.showinfo("Success", f"Image captured as {image_file}")
                count += 1

        camera.release()
        cv2.destroyAllWindows()

    def convert_to_pdf(self):
        """Converts the captured images to a PDF."""
        if not self.image_files:
            messagebox.showerror("Error", "No images found. Please capture images first.")
            return

        # Get the SO number and Sr.No from the entry fields
        self.so_number = self.so_entry.get().strip()
        self.sr_number = self.sr_entry.get().strip()

        if not self.so_number or not self.sr_number:
            messagebox.showerror("Error", "Please enter valid SO Number and Sr.No.")
            return

        # Generate the PDF filename based on the SO number
        self.pdf_file = f"RTC_{self.so_number}_Sr{self.sr_number}.pdf"

        # Convert each image to PDF
        image_list = []
        for image_file in self.image_files:
            if os.path.exists(image_file):
                img = Image.open(image_file)
                img = img.convert("RGB")
                image_list.append(img)

        if image_list:
            image_list[0].save(self.pdf_file, save_all=True, append_images=image_list[1:])
            messagebox.showinfo("Success", f"Images converted to PDF as {self.pdf_file}")
        else:
            messagebox.showerror("Error", "No valid images to convert.")

    def send_email(self):
        """Sends the PDF via Gmail SMTP."""
        if not os.path.exists(self.pdf_file):
            messagebox.showerror("Error", "No PDF found. Please convert images to PDF first.")
            return

        # Get the SO number and Sr.No from the entry fields
        self.so_number = self.so_entry.get().strip()
        self.sr_number = self.sr_entry.get().strip()

        if not self.so_number or not self.sr_number:
            messagebox.showerror("Error", "Please enter valid SO Number and Sr.No.")
            return

        sender_email = "kshetty200319@gmail.com"
        sender_password = "kdpo givc nwoi mnhl"
        recipient_email = "kshetty200319@gmail.com"  # Replace with actual recipient email

        # Email setup
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = f"RTC of SO {self.so_number}, Sr.No {self.sr_number}"

        body = (
            f"Dear Sir,\n\n"
            f"Please find the attached PDF for:\n"
            f"SO Number: {self.so_number}\n"
            f"Sr.No: {self.sr_number}\n\n"
            f"Regards,\nAutomation Team"
        )
        message.attach(MIMEText(body, "plain"))

        # Attach the PDF
        with open(self.pdf_file, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={self.pdf_file}")
            message.attach(part)

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)
            messagebox.showinfo("Success", "Email sent successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {str(e)}")

        # Cleanup
        for image_file in self.image_files:
            if os.path.exists(image_file):
                os.remove(image_file)
        os.remove(self.pdf_file)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageToPDFMailer(root)
    root.mainloop()