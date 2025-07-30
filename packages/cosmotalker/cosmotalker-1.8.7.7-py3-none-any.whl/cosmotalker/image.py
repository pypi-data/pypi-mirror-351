def image():
    import tkinter as tk
    import customtkinter as ctk
    from PIL import Image, ImageTk
    import requests
    from io import BytesIO
    import threading
    import webbrowser
    from tkinter import filedialog
    import pyperclip

    def img(name):
        image_dict = {
            "neptune": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Neptune_like_planet_or_mini_neptune_2_1_1_1.png/960px-Neptune_like_planet_or_mini_neptune_2_1_1_1.png?20230920134641",
            "uranus": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Uranus_and_Neptune.jpg/960px-Uranus_and_Neptune.jpg?20230622181218",
            "saturn": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Saturn_square_crop.jpg/960px-Saturn_square_crop.jpg?20220813182013",
            "jupiter": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupiter_%28January_2023%29_%28heic2303e%29.jpg/960px-Jupiter_%28January_2023%29_%28heic2303e%29.jpg?20230416215004",
            "mars": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/MARS_THE_RED_PLANET.jpg/960px-MARS_THE_RED_PLANET.jpg?20210319054849",
            "earth": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Artistic_depiction_of_planet_Earth.jpg/960px-Artistic_depiction_of_planet_Earth.jpg?20201109194112",
            "dog": "https://upload.wikimedia.org/wikipedia/commons/6/6e/Golde33443.jpg",
            "cat": "https://upload.wikimedia.org/wikipedia/commons/3/3a/Cat03.jpg",
            "mercury": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Mercury_render_with_Blender_01.png/800px-Mercury_render_with_Blender_01.png",
            "venus": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Venus_-_December_23_2016.png/960px-Venus_-_December_23_2016.png?20201026180121"
            }
        return image_dict.get(name.lower(), None)
    def image_source(name):
        image_desc_dict = {
            "neptune": "https://commons.wikimedia.org/wiki/File:Neptune_like_planet_or_mini_neptune_2_1_1_1.png",
            "uranus": "https://commons.wikimedia.org/wiki/File:Uranus_and_Neptune.jpg",
            "saturn": "https://commons.wikimedia.org/wiki/File:Saturn_square_crop.jpg",
            "jupiter": "https://commons.wikimedia.org/wiki/File:Jupiter_%28January_2023%29_%28heic2303e%29.jpg",
            "mars": "https://commons.wikimedia.org/wiki/File:MARS_THE_RED_PLANET.jpg",
            "earth": "https://commons.wikimedia.org/wiki/File:Artistic_depiction_of_planet_Earth.jpg",
            "mercury": "https://commons.wikimedia.org/wiki/File:Mercury_render_with_Blender_01.png",
            "dog": "https://commons.wikimedia.org/wiki/File:Golde33443.jpg",
            "cat": "https://commons.wikimedia.org/wiki/File:Cat03.jpg",
            "venus": "https://commons.wikimedia.org/wiki/File:Venus_-_December_23_2016.png"
            }
        return image_desc_dict.get(name.lower(), None)


    # Theme Setup
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("dark-blue")

    class ImageApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Image Viewer with Animation")
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

            self.entry = ctk.CTkEntry(self, placeholder_text="Type: dog, cat, lion...",
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
            disclaimer_text = (
                "Disclaimer: The images shown are fetched from the internet using engines like Google, Bing, "
                "DuckDuckGo, Ecosia, etc. CosmoTalker does not own or claim rights to them. "
                "They are licensed under Creative Commons or similar licenses and credited via the 'Verify Website' button.\n\n"
                "If you're the copyright holder and believe an image is being misused, "
                "contact BHUVANESH M. Upon verification, the image will be removed.\n\n"
                "CosmoTalker is open-source and not monetized."
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
            url = img(keyword)
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
