def img():
    import tkinter as tk
    import customtkinter as ctk
    from PIL import Image, ImageTk
    import requests
    from io import BytesIO
    import threading
    import webbrowser
    from tkinter import filedialog
    import pyperclip

    def image(name):
        image_dict = {
            "deimos":"https://live.staticflickr.com/5575/14707114439_1ff30dbdd3_c.jpg",
            "phobos":"https://cdn2.picryl.com/photo/2008/04/09/phobos-from-5800-kilometers-color-793655-1024.jpg",
            "moon":"https://images.rawpixel.com/image_800/czNmcy1wcml2YXRlL3Jhd3BpeGVsX2ltYWdlcy93ZWJzaXRlX2NvbnRlbnQvbHIvcGQzNi0xLWdzZmNfMjAxNzEyMDhfYXJjaGl2ZV9lMDAwODY4LWt6cHl3MG90LmpwZw.jpg",
            "neptune": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Sub-neptune.jpg/960px-Sub-neptune.jpg",
            "uranus": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Transparent_Uranus.png/600px-Transparent_Uranus.png",
            "saturn": "https://live.staticflickr.com/7823/45752907895_295bd37423_b.jpg",
            "jupiter": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupiter_%28January_2023%29_%28heic2303e%29.jpg/960px-Jupiter_%28January_2023%29_%28heic2303e%29.jpg?20230416215004",
            "mars": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/MARS_THE_RED_PLANET.jpg/960px-MARS_THE_RED_PLANET.jpg",
            "earth": "https://images.pexels.com/photos/87651/earth-blue-planet-globe-planet-87651.jpeg",
            "dog": "https://upload.wikimedia.org/wikipedia/commons/6/6e/Golde33443.jpg",
            "cat": "https://upload.wikimedia.org/wikipedia/commons/3/3a/Cat03.jpg",
            "mercury": "https://live.staticflickr.com/8374/8497942353_f0756442f5_b.jpg",
            "venus": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Venus.png/600px-Venus.png",
            "sun":"https://live.staticflickr.com/8256/8673066962_f8ffaab262_b.jpg"
            }
        return image_dict.get(name.lower(), None)
    def image_source(name):
        image_desc_dict = {
            "deimos":"https://www.flickr.com/photos/24354425@N03/14707114439",
            "phobos":"https://itoldya420.getarchive.net/media/phobos-from-5800-kilometers-color-793655",
            "moon":"https://www.rawpixel.com/search?page=1&path=1522.sub_topic-4568&sort=curated",
            "neptune": "https://commons.wikimedia.org/wiki/File:Sub-neptune.jpg",
            "uranus": "https://commons.wikimedia.org/wiki/File:Transparent_Uranus.png",
            "saturn": "https://www.flickr.com/photos/nasahubble/45752907895/in/photostream/",
            "jupiter": "https://commons.wikimedia.org/wiki/File:Jupiter_%28January_2023%29_%28heic2303e%29.jpg",
            "mars": "https://commons.wikimedia.org/wiki/File:MARS_THE_RED_PLANET.jpg",
            "earth": "https://www.pexels.com/photo/planet-earth-87651/",
            "mercury": "https://www.flickr.com/photos/gsfc/8497942353",
            "dog": "https://commons.wikimedia.org/wiki/File:Golde33443.jpg",
            "cat": "https://commons.wikimedia.org/wiki/File:Cat03.jpg",
            "venus": "https://commons.wikimedia.org/wiki/File:Venus.png",
            "sun":"https://www.flickr.com/photos/gsfc/8673066962"
            }
        return image_desc_dict.get(name.lower(), None)


    # Theme Setup
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("dark-blue")

    class ImageApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Image Viewer by CosmoTalker")
            self.geometry("650x600")
            self.configure(bg="#1e1e2f")
            self.resizable(True, True)

            self.fullscreen = False
            self.current_image_url = None
            self.current_image_data = None
            self.timer_id = None

            # Fade in/out on open/close
            self.attributes('-alpha', 0.0)
            self.after(0, self.fade_in_window)
            self.protocol("WM_DELETE_WINDOW", self.fade_out_window)

            self.bind("<F11>", self.toggle_fullscreen)
            self.bind("<Escape>", self.exit_fullscreen)

            # UI Widgets
            self.label = ctk.CTkLabel(self, text="Enter Image Name:",
                                      font=("Arial", 20, "bold"), text_color="white")
            self.label.pack(pady=20)

            self.entry = ctk.CTkEntry(self, placeholder_text="Type: Earth, Sun , Neptune ...",
                                      font=("Arial", 16), width=300)
            self.entry.pack(pady=10)
            self.entry.bind('<Return>', lambda event: self.check_input())

            self.button = ctk.CTkButton(self, text="Show Image", width=300,
                                        fg_color="#a020f0", hover_color="#c070f0",
                                        text_color="white", font=("Arial", 16),
                                        command=self.check_input)
            self.button.pack(pady=10)

            self.image_label = tk.Label(self, bg="#1e1e2f")
            self.image_label.pack(pady=20)

            self.url_button = ctk.CTkButton(self, text="Copy Image URL", width=200,
                                            fg_color="#5a4fbf", hover_color="#8675f0",
                                            text_color="white", font=("Arial", 14),
                                            command=self.copy_url, state="disabled")
            self.url_button.pack(pady=5)

            self.download_button = ctk.CTkButton(self, text="Download Image", width=200,
                                                 fg_color="#5a4fbf", hover_color="#8675f0",
                                                 text_color="white", font=("Arial", 14),
                                                 command=self.download_image, state="disabled")
            self.download_button.pack(pady=5)

            self.verify_button = ctk.CTkButton(self, text="Verify Website", width=200,
                                               fg_color="#3b7ddd", hover_color="#5a9eff",
                                               text_color="white", font=("Arial", 14),
                                               command=self.verify_website)
            self.verify_button.pack(pady=5)

            self.toast_label = tk.Label(self, bg="#1e1e2f", fg="lightgreen", font=("Arial", 12))
            self.toast_label.pack_forget()

            # Disclaimer
            disclaimer_text = ('''Disclaimer: The images displayed in this project are fetched from publicly available sources on the internet through search engines such as Google, Bing, DuckDuckGo, Ecosia, and others. These images are not created, owned, or developed by CosmoTalker or its developer. All rights to the images remain with their original creators or copyright holders.\n\n

CosmoTalker is a free and open-source Python library. This project is not monetized in any form. Every image used through the img() function in CosmoTalker is selected only after confirming that it is licensed under a Creative Commons (CC) or similar open license. The links provided through the "Verify Website" button lead directly to the original source of the image, where license information and proper credit can be viewed.\n\n

Although the images are initially used under Creative Commons terms, it is possible that license terms may change over time. In such rare cases, if you are the copyright holder and believe that an image is being used improperly, you may notify the creator of this project (BHUVANESH M), CosmoTalker. Upon appropriate notice and verification, the image will be promptly reviewed and removed.\n\n

Thank you for your understanding and support. CosmoTalker is committed to respecting the rights of all creators, maintaining transparency, and ensuring responsible use of digital content.'''
            )
            self.disclaimer_label = ctk.CTkLabel(self, text=disclaimer_text,
                                                 font=("Arial", 10), text_color="gray", wraplength=600)
            self.disclaimer_label.pack(pady=10)

        # Fade animation
        def fade_in_window(self, alpha=0.0):
            if alpha < 1.0:
                self.attributes('-alpha', alpha)
                self.after(30, lambda: self.fade_in_window(alpha + 0.05))
            else:
                self.attributes('-alpha', 1.0)

        def fade_out_window(self, alpha=1.0):
            if alpha > 0:
                self.attributes('-alpha', alpha)
                self.after(30, lambda: self.fade_out_window(alpha - 0.05))
            else:
                self.destroy()

        def toggle_fullscreen(self, _=None):
            self.fullscreen = not self.fullscreen
            self.attributes('-fullscreen', self.fullscreen)

        def exit_fullscreen(self, _=None):
            self.fullscreen = False
            self.attributes('-fullscreen', False)

        # Fetch & Display
        def check_input(self):
            keyword = self.entry.get().strip().lower()
            url = image(keyword)
            if url:
                self.current_image_url = url
                self.image_label.config(image='', text="Loading...")
                threading.Thread(target=self.load_image, args=(url,)).start()
            else:
                self.image_label.config(image='', text="❌ No image found!", fg="white")
                self.url_button.configure(state="disabled")
                self.download_button.configure(state="disabled")

        def load_image(self, url):
            try:
                response = requests.get(url)
                image = Image.open(BytesIO(response.content)).convert("RGBA")
                image = image.resize((300, 300), Image.LANCZOS)
                self.current_image_data = image
                self.fade_in_image(image, 0.0)
                self.url_button.configure(state="normal")
                self.download_button.configure(state="normal")
            except Exception:
                self.image_label.config(text="⚠️ Error loading image!", fg="white")

        def fade_in_image(self, pil_image, alpha):
            if alpha >= 1.0:
                photo = ImageTk.PhotoImage(pil_image)
                self.image_label.config(image=photo, text='')
                self.image_label.image = photo
            else:
                faded = pil_image.copy()
                faded.putalpha(int(255 * alpha))
                faded = faded.convert("RGBA")
                photo = ImageTk.PhotoImage(faded)
                self.image_label.config(image=photo, text='')
                self.image_label.image = photo
                self.after(50, lambda: self.fade_in_image(pil_image, alpha + 0.1))

        def copy_url(self):
            if self.current_image_url:
                pyperclip.copy(self.current_image_url)
                self.animate_button_text(self.url_button, "✅ URL Copied!", "Copy Image URL", 3000)

        def animate_button_text(self, button, temp_text, original_text, duration_ms):
            button.configure(text=temp_text)
            self.after(duration_ms, lambda: button.configure(text=original_text, text_color="white"))

        def download_image(self):
            if self.current_image_data:
                keyword = self.entry.get().strip().lower()
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png")],
                    initialfile=f"{keyword}_cosmotalker.png",
                    title="Save Image As"
                )
                if file_path:
                    try:
                        self.current_image_data.save(file_path, format="PNG")
                        self.show_toast("✅ Image downloaded successfully!")
                    except Exception:
                        self.show_toast("❌ Failed to save image!")

        def verify_website(self):
            keyword = self.entry.get().strip().lower()
            source_url = image_source(keyword)
            if source_url:
                webbrowser.open(source_url)
                self.show_toast("🌐 Opened source website!")
            else:
                self.show_toast("❌ Source website not found!")

        # Toast Notifications
        def show_toast(self, message):
            if self.timer_id:
                self.after_cancel(self.timer_id)

            self.toast_label.config(text=f"{message} (5s)", fg="lightgreen")
            self.toast_label.pack(pady=10)
            self.timer_counter = 5
            self.update_toast_timer()

            if not hasattr(self, 'close_toast_button'):
                self.close_toast_button = ctk.CTkButton(self, text="Dismiss", width=100,
                                                        fg_color="#ff5555", hover_color="#ff7777",
                                                        command=self.hide_toast)
                self.close_toast_button.pack(pady=5)

        def update_toast_timer(self):
            if self.timer_counter <= 0:
                self.hide_toast()
            else:
                self.toast_label.config(text=self.toast_label.cget("text").split('(')[0] + f" ({self.timer_counter}s)")
                self.timer_counter -= 1
                self.timer_id = self.after(1000, self.update_toast_timer)

        def hide_toast(self):
            self.toast_label.pack_forget()
            if hasattr(self, 'close_toast_button'):
                self.close_toast_button.pack_forget()

    app = ImageApp()
    app.mainloop()
img()