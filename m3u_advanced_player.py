import os
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import vlc
import requests

class M3UPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎧 M3U Playlist Player")
        self.root.geometry("950x600")
        self.root.config(bg="#2C3E50")

        self.playlist = []
        self.filtered_playlist = []
        self.current_index = 0
        self.player = vlc.MediaPlayer()
        self.is_playing = False

        self.create_widgets()

    def create_widgets(self):
        # Left and right layout
        self.left_frame = tk.Frame(self.root, bg="#2C3E50")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.right_frame = tk.Frame(self.root, bg="#34495E", width=300)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=20)

        # Title
        self.title_label = tk.Label(self.left_frame, text="🎶 M3U Player", font=("Arial", 28, "bold"), bg="#2C3E50", fg="#F1C40F")
        self.title_label.pack(pady=30)

        # Buttons
        button_style = {"font": ("Arial", 14), "width": 20, "pady": 5}

        self.load_button = tk.Button(self.left_frame, text="📁 Load Local Playlist", command=self.load_playlist, bg="#2980B9", fg="white", **button_style)
        self.load_button.pack(pady=10)

        self.load_url_button = tk.Button(self.left_frame, text="🌐 Load Online Playlist", command=self.load_online_playlist, bg="#1ABC9C", fg="white", **button_style)
        self.load_url_button.pack(pady=10)

        self.play_button = tk.Button(self.left_frame, text="▶️ Play", command=self.toggle_play, bg="#27AE60", fg="white", **button_style)
        self.play_button.pack(pady=10)

        self.stop_button = tk.Button(self.left_frame, text="⏹️ Stop", command=self.stop_music, bg="#C0392B", fg="white", **button_style)
        self.stop_button.pack(pady=10)

        nav_frame = tk.Frame(self.left_frame, bg="#2C3E50")
        nav_frame.pack(pady=10)

        self.prev_button = tk.Button(nav_frame, text="⏮ Prev", command=self.prev_track, bg="#F39C12", fg="white", font=("Arial", 14), width=10)
        self.prev_button.grid(row=0, column=0, padx=5)

        self.next_button = tk.Button(nav_frame, text="Next ⏭", command=self.next_track, bg="#F39C12", fg="white", font=("Arial", 14), width=10)
        self.next_button.grid(row=0, column=1, padx=5)

        # Volume
        self.volume_label = tk.Label(self.left_frame, text="🔊 Volume", font=("Arial", 14), bg="#2C3E50", fg="white")
        self.volume_label.pack(pady=(30, 5))

        self.volume_slider = tk.Scale(self.left_frame, from_=0, to=100, orient=tk.HORIZONTAL, bg="#2C3E50", fg="white",
                                      troughcolor="#1ABC9C", sliderrelief=tk.RAISED, command=self.change_volume)
        self.volume_slider.set(80)
        self.volume_slider.pack()

        # Search bar
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_playlist)

        self.search_entry = tk.Entry(self.right_frame, textvariable=self.search_var, font=("Arial", 12), width=30)
        self.search_entry.pack(pady=5)

        # Playlist display
        self.playlist_label = tk.Label(self.right_frame, text="Playlist", font=("Arial", 16, "bold"), bg="#34495E", fg="#F1C40F")
        self.playlist_label.pack(pady=10)

        self.playlist_frame = tk.Frame(self.right_frame, bg="#34495E")
        self.playlist_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        self.playlist_box = tk.Listbox(self.playlist_frame, bg="#2C3E50", fg="white", width=40, height=25, font=("Arial", 12), activestyle="none")
        self.playlist_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.playlist_frame, command=self.playlist_box.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.playlist_box.config(yscrollcommand=self.scrollbar.set)

        self.playlist_box.bind("<<ListboxSelect>>", self.select_song_from_list)
        self.playlist_box.bind("<Button-3>", self.rename_song_popup)  # Right-click to rename

    def load_playlist(self):
        file_path = filedialog.askopenfilename(filetypes=[("M3U Files", "*.m3u")])
        if file_path:
            self.load_playlist_from_lines(open(file_path, "r").readlines())

    def load_online_playlist(self):
        url = simpledialog.askstring("Load Online Playlist", "Enter the URL of the M3U playlist:")
        if url:
            try:
                response = requests.get(url)
                response.raise_for_status()
                lines = response.text.splitlines()
                self.load_playlist_from_lines(lines)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load playlist:\n{e}")

    def load_playlist_from_lines(self, lines):
        self.playlist = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                self.playlist.append({
                    "path": line,
                    "display_name": os.path.basename(line)
                })
        self.filtered_playlist = self.playlist.copy()
        self.update_playlist_display()

    def update_playlist_display(self):
        self.playlist_box.delete(0, tk.END)
        for item in self.filtered_playlist:
            self.playlist_box.insert(tk.END, item["display_name"])

    def filter_playlist(self, *args):
        search_text = self.search_var.get().lower()
        self.filtered_playlist = [item for item in self.playlist if search_text in item["display_name"].lower()]
        self.update_playlist_display()

    def toggle_play(self):
        if self.is_playing:
            self.player.pause()
            self.is_playing = False
            self.play_button.config(text="▶️ Play")
        else:
            self.play_music()

    def play_music(self):
        if not self.filtered_playlist:
            return
        item = self.filtered_playlist[self.playlist_box.curselection()[0]] if self.playlist_box.curselection() else self.filtered_playlist[self.current_index]
        self.current_index = self.playlist.index(item)
        self.player.stop()
        self.player = vlc.MediaPlayer(item["path"])
        self.player.audio_set_volume(self.volume_slider.get())
        self.player.play()
        self.is_playing = True
        self.play_button.config(text="⏸ Pause")
        self.playlist_box.selection_clear(0, tk.END)
        self.playlist_box.selection_set(self.filtered_playlist.index(item))
        self.playlist_box.see(self.filtered_playlist.index(item))

    def stop_music(self):
        self.player.stop()
        self.is_playing = False
        self.play_button.config(text="▶️ Play")

    def next_track(self):
        if self.filtered_playlist:
            self.current_index = (self.current_index + 1) % len(self.filtered_playlist)
            self.playlist_box.selection_clear(0, tk.END)
            self.playlist_box.selection_set(self.current_index)
            self.play_music()

    def prev_track(self):
        if self.filtered_playlist:
            self.current_index = (self.current_index - 1) % len(self.filtered_playlist)
            self.playlist_box.selection_clear(0, tk.END)
            self.playlist_box.selection_set(self.current_index)
            self.play_music()

    def change_volume(self, value):
        self.player.audio_set_volume(int(value))

    def select_song_from_list(self, event):
        selection = self.playlist_box.curselection()
        if selection:
            index = selection[0]
            item = self.filtered_playlist[index]
            self.current_index = self.playlist.index(item)
            self.play_music()

    def rename_song_popup(self, event):
        widget = event.widget
        try:
            index = widget.nearest(event.y)
            old_name = self.filtered_playlist[index]["display_name"]
            new_name = simpledialog.askstring("Rename Song", "Enter a new display name:", initialvalue=old_name)
            if new_name:
                self.filtered_playlist[index]["display_name"] = new_name
                # Update in original playlist too
                real_index = self.playlist.index(self.filtered_playlist[index])
                self.playlist[real_index]["display_name"] = new_name
                self.update_playlist_display()
                self.playlist_box.selection_set(index)
        except Exception as e:
            print("Rename error:", e)


# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = M3UPlayerApp(root)
    root.mainloop()
