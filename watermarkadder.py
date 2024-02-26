import os
from moviepy.editor import VideoFileClip, AudioFileClip, clips_array
import cv2
import numpy as np
def process_frame(frame, lgo, logo_position, move_up):

    ovr = np.zeros_like(frame)

    if move_up:
        logo_position[1] -= 1
        if logo_position[1] < 0:
            logo_position[1] = 0
            move_up = False
    else:
        logo_position[1] += 1
        if logo_position[1] > frame.shape[0] - lgo.shape[0]:
            logo_position[1] = frame.shape[0] - lgo.shape[0]
            move_up = True

    ovr[logo_position[1]:logo_position[1] + lH, logo_position[0]:logo_position[0] + lW] += lgo


    umat_frame = cv2.UMat(frame)
    ovr_umat = cv2.UMat(ovr)
    frame = cv2.addWeighted(ovr_umat, 0.5, umat_frame, 1.0, 0, umat_frame)
    frame = umat_frame.get()


    return frame, move_up

def process_video(video_path, output_path, audio_output_path):
    video_clip = VideoFileClip(video_path)


    lgo_img = cv2.imread('onlyluxuryvip2.png', cv2.IMREAD_UNCHANGED)
    global lgo
    lgo = cv2.cvtColor(lgo_img, cv2.COLOR_BGRA2BGR)  

    new_width = 200
    aspect_ratio = lgo.shape[1] / float(lgo.shape[0])
    lgo = cv2.resize(lgo, (new_width, int(new_width / aspect_ratio)), interpolation=cv2.INTER_AREA)

    global lH, lW
    lH, lW = lgo.shape[:2]

    logo_position = [video_clip.size[0] - lW - 10, video_clip.size[1] - lH - 60]
    move_up = True

    def process_frame_wrapper(gf, t):
        nonlocal move_up
        frame = gf(t)
        frame, move_up = process_frame(frame, lgo, logo_position, move_up)
        return frame

    processed_clip = video_clip.fl(process_frame_wrapper)

    audio_clip = video_clip.audio
    audio_path = audio_output_path + '/' + os.path.basename(video_path) + '_o.mp3'
    audio_clip.write_audiofile(audio_path, codec='mp3')

    audio_clip = AudioFileClip(audio_path)

    final_clip = clips_array([[processed_clip.set_audio(audio_clip)]])

    final_output_path = output_path + '/' + os.path.basename(video_path) + '_d.mp4'
    final_clip.write_videofile(final_output_path, codec='libx264', audio_codec='aac')

    print(f"Video {os.path.basename(video_path)} başarıyla işlendi.")

if __name__ == "__main__":
    input_folder = 'videos'
    output_folder = 'islenmisvideolar'
    audio_output_folder = 'sesler'

    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(audio_output_folder, exist_ok=True)

    video_files = [f for f in os.listdir(input_folder) if f.endswith('.mp4')]
    for video_file in video_files:
        video_path = os.path.join(input_folder, video_file)
        process_video(video_path, output_folder, audio_output_folder)
