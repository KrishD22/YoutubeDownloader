import tkinter as tk
import customtkinter
from tkinter import filedialog
from pytube import YouTube
from threading import Thread
import json
import os

class YouTubeDownloaderApp:
    def __init__(self):
        # System Settings
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")
        

        # App frame
        self.app = customtkinter.CTk()
        self.app.geometry("1080x800")
        self.app.title("YouTube Downloader")

        # Adding UI elements
        self.title = customtkinter.CTkLabel(self.app, text="Insert a YouTube link", font=("Arial", 20, "bold"))
        self.title.pack(padx=10, pady=10)

        # Link Input
        self.url_var = tk.StringVar()
        self.link = customtkinter.CTkEntry(self.app, width=450, height=40, textvariable=self.url_var, font=("Arial", 14))
        self.link.pack(pady=10)

        # Queue Listbox
        self.queue_label = customtkinter.CTkLabel(self.app, text="Queue", font=("Arial", 16, "bold"))
        self.queue_label.pack(pady=5)
        self.queue_listbox = tk.Listbox(self.app, width=50, height=10, font=("Arial", 12))
        self.queue_listbox.pack(pady=10)

        # Finished Downloading
        self.finish_label = customtkinter.CTkLabel(self.app, text="", font=("Arial", 14))
        self.finish_label.pack(pady=5)

        # Progress Percentage
        self.progress_percentage = customtkinter.CTkLabel(self.app, text="0%", font=("Arial", 14))
        self.progress_percentage.pack(pady=5)

        self.progress_bar = customtkinter.CTkProgressBar(self.app, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(padx=10, pady=10)

        # Download Button
        self.download_button = customtkinter.CTkButton(self.app, text="Add to Queue", command=self.add_to_queue, font=("Arial", 14, "bold"))
        self.download_button.pack(padx=10, pady=10)

        # Start Downloading Button
        self.start_button = customtkinter.CTkButton(self.app, text="Start Downloading", command=self.start_download, font=("Arial", 14, "bold"))
        self.start_button.pack(padx=10, pady=10)

        # Remove from Queue Button
        self.remove_button = customtkinter.CTkButton(self.app, text="Remove from Queue", command=self.remove_from_queue, font=("Arial", 14, "bold"))
        self.remove_button.pack(padx=10, pady=10)

        # Select Download Location Button
        self.location_button = customtkinter.CTkButton(self.app, text="Select Download Location", command=self.select_download_location, font=("Arial", 14, "bold"))
        self.location_button.pack(padx=10, pady=10)

        # Download Location Label
        self.download_location_label = customtkinter.CTkLabel(self.app, text="Download Location: Not Selected", font=("Arial", 14))
        self.download_location_label.pack(pady=5)

        # List to store video URLs and titles
        self.video_urls = []
        self.video_titles = []

        # Load previous queue state and settings
        self.load_queue()
        self.load_settings()

    def add_to_queue(self):
        yt_link = self.url_var.get()
        if yt_link:
            try:
                yt_object = YouTube(yt_link)
                self.video_urls.append(yt_link)
                self.video_titles.append(yt_object.title)
                self.queue_listbox.insert(tk.END, yt_object.title)
                self.finish_label.configure(text=f"Added to queue: {yt_object.title}", text_color="blue")
                self.url_var.set("")
                self.save_queue()
            except Exception as e:
                self.finish_label.configure(text="Invalid URL", text_color="red")

    def remove_from_queue(self):
        selected_indices = self.queue_listbox.curselection()
        for index in selected_indices[::-1]:  # Reverse to avoid index shifting issues
            self.queue_listbox.delete(index)
            del self.video_urls[index]
            del self.video_titles[index]
        self.finish_label.configure(text="Removed selected items from queue", text_color="blue")
        self.save_queue()

    def start_download(self):
        self.finish_label.configure(text="Downloading...", text_color="white")
        download_thread = Thread(target=self.download_videos)
        download_thread.start()

    def download_videos(self):
        for yt_link in self.video_urls:
            try:
                yt_object = YouTube(yt_link, on_progress_callback=self.on_progress)
                video = yt_object.streams.get_highest_resolution()

                self.title.configure(text=yt_object.title, text_color="white")
                self.finish_label.configure(text="")

                video.download(output_path=self.download_location)
                self.finish_label.configure(text=f"Downloaded: {yt_object.title}", text_color="green")
            except Exception as e:
                self.finish_label.configure(text="Download Error", text_color="red")
            
        self.finish_label.configure(text="All videos downloaded", text_color="green")
        self.video_urls.clear()
        self.video_titles.clear()
        self.queue_listbox.delete(0, tk.END)
        self.save_queue()

    def on_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage_of_completion = bytes_downloaded / total_size * 100
        per = str(int(percentage_of_completion))
        self.progress_percentage.configure(text=per + '%')
        self.progress_percentage.update()

        # Update progress bar
        self.progress_bar.set(float(percentage_of_completion) / 100)

    def select_download_location(self):
        self.download_location = filedialog.askdirectory()
        if self.download_location:
            self.download_location_label.configure(text=f"Download Location: {self.download_location}")
            self.save_settings()

    def save_queue(self):
        queue_data = {
            'video_urls': self.video_urls,
            'video_titles': self.video_titles
        }
        with open('queue_data.json', 'w') as f:
            json.dump(queue_data, f)

    def load_queue(self):
        if os.path.exists('queue_data.json'):
            with open('queue_data.json', 'r') as f:
                queue_data = json.load(f)
                self.video_urls = queue_data.get('video_urls', [])
                self.video_titles = queue_data.get('video_titles', [])
                for title in self.video_titles:
                    self.queue_listbox.insert(tk.END, title)

    def save_settings(self):
        settings_data = {
            'download_location': self.download_location
        }
        with open('settings.json', 'w') as f:
            json.dump(settings_data, f)

    def load_settings(self):
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                settings_data = json.load(f)
                self.download_location = settings_data.get('download_location', '')
                if self.download_location:
                    self.download_location_label.configure(text=f"Download Location: {self.download_location}")
                else:
                    self.download_location_label.configure(text="Download Location: Not Selected")

    def run(self):
        self.app.mainloop()

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.run()
