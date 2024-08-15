@echo off

REM Create the temp directory if it doesn't exist
if not exist "temp" (
    mkdir temp
)

if not exist "gifs" (
    mkdir gifs
)

REM Copy all files from the 'combined' folder to the temp directory
if exist "render\combined" (
    xcopy /s /y "render\combined\*" "temp\"
) else (
    echo Directory render\combined does not exist.
)

REM Loop through folders 1 to 20
for /l %%i in (1,1,20) do (
    if exist "render\%%i" (
        xcopy /s /y "render\%%i\*" "temp\"
        
        REM Change directory to temp to process the images
        cd temp

        REM Generate the video from the image sequence with optimized settings
        ffmpeg -y -framerate 60 -i %%04d.png -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p output%%i.mp4

        REM Apply a frame difference filter to detect only changing regions (optimize for static backgrounds)
        ffmpeg -y -i output%%i.mp4 -vf "minterpolate,fps=30,mpdecimate" output_static_optimized%%i.mp4

        REM Generate the palette for the GIF from the optimized video
        ffmpeg -y -i output_static_optimized%%i.mp4 -vf "palettegen=max_colors=256" palette.png
        
        REM Create the GIF using the palette, optimized for static backgrounds and 30 FPS
        ffmpeg -y -i output_static_optimized%%i.mp4 -i palette.png -filter_complex "fps=30,scale=640:-1:flags=lanczos,paletteuse=dither=sierra2_4a" -gifflags +transdiff ../gifs/%%i.gif

        
        REM Return to the original directory
        cd ..

        echo Processing completed for folder %%i...
    ) else (
        echo Directory render\%%i does not exist.
    )
)

rd /s /q temp

pause
