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

        REM Generate the video from the image sequence
        ffmpeg -y -framerate 60 -i %%04d.png -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p output%%i.mp4

        REM Run the first ffmpeg command to generate the palette
        ffmpeg -y -i output%%i.mp4 -vf "palettegen" palette.png
        
        REM Run the second ffmpeg command to create the GIF with the palette
        ffmpeg -y -i output%%i.mp4 -i palette.png -filter_complex "fps=30,scale=640:-1:flags=lanczos,paletteuse=dither=sierra2_4a" ../gifs/%%i.gif
        
        REM Return to the original directory
        cd ..

        echo Processing completed for folder %%i...
    ) else (
        echo Directory render\%%i does not exist.
    )
)

rd /s /q temp

pause
