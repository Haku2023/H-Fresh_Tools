import subprocess
import glob
import datetime
import cv2
import os
import re
import tkinter as tk
from tkinter import filedialog
from tkVideoPlayer import TkinterVideo
from pathlib import Path





def main():
    # Create a Tkinter window
    window = tk.Tk()
    window.title("Animation Program")
    window.configure(bg="#79D7BE")  


    # Set the window size and position
    global screen_width
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x_percent = 0.25
    y_percent = 0.25

    x_offset = screen_width * x_percent
    y_offset = screen_height * y_percent

    window.geometry(f"{screen_width // 2}x{screen_height // 2}+{int(x_offset)}+{int(y_offset)}")
    window.grid_rowconfigure(0, weight=1)
    window.grid_rowconfigure(1, weight=6)

    title_frame = tk.Frame(window, bg="#79D7BE")
    title_frame.pack(fill="x")
    title_frame.grid_columnconfigure(0, weight=1000)
    title_frame.grid_columnconfigure(1, weight=1)
    title_word = tk.Label(title_frame,text="Welcome to the Animation Service",font="Impact 48",bg="#79D7BE")
    title_word.grid(row=0,column=0,sticky="nsew")
    
    Author_label = tk.Label(title_frame,text="by Haku",font="Modern 18 bold",bg="#79D7BE")
    Author_label.grid(row=0,column=1,sticky="se")

    content_frame = tk.Frame(window, bg="#79D7BE")
    content_frame.pack(expand=True, fill="both")

    content_frame.grid_columnconfigure(0, weight=1)
    content_frame.grid_columnconfigure(1, weight=1)
    content_frame.grid_rowconfigure(0, weight=1)


    left_frame = tk.Frame(content_frame, bg="#2E5077")
    left_frame.grid( row = 0, column = 0, padx=5,pady=5,sticky="nsew")

    global right_frame
    right_frame = tk.Frame(content_frame, bg="#4DA1A9")
    right_frame.grid( row = 0, column = 1, padx=5,pady=5, sticky="nsew")

    left_frame.grid_rowconfigure(0, weight=1)
    left_frame.grid_rowconfigure(1, weight=2)
    left_frame.grid_rowconfigure(2, weight=1)
    left_frame.grid_rowconfigure(3, weight=2)
    left_frame.grid_rowconfigure(4, weight=3)
    left_frame.grid_rowconfigure(5, weight=1)
    left_frame.grid_columnconfigure(0, weight=1)


    # Label to display the selected folder path
    global folder_label 
    folder_label = tk.Label(left_frame, text="Step 1: Select a Folder", font=("Comic Sans MS", 24,"bold"),fg="white",bg="#2E5077")
    folder_label.grid(row=0, sticky="w")


    select_button = tk.Button(left_frame, text="Select Images Folder", command=select_folder, bg="#FFF5D7",bd=5,font=("Segoe UI Black" ,24))
    select_button.grid(row=1, sticky="sn")

    # Label to prompt the fps input
    fps_label = tk.Label(left_frame, text="Step 2: Enter the fps (frame/s)", font=("Comic Sans MS", 24,"bold"),fg="white",bg="#2E5077")
    fps_label.grid(row=2, sticky="w")

    # Input field for user to enter fps
    global input_entry
    input_entry = tk.Entry(left_frame,font="Times 24")
    input_entry.grid(row=3,column=0)

    fps_unit = tk.Label(left_frame, text="fps", font=("Comic Sans MS", 24,"bold"),fg="white",bg="#2E5077")
    fps_unit.grid(row=3, column=0,padx=(300,0))


    select_button = tk.Button(left_frame, text="Generate Animation", command=animation, font=("Segoe UI Black", 24),bg = "#F5F0CD",bd=5)
    select_button.grid(row=4, sticky="sn")

    global output_message
    output_message = tk.Label(left_frame, text="Here is the output", font=("Comic Sans MS", 24, "bold"),fg="white",bg="#2E5077")
    output_message.grid(row=5, sticky="w")

    explorer_button = tk.Button(right_frame, text="Open Movie Folder Location", command=open_movie_folder, font=("Segoe UI Black",24),bg="#FFB38E",bd=10)
    explorer_button.pack(side="top",pady=10)   

    global video_frame
    video_frame = tk.Frame(right_frame, bg="white")
    video_frame.pack(expand=True, fill="both")
    video_frame.pack_propagate(False)

    window.mainloop()

def select_folder():
    # Open a  folder selection dialog and get the selected folder path
    global selected_folder
    selected_folder = filedialog.askdirectory()

# definition of video functions
def seek(event=None):
    """ used to seek a specific timeframe """
    vid_player.seek(int(video_slider.get()))


def skip(value: int):
    """ skip seconds """
    vid_player.seek(int(video_slider.get())+value)
    video_slider.set(video_slider.get() + value)

def play_pause():
    """ pauses and plays """
    if vid_player.is_paused():
        vid_player.play()
        video_play_pause_btn["text"] = "Pause"

    else:
        vid_player.pause()
        video_play_pause_btn["text"] = "Play"

def video_ended(event):
    """ handle video ended """
    video_slider.set(video_slider["to"])
    video_play_pause_btn["text"] = "Play"
    video_slider.set(0)

def update_duration(event):
    """ updates the duration after finding the duration """
    duration = vid_player.video_info()["duration"]
    slider_end_time["text"] = str(datetime.timedelta(seconds=duration))
    video_slider["to"] = duration


def update_scale(event):
    """ updates the scale value """
    video_slider.set(vid_player.current_duration())

def animation():
    global output_message
    # Get the user input of fps
    fps = input_entry.get() #the fps which means how many pictures in one second
    if not fps.isdigit() or int(fps) <= 0:
        output_message.config(text = "Please enter a valid fps")
        return
    elif not selected_folder:
        output_message.config(text = "Please select a folder")
        return 


    base_location = selected_folder

    location_Vis = f'{base_location}/*.jpg' #here is the vis location, need begin with DATA
    info = location_Vis.rsplit('/',4)[1]   
    movie_folder_path =  location_Vis.rsplit('/',2)[0]  + '/movie/'
    make_animation(location_Vis,movie_folder_path,info,int(fps))

def extract_information(filepath):
    key = "OUT_DIR"
    with open(filepath, 'r') as file:
        for line in file:
            if key in line:
                # Extract the last segment after the last '/' in the path
                extracted_part = line.rstrip().split('/')[-1]
                return extracted_part
    return None  # Return None if OUT_DIR is not found

def extract_numeric_part(filename):
    match = re.search(r't(\d+)', filename)  # Extract numeric part using regex
    if match:
        return int(match.group(1))  # Convert the matched string to an integer
    return 0  # Default value if no numeric part is found

def make_animation(filesname,movie_folder_path,info,fps):

    for widget in video_frame.winfo_children():
        widget.destroy()

    img_array = []

    sorted_filenames = sorted(glob.glob(filesname), key=extract_numeric_part)
    for filename in sorted_filenames: 
        img = cv2.imread(filename)
        height, width  = img.shape[:2]
        size = (width, height)
        img_array.append(img)

    # Check if the folder already exists, if not, create it
    if not os.path.exists(movie_folder_path):
        os.makedirs(movie_folder_path)
    global movie_file_path
    movie_file_path = movie_folder_path + info + '.mp4'
    out = cv2.VideoWriter(movie_file_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, size)
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()
    # Add video components

    output_message.config(text = f"Successful!!")

    player_frame = tk.Frame(video_frame, bg="black",width=(screen_width)//4.5,height=(screen_width)//4.5/4*3)
    player_frame.pack()
    player_frame.pack_propagate(False)

    global vid_player
    vid_player  = TkinterVideo(master=player_frame, scaled=True)
    vid_player.pack(expand=True, fill="both")

    global video_play_pause_btn
    video_play_pause_btn = tk.Button(video_frame, text="Play",font=("Segoe UI Black",14),bd=3,relief="solid", command=play_pause)
    video_play_pause_btn.pack(side="top")

    video_slider_frame = tk.Frame(video_frame, bg="white")
    video_slider_frame.pack(side="top", fill="x", expand=True)

    video_skip_minus_5sec = tk.Button(video_slider_frame, text="-5s", command=lambda: skip(-5),bd=2,relief="solid",bg="#FBFBFB",font=("Segoe UI Black",14))
    video_skip_minus_5sec.pack(side="left")

    video_start_time = tk.Label(video_slider_frame, text=str(datetime.timedelta(seconds=0)))
    video_start_time.pack(side="left")

    global video_slider
    video_slider = tk.Scale(video_slider_frame, from_=0, to=0, orient="horizontal")
    video_slider.bind("<ButtonRelease-1>", seek)
    video_slider.pack(side="left", fill="x", expand=True)

    global slider_end_time
    slider_end_time = tk.Label(video_slider_frame, text=str(datetime.timedelta(seconds=0)))
    slider_end_time.pack(side="left")

    video_skip_plus_5sec = tk.Button(video_slider_frame, text="+5s",bg="#FBFBFB", command=lambda: skip(5),bd=3,font=("Segoe UI Black",14),relief="solid")
    video_skip_plus_5sec.pack(side="left")

    vid_player.bind("<<Duration>>", update_duration)
    vid_player.bind("<<SecondChanged>>", update_scale)
    vid_player.bind("<<Ended>>", video_ended )

    vid_player.load(rf"{movie_file_path}")
    video_slider.config(to=0, from_=0)
    video_slider.set(0)
    vid_player.play()
    video_play_pause_btn["text"] = "Pause"

def open_movie_folder():
    # Open the movie folder in the file explorer
    open_movie_folder_path = movie_file_path.replace("/", "\\")
    subprocess.Popen(f'explorer /select,{open_movie_folder_path}')

if __name__ == "__main__":
    main()
